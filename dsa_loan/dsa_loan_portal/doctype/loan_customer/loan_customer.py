# Copyright (c) 2026
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import clean_mobile, clean_pan


class LoanCustomer(Document):
	def validate(self):
		clean_mobile(self, "mobile", "alternate_mobile")
		clean_pan(self)
		if self.aadhaar_last_4 and not re.fullmatch(r"\d{4}", self.aadhaar_last_4.strip()):
			frappe.throw(_("Aadhaar (Last 4 Digits) must be exactly 4 digits. Do not store the full number."))
		if self.is_new() and frappe.db.exists("Loan Customer", {"mobile": self.mobile}):
			frappe.msgprint(_("Another customer already uses mobile {0}.").format(self.mobile), indicator="orange")
