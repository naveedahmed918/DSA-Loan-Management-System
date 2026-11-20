# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.utils import emi

# Order of the overall statuses, so lender updates only ever move an application forward.
STATUS_ORDER = [
	"Draft",
	"Documents Pending",
	"Ready for Login",
	"Logged In",
	"Sanctioned",
	"Partially Disbursed",
	"Disbursed",
]


class LoanApplication(Document):
	def validate(self):
		self.validate_co_applicants()
		self.estimated_emi = emi(self.required_amount, self.expected_interest_rate, self.tenure_months)
		self.foir = self.calculate_foir()

	def validate_co_applicants(self):
		seen = set()
		for row in self.co_applicants:
			if row.loan_customer == self.loan_customer:
				frappe.throw(_("Row {0}: the primary applicant cannot also be a co-applicant.").format(row.idx))
			if row.loan_customer in seen:
				frappe.throw(_("Row {0}: {1} is added twice.").format(row.idx, row.loan_customer))
			seen.add(row.loan_customer)

	def calculate_foir(self):
		"""(existing EMIs + new EMI) / considered income, as a percentage."""
		income = flt(self.monthly_income) + flt(self.other_monthly_income)
		obligations = flt(self.existing_emi) + flt(self.estimated_emi)
		for row in self.co_applicants:
			if row.is_income_considered:
				income += flt(row.monthly_income)
				obligations += flt(row.existing_emi)
		return flt(obligations * 100 / income, 2) if income else 0


def advance_status(application, new_status, **extra):
	"""Move a Loan Application forward to new_status (never backwards); set extra fields too."""
	current = frappe.db.get_value("Loan Application", application, "application_status")
	values = dict(extra)
	if current in STATUS_ORDER and new_status in STATUS_ORDER:
		if STATUS_ORDER.index(new_status) > STATUS_ORDER.index(current):
			values["application_status"] = new_status
	if values:
		frappe.db.set_value("Loan Application", application, values)
