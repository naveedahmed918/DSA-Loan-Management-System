"""End-to-end check of the DSA loan flow (Blueprint fields). Everything runs in one transaction and is rolled back.

Run from the bench:  cd sites && ../env/bin/python ../apps/dsa_loan/scripts/e2e_flow_test.py dsaloan.localhost
"""
import sys

import frappe
from frappe.utils import add_days, nowdate

SITE = sys.argv[1] if len(sys.argv) > 1 else "dsaloan.localhost"
results = []


def check(label, cond, detail=""):
	results.append((label, bool(cond), detail))
	print(("PASS " if cond else "FAIL ") + label + (f"  [{detail}]" if detail else ""))


def expect_error(label, fn):
	try:
		fn()
	except frappe.ValidationError as e:
		frappe.clear_messages()
		check(label, True, str(e)[:90])
		return
	check(label, False, "no error raised")


def doc(d):
	return frappe.get_doc(d).insert()


def bare(doctype, name, **values):
	"""Insert a minimal ERPNext record without its hooks (rolled back at the end)."""
	if frappe.db.exists(doctype, name):
		return name
	d = frappe.get_doc(dict(doctype=doctype, **values))
	d.name = name
	d.db_insert()
	return name


def status(doctype, name, field):
	return frappe.db.get_value(doctype, name, field)


def run():
	today = nowdate()
	company = frappe.db.get_value("Company", {}) or bare("Company", "E2E DSA Test Co", company_name="E2E DSA Test Co", abbr="E2E", default_currency="INR", country="India")
	agent = bare("Employee", "E2E-EMP-0001", first_name="E2E Agent", employee_name="E2E Agent", company=company, status="Active")

	# ---------- masters ----------
	lt = doc({"doctype": "Lender Type", "lender_type_name": "E2E Bank", "type_code": "E2EBK"}).name
	lender = doc({"doctype": "Lender", "lender_name": "E2E Test Bank", "lender_code": "e2eb", "lender_type": lt, "pan": "aaacb1234c"})
	check("Lender code and PAN normalised", lender.name == "E2EB" and lender.pan == "AAACB1234C", lender.name)
	expect_error("Lender rejects bad GSTIN", lambda: doc({"doctype": "Lender", "lender_name": "Bad", "lender_code": "BAD",
	             "lender_type": lt, "gstin": "123"}))
	group = frappe.get_doc({"doctype": "Email Group", "title": "E2E Bank Invoices"}).insert().name
	for email, unsub in (("loans@e2ebank.example", 0), ("ops@e2ebank.example", 0), ("left@e2ebank.example", 1)):
		frappe.get_doc({"doctype": "Email Group Member", "email_group": group, "email": email, "unsubscribed": unsub}).insert()
	lender.update({"invoice_email_group": group, "invoice_cc": "dsa.desk@example.com", "contact_person": "Ms Rao"})
	lender.save()
	other = doc({"doctype": "Lender", "lender_name": "E2E Other Bank", "lender_code": "E2EO", "lender_type": lt}).name

	lbr = doc({"doctype": "Lender Branch", "lender_branch_name": "E2E Pune Main", "branch_code": "pn01", "lender": lender.name,
	           "branch_type": "Branch", "address_line_1": "MG Road", "city": "Pune", "state": "Maharashtra", "pincode": "411001"}).name
	prod = doc({"doctype": "Loan Product", "lender": lender.name, "product_name": "E2E Home Loan", "product_code": "e2ehl",
	            "loan_category": "Home Loan", "minimum_loan_amount": 100000, "maximum_loan_amount": 10000000}).name
	expect_error("Loan Product rejects max < min", lambda: doc({"doctype": "Loan Product", "lender": lender.name,
	             "product_name": "Bad", "product_code": "BADP", "loan_category": "Home Loan", "minimum_loan_amount": 5, "maximum_loan_amount": 1}))
	other_prod = doc({"doctype": "Loan Product", "lender": other, "product_name": "Other HL", "product_code": "E2EOHL", "loan_category": "Home Loan"}).name
	doc({"doctype": "Loan Scheme", "scheme_name": "E2E Salaried", "scheme_code": "e2es", "lender": lender.name, "loan_product": prod,
	     "effective_from": add_days(today, -60), "scheme_status": "Active"})
	expect_error("Scheme rejects product of another lender", lambda: doc({"doctype": "Loan Scheme", "scheme_name": "X", "scheme_code": "X1",
	             "lender": lender.name, "loan_product": other_prod, "effective_from": today}))

	slab = doc({"doctype": "Commission Slab Structure", "slab_name": "E2E HL slab", "lender": lender.name, "loan_product": prod,
	            "calculation_basis": "Disbursed Amount", "commission_percentage": 0.5, "gst_rate": 18, "tds_rate": 10,
	            "clawback_window_months": 6, "clawback_percentage": 100, "effective_from": add_days(today, -30), "slab_status": "Active"}).name
	expect_error("Overlapping Active slab rejected", lambda: doc({"doctype": "Commission Slab Structure", "slab_name": "Dup",
	             "lender": lender.name, "loan_product": prod, "calculation_basis": "Disbursed Amount", "effective_from": today, "slab_status": "Active"}))

	branch = doc({"doctype": "DSA Branch", "branch_name": "E2E Pune", "branch_code": "e2epn", "company": company,
	              "address_line_1": "FC Road", "city": "Pune", "state": "Maharashtra", "pincode": "411004"})
	check("DSA Branch code normalised", branch.name == "E2EPN", branch.name)
	fr = doc({"doctype": "Franchise", "franchise_name": "E2E Partner", "franchise_code": "e2efr", "franchise_owner": "Owner",
	          "company": company, "contact_number": "+91 98765 00000"})
	check("Franchise mobile normalised", fr.contact_number == "9876500000", fr.contact_number)
	fr_branch = doc({"doctype": "DSA Branch", "branch_name": "E2E Kothrud (franchise)", "branch_code": "E2EKT", "franchise": fr.name,
	                 "company": company, "address_line_1": "Karve Road", "city": "Pune", "state": "Maharashtra", "pincode": "411038"})

	# ---------- lead -> customer -> application ----------
	lead = doc({"doctype": "Loan Lead", "lead_title": "E2E walk-in", "customer_name": "E2E Borrower", "mobile_number": "9123456780",
	            "lead_source": "Walk-in", "loan_type": "Home Loan", "estimated_loan_amount": 3000000, "employment_type": "Salaried",
	            })
	expect_error("Lead cannot be set Converted by hand", lambda: (setattr(lead, "lead_status", "Converted"), lead.save()))
	lead.reload()
	from dsa_loan.dsa_loan_portal.doctype.loan_lead.loan_lead import convert_to_customer
	cust = convert_to_customer(lead.name)
	check("Lead converted into a Loan Customer", status("Loan Customer", cust, "mobile_number") == "9123456780", cust)
	check("Lead marked Converted", status("Loan Lead", lead.name, "lead_status") == "Converted")

	co = doc({"doctype": "Loan Customer", "customer_name": "E2E Spouse", "mobile_number": "9123456781", "employment_type": "Salaried"}).name
	expect_error("Loan Customer rejects a short Aadhaar", lambda: doc({"doctype": "Loan Customer", "customer_name": "X",
	             "mobile_number": "9123456782", "aadhaar_number": "1234"}))
	masked = doc({"doctype": "Loan Customer", "customer_name": "E2E Masked", "mobile_number": "9123456783",
	             "aadhaar_number": "1234 5678 9012", "cibil_score": 760, "cibil_report_date": today})
	check("Aadhaar stored masked", masked.aadhaar_number == "XXXX-XXXX-9012", masked.aadhaar_number)
	masked.save()
	check("Masked Aadhaar survives re-save", masked.aadhaar_number == "XXXX-XXXX-9012")
	expect_error("CIBIL score outside 300-900 rejected", lambda: (setattr(masked, "cibil_score", 950), masked.save()))
	masked.reload()
	expect_error("CIBIL score needs a report date", lambda: (setattr(masked, "cibil_report_date", None), masked.save()))
	masked.reload()
	base_app = {"doctype": "Loan Application", "loan_customer": cust, "lender": lender.name,
	            "loan_product": prod, "loan_type": "Home Loan", "business_channel": "Franchise Owned", "franchise": fr.name,
	            "dsa_branch": fr_branch.name,
	            "assigned_agent": agent, "requested_loan_amount": 3000000, "requested_tenure_months": 240,
	            "expected_interest_rate": 8.5, "loan_purpose": "Purchase - Ready Property"}
	expect_error("Application rejects product of another lender", lambda: doc(dict(base_app, loan_product=other_prod)))
	expect_error("DSA Owned loan rejects a franchise branch", lambda: doc(dict(base_app, business_channel="DSA Owned")))
	expect_error("Franchise loan rejects a DSA-owned branch", lambda: doc(dict(base_app, dsa_branch=branch.name)))
	expect_error("Franchise loan needs the franchise", lambda: doc(dict(base_app, franchise=None)))
	expect_error("RBI LTV: 30 lakh loan on a 30 lakh property rejected (cap 90%)",
	             lambda: doc(dict(base_app, property_value=3000000)))
	expect_error("Amount above the product maximum rejected", lambda: doc(dict(base_app, requested_loan_amount=20000000)))
	expect_error("Invalid property PIN code rejected", lambda: doc(dict(base_app, property_pincode="000000")))
	from dsa_loan.dsa_loan_portal.doctype.loan_application.loan_application import rbi_ltv_cap
	check("RBI LTV slabs 90/80/75", (rbi_ltv_cap(3000000), rbi_ltv_cap(5000000), rbi_ltv_cap(9000000)) == (90, 80, 75))
	app = doc(dict(base_app, co_applicants=[{"applicant": co,
	                                         "relationship_with_primary": "Spouse", "is_income_considered": 1}]))
	check("EMI calculated", 25000 < app.estimated_emi < 27000, app.estimated_emi)
	check("Company taken from the DSA branch", app.company == company, app.company)
	check("Co-applicant name filled", app.co_applicants[0].applicant_name == "E2E Spouse", app.co_applicants[0].applicant_name)
	check("Converting the lead again reuses the same customer", convert_to_customer(lead.name) == cust)
	check("Lead -> Customer -> Application linked", status("Loan Customer", cust, "loan_lead") == lead.name
	      and status("Loan Application", app.name, "loan_lead") == lead.name,
	      (status("Loan Customer", cust, "loan_lead"), status("Loan Application", app.name, "loan_lead")))

	lists = {c.applicant: c.name for c in frappe.get_all("Document Checklist", {"loan_application": app.name}, ["name", "applicant"])}
	check("One checklist per applicant (primary + co-applicant)", set(lists) == {cust, co}, lists)
	main = frappe.get_doc("Document Checklist", lists[cust])
	docs = [r.document_name for r in main.documents]
	check("Customer checklist has the 13 standard rows", len(docs) == 13, len(docs))
	expect_error("Second checklist for same applicant rejected", lambda: doc({"doctype": "Document Checklist",
	             "loan_application": app.name, "applicant": cust}))

	# ---------- checklist rows: attach, verify ----------
	pan_row = next(r for r in main.documents if r.document_name == "PAN Card")
	pan_row.document_status = "Verified"
	expect_error("Row cannot be Verified without its file", lambda: main.save())
	main.reload()
	pan_row = next(r for r in main.documents if r.document_name == "PAN Card")
	pan_row.update({"document_file": "/private/files/e2e_pan.pdf", "document_status": "Received"})
	main.save()
	from dsa_loan.dsa_loan_portal.flow import verify_received
	check("Mark Received as Verified verifies the attached row", verify_received(main.name) == 1
	      and frappe.db.get_value("Document Checklist Item", {"parent": main.name, "document_name": "PAN Card"},
	                              "document_status") == "Verified")

	expect_error("Disbursement before sanction rejected", lambda: doc({"doctype": "Loan Disbursement", "loan_application": app.name,
	             "disbursement_date": today, "current_disbursement_amount": 100}))
	expect_error("Sanctioned status needs sanction amount and date", lambda: (setattr(app, "final_status", "Sanctioned"), app.save()))
	app.reload()
	app.final_status = "Submitted"
	app.save()
	check("Submitted", status("Loan Application", app.name, "final_status") == "Submitted")
	check("Checklist carries the branch", status("Document Checklist", main.name, "dsa_branch") == fr_branch.name)
	expect_error("Disbursed cannot be chosen by hand without a Confirmed disbursement",
	             lambda: (setattr(app, "final_status", "Disbursed"), app.save()))
	app.reload()
	app.update({"final_status": "Sanctioned", "sanctioned_amount": 3000000, "sanction_date": today, "lender_submission_date": add_days(today, -5)})
	app.save()
	check("Application Status Sanctioned", app.final_status == "Sanctioned", app.final_status)

	# ---------- disbursement -> commission ----------
	d1 = doc({"doctype": "Loan Disbursement", "loan_application": app.name, "disbursement_date": today,
	          "current_disbursement_amount": 2000000, "disbursement_status": "Confirmed"})
	check("Disbursement totals", d1.total_disbursed_amount == 2000000 and d1.balance_amount == 1000000, f"{d1.total_disbursed_amount} / {d1.balance_amount}")
	check("Application Partially Disbursed", status("Loan Application", app.name, "final_status") == "Partially Disbursed")
	expect_error("Over-disbursement rejected", lambda: doc({"doctype": "Loan Disbursement", "loan_application": app.name,
	             "disbursement_date": today, "current_disbursement_amount": 1500000}))
	d1.current_disbursement_amount = 1
	expect_error("Confirmed disbursement amount locked", lambda: d1.save())
	d1.reload()
	d2 = doc({"doctype": "Loan Disbursement", "loan_application": app.name, "disbursement_date": today,
	          "current_disbursement_amount": 1000000, "disbursement_status": "Confirmed"})
	check("Disbursement numbers set automatically (1, 2)", (d1.disbursement_number, d2.disbursement_number) == (1, 2),
	      (d1.disbursement_number, d2.disbursement_number))
	check("Application Disbursed once nothing is left to release", status("Loan Application", app.name, "final_status") == "Disbursed")

	# ---------- automation: commission created on Confirmed, invoice follows ----------
	calc1 = frappe.get_doc("Commission Calculation", {"loan_disbursement": d1.name})
	check("AUTO: Commission Calculation created when tranche 1 was Confirmed, slab picked",
	      calc1.gross_commission == 10000 and calc1.commission_slab == slab and calc1.gst_rate == 18 and calc1.tds_rate == 10,
	      f"{calc1.gross_commission} {calc1.commission_slab} {calc1.gst_rate}/{calc1.tds_rate}")
	check("Lender/company/franchise/agent filled from application", calc1.franchise == fr.name and calc1.assigned_agent == agent)
	expect_error("One commission per disbursement", lambda: doc({"doctype": "Commission Calculation", "loan_application": app.name,
	             "loan_disbursement": d1.name, "commission_percentage": 1}))
	calc2 = frappe.get_doc("Commission Calculation", {"loan_disbursement": d2.name})
	check("Commission % taken from the slab when left empty", calc2.commission_percentage == 0.5 and calc2.gross_commission == 5000,
	      f"{calc2.commission_percentage} {calc2.gross_commission}")
	check("GST/TDS and net commission", calc2.gst_amount == 900 and calc2.tds_amount == 500 and calc2.net_commission == 5400,
	      f"{calc2.gst_amount} {calc2.tds_amount} {calc2.net_commission}")

	check_lender_invoice(app, lender, cust)
	si_name = status("Loan Application", app.name, "sales_invoice")
	ci = frappe.get_all("Commission Invoice", {"erpnext_sales_invoice": si_name}, ["name", "taxable_amount", "total_gst_amount",
	                                                                               "tds_expected", "invoice_status"])
	check("AUTO: Commission Invoice linked to the Sales Invoice (taxable 15000, GST 2700, TDS 1500)",
	      len(ci) == 1 and ci[0].taxable_amount == 15000 and ci[0].total_gst_amount == 2700 and ci[0].tds_expected == 1500
	      and ci[0].invoice_status == "Submitted", ci)
	check("AUTO: commissions marked Invoiced", {status("Commission Calculation", c, "calculation_status") for c in (calc1.name, calc2.name)}
	      == {"Invoiced"})

	# ---------- invoice ----------
	inv = doc({"doctype": "Commission Invoice", "company": company, "lender": lender.name, "invoice_type": "Commission",
	           "invoice_number": "DSA/26/001", "taxable_amount": 15000, "cgst_amount": 1350, "sgst_amount": 1350})
	check("Invoice totals", inv.total_gst_amount == 2700 and inv.invoice_total == 17700, f"{inv.total_gst_amount} / {inv.invoice_total}")
	expect_error("IGST with CGST/SGST rejected", lambda: doc({"doctype": "Commission Invoice", "company": company, "lender": lender.name,
	             "invoice_type": "Commission", "taxable_amount": 1, "cgst_amount": 1, "sgst_amount": 1, "igst_amount": 1}))
	expect_error("Invoice number must be unique", lambda: doc({"doctype": "Commission Invoice", "company": company, "lender": lender.name,
	             "invoice_type": "Commission", "invoice_number": "DSA/26/001", "taxable_amount": 1}))

	# ---------- payout reconciliation ----------
	from frappe.utils import get_first_day
	from dsa_loan.dsa_loan_portal.automation import create_monthly_payout_statements, debit_note_for_shortfall
	made = create_monthly_payout_statements(get_first_day(today))
	lps = frappe.get_doc("Lender Payout Statement", made[0]) if made else None
	check("AUTO: monthly payout statement pre-filled (expected 15000, TDS 1500, Pending Reconciliation)",
	      lps and lps.total_lender_commission == 15000 and lps.total_tds == 1500 and lps.reconciliation_status == "Pending Reconciliation",
	      made)
	check("AUTO: running the monthly job again creates nothing", create_monthly_payout_statements(get_first_day(today)) == [])
	check("AUTO: the statement claimed both commissions",
	      {status("Commission Calculation", c, "payout_statement") for c in (calc1.name, calc2.name)} == {lps.name})
	lps.actual_received_amount = 13500
	lps.save()
	check("Payout expected from calculations, net payable", lps.total_expected_commission == 15000 and lps.net_payable == 13500,
	      f"{lps.total_expected_commission} / {lps.net_payable}")
	check("Payout Matched, commissions Paid", lps.reconciliation_status == "Matched"
	      and status("Commission Calculation", calc1.name, "calculation_status") == "Paid", lps.reconciliation_status)
	# a commission that arrives after the month was reconciled -> top-up statement, the reconciled one stays frozen
	frappe.db.set_value("Commission Calculation", calc2.name, {"payout_statement": None, "calculation_status": "Invoiced"})
	top = create_monthly_payout_statements(get_first_day(today))
	top_doc = frappe.get_doc("Lender Payout Statement", top[0]) if top else None
	check("AUTO: late commission -> top-up statement for that month only (expected 5000, numbered -2)",
	      top_doc and top_doc.total_expected_commission == 5000 and top_doc.statement_number.endswith("-2")
	      and status("Commission Calculation", calc2.name, "payout_statement") == top_doc.name, top)
	frappe.delete_doc("Lender Payout Statement", top_doc.name, force=1)
	frappe.db.set_value("Commission Calculation", calc2.name, {"payout_statement": lps.name, "calculation_status": "Paid"})
	expect_error("Statement number unique per lender", lambda: doc({"doctype": "Lender Payout Statement", "statement_number": lps.statement_number,
	             "lender": lender.name, "statement_date": today, "period_from": today, "period_to": today, "total_lender_commission": 1}))

	# ---------- clawback + franchise settlement ----------
	expect_error("Clawback cannot exceed original", lambda: doc({"doctype": "Commission Clawback", "commission_calculation": calc2.name,
	             "clawback_reason": "Loan Closure", "clawback_amount": 999999}))
	cb = doc({"doctype": "Commission Clawback", "commission_calculation": calc2.name, "commission_invoice": inv.name,
	          "clawback_reason": "Loan Closure", "clawback_percentage": 50, "recovery_amount": 1000})
	check("Clawback amount and recovery status derived", cb.clawback_amount == 2500 and cb.recovery_status == "Partially Recovered",
	      f"{cb.clawback_amount} {cb.recovery_status}")
	check("AUTO: Credit Note drafted for the clawback", frappe.db.exists("Commission Invoice", {"invoice_type": "Credit Note",
	      "invoice_status": "Draft", "taxable_amount": 2500, "invoice_number": f"CN-{cb.name}"}))
	dn = debit_note_for_shortfall(frappe._dict(name="E2E-SHORT", lender=lender.name, total_expected_commission=15000,
	                                           total_lender_commission=13000))
	check("AUTO: Debit Note drafted when a lender pays short", dn and dn.taxable_amount == 2000 and dn.invoice_status == "Draft")

	auto_fs = frappe.get_all("Franchise Settlement", {"franchise": fr.name}, pluck="name")
	check("AUTO: Franchise Settlement drafted when the payout was reconciled", len(auto_fs) == 1, auto_fs)
	fs = frappe.get_doc("Franchise Settlement", auto_fs[0])
	fs.update({"deductions": 1000, "tds_amount": 500})
	fs.save()
	check("Franchise Owned loan: settlement share 60% of received commission", fs.total_gross_commission == 15000
	      and fs.franchise_share_percentage == 60 and fs.franchise_share_amount == 9000 and fs.net_payable == 7500,
	      f"{fs.total_gross_commission} {fs.franchise_share_amount} {fs.net_payable}")
	check_access(company, lender, prod, agent, fr_branch, app, cust)

	expect_error("Overlapping settlement period rejected", lambda: doc({"doctype": "Franchise Settlement", "settlement_number": "E2E-FS-2",
	             "franchise": fr.name, "settlement_period_from": today, "settlement_period_to": today}))

	app.reload()
	app.final_status = "Closed"
	app.save()
	auto_cb = frappe.get_all("Commission Clawback", {"commission_calculation": calc1.name}, ["clawback_reason", "clawback_amount"])
	check("AUTO: loan closed inside the 6-month window -> 100% clawback (tranche already clawed back is skipped)",
	      len(auto_cb) == 1 and auto_cb[0].clawback_reason == "Loan Closure" and auto_cb[0].clawback_amount == 10000
	      and frappe.db.count("Commission Clawback", {"commission_calculation": calc2.name}) == 1, auto_cb)


def check_lender_invoice(app, lender, cust):
	"""Disbursed + all commissions calculated -> Sales Invoice on the lender, templated email kept as Communication."""
	app.reload()
	si_name = app.sales_invoice
	check("Sales Invoice raised once last commission saved", bool(si_name) and app.invoice_status in ("Emailed", "Email Pending"),
	      f"{si_name} {app.invoice_status} {app.invoice_error}")
	if not si_name:
		return
	si = frappe.get_doc("Sales Invoice", si_name)
	cust_name = frappe.db.get_value("Lender", lender.name, "erpnext_customer")
	check("Invoice submitted on the lender's ERPNext customer, one line per commission, 15000",
	      si.docstatus == 1 and si.customer == cust_name and len(si.items) == 2 and si.net_total == 15000,
	      f"{si.docstatus} {si.customer} {len(si.items)} {si.net_total}")
	check("Invoice amount stored on application", app.invoice_amount == si.grand_total)
	comm = frappe.get_doc("Communication", app.invoice_communication)
	linked = {(l.link_doctype, l.link_name) for l in comm.timeline_links}
	check("Templated email kept as Communication on invoice + application + lender",
	      comm.reference_name == si_name and ("Loan Application", app.name) in linked and ("Lender", lender.name) in linked
	      and "E2E Borrower" in comm.content and si_name in comm.subject, comm.subject)
	check("Recipients from the lender's email group (unsubscribed left out), CC added",
	      app.invoice_email_recipients == "loans@e2ebank.example, ops@e2ebank.example, dsa.desk@example.com",
	      app.invoice_email_recipients)

	from dsa_loan.dsa_loan_portal.invoicing import create_and_send, resend_email
	create_and_send(app.name)
	check("Running it again does not raise a second invoice",
	      frappe.db.count("Sales Invoice", {"customer": cust_name, "docstatus": 1}) == 1)
	before = frappe.db.count("Communication", {"reference_name": si_name})
	resend_email(app.name)
	check("Resend keeps one more Communication", frappe.db.count("Communication", {"reference_name": si_name}) == before + 1)


def check_access(company, lender, prod, agent, branch, app, cust):
	"""Roles, field-level access and branch separation, checked as real users."""
	from dsa_loan.dsa_loan_portal.access import ROLES, grant_branch_access

	check("All 9 roles exist, old Branch Manager gone", len(ROLES) == 9 and all(frappe.db.exists("Role", r) for r in ROLES)
	      and not frappe.db.exists("Role", "Branch Manager"))
	b2 = doc({"doctype": "DSA Branch", "branch_name": "E2E Mumbai", "branch_code": "E2EMU",
	          "company": company, "address_line_1": "LBS Marg", "city": "Mumbai", "state": "Maharashtra", "pincode": "400070"})
	other = doc({"doctype": "Loan Customer", "customer_name": "E2E Other", "mobile_number": "9123456790", "dsa_branch": b2.name})

	def user(email, role):
		u = frappe.get_doc({"doctype": "User", "email": email, "first_name": email.split("@")[0], "send_welcome_email": 0,
		                    "roles": [{"role": role}]}).insert(ignore_permissions=True)
		return u.name

	agent_u = user("e2e.agent@example.com", "Franchise Agent")  # the application is in a franchise branch
	dsa_agent_u = user("e2e.dsaagent@example.com", "DSA Agent")
	fbm_u = user("e2e.fbm@example.com", "Franchise Branch Manager")
	acc_u = user("e2e.accounts@example.com", "DSA Accounts")
	ver_u = user("e2e.verifier@example.com", "Document Verifier")
	grant_branch_access(agent_u, dsa_branch=branch.name)
	grant_branch_access(fbm_u, dsa_branch=branch.name)
	grant_branch_access(dsa_agent_u, dsa_branch=b2.name)
	expect_error("A DSA Agent cannot be given a franchise's branch", lambda: grant_branch_access(dsa_agent_u, dsa_branch=branch.name))
	expect_error("A Franchise Agent cannot be given a DSA branch", lambda: grant_branch_access(agent_u, dsa_branch=b2.name))
	try:
		frappe.set_user(dsa_agent_u)
		seen = frappe.get_list("Loan Customer", pluck="name")
		check("DSA Agent sees only their DSA branch", other.name in seen and cust not in seen, seen)
		frappe.set_user(fbm_u)
		check("Franchise Branch Manager can delete own-branch applications, cannot see lender commission",
		      frappe.has_permission("Loan Application", "delete", app.name)
		      and not frappe.has_permission("Commission Calculation", "read"))
		check("Franchise Branch Manager sees own franchise's settlement only via the franchise",
		      frappe.has_permission("Franchise Settlement", "read"))
		frappe.set_user(agent_u)
		seen = frappe.get_list("Loan Customer", pluck="name")
		check("Agent sees own-branch customers only", cust in seen and other.name not in seen, seen)
		check("Agent sees own-branch application", app.name in frappe.get_list("Loan Application", pluck="name"))
		check("Agent can read PAN (permlevel 1)", frappe.get_doc("Loan Customer", cust).has_permlevel_access_to("pan"))
		check("Agent cannot delete applications", not frappe.has_permission("Loan Application", "delete", app.name))
		check("Agent cannot create commissions", not frappe.has_permission("Commission Calculation", "create"))
		check("Agent cannot edit lenders", not frappe.has_permission("Lender", "write", lender.name)
		      and frappe.has_permission("Lender", "read", lender.name))
		frappe.set_user(acc_u)
		c = frappe.get_doc("Loan Customer", cust)
		check("Accounts can read customers but not PAN / Aadhaar / CIBIL",
		      not c.has_permlevel_access_to("pan") and not c.has_permlevel_access_to("cibil_score"))
		check("Accounts can create disbursements", frappe.has_permission("Loan Disbursement", "create"))
		check("Accounts sees every branch (no branch restriction)", other.name in frappe.get_list("Loan Customer", pluck="name"))
		frappe.set_user(user("e2e.ops@example.com", "DSA Operations Manager"))
		seen = frappe.get_list("Loan Customer", pluck="name")
		check("Operations Manager sees every branch, runs loans and disbursements, only reads commission",
		      cust in seen and other.name in seen and frappe.has_permission("Loan Application", "delete", app.name)
		      and frappe.has_permission("Loan Disbursement", "create") and frappe.has_permission("Commission Calculation", "read")
		      and not frappe.has_permission("Commission Calculation", "write")
		      and not frappe.has_permission("Lender", "write", lender.name))
		frappe.set_user(ver_u)
		check("Verifier can verify checklists but not create applications",
		      frappe.has_permission("Document Checklist", "write") and not frappe.has_permission("Loan Application", "create"))
	finally:
		frappe.set_user("Administrator")


frappe.init(site=SITE, sites_path=".")
frappe.connect()
frappe.set_user("Administrator")
try:
	run()
except Exception:
	import traceback

	traceback.print_exc()
	results.append(("unexpected error", False, ""))
finally:
	frappe.db.rollback()
	frappe.destroy()

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} checks passed; all test data rolled back.")
sys.exit(1 if failed else 0)
