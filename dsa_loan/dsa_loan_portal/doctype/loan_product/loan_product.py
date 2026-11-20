# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import check_range


class LoanProduct(Document):
	def before_naming(self):
		# The code is the record name, so normalise it before naming, not in validate.
		self.product_code = (self.product_code or "").strip().upper()

	def validate(self):
		check_range(self, "min_amount", "max_amount")
		check_range(self, "min_tenure_months", "max_tenure_months")
		check_range(self, "min_interest_rate", "max_interest_rate")
		if self.processing_fee_type == "Percentage" and (self.processing_fee or 0) > 100:
			frappe.throw(_("Processing fee percentage cannot exceed 100."))
