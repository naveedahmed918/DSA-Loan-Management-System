# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.utils import check_range

TOLERANCE = 1.0  # rupees of rounding difference treated as a match
AUTO = ("Pending", "Matched", "Short Paid", "Excess Paid")


class LenderPayoutStatement(Document):
	"""Reconciles what a lender actually paid against one Commission Invoice."""

	def validate(self):
		check_range(self, "period_from", "period_to")
		inv = frappe.db.get_value(
			"Commission Invoice", self.commission_invoice, ["lender", "status", "grand_total", "tds_expected"], as_dict=True
		)
		if inv.lender != self.lender:
			frappe.throw(_("Commission Invoice {0} belongs to lender {1}.").format(self.commission_invoice, inv.lender))
		if inv.status in ("Draft", "Pending Approval", "Cancelled"):
			frappe.throw(_("Commission Invoice {0} is {1}; reconcile only issued invoices.").format(self.commission_invoice, inv.status))
		dup = frappe.db.get_value(
			"Lender Payout Statement",
			{"commission_invoice": self.commission_invoice, "reconciliation_status": ("!=", "Disputed"), "name": ("!=", self.name)},
		)
		if dup:
			frappe.throw(_("Invoice {0} is already reconciled in {1}.").format(self.commission_invoice, dup))

		self.expected_amount = flt(flt(inv.grand_total) - flt(inv.tds_expected), 2)
		accounted = flt(self.amount_received) + flt(self.tds_deducted) + flt(self.other_deductions)
		self.difference_amount = flt(accounted - flt(inv.grand_total), 2)
		if self.reconciliation_status in AUTO:
			d = self.difference_amount
			self.reconciliation_status = "Matched" if abs(d) <= TOLERANCE else ("Short Paid" if d < 0 else "Excess Paid")

	def on_update(self):
		if self.reconciliation_status not in ("Matched", "Short Paid", "Excess Paid", "Closed"):
			return
		fully = self.reconciliation_status in ("Matched", "Excess Paid", "Closed")
		frappe.db.set_value("Commission Invoice", self.commission_invoice, "status", "Paid" if fully else "Partially Paid")
		for name in frappe.get_all("Commission Calculation", {"commission_invoice": self.commission_invoice}, pluck="name"):
			frappe.db.set_value("Commission Calculation", name, "status", "Received" if fully else "Partially Received")
