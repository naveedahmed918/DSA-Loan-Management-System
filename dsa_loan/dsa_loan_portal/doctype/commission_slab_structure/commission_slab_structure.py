# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

from dsa_loan.dsa_loan_portal.utils import check_belongs, check_range


class CommissionSlabStructure(Document):
	def validate(self):
		check_range(self, "valid_from", "valid_to")
		check_belongs("Loan Product", self.loan_product, "lender", self.lender, "Lender")
		check_belongs("Loan Scheme", self.loan_scheme, "loan_product", self.loan_product, "Loan Product")
		self.validate_slabs()
		if self.status == "Active":
			self.validate_no_overlap()

	def validate_slabs(self):
		if not self.slabs:
			frappe.throw(_("Add at least one commission slab."))
		rows = sorted(self.slabs, key=lambda r: flt(r.from_amount))
		for i, row in enumerate(rows):
			if not flt(row.rate_percent) and not flt(row.fixed_commission):
				frappe.throw(_("Row {0}: enter a rate or a fixed commission.").format(row.idx))
			if row.to_amount and flt(row.to_amount) < flt(row.from_amount):
				frappe.throw(_("Row {0}: To Amount cannot be lower than From Amount.").format(row.idx))
			if row.minimum_commission and row.maximum_commission and flt(row.maximum_commission) < flt(row.minimum_commission):
				frappe.throw(_("Row {0}: Maximum Commission cannot be lower than Minimum Commission.").format(row.idx))
			if i + 1 < len(rows):
				nxt = rows[i + 1]
				if not row.to_amount or flt(row.to_amount) >= flt(nxt.from_amount):
					frappe.throw(_("Slab rows {0} and {1} overlap.").format(row.idx, nxt.idx))

	def validate_no_overlap(self):
		"""Only one Active structure may cover the same lender/product/scheme on any date."""
		others = frappe.get_all(
			"Commission Slab Structure",
			filters={
				"status": "Active",
				"lender": self.lender,
				"loan_product": self.loan_product,
				"loan_scheme": self.loan_scheme or ("is", "not set"),
				"name": ("!=", self.name),
			},
			fields=["name", "valid_from", "valid_to"],
		)
		start, end = getdate(self.valid_from), getdate(self.valid_to) if self.valid_to else None
		for o in others:
			o_start, o_end = getdate(o.valid_from), getdate(o.valid_to) if o.valid_to else None
			if (end is None or o_start <= end) and (o_end is None or start <= o_end):
				frappe.throw(_("Active structure {0} already covers these dates for the same lender, product and scheme.").format(o.name))

	def slab_for(self, amount):
		amount = flt(amount)
		for row in sorted(self.slabs, key=lambda r: flt(r.from_amount)):
			if amount >= flt(row.from_amount) and (not row.to_amount or amount <= flt(row.to_amount)):
				return row
		return None


def find_structure(lender, loan_product, loan_scheme, on_date):
	"""The Active structure for a scope and date; a scheme-specific one wins over the product-wide one."""
	base = {"status": "Active", "lender": lender, "loan_product": loan_product, "valid_from": ("<=", on_date)}
	for scheme in ([loan_scheme] if loan_scheme else []) + [None]:
		filters = dict(base, loan_scheme=scheme or ("is", "not set"))
		rows = frappe.get_all(
			"Commission Slab Structure",
			filters=filters,
			or_filters=[["valid_to", "is", "not set"], ["valid_to", ">=", on_date]],
			pluck="name",
			order_by="valid_from desc",
			limit=1,
		)
		if rows:
			return rows[0]
	return None
