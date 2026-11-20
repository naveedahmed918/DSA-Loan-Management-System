# Copyright (c) 2026
# For license information, please see license.txt

from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import check_range


class LoanScheme(Document):
	def validate(self):
		check_range(self, "valid_from", "valid_to")
		check_range(self, "min_age", "max_age")
		check_range(self, "min_loan_amount", "max_loan_amount")
