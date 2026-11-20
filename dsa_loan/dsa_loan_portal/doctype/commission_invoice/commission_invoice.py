# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.utils import check_range

INVOICEABLE = ("Calculated", "Approved", "Invoiced")
LIVE = ("Invoiced", "Sent", "Partially Paid", "Paid")


class CommissionInvoice(Document):
	def validate(self):
		check_range(self, "period_from", "period_to")
		self.validate_items()
		self.total_commission = flt(sum(flt(r.taxable_amount) for r in self.items), 2)
		item_gst = sum(flt(r.gst_amount) for r in self.items)
		split = flt(self.cgst_amount) + flt(self.sgst_amount) + flt(self.igst_amount)
		self.grand_total = flt(self.total_commission + (split or item_gst), 2)
		if not self.billing_email:
			self.billing_email = frappe.db.get_value("Lender", self.lender, "billing_email")

	def validate_items(self):
		seen = set()
		for row in self.items:
			calc = frappe.db.get_value(
				"Commission Calculation",
				row.commission_calculation,
				["lender", "status", "commission_invoice", "gross_commission", "gst_amount", "loan_application", "loan_disbursement", "commission_basis_amount", "commission_rate"],
				as_dict=True,
			)
			if calc.lender != self.lender:
				frappe.throw(_("Row {0}: {1} belongs to lender {2}.").format(row.idx, row.commission_calculation, calc.lender))
			if calc.status not in INVOICEABLE:
				frappe.throw(_("Row {0}: {1} is {2} and cannot be invoiced.").format(row.idx, row.commission_calculation, calc.status))
			if calc.commission_invoice and calc.commission_invoice != self.name:
				frappe.throw(_("Row {0}: {1} is already on invoice {2}.").format(row.idx, row.commission_calculation, calc.commission_invoice))
			if row.commission_calculation in seen:
				frappe.throw(_("Row {0}: {1} is listed twice.").format(row.idx, row.commission_calculation))
			seen.add(row.commission_calculation)
			row.loan_application = calc.loan_application
			row.loan_disbursement = calc.loan_disbursement
			row.loan_customer = frappe.db.get_value("Loan Application", calc.loan_application, "loan_customer")
			row.disbursed_amount = calc.commission_basis_amount
			row.commission_rate = calc.commission_rate
			if not row.taxable_amount:
				row.taxable_amount = calc.gross_commission
			if not row.gst_amount:
				row.gst_amount = calc.gst_amount
			row.line_total = flt(flt(row.taxable_amount) + flt(row.gst_amount), 2)

	def on_update(self):
		names = [r.commission_calculation for r in self.items]
		if self.status == "Cancelled":
			for name in names:
				frappe.db.set_value("Commission Calculation", name, {"commission_invoice": None, "status": "Approved"})
			return
		# Release calculations that were removed from this invoice.
		for name in frappe.get_all("Commission Calculation", {"commission_invoice": self.name, "name": ("not in", names or [""])}, pluck="name"):
			frappe.db.set_value("Commission Calculation", name, {"commission_invoice": None, "status": "Approved"})
		for name in names:
			values = {"commission_invoice": self.name}
			if self.status in LIVE:
				values["status"] = "Invoiced" if self.status != "Paid" else "Received"
			frappe.db.set_value("Commission Calculation", name, values)


@frappe.whitelist()
def get_invoiceable_commissions(lender, period_from=None, period_to=None):
	"""Calculations for a lender that are not yet on any invoice, for the Get Commissions button."""
	filters = {"lender": lender, "status": ("in", ["Calculated", "Approved"]), "commission_invoice": ("is", "not set")}
	if period_from and period_to:
		filters["calculation_date"] = ("between", [period_from, period_to])
	return frappe.get_all(
		"Commission Calculation",
		filters=filters,
		fields=["name", "gross_commission", "gst_amount", "loan_application"],
		order_by="calculation_date",
	)
