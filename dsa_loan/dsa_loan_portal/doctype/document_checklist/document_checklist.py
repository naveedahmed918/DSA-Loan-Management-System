# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

from dsa_loan.dsa_loan_portal.utils import check_belongs


class DocumentChecklist(Document):
	def validate(self):
		check_belongs("Lender Login", self.lender_login, "loan_application", self.loan_application, "Loan Application")
		if self.attachment and self.verification_status == "Pending":
			self.verification_status = "Received"
		if self.attachment and not self.received_date:
			self.received_date = nowdate()
		if self.has_value_changed("verification_status") and self.verification_status in ("Verified", "Rejected"):
			self.verified_by = frappe.session.user
			self.verification_date = nowdate()
