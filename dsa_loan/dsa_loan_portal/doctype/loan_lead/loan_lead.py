# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

from dsa_loan.dsa_loan_portal.utils import clean_mobile


class LoanLead(Document):
	def validate(self):
		clean_mobile(self, "mobile")
		if self.status == "Converted" and not self.converted_customer:
			frappe.throw(_("Use the Convert to Application button to convert a lead."))
		if self.is_new() or self.has_value_changed("mobile"):
			dup = frappe.db.get_value(
				"Loan Lead", {"mobile": self.mobile, "status": ("not in", ["Lost", "Converted"]), "name": ("!=", self.name)}
			)
			if dup:
				frappe.msgprint(_("An open lead {0} already exists with this mobile number.").format(dup), indicator="orange")


@frappe.whitelist()
def convert_to_application(lead):
	"""Create (or reuse) the Loan Customer and create a draft Loan Application. Runs once per lead."""
	lead = frappe.get_doc("Loan Lead", lead)
	lead.check_permission("write")
	if lead.status == "Converted":
		frappe.throw(_("Lead {0} is already converted.").format(lead.name))
	if lead.status == "Lost":
		frappe.throw(_("A lost lead cannot be converted."))

	customer = frappe.db.get_value("Loan Customer", {"mobile": lead.mobile})
	if not customer:
		customer = frappe.get_doc(
			{
				"doctype": "Loan Customer",
				"customer_name": lead.lead_name,
				"mobile": lead.mobile,
				"email": lead.email,
				"city": lead.city,
				"employment_type": lead.employment_type,
				"monthly_income": lead.monthly_income,
			}
		).insert().name

	application = frappe.get_doc(
		{
			"doctype": "Loan Application",
			"application_date": nowdate(),
			"loan_lead": lead.name,
			"loan_customer": customer,
			"loan_type": lead.loan_type,
			"application_type": "Fresh",
			"loan_purpose": "Purchase",
			"required_amount": lead.required_amount,
			"tenure_months": 240,
			"employment_type": lead.employment_type or "Salaried",
			"monthly_income": lead.monthly_income or 0,
			"dsa_branch": lead.dsa_branch,
			"franchise": lead.franchise,
			"relationship_manager": lead.assigned_to,
		}
	)
	application.flags.ignore_mandatory = True  # income may still be unknown at conversion
	application.insert()

	lead.db_set({"status": "Converted", "converted_customer": customer})
	return application.name
