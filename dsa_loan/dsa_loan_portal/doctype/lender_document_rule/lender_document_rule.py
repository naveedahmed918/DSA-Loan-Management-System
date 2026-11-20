# Copyright (c) 2026
# For license information, please see license.txt

from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import check_belongs, check_range


class LenderDocumentRule(Document):
	def validate(self):
		check_range(self, "valid_from", "valid_to")
		check_belongs("Loan Product", self.loan_product, "lender", self.lender, "Lender")
		check_belongs("Loan Scheme", self.loan_scheme, "loan_product", self.loan_product, "Loan Product")
