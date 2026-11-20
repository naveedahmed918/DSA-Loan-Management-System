# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, nowdate

from dsa_loan.dsa_loan_portal.doctype.loan_application.loan_application import advance_status
from dsa_loan.dsa_loan_portal.utils import check_belongs, is_active_on

CLOSED = ("Rejected", "Withdrawn", "Closed")
DECIDED = ("Sanctioned", "Rejected", "Disbursed", "Closed")


class LenderLogin(Document):
	def validate(self):
		self.loan_customer = frappe.db.get_value("Loan Application", self.loan_application, "loan_customer")
		if not self.expected_tat_days:
			self.expected_tat_days = frappe.db.get_value("Loan Product", self.loan_product, "tat_days")
		check_belongs("Loan Product", self.loan_product, "lender", self.lender, "Lender")
		check_belongs("Lender Branch", self.lender_branch, "lender", self.lender, "Lender")
		check_belongs("Loan Scheme", self.loan_scheme, "loan_product", self.loan_product, "Loan Product")
		self.validate_duplicate()
		self.validate_sanction()
		self.set_tat()

	def validate_duplicate(self):
		if self.status in CLOSED:
			return
		dup = frappe.db.get_value(
			"Lender Login",
			{
				"loan_application": self.loan_application,
				"lender": self.lender,
				"status": ("not in", CLOSED),
				"name": ("!=", self.name),
			},
		)
		if dup:
			frappe.throw(_("Lender Login {0} is already open for this application with {1}.").format(dup, self.lender))

	def validate_sanction(self):
		if self.sanctioned_amount and self.sanctioned_amount > self.requested_amount * 1.5:
			frappe.msgprint(_("Sanctioned amount is much higher than the requested amount. Please check."), indicator="orange")
		if self.sanction_date and self.login_date and getdate(self.sanction_date) < getdate(self.login_date):
			frappe.throw(_("Sanction Date cannot be before Login Date."))

	def set_tat(self):
		if self.status in DECIDED and self.login_date:
			self.actual_tat_days = date_diff(self.sanction_date or nowdate(), self.login_date)

	def after_insert(self):
		created = make_checklist(self)
		if created:
			frappe.msgprint(_("{0} document checklist items created from lender rules.").format(created), alert=True)

	def on_update(self):
		if self.status in ("Logged In", "Under Review", "Query Raised"):
			advance_status(self.loan_application, "Logged In")
		elif self.status == "Sanctioned":
			advance_status(self.loan_application, "Sanctioned")


def make_checklist(login):
	"""One Document Checklist record per matching active Lender Document Rule and person."""
	app = frappe.get_doc("Loan Application", login.loan_application)
	on_date = login.login_date or nowdate()
	rules = frappe.get_all(
		"Lender Document Rule",
		filters={"lender": login.lender, "loan_product": login.loan_product, "status": "Active"},
		fields=[
			"name", "loan_scheme", "applicable_for", "employment_type", "valid_from", "valid_to",
			"document_name", "document_category", "is_mandatory",
		],
	)
	people = {
		"Applicant": [app.loan_customer],
		"Property": [app.loan_customer],
		"Co-Applicant": [r.loan_customer for r in app.co_applicants if r.applicant_role == "Co-Applicant"],
		"Guarantor": [r.loan_customer for r in app.co_applicants if r.applicant_role == "Guarantor"],
	}
	count = 0
	for rule in rules:
		if rule.loan_scheme and rule.loan_scheme != login.loan_scheme:
			continue
		if rule.employment_type not in (None, "", "Both", app.employment_type):
			continue
		if not is_active_on(rule.valid_from, rule.valid_to, on_date):
			continue
		for customer in people.get(rule.applicable_for, []):
			if frappe.db.exists(
				"Document Checklist",
				{"lender_login": login.name, "lender_document_rule": rule.name, "loan_customer": customer},
			):
				continue
			frappe.get_doc(
				{
					"doctype": "Document Checklist",
					"loan_application": app.name,
					"lender_login": login.name,
					"lender_document_rule": rule.name,
					"lender": login.lender,
					"document_name": rule.document_name,
					"document_category": rule.document_category,
					"is_mandatory": rule.is_mandatory,
					"loan_customer": customer,
					"applicable_for": rule.applicable_for,
					"verification_status": "Pending",
				}
			).insert(ignore_permissions=True)
			count += 1
	return count


@frappe.whitelist()
def regenerate_checklist(lender_login):
	login = frappe.get_doc("Lender Login", lender_login)
	login.check_permission("write")
	return make_checklist(login)
