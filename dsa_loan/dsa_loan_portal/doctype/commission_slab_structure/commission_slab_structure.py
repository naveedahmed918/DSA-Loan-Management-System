# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

from dsa_loan.dsa_loan_portal.utils import check_belongs, check_range


class CommissionSlabStructure(Document):
	"""One commission band (from/to amount, rate or fixed amount) for a lender/product/scheme and period.
	Slab-wise rates are several records with consecutive amount bands."""

	def validate(self):
		check_range(self, "valid_from", "valid_to")
		check_range(self, "minimum_commission", "maximum_commission")
		check_belongs("Loan Product", self.loan_product, "lender", self.lender, "Lender")
		check_belongs("Loan Scheme", self.loan_scheme, "loan_product", self.loan_product, "Loan Product")
		if self.to_amount and flt(self.to_amount) < flt(self.from_amount):
			frappe.throw(_("To Amount cannot be lower than From Amount."))
		if not flt(self.rate_percent) and not flt(self.fixed_commission):
			frappe.throw(_("Enter a Rate Percent or a Fixed Commission."))
		if self.status == "Active":
			self.validate_no_overlap()

	def validate_no_overlap(self):
		"""Two Active records for the same scope may not share both dates and amounts."""
		others = frappe.get_all(
			"Commission Slab Structure",
			filters={
				"status": "Active",
				"lender": self.lender,
				"loan_product": self.loan_product,
				"loan_scheme": self.loan_scheme or ("is", "not set"),
				"name": ("!=", self.name),
			},
			fields=["name", "valid_from", "valid_to", "from_amount", "to_amount"],
		)
		start, end = getdate(self.valid_from), getdate(self.valid_to) if self.valid_to else None
		low, high = flt(self.from_amount), flt(self.to_amount) if self.to_amount else None
		for o in others:
			o_start, o_end = getdate(o.valid_from), getdate(o.valid_to) if o.valid_to else None
			dates_overlap = (end is None or o_start <= end) and (o_end is None or start <= o_end)
			o_low, o_high = flt(o.from_amount), flt(o.to_amount) if o.to_amount else None
			amounts_overlap = (high is None or o_low <= high) and (o_high is None or low <= o_high)
			if dates_overlap and amounts_overlap:
				frappe.throw(
					_("Active slab {0} already covers these dates and amounts for the same lender, product and scheme.").format(o.name)
				)

	def covers(self, amount):
		amount = flt(amount)
		return amount >= flt(self.from_amount) and (not self.to_amount or amount <= flt(self.to_amount))


def find_structures(lender, loan_product, loan_scheme, on_date):
	"""Active slabs valid on a date: the scheme-specific ones if any exist, else the product-wide ones."""
	base = {"status": "Active", "lender": lender, "loan_product": loan_product, "valid_from": ("<=", on_date)}
	for scheme in ([loan_scheme] if loan_scheme else []) + [None]:
		names = frappe.get_all(
			"Commission Slab Structure",
			filters=dict(base, loan_scheme=scheme or ("is", "not set")),
			or_filters=[["valid_to", "is", "not set"], ["valid_to", ">=", on_date]],
			pluck="name",
			order_by="from_amount asc",
		)
		if names:
			return [frappe.get_doc("Commission Slab Structure", n) for n in names]
	return []
