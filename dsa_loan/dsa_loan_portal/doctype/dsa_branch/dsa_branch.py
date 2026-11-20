# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import clean_mobile


class DSABranch(Document):
	def before_naming(self):
		# The code is the record name, so normalise it before naming, not in validate.
		self.branch_code = (self.branch_code or "").strip().upper()

	def validate(self):
		clean_mobile(self, "contact_number")
		if self.parent_branch and self.parent_branch == self.name:
			frappe.throw(_("A branch cannot be its own parent."))
