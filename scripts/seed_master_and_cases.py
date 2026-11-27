"""Sample master data + one complete loan for each business channel (DSA Owned, Franchise Operated, Franchise Owned).

Lender names are real; every rate, commission %, person, phone number, PAN and email is SAMPLE data.
Emails use example.com, which can never be delivered. Safe to run again: existing records are reused.

Run from the bench:  cd sites && ../env/bin/python ../apps/dsa_loan/scripts/seed_master_and_cases.py dsaloan.localhost
"""
import sys

import frappe
from frappe.utils import add_days, add_months, nowdate

SITE = sys.argv[1] if len(sys.argv) > 1 else "dsaloan.localhost"
TODAY = None  # set after connecting
FY_START = "2026-04-01"

LENDER_TYPES = [("Public Sector Bank", "PSB"), ("Private Sector Bank", "PVB"),
                ("Housing Finance Company", "HFC"), ("NBFC", "NBFC")]

# code, name, type, gstin-less sample, home-loan rate range, LAP rate range, commission % (sample), city of branch
LENDERS = [
	("SBI", "State Bank of India", "Public Sector Bank", (7.50, 9.65), (9.20, 10.80), 0.35, "Pune"),
	("HDFC", "HDFC Bank", "Private Sector Bank", (7.90, 9.85), (9.50, 11.30), 0.45, "Pune"),
	("ICICI", "ICICI Bank", "Private Sector Bank", (8.00, 9.80), (9.60, 11.50), 0.45, "Nagpur"),
	("LICHFL", "LIC Housing Finance", "Housing Finance Company", (7.75, 10.25), (9.75, 12.00), 0.50, "Nashik"),
	("BAJAJHF", "Bajaj Housing Finance", "NBFC", (8.25, 11.00), (9.90, 13.00), 0.60, "Pune"),
]

# one product (and one commission slab) per loan type, for every lender. SAMPLE figures:
# code suffix, loan type, added to the lender's home-loan rate, max amount, max tenure (months), added to commission %
PRODUCT_TYPES = [
	("HL", "Home Loan", 0, 75000000, 360, 0),
	("LAP", "Loan Against Property", None, 50000000, 180, 0.15),
	("BT", "Balance Transfer", -0.10, 75000000, 360, 0),
	("PP", "Plot", 0.40, 20000000, 180, 0.10),
	("PC", "Plot + Construction", 0.15, 50000000, 360, 0.05),
]

# extra branches per lender (city, branch type), on top of the first branch made with the lender: 3-4 each
EXTRA_LENDER_BRANCHES = {
	"SBI": [("Mumbai", "Regional Office"), ("Nagpur", "Branch"), ("Nashik", "Processing Centre")],
	"HDFC": [("Mumbai", "Regional Office"), ("Nagpur", "Branch")],
	"ICICI": [("Mumbai", "Regional Office"), ("Pune", "Branch"), ("Aurangabad", "Branch")],
	"LICHFL": [("Mumbai", "Head Office"), ("Pune", "Branch")],
	"BAJAJHF": [("Mumbai", "Regional Office"), ("Nagpur", "Branch")],
}
PINCODES = {"Pune": "411001", "Nagpur": "440001", "Nashik": "422001", "Mumbai": "400001", "Aurangabad": "431001"}

# code, name, owner name, city, state, pincode
DSA_BRANCH = ("PUN-HO", "DSA Pune Head Office", None, "Pune", "Maharashtra", "411004")
FRANCHISES = [
	# franchise used for the Franchise Operated case (DSA owns, franchise runs)
	("NGP", "Orange City Loan Point", "Sample Owner One", "Nagpur", "Maharashtra", "440010"),
	# franchise used for the Franchise Owned case (franchise owns, DSA runs)
	("NSK", "Godavari Home Finance Partners", "Sample Owner Two", "Nashik", "Maharashtra", "422005"),
]

# one complete loan per business channel
CASES = [
	dict(channel="DSA Owned", branch="PUN-HO", franchise=None, lender="SBI", product="SBI-HL",
	     customer="Amit Kulkarni (Sample)", mobile="9000000101", pan="AAAPK1001A", income=125000,
	     amount=4000000, property_value=6000000, tranches=[4000000]),
	dict(channel="Franchise Operated", branch="NGP-01", franchise="NGP", lender="HDFC", product="HDFC-HL",
	     customer="Sneha Deshmukh (Sample)", mobile="9000000102", pan="AAAPD1002B", income=98000,
	     amount=3000000, property_value=4500000, tranches=[2000000, 1000000]),  # two tranches
	dict(channel="Franchise Owned", branch="NSK-01", franchise="NSK", lender="LICHFL", product="LICHFL-HL",
	     customer="Rahul Patil (Sample)", mobile="9000000103", pan="AAAPP1003C", income=110000,
	     amount=3500000, property_value=5200000, tranches=[3500000]),
]

made = {}


def get_or_make(doctype, filters, values):
	name = frappe.db.get_value(doctype, filters)
	if name:
		return frappe.get_doc(doctype, name)
	doc = frappe.get_doc(dict(doctype=doctype, **values)).insert()
	made[doctype] = made.get(doctype, 0) + 1
	return doc


def masters(company):
	for name, code in LENDER_TYPES:
		get_or_make("Lender Type", {"lender_type_name": name}, {"lender_type_name": name, "type_code": code,
		            "description": f"{name} (sample master)"})

	for code, name, ltype, hl, lap, comm, city in LENDERS:
		# members are added separately with the team's real addresses (tools/_add_team_emails.py, local only)
		group = get_or_make("Email Group", {"title": f"{name} Invoices"}, {"title": f"{name} Invoices"}).name
		get_or_make("Lender", {"lender_code": code}, {
			"lender_name": name, "lender_code": code, "lender_type": ltype, "website": "",
			"contact_person": "Relationship Manager (sample)", "contact_number": "9000000000",
			"official_email": f"rm.{code.lower()}@example.com", "auto_invoice_on_disbursement": 1,
			"invoice_email_group": group, "invoice_cc": "dsa.accounts@example.com"})
		for b_city, b_type, b_label in [(city, "Branch", "Main")] + [(c, t, t) for c, t in EXTRA_LENDER_BRANCHES.get(code, [])]:
			b_code = f"{code}-{b_city[:3].upper()}"
			get_or_make("Lender Branch", {"lender": code, "branch_code": b_code}, {
				"lender_branch_name": f"{name} {b_city} {b_label}", "branch_code": b_code, "lender": code,
				"branch_type": b_type, "address_line_1": "Main Road (sample address)", "city": b_city,
				"state": "Maharashtra", "pincode": PINCODES[b_city],
				"branch_manager_name": "Branch Manager (sample)", "contact_number": "9000000001",
				"email": f"{b_city.lower()}.{code.lower()}@example.com"})
		for suffix, label, rate_add, max_amt, max_months, comm_add in PRODUCT_TYPES:
			rates = lap if suffix == "LAP" else (round(hl[0] + rate_add, 2), round(hl[1] + rate_add, 2))
			get_or_make("Loan Product", {"product_code": f"{code}-{suffix}"}, {
				"product_name": f"{name} {label}", "product_code": f"{code}-{suffix}", "lender": code,
				"loan_category": label, "is_active": 1, "minimum_loan_amount": 500000, "maximum_loan_amount": max_amt,
				"minimum_tenure_months": 12, "maximum_tenure_months": max_months,
				"minimum_interest_rate": rates[0], "maximum_interest_rate": rates[1], "interest_type": "Floating",
				"repayment_type": "EMI", "product_description": f"Sample {label.lower()} product; rates are illustrative."})
			get_or_make("Commission Slab Structure", {"lender": code, "loan_product": f"{code}-{suffix}", "slab_status": "Active"}, {
				"slab_name": f"{name} {label} payout FY26-27", "lender": code, "loan_product": f"{code}-{suffix}",
				"calculation_basis": "Disbursed Amount", "commission_percentage": round(comm + comm_add, 2), "gst_rate": 18,
				"tds_rate": 2, "clawback_window_months": 6, "clawback_percentage": 100, "effective_from": FY_START,
				"effective_to": "2027-03-31", "slab_status": "Active"})
		get_or_make("Loan Scheme", {"scheme_code": f"{code}-HL-SAL"}, {
			"scheme_name": f"{name} Home Loan - Salaried", "scheme_code": f"{code}-HL-SAL", "lender": code,
			"loan_product": f"{code}-HL", "effective_from": FY_START, "scheme_status": "Active",
			"applicant_category": "Salaried", "minimum_age": 21, "maximum_age": 60, "minimum_monthly_income": 25000,
			"minimum_credit_score": 700, "maximum_ltv": 80, "maximum_foir": 55, "minimum_loan_amount": 500000,
			"maximum_loan_amount": 50000000, "minimum_interest_rate": hl[0], "maximum_interest_rate": hl[1],
			"minimum_tenure_months": 60, "maximum_tenure_months": 360,
			"scheme_description": "Sample scheme for salaried applicants."})

	manager = frappe.db.get_value("Employee", {"status": "Active"})
	code, name, _o, city, state, pin = DSA_BRANCH
	get_or_make("DSA Branch", {"branch_code": code}, {
		"branch_name": name, "branch_code": code, "company": company, "branch_manager": manager,
		"contact_number": "9000000010", "email": "pune.ho@example.com", "opening_date": "2024-04-01",
		"branch_status": "Active", "address_line_1": "FC Road (sample address)", "city": city, "state": state, "pincode": pin})
	for code, name, owner, city, state, pin in FRANCHISES:
		get_or_make("Franchise", {"franchise_code": code}, {
			"franchise_name": name, "franchise_code": code, "franchise_owner": owner, "company": company,
			"contact_number": "9000000020", "email": f"owner.{code.lower()}@example.com", "franchise_status": "Active",
			"agreement_start_date": "2025-04-01", "agreement_end_date": "2028-03-31"})
		get_or_make("DSA Branch", {"branch_code": f"{code}-01"}, {
			"branch_name": f"{name} - {city}", "branch_code": f"{code}-01", "franchise": code, "company": company,
			"contact_number": "9000000030", "email": f"branch.{code.lower()}@example.com", "opening_date": "2025-04-01",
			"branch_status": "Active", "address_line_1": "Main Road (sample address)", "city": city, "state": state,
			"pincode": pin})


def run_case(c, company, agent):
	from dsa_loan.dsa_loan_portal.doctype.loan_lead.loan_lead import convert_to_customer

	if frappe.db.exists("Loan Customer", {"mobile_number": c["mobile"]}):
		cust = frappe.db.get_value("Loan Customer", {"mobile_number": c["mobile"]})
		if frappe.db.exists("Loan Application", {"loan_customer": cust}):
			return frappe.db.get_value("Loan Application", {"loan_customer": cust})
	lead = get_or_make("Loan Lead", {"mobile_number": c["mobile"]}, {
		"lead_title": f"Home Loan - {c['customer']}", "lead_date": add_days(TODAY, -45), "customer_name": c["customer"],
		"mobile_number": c["mobile"], "email": f"customer{c['mobile'][-3:]}@example.com", "city": "Pune",
		"lead_source": "Walk-in", "loan_type": "Home Loan", "estimated_loan_amount": c["amount"],
		"employment_type": "Salaried"})
	cust = convert_to_customer(lead.name)
	customer = frappe.get_doc("Loan Customer", cust)
	customer.update({"pan": c["pan"], "date_of_birth": "1990-06-15", "gender": "Male" if c["mobile"] != "9000000102" else "Female",
	                 "employment_type": "Salaried", "employer_business_name": "Sample Employer Pvt Ltd",
	                 "monthly_income": c["income"], "kyc_status": "Verified", "cibil_score": 780,
	                 "cibil_report_date": add_days(TODAY, -10)})
	customer.save()

	app = frappe.get_doc({
		"doctype": "Loan Application", "application_date": add_days(TODAY, -40), "loan_customer": cust,
		"lender": c["lender"], "loan_product": c["product"], "loan_scheme": f"{c['lender']}-HL-SAL", "loan_type": "Home Loan",
		"business_channel": c["channel"], "franchise": c["franchise"], "dsa_branch": c["branch"], "assigned_agent": agent,
		"requested_loan_amount": c["amount"], "requested_tenure_months": 240, "expected_interest_rate": 8.5,
		"loan_purpose": "Purchase - Ready Property", "property_type": "Flat", "property_value": c["property_value"],
		"property_city": "Pune", "property_state": "Maharashtra", "property_pincode": "411001"}).insert()
	for status in ("Documents Pending", "Ready for Submission"):
		app.final_status = status
		app.save()
	app.update({"final_status": "Submitted", "lender_application_number": f"{c['lender']}/HL/{app.name[-5:]}",
	            "lender_submission_date": add_days(TODAY, -30)})
	app.save()
	app.final_status = "Under Review"
	app.save()
	app.update({"final_status": "Sanctioned", "sanction_date": add_days(TODAY, -15), "sanctioned_amount": c["amount"],
	            "sanctioned_interest_rate": 8.5, "sanctioned_tenure_months": 240,
	            "sanction_valid_until": add_months(TODAY, 3)})
	app.save()
	for i, amount in enumerate(c["tranches"]):
		frappe.get_doc({"doctype": "Loan Disbursement", "loan_application": app.name,
		                "disbursement_date": add_days(TODAY, -10 + i * 5), "disbursement_status": "Confirmed",
		                "current_disbursement_amount": amount, "payment_mode": "RTGS",
		                "payment_reference": f"UTRSAMPLE{app.name[-5:]}{i + 1}",
		                "beneficiary_name": "Builder (sample)"}).insert()
	return app.name


frappe.init(site=SITE, sites_path=".")
frappe.connect()
frappe.set_user("Administrator")
TODAY = nowdate()
frappe.flags.mute_emails = True  # sample data: never send mail
try:
	company = frappe.db.get_value("Company", {})
	agent = frappe.db.get_value("Employee", {"status": "Active"}, order_by="name desc")
	masters(company)
	apps = [run_case(c, company, agent) for c in CASES]
	# the invoice emails stay recorded on each invoice, but are taken out of the send queue (sample addresses)
	for q in frappe.get_all("Email Queue", {"status": "Not Sent"}, pluck="name"):
		if all(r.endswith("@example.com") for r in frappe.get_all("Email Queue Recipient", {"parent": q}, pluck="recipient")):
			frappe.delete_doc("Email Queue", q, force=True, ignore_permissions=True)
	frappe.db.commit()
finally:
	frappe.flags.mute_emails = False

print("created:", made)
for name in apps:
	a = frappe.db.get_value("Loan Application", name, ["business_channel", "lender", "final_status", "customer_name",
	                        "sales_invoice", "invoice_status"], as_dict=True)
	calcs = frappe.get_all("Commission Calculation", {"loan_application": name}, ["name", "gross_commission", "net_commission"])
	print(name, dict(a), calcs)
frappe.destroy()
