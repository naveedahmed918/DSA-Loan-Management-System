# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

from dsa_loan.dsa_loan_portal.doctype.commission_slab_structure.commission_slab_structure import find_structure


class NoSlabError(frappe.ValidationError):
	pass


class CommissionCalculation(Document):
	def validate(self):
		disb = frappe.db.get_value(
			"Loan Disbursement",
			self.loan_disbursement,
			["docstatus", "status", "disbursed_amount", "disbursement_date", "lender_login", "sanctioned_amount"],
			as_dict=True,
		)
		if not disb or disb.docstatus != 1 or disb.status != "Confirmed":
			frappe.throw(_("Commission can only be calculated on a submitted, Confirmed disbursement."))
		self.fill_links(disb)
		# Rates are a snapshot: work them out once, then leave them alone even if slabs change later.
		if self.is_new() or self.status == "Draft":
			self.snapshot_rates(disb)
		self.calculate()
		if self.status == "Draft":
			self.status = "Calculated"

	def fill_links(self, disb):
		"""fetch_from only runs in the form; fill the same values on server-side inserts."""
		self.lender_login = disb.lender_login
		login = frappe.db.get_value("Lender Login", disb.lender_login, ["loan_application", "lender", "loan_product", "loan_scheme"], as_dict=True)
		self.loan_application, self.lender, self.loan_product = login.loan_application, login.lender, login.loan_product
		app = frappe.db.get_value("Loan Application", login.loan_application, ["dsa_branch", "franchise"], as_dict=True)
		self.dsa_branch, self.franchise = app.dsa_branch, app.franchise
		self._loan_scheme = login.loan_scheme

	def snapshot_rates(self, disb):
		on_date = disb.disbursement_date or nowdate()
		if not self.commission_slab_structure:
			self.commission_slab_structure = find_structure(self.lender, self.loan_product, self._loan_scheme, on_date)
		if not self.commission_slab_structure:
			frappe.throw(
				_("No Active Commission Slab Structure for {0} / {1} on {2}.").format(self.lender, self.loan_product, on_date),
				NoSlabError,
			)
		structure = frappe.get_doc("Commission Slab Structure", self.commission_slab_structure)
		basis = disb.sanctioned_amount if structure.commission_basis == "Sanctioned Amount" else disb.disbursed_amount
		self.commission_basis_amount = flt(basis)
		slab = structure.slab_for(self.commission_basis_amount)
		if not slab:
			frappe.throw(_("No slab in {0} covers the amount {1}.").format(structure.name, self.commission_basis_amount), NoSlabError)
		self.commission_rate = flt(slab.rate_percent)
		self.fixed_commission = flt(slab.fixed_commission)
		self._min, self._max = flt(slab.minimum_commission), flt(slab.maximum_commission)
		self.gst_applicable = structure.gst_applicable
		if self.franchise and not self.franchise_share_percent:
			comp, pct = frappe.db.get_value("Franchise", self.franchise, ["compensation_type", "payout_percent"])
			self.franchise_share_percent = flt(pct) if comp != "Fixed Fee" else 0

	def calculate(self):
		gross = self.fixed_commission or self.commission_basis_amount * flt(self.commission_rate) / 100
		if getattr(self, "_min", 0):
			gross = max(gross, self._min)
		if getattr(self, "_max", 0):
			gross = min(gross, self._max)
		self.gross_commission = flt(gross, 2)
		# GST/TDS rates are entered by accounts; nothing is hard-coded here.
		self.gst_amount = flt(self.gross_commission * flt(self.gst_rate) / 100, 2) if self.gst_applicable else 0
		self.tds_amount = flt(self.gross_commission * flt(self.tds_rate) / 100, 2)
		self.net_receivable = flt(self.gross_commission + self.gst_amount - self.tds_amount, 2)
		self.franchise_share_amount = flt(self.gross_commission * flt(self.franchise_share_percent) / 100, 2) if self.franchise else 0
		self.dsa_retained_amount = flt(self.gross_commission - self.franchise_share_amount, 2)
