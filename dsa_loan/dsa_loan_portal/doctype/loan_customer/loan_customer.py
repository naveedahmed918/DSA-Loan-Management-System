# Copyright (c) 2026
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import clean_mobile, clean_pan


class LoanCustomer(Document):
	def validate(self):
		clean_mobile(self, "mobile_number", "alternate_mobile")
		clean_pan(self)
		self.clean_aadhaar()
		if self.is_new() and frappe.db.exists("Loan Customer", {"mobile_number": self.mobile_number}):
			frappe.msgprint(_("Another customer already uses mobile {0}.").format(self.mobile_number), indicator="orange")

	def clean_aadhaar(self):
		"""Aadhaar is 12 digits; the field is on permission level 1 so only authorised roles see it."""
		if not self.aadhaar_number:
			return
		digits = re.sub(r"\D", "", self.aadhaar_number)
		if len(digits) != 12:
			frappe.throw(_("Aadhaar Number must have 12 digits."))
		self.aadhaar_number = digits
