# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CommissionClawback(Document):
	def validate(self):
		calc = frappe.db.get_value(
			"Commission Calculation",
			self.commission_calculation,
			["loan_application", "loan_disbursement", "lender", "franchise", "commission_invoice", "gross_commission", "franchise_share_amount"],
			as_dict=True,
		)
		self.loan_application, self.loan_disbursement = calc.loan_application, calc.loan_disbursement
		self.lender, self.franchise = calc.lender, calc.franchise
		self.commission_invoice = self.commission_invoice or calc.commission_invoice
		self.original_commission = calc.gross_commission

		if self.clawback_percent and not self.clawback_amount:
			self.clawback_amount = flt(self.original_commission * flt(self.clawback_percent) / 100, 2)
		elif self.clawback_amount and self.original_commission:
			self.clawback_percent = flt(self.clawback_amount * 100 / self.original_commission, 2)
		if flt(self.clawback_amount) <= 0:
			frappe.throw(_("Clawback Amount must be greater than zero."))
		if flt(self.clawback_amount) > flt(self.original_commission):
			frappe.throw(_("Clawback Amount cannot exceed the original commission {0}.").format(self.original_commission))
		if self.franchise and not self.franchise_recovery_amount and calc.franchise_share_amount:
			# Default: recover the franchise's share in the same proportion. Editable, since agreements differ.
			self.franchise_recovery_amount = flt(calc.franchise_share_amount * flt(self.clawback_percent) / 100, 2)
		if self.has_value_changed("status") and self.status == "Approved":
			self.approved_by = frappe.session.user

	def on_update(self):
		if self.status in ("Approved", "Partially Recovered", "Recovered") and flt(self.clawback_amount) >= flt(self.original_commission):
			frappe.db.set_value("Commission Calculation", self.commission_calculation, "status", "Reversed")
