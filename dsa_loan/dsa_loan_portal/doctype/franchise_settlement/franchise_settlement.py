# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.utils import check_range

RECEIVED = ("Received", "Partially Received")


class FranchiseSettlement(Document):
	def validate(self):
		check_range(self, "period_from", "period_to")
		franchise = frappe.db.get_value("Franchise", self.franchise, ["dsa_branch", "compensation_type", "fixed_monthly_fee"], as_dict=True)
		self.dsa_branch, self.compensation_type = franchise.dsa_branch, franchise.compensation_type
		if not self.fixed_fee_amount and franchise.compensation_type in ("Fixed Fee", "Both"):
			self.fixed_fee_amount = franchise.fixed_monthly_fee
		self.validate_items()

		self.gross_commission_share = flt(sum(flt(r.gross_share) for r in self.items), 2)
		self.clawback_deduction = flt(sum(flt(r.deduction) for r in self.items if r.commission_clawback), 2)
		line_deductions = flt(sum(flt(r.deduction) for r in self.items if not r.commission_clawback), 2)
		self.net_payable = flt(
			self.gross_commission_share
			+ flt(self.fixed_fee_amount)
			- self.clawback_deduction
			- line_deductions
			- flt(self.other_adjustments)
			+ flt(self.gst_amount)
			- flt(self.tds_amount),
			2,
		)
		if self.has_value_changed("status") and self.status == "Paid" and not self.payment_date:
			frappe.throw(_("Enter the Payment Date before marking the settlement Paid."))

	def validate_items(self):
		for row in self.items:
			if row.commission_clawback:
				cb = frappe.db.get_value("Commission Clawback", row.commission_clawback, ["franchise", "franchise_recovery_amount", "franchise_settlement", "status"], as_dict=True)
				if cb.franchise != self.franchise:
					frappe.throw(_("Row {0}: clawback {1} is not for this franchise.").format(row.idx, row.commission_clawback))
				if cb.franchise_settlement and cb.franchise_settlement != self.name:
					frappe.throw(_("Row {0}: clawback {1} was already settled in {2}.").format(row.idx, row.commission_clawback, cb.franchise_settlement))
				if cb.status not in ("Approved", "Partially Recovered", "Recovered"):
					frappe.throw(_("Row {0}: clawback {1} must be Approved first.").format(row.idx, row.commission_clawback))
				row.gross_share = row.gross_share or 0
				row.deduction = row.deduction or cb.franchise_recovery_amount
			if row.commission_calculation:
				calc = frappe.db.get_value(
					"Commission Calculation",
					row.commission_calculation,
					["franchise", "status", "franchise_settlement", "loan_application", "net_receivable", "franchise_share_percent", "franchise_share_amount"],
					as_dict=True,
				)
				if calc.franchise != self.franchise:
					frappe.throw(_("Row {0}: {1} is not sourced by this franchise.").format(row.idx, row.commission_calculation))
				if calc.status not in RECEIVED:
					frappe.throw(_("Row {0}: commission {1} has not been received from the lender yet ({2}).").format(row.idx, row.commission_calculation, calc.status))
				if calc.franchise_settlement and calc.franchise_settlement != self.name:
					frappe.throw(_("Row {0}: {1} was already settled in {2}.").format(row.idx, row.commission_calculation, calc.franchise_settlement))
				row.loan_application = calc.loan_application
				row.commission_received = row.commission_received or calc.net_receivable
				row.share_percent = row.share_percent or calc.franchise_share_percent
				if not row.gross_share:
					row.gross_share = calc.franchise_share_amount
			if not row.commission_calculation and not row.commission_clawback:
				frappe.throw(_("Row {0}: link a Commission Calculation or a Commission Clawback.").format(row.idx))
			row.net_share = flt(flt(row.gross_share) - flt(row.deduction), 2)

	def on_update(self):
		cancelled = self.status == "Cancelled"
		for row in self.items:
			if row.commission_calculation:
				frappe.db.set_value("Commission Calculation", row.commission_calculation, "franchise_settlement", None if cancelled else self.name)
			if row.commission_clawback:
				frappe.db.set_value("Commission Clawback", row.commission_clawback, "franchise_settlement", None if cancelled else self.name)


@frappe.whitelist()
def get_settleable(franchise):
	"""Received commissions and approved clawbacks for this franchise that are not settled yet."""
	calcs = frappe.get_all(
		"Commission Calculation",
		filters={"franchise": franchise, "status": ("in", RECEIVED), "franchise_settlement": ("is", "not set")},
		fields=["name", "franchise_share_amount"],
	)
	clawbacks = frappe.get_all(
		"Commission Clawback",
		filters={"franchise": franchise, "status": ("in", ["Approved", "Partially Recovered", "Recovered"]), "franchise_settlement": ("is", "not set")},
		fields=["name", "franchise_recovery_amount"],
	)
	return {"calculations": calcs, "clawbacks": clawbacks}
