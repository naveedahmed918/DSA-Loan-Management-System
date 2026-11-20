# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.utils import check_range

OPEN = ("Draft", "Pending Approval")
LIVE = ("Invoiced", "Sent", "Partially Paid", "Paid")
INVOICEABLE = ("Calculated", "Approved")


class CommissionInvoice(Document):
	"""Groups a lender's commissions for a period. Each included Commission Calculation points back
	here through its commission_invoice field; there are no item rows."""

	def validate(self):
		check_range(self, "period_from", "period_to")
		if not self.billing_email:
			self.billing_email = frappe.db.get_value("Lender", self.lender, "billing_email")
		calcs = self.collect() if (self.status in OPEN or self.is_new()) else self.linked()
		if not calcs and self.status != "Cancelled":
			frappe.throw(_("No un-invoiced commissions found for {0} between {1} and {2}.").format(self.lender, self.period_from, self.period_to))
		self._calc_names = [c.name for c in calcs]
		self.commission_count = len(calcs)
		self.total_commission = flt(sum(flt(c.gross_commission) for c in calcs), 2)
		self.total_gst = flt(sum(flt(c.gst_amount) for c in calcs), 2)
		split = flt(self.cgst_amount) + flt(self.sgst_amount) + flt(self.igst_amount)
		if split and abs(split - self.total_gst) > 0.5:
			frappe.msgprint(_("CGST + SGST + IGST ({0}) does not equal the commissions' GST ({1}).").format(split, self.total_gst), indicator="orange")
		self.grand_total = flt(self.total_commission + (split or self.total_gst), 2)

	def linked(self):
		return frappe.get_all(
			"Commission Calculation", {"commission_invoice": self.name}, ["name", "gross_commission", "gst_amount"]
		)

	def collect(self):
		"""This invoice's commissions plus every un-invoiced one of the lender within the period."""
		return frappe.get_all(
			"Commission Calculation",
			filters={
				"lender": self.lender,
				"calculation_date": ("between", [self.period_from, self.period_to]),
				"status": ("in", INVOICEABLE + ("Invoiced",)),
			},
			or_filters=[["commission_invoice", "is", "not set"], ["commission_invoice", "=", self.name]],
			fields=["name", "gross_commission", "gst_amount"],
		)

	def on_update(self):
		if self.status == "Cancelled":
			self.release(self.linked())
			return
		names = set(getattr(self, "_calc_names", []))
		self.release([c for c in self.linked() if c.name not in names])
		for name in names:
			values = {"commission_invoice": self.name}
			if self.status in LIVE:
				values["status"] = "Received" if self.status == "Paid" else "Invoiced"
			frappe.db.set_value("Commission Calculation", name, values)

	def on_trash(self):
		self.release(self.linked())

	@staticmethod
	def release(calcs):
		for c in calcs:
			frappe.db.set_value("Commission Calculation", c.name, {"commission_invoice": None, "status": "Approved"})
