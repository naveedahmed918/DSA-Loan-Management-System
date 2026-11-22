# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate

from dsa_loan.dsa_loan_portal.utils import check_belongs, emi, is_active_on

# Order of final_status values that code may move forward automatically.
FORWARD = ["Draft", "Documents Pending", "Ready for Submission", "Submitted", "Under Review", "Query Raised",
           "Sanctioned", "Partially Disbursed", "Disbursed"]
DISBURSABLE = ("Sanctioned", "Partially Disbursed")


class LoanApplication(Document):
	def validate(self):
		check_belongs("Loan Product", self.loan_product, "lender", self.lender, "Lender")
		check_belongs("Lender Branch", self.lender_branch, "lender", self.lender, "Lender")
		check_belongs("Loan Scheme", self.loan_scheme, "loan_product", self.loan_product, "Loan Product")
		self.validate_co_applicants()
		self.validate_status_fields()
		self.estimated_emi = emi(self.requested_loan_amount, self.expected_interest_rate, self.requested_tenure_months)
		if self.sanction_date and self.lender_submission_date and getdate(self.sanction_date) < getdate(self.lender_submission_date):
			frappe.throw(_("Sanction Date cannot be before Lender Submission Date."))
		if self.has_value_changed("manager_approval") and self.manager_approval in ("Approved", "Rejected"):
			self.manager_approval_date = now_datetime()
		self.application_status = self.coarse_status()

	def validate_co_applicants(self):
		seen = set()
		for row in self.co_applicants:
			if row.applicant == self.primary_customer:
				frappe.throw(_("Row {0}: the primary customer cannot also be a co-applicant.").format(row.idx))
			if row.applicant in seen:
				frappe.throw(_("Row {0}: {1} is added twice.").format(row.idx, row.applicant))
			seen.add(row.applicant)

	def validate_status_fields(self):
		"""Server-side twin of the form's mandatory_depends_on rules."""
		if self.final_status == "Sanctioned" and not (self.sanctioned_amount and self.sanction_date):
			frappe.throw(_("Enter the Sanctioned Amount and Sanction Date before marking the application Sanctioned."))
		if self.final_status == "Rejected" and not self.rejection_reason:
			frappe.throw(_("Enter the Rejection Reason before marking the application Rejected."))

	def coarse_status(self):
		if self.final_status in ("Disbursed", "Closed"):
			return "Completed"
		if self.final_status in ("Rejected", "Withdrawn"):
			return "Cancelled"
		if self.final_status == "On Hold":
			return "On Hold"
		return "Open" if self.final_status == "Draft" else "In Progress"

	def after_insert(self):
		if self.loan_lead:
			from dsa_loan.dsa_loan_portal.doctype.loan_lead.loan_lead import mark_converted

			mark_converted(self.loan_lead)

	def on_update(self):
		created = make_checklist(self)
		if created:
			frappe.msgprint(_("{0} document checklist items created from lender rules.").format(created), alert=True)


def set_final_status(application, new_status):
	"""Move final_status forward only (never back), keeping application_status in step."""
	doc = frappe.get_doc("Loan Application", application)
	if doc.final_status in FORWARD and new_status in FORWARD and FORWARD.index(new_status) <= FORWARD.index(doc.final_status):
		return
	doc.final_status = new_status
	doc.application_status = doc.coarse_status()
	doc.db_update()


def make_checklist(app):
	"""One Document Checklist record per matching active Lender Document Rule and applicant."""
	if not app.lender:
		return 0
	rules = frappe.get_all(
		"Lender Document Rule",
		filters={"lender": app.lender, "is_active": 1},
		fields=["name", "loan_product", "loan_scheme", "applicant_type", "employment_type", "property_type",
		        "document_name", "document_category", "is_mandatory"],
	)
	co = [r.applicant for r in app.co_applicants if r.applicant_type == "Co-Applicant"]
	guarantors = [r.applicant for r in app.co_applicants if r.applicant_type == "Guarantor"]
	people = {
		"Primary Applicant": [app.primary_customer],
		"Property Owner": [app.primary_customer],
		"Co-Applicant": co,
		"Guarantor": guarantors,
		"All": [app.primary_customer] + co + guarantors,
	}
	employment = {c: frappe.db.get_value("Loan Customer", c, "employment_type") for c in people["All"]}
	count = 0
	for rule in rules:
		if rule.loan_product and rule.loan_product != app.loan_product:
			continue
		if rule.loan_scheme and rule.loan_scheme != app.loan_scheme:
			continue
		if rule.property_type and rule.property_type != app.property_type:
			continue
		for customer in people.get(rule.applicant_type, []):
			if rule.employment_type and employment.get(customer) != rule.employment_type:
				continue
			if frappe.db.exists(
				"Document Checklist",
				{"loan_application": app.name, "lender_document_rule": rule.name, "applicant": customer},
			):
				continue
			frappe.get_doc(
				{
					"doctype": "Document Checklist",
					"loan_application": app.name,
					"applicant": customer,
					"lender_document_rule": rule.name,
					"document_name": rule.document_name,
					"document_category": rule.document_category,
					"is_mandatory": rule.is_mandatory,
					"verification_status": "Pending",
				}
			).insert(ignore_permissions=True)
			count += 1
	return count
