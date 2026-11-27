# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import clean_mobile


class LoanLead(Document):
	def validate(self):
		clean_mobile(self, "mobile_number", "alternate_mobile")
		if (self.lead_status == "Converted" and self.has_value_changed("lead_status")
				and not frappe.db.exists("Loan Customer", {"loan_lead": self.name})):
			frappe.throw(_("Use the Convert to Customer button to convert a lead."))
		if self.is_new() or self.has_value_changed("mobile_number"):
			dup = frappe.db.get_value(
				"Loan Lead",
				{"mobile_number": self.mobile_number, "lead_status": ("not in", ["Converted", "Not Interested", "Lost"]), "name": ("!=", self.name)},
			)
			if dup:
				frappe.msgprint(_("An open lead {0} already exists with this mobile number.").format(dup), indicator="orange")


@frappe.whitelist()
def convert_to_customer(lead):
	"""Lead -> Loan Customer: create the customer (or reuse the one with this mobile number), link it to this lead,
	mark the lead Converted and return the customer. Loan Applications made for the customer then carry the lead."""
	lead = frappe.get_doc("Loan Lead", lead)
	lead.check_permission("write")
	if lead.lead_status in ("Not Interested", "Lost"):
		frappe.throw(_("A {0} lead cannot be converted.").format(lead.lead_status))

	customer = (frappe.db.get_value("Loan Customer", {"loan_lead": lead.name})
	            or frappe.db.get_value("Loan Customer", {"mobile_number": lead.mobile_number}))
	if not customer:
		customer = frappe.get_doc(
			{
				"doctype": "Loan Customer",
				"loan_lead": lead.name,
				"customer_name": lead.customer_name,
				"mobile_number": lead.mobile_number,
				"alternate_mobile": lead.alternate_mobile,
				"email": lead.email,
				"employment_type": lead.employment_type,
			}
		).insert().name
	else:
		# a returning customer: point them at their latest lead (older applications keep the lead they had)
		frappe.db.set_value("Loan Customer", customer, "loan_lead", lead.name)
	frappe.db.set_value("Loan Lead", lead.name, "lead_status", "Converted")
	return customer
