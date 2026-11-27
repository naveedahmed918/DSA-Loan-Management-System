"""Server side of the guided flow on the forms (buttons and the progress bar on Loan Application).

Everything goes through the normal controllers, so every rule and automatic step still applies.
"""

import json

import frappe
from frappe import _
from frappe.utils import flt, nowdate


@frappe.whitelist()
def application_flow(application):
	"""Progress of one application: documents per applicant, money and commission."""
	app = frappe.get_doc("Loan Application", application)
	app.check_permission("read")
	checklists = []
	for c in frappe.get_all("Document Checklist", {"loan_application": app.name}, ["name", "applicant"], order_by="creation"):
		rows = frappe.get_all("Document Checklist Item", {"parent": c.name, "parenttype": "Document Checklist"}, pluck="document_status")
		needed = [r for r in rows if r != "Not Applicable"]
		checklists.append({"name": c.name, "applicant": c.applicant,
		                   "customer_name": frappe.db.get_value("Loan Customer", c.applicant, "customer_name"),
		                   "verified": sum(1 for r in needed if r == "Verified"), "total": len(needed),
		                   "attention": sum(1 for r in needed if r in ("Rejected", "Resubmission Required"))})
	tranches = frappe.get_all("Loan Disbursement", {"loan_application": app.name},
	                          ["name", "disbursement_number", "disbursement_status", "current_disbursement_amount"], order_by="creation")
	disbursed = sum(flt(t.current_disbursement_amount) for t in tranches if t.disbursement_status == "Confirmed")
	numbers = [int(t.disbursement_number) for t in tranches if str(t.disbursement_number).isdigit()]
	return {
		"checklists": checklists,
		"tranches": tranches,
		"disbursed": disbursed,
		"balance": max(flt(app.sanctioned_amount) - disbursed, 0),
		"next_number": str(max(numbers or [0]) + 1),
		"commissions": frappe.get_all("Commission Calculation", {"loan_application": app.name},
		                              ["name", "gross_commission", "calculation_status"], order_by="creation"),
	}


@frappe.whitelist()
def record_disbursement(application, values):
	"""Create a Confirmed Loan Disbursement from the application's dialog; automation then takes over."""
	app = frappe.get_doc("Loan Application", application)
	app.check_permission("write")
	v = json.loads(values) if isinstance(values, str) else values
	doc = frappe.get_doc({
		"doctype": "Loan Disbursement", "loan_application": app.name,
		"disbursement_date": v.get("disbursement_date") or nowdate(),
		"disbursement_status": "Confirmed", "current_disbursement_amount": flt(v.get("amount")),
		"payment_mode": v.get("payment_mode"), "payment_reference": v.get("payment_reference"),
		"beneficiary_name": v.get("beneficiary_name"), "lender_reference_number": v.get("lender_reference_number"),
	})
	doc.insert()
	return doc.name


@frappe.whitelist()
def verify_received(checklist):
	"""Mark every Received row that has its file attached Verified."""
	doc = frappe.get_doc("Document Checklist", checklist)
	doc.check_permission("write")
	changed = 0
	for row in doc.documents:
		if row.document_status == "Received" and row.document_file:
			row.document_status = "Verified"
			changed += 1
	if changed:
		doc.save()
	return changed
