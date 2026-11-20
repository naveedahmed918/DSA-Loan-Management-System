# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.utils import check_range

OPEN = ("Draft", "Pending Approval")
RECEIVED = ("Received", "Partially Received")
APPROVED_CLAWBACK = ("Approved", "Partially Recovered", "Recovered")


class FranchiseSettlement(Document):
	"""Pays a franchise its share of commission actually received in a period, less approved clawbacks.
	Included commissions and clawbacks point back here through their franchise_settlement field."""

	def validate(self):
		check_range(self, "period_from", "period_to")
		franchise = frappe.db.get_value("Franchise", self.franchise, ["dsa_branch", "compensation_type", "fixed_monthly_fee"], as_dict=True)
		self.dsa_branch, self.compensation_type = franchise.dsa_branch, franchise.compensation_type
		if not self.fixed_fee_amount and franchise.compensation_type in ("Fixed Fee", "Both"):
			self.fixed_fee_amount = franchise.fixed_monthly_fee

		calcs, clawbacks = self.collect() if (self.status in OPEN or self.is_new()) else self.linked()
		if not calcs and not clawbacks and not flt(self.fixed_fee_amount) and self.status != "Cancelled":
			frappe.throw(_("Nothing to settle for {0} between {1} and {2}.").format(self.franchise, self.period_from, self.period_to))
		self._calcs, self._clawbacks = [c.name for c in calcs], [c.name for c in clawbacks]
		self.commission_count, self.clawback_count = len(calcs), len(clawbacks)
		self.gross_commission_share = flt(sum(flt(c.franchise_share_amount) for c in calcs), 2)
		self.clawback_deduction = flt(sum(flt(c.franchise_recovery_amount) for c in clawbacks), 2)
		self.net_payable = flt(
			self.gross_commission_share
			+ flt(self.fixed_fee_amount)
			- self.clawback_deduction
			- flt(self.other_adjustments)
			+ flt(self.gst_amount)
			- flt(self.tds_amount),
			2,
		)
		if self.has_value_changed("status") and self.status == "Paid" and not self.payment_date:
			frappe.throw(_("Enter the Payment Date before marking the settlement Paid."))

	def linked(self):
		calcs = frappe.get_all("Commission Calculation", {"franchise_settlement": self.name}, ["name", "franchise_share_amount"])
		clawbacks = frappe.get_all("Commission Clawback", {"franchise_settlement": self.name}, ["name", "franchise_recovery_amount"])
		return calcs, clawbacks

	def collect(self):
		"""Commission the DSA has received from the lender, and approved clawbacks, not yet settled."""
		mine_or_free = [["franchise_settlement", "is", "not set"], ["franchise_settlement", "=", self.name]]
		calcs = frappe.get_all(
			"Commission Calculation",
			filters={"franchise": self.franchise, "status": ("in", RECEIVED), "calculation_date": ("between", [self.period_from, self.period_to])},
			or_filters=mine_or_free,
			fields=["name", "franchise_share_amount"],
		)
		clawbacks = frappe.get_all(
			"Commission Clawback",
			filters={"franchise": self.franchise, "status": ("in", APPROVED_CLAWBACK), "clawback_date": ("<=", self.period_to)},
			or_filters=mine_or_free,
			fields=["name", "franchise_recovery_amount"],
		)
		return calcs, clawbacks

	def on_update(self):
		calcs, clawbacks = self.linked()
		if self.status == "Cancelled":
			self.release(calcs, clawbacks)
			return
		keep_calcs, keep_cbs = set(getattr(self, "_calcs", [])), set(getattr(self, "_clawbacks", []))
		self.release([c for c in calcs if c.name not in keep_calcs], [c for c in clawbacks if c.name not in keep_cbs])
		for name in keep_calcs:
			frappe.db.set_value("Commission Calculation", name, "franchise_settlement", self.name)
		for name in keep_cbs:
			frappe.db.set_value("Commission Clawback", name, "franchise_settlement", self.name)

	def on_trash(self):
		self.release(*self.linked())

	@staticmethod
	def release(calcs, clawbacks):
		for c in calcs:
			frappe.db.set_value("Commission Calculation", c.name, "franchise_settlement", None)
		for c in clawbacks:
			frappe.db.set_value("Commission Clawback", c.name, "franchise_settlement", None)
