# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, date_diff, flt, getdate, nowdate

from dsa_loan.dsa_loan_portal.utils import check_belongs, emi, is_active_on

# Order of final_status values that code may move forward automatically.
FORWARD = ["Draft", "Documents Pending", "Ready for Submission", "Submitted", "Under Review", "Query Raised",
           "Sanctioned", "Partially Disbursed", "Disbursed"]
DISBURSABLE = ("Sanctioned", "Partially Disbursed")
# Business channel -> franchise's share of the commission (%). The DSA keeps the rest.
FRANCHISE_SHARE = {"DSA Owned": 0, "Franchise Operated": 30, "Franchise Owned": 60}
CIBIL_VALID_DAYS = 30
RBI_LTV_LOAN_TYPES = ("Home Loan", "Balance Transfer")
# Loan Purpose choices per Loan Type (the form offers only these; kept in step with generate_doctypes.LOAN_PURPOSES)
LOAN_PURPOSES = {
	"Home Loan": ["Purchase - Ready Property", "Purchase - Under Construction", "Self Construction",
	              "Extension / Renovation"],
	"Loan Against Property": ["Business Expansion", "Working Capital", "Education", "Medical", "Marriage",
	                          "Debt Consolidation", "Other Personal Need"],
	"Balance Transfer": ["Balance Transfer", "Balance Transfer + Top-up"],
	"Plot": ["Plot Purchase"],
	"Plot + Construction": ["Plot Purchase + Construction"],
}


def rbi_ltv_cap(amount):
	"""RBI housing-loan LTV ceiling: up to 30 lakh 90%, above 30 up to 75 lakh 80%, above 75 lakh 75%."""
	return 90 if amount <= 3000000 else 80 if amount <= 7500000 else 75


class LoanApplication(Document):
	def validate(self):
		from dsa_loan.dsa_loan_portal.utils import clean_pincode

		clean_pincode(self, "property_pincode")
		check_belongs("Loan Product", self.loan_product, "lender", self.lender, "Lender")
		check_belongs("Lender Branch", self.lender_branch, "lender", self.lender, "Lender")
		check_belongs("Loan Scheme", self.loan_scheme, "loan_product", self.loan_product, "Loan Product")
		if not self.loan_lead and self.loan_customer:  # Lead -> Customer -> Application
			self.loan_lead = frappe.db.get_value("Loan Customer", self.loan_customer, "loan_lead")
		self.validate_channel()
		self.fill_branch_staff()
		allowed = LOAN_PURPOSES.get(self.loan_type, [])
		if self.loan_purpose not in allowed:
			frappe.throw(_("For a {0}, choose the Loan Purpose from: {1}.").format(self.loan_type, ", ".join(allowed)))
		self.validate_co_applicants()
		self.validate_status_fields()
		self.warn_old_cibil()
		self.validate_limits()
		self.estimated_emi = emi(self.requested_loan_amount, self.expected_interest_rate, self.requested_tenure_months)
		if self.sanction_date and self.lender_submission_date and getdate(self.sanction_date) < getdate(self.lender_submission_date):
			frappe.throw(_("Sanction Date cannot be before Lender Submission Date."))

	def validate_channel(self):
		"""DSA Owned -> a DSA branch (no franchise). Franchise Operated / Owned -> the franchise and one of its branches."""
		branch_franchise, self.company = frappe.db.get_value("DSA Branch", self.dsa_branch, ["franchise", "company"]) or (None, None)
		if self.business_channel == "DSA Owned":
			self.franchise = None
			if branch_franchise:
				frappe.throw(_("{0} is franchise {1}'s branch. Pick a DSA branch, or change the Business Channel.").format(
					self.dsa_branch, branch_franchise))
			return
		if not self.franchise:
			frappe.throw(_("Select the Franchise for a {0} loan.").format(self.business_channel))
		if branch_franchise != self.franchise:
			frappe.throw(_("{0} is not a branch of franchise {1}.").format(self.dsa_branch, self.franchise))

	def fill_branch_staff(self):
		"""Branch Manager and Assigned Agent come from the DSA Branch (its Branch Manager and Branch Agent)."""
		manager, agent = frappe.db.get_value("DSA Branch", self.dsa_branch, ["branch_manager", "default_agent"]) or (None, None)
		if self.is_new() or self.has_value_changed("dsa_branch"):
			self.branch_manager = manager or self.branch_manager
		self.assigned_agent = self.assigned_agent or agent
		if not self.assigned_agent:
			frappe.throw(_("Set the Branch Agent on DSA Branch {0}, or choose the Assigned Agent.").format(self.dsa_branch))

	def validate_co_applicants(self):
		seen = set()
		for row in self.co_applicants:
			if row.applicant == self.loan_customer:
				frappe.throw(_("Row {0}: the loan customer cannot also be a co-applicant.").format(row.idx))
			if row.applicant in seen:
				frappe.throw(_("Row {0}: {1} is added twice.").format(row.idx, row.applicant))
			seen.add(row.applicant)

	def validate_status_fields(self):
		"""Server-side twin of the form's mandatory_depends_on rules."""
		if self.final_status == "Sanctioned" and not (self.sanctioned_amount and self.sanction_date):
			frappe.throw(_("Enter the Sanctioned Amount and Sanction Date before marking the application Sanctioned."))
		if self.final_status == "Rejected" and not self.rejection_reason:
			frappe.throw(_("Enter the Rejection Reason before marking the application Rejected."))
		# Disbursed / Partially Disbursed are set by confirming a Loan Disbursement (which also creates the
		# commission and the lender invoice); typing them here by hand would skip all of that.
		if (self.final_status in ("Partially Disbursed", "Disbursed") and self.has_value_changed("final_status")
				and not frappe.db.exists("Loan Disbursement", {"loan_application": self.name, "disbursement_status": "Confirmed"})):
			frappe.throw(_("Record the money released with the <b>New Disbursement</b> button (status Confirmed). The application "
			               "then becomes {0} by itself, and the commission and lender invoice are created.").format(self.final_status))

	def validate_limits(self):
		"""Requested amount / tenure inside the product and scheme limits; LTV inside the RBI cap and the scheme's."""
		amount, tenure = flt(self.requested_loan_amount), cint(self.requested_tenure_months)
		for doctype, name in (("Loan Product", self.loan_product), ("Loan Scheme", self.loan_scheme)):
			if not name:
				continue
			lim = frappe.db.get_value(doctype, name, ["minimum_loan_amount", "maximum_loan_amount",
				"minimum_tenure_months", "maximum_tenure_months"], as_dict=True)
			if flt(lim.minimum_loan_amount) and amount < flt(lim.minimum_loan_amount):
				frappe.throw(_("{0} {1} lends at least {2}.").format(doctype, name, frappe.format(lim.minimum_loan_amount, "Currency")))
			if flt(lim.maximum_loan_amount) and amount > flt(lim.maximum_loan_amount):
				frappe.throw(_("{0} {1} lends at most {2}.").format(doctype, name, frappe.format(lim.maximum_loan_amount, "Currency")))
			if cint(lim.minimum_tenure_months) and tenure < cint(lim.minimum_tenure_months):
				frappe.throw(_("{0} {1} needs a tenure of at least {2} months.").format(doctype, name, lim.minimum_tenure_months))
			if cint(lim.maximum_tenure_months) and tenure > cint(lim.maximum_tenure_months):
				frappe.throw(_("{0} {1} allows at most {2} months.").format(doctype, name, lim.maximum_tenure_months))

		if not flt(self.property_value) or self.loan_type not in RBI_LTV_LOAN_TYPES:
			return
		for which, value in (("requested", amount), ("sanctioned", flt(self.sanctioned_amount))):
			if not value:
				continue
			cap = rbi_ltv_cap(value)
			scheme_cap = flt(frappe.db.get_value("Loan Scheme", self.loan_scheme, "maximum_ltv")) if self.loan_scheme else 0
			if scheme_cap:
				cap = min(cap, scheme_cap)
			ltv = value / flt(self.property_value) * 100
			if ltv > cap:
				frappe.throw(_("The {0} amount is {1}% of the property value; the limit is {2}% (RBI cap for this loan size{3}).").format(
					which, round(ltv, 1), cap, _(" and the scheme's limit") if scheme_cap else ""))

	def warn_old_cibil(self):
		if self.has_value_changed("final_status") and self.final_status == "Submitted":
			report_date = frappe.db.get_value("Loan Customer", self.loan_customer, "cibil_report_date")
			if not report_date or date_diff(nowdate(), report_date) > CIBIL_VALID_DAYS:
				frappe.msgprint(_("The customer's CIBIL report is missing or older than {0} days.").format(CIBIL_VALID_DAYS),
					indicator="orange", alert=True)

	def on_update(self):
		from dsa_loan.dsa_loan_portal.document_data import make_checklists

		# a customer without a branch inherits it so branch users can see them
		for applicant in [self.loan_customer] + [r.applicant for r in self.co_applicants]:
			if not frappe.db.get_value("Loan Customer", applicant, "dsa_branch"):
				frappe.db.set_value("Loan Customer", applicant, "dsa_branch", self.dsa_branch)
		created = make_checklists(self)
		if created:
			frappe.msgprint(_("{0} document checklist(s) created, one per applicant.").format(created), alert=True)

		from dsa_loan.dsa_loan_portal.invoicing import on_application_update

		on_application_update(self)
		if self.final_status == "Closed" and self.has_value_changed("final_status"):
			from dsa_loan.dsa_loan_portal.automation import on_application_closed

			on_application_closed(self)


def set_final_status(application, new_status):
	"""Move the Application Status (final_status) forward only, never back."""
	doc = frappe.get_doc("Loan Application", application)
	if doc.final_status in FORWARD and new_status in FORWARD and FORWARD.index(new_status) <= FORWARD.index(doc.final_status):
		return
	doc.final_status = new_status
	doc.db_update()
	if new_status == "Disbursed":
		from dsa_loan.dsa_loan_portal.invoicing import start_invoicing

		start_invoicing(doc)

