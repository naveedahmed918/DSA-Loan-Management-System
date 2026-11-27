# Copyright (c) 2026
# For license information, please see license.txt

from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import check_range


class LoanProduct(Document):
	def before_naming(self):
		# The code is the record name, so normalise it before naming, not in validate.
		self.product_code = (self.product_code or "").strip().upper()

	def validate(self):
		check_range(self, "minimum_loan_amount", "maximum_loan_amount")
		check_range(self, "minimum_tenure_months", "maximum_tenure_months")
		check_range(self, "minimum_interest_rate", "maximum_interest_rate")
