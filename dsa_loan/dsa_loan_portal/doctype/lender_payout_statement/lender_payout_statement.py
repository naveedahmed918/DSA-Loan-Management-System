# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.utils import check_range

TOLERANCE = 1.0  # rupees of rounding difference treated as a match


def line_status(diff):
	if abs(diff) <= TOLERANCE:
		return "Matched"
	return "Short Paid" if diff < 0 else "Excess Paid"


class LenderPayoutStatement(Document):
	def validate(self):
		check_range(self, "period_from", "period_to")
		for row in self.items:
			if row.commission_calculation:
				calc = frappe.db.get_value(
					"Commission Calculation", row.commission_calculation, ["lender", "loan_application", "net_receivable"], as_dict=True
				)
				if calc.lender != self.lender:
					frappe.throw(_("Row {0}: {1} belongs to lender {2}.").format(row.idx, row.commission_calculation, calc.lender))
				row.loan_application = calc.loan_application
				row.expected_amount = calc.net_receivable
			received_with_tds = flt(row.received_amount) + flt(row.tds_amount)
			row.difference_amount = flt(received_with_tds - flt(row.expected_amount), 2)
			if not row.commission_calculation:
				row.line_status = "Unmatched"
			elif row.line_status in (None, "", "Matched", "Short Paid", "Excess Paid"):
				row.line_status = line_status(row.difference_amount)

		self.total_expected = flt(sum(flt(r.expected_amount) for r in self.items), 2)
		self.total_reported = flt(sum(flt(r.reported_amount) for r in self.items), 2)
		accounted = flt(self.amount_received) + flt(self.tds_deducted) + flt(self.other_deductions)
		self.difference_amount = flt(accounted - self.total_expected, 2)

		lines_received = sum(flt(r.received_amount) for r in self.items)
		if self.items and abs(lines_received - flt(self.amount_received)) > TOLERANCE:
			frappe.msgprint(
				_("Line received amounts add up to {0}, but Amount Received is {1}.").format(lines_received, self.amount_received),
				indicator="orange",
			)
		if self.reconciliation_status in ("Pending", "Matched", "Short Paid", "Excess Paid", "Partially Matched"):
			statuses = {r.line_status for r in self.items}
			if statuses and statuses <= {"Matched"}:
				self.reconciliation_status = "Matched"
			elif "Matched" in statuses:
				self.reconciliation_status = "Partially Matched"
			elif self.items:
				self.reconciliation_status = line_status(self.difference_amount)

	def on_update(self):
		if self.reconciliation_status not in ("Matched", "Partially Matched", "Short Paid", "Excess Paid", "Closed"):
			return
		for row in self.items:
			if not row.commission_calculation or not flt(row.received_amount):
				continue
			status = "Received" if row.line_status in ("Matched", "Excess Paid") else "Partially Received"
			frappe.db.set_value("Commission Calculation", row.commission_calculation, "status", status)
