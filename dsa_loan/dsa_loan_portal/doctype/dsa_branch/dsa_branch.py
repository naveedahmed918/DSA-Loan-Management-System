# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class DSABranch(Document):
	def before_naming(self):
		# The code is the record name, so normalise it before naming, not in validate.
		self.branch_code = (self.branch_code or "").strip().upper()

	def validate(self):
		if self.branch_type in ("Franchise Owned", "Franchise Operated") and not self.franchise:
			frappe.throw(_("Select the Franchise for a {0} branch.").format(self.branch_type))
