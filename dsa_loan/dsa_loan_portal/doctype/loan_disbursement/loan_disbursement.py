# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

from dsa_loan.dsa_loan_portal.doctype.loan_application.loan_application import advance_status

ALLOWED_LOGIN_STATUS = ("Sanctioned", "Disbursed")


class LoanDisbursement(Document):
	def validate(self):
		login = frappe.db.get_value(
			"Lender Login", self.lender_login, ["status", "loan_application", "lender", "loan_customer", "sanctioned_amount"], as_dict=True
		)
		login_status = login.status
		self.loan_application, self.lender, self.loan_customer = login.loan_application, login.lender, login.loan_customer
		self.sanctioned_amount = login.sanctioned_amount
		if login_status not in ALLOWED_LOGIN_STATUS:
			frappe.throw(_("Lender Login {0} must be Sanctioned before disbursement (it is {1}).").format(self.lender_login, login_status))
		if flt(self.disbursed_amount) <= 0:
			frappe.throw(_("Disbursed Amount must be greater than zero."))
		if frappe.db.exists(
			"Loan Disbursement",
			{"lender_login": self.lender_login, "tranche_no": self.tranche_no, "docstatus": ("<", 2), "name": ("!=", self.name)},
		):
			frappe.throw(_("Tranche {0} already exists for {1}.").format(self.tranche_no, self.lender_login))
		self.set_amounts()

	def set_amounts(self):
		rows = frappe.get_all(
			"Loan Disbursement",
			filters={"lender_login": self.lender_login, "docstatus": 1, "status": "Confirmed", "name": ("!=", self.name)},
			fields=[{"SUM": "disbursed_amount", "as": "total"}],
		)
		previous = flt(rows[0].total) if rows else 0
		self.cumulative_disbursed = previous + flt(self.disbursed_amount)
		if flt(self.sanctioned_amount) and self.cumulative_disbursed > flt(self.sanctioned_amount):
			frappe.throw(
				_("Total disbursed {0} would exceed the sanctioned amount {1}.").format(
					frappe.format(self.cumulative_disbursed, "Currency"), frappe.format(self.sanctioned_amount, "Currency")
				)
			)
		self.balance_to_disburse = flt(self.sanctioned_amount) - self.cumulative_disbursed

	def before_submit(self):
		# Submitting a disbursement confirms it.
		self.status = "Confirmed"
		self.confirmed_by = frappe.session.user
		self.confirmation_date = nowdate()

	def on_submit(self):
		fully = flt(self.balance_to_disburse) <= 0 or self.disbursement_type in ("Full", "Final")
		frappe.db.set_value("Lender Login", self.lender_login, "status", "Disbursed")
		advance_status(
			self.loan_application,
			"Disbursed" if fully else "Partially Disbursed",
			final_lender_login=self.lender_login,
		)
		self.create_commission()

	def create_commission(self):
		from dsa_loan.dsa_loan_portal.doctype.commission_calculation.commission_calculation import NoSlabError

		try:
			calc = frappe.get_doc({"doctype": "Commission Calculation", "loan_disbursement": self.name})
			calc.insert(ignore_permissions=True)
			frappe.msgprint(_("Commission Calculation {0} created.").format(calc.name), alert=True)
		except NoSlabError as e:
			frappe.clear_last_message()
			frappe.msgprint(
				_("No commission was calculated: {0} Create the Commission Calculation manually once a slab exists.").format(e),
				indicator="orange",
			)

	def before_cancel(self):
		calc = frappe.db.get_value("Commission Calculation", {"loan_disbursement": self.name}, ["name", "status"], as_dict=True)
		if calc and calc.status not in ("Draft", "Calculated", "Reversed"):
			frappe.throw(_("Commission {0} is already {1}. Record a Commission Clawback instead of cancelling.").format(calc.name, calc.status))
		self.ignore_linked_doctypes = ("Commission Calculation",)

	def on_cancel(self):
		self.db_set("status", "Reversed")
		calc = frappe.db.get_value("Commission Calculation", {"loan_disbursement": self.name})
		if calc:
			frappe.db.set_value("Commission Calculation", calc, "status", "Reversed")
