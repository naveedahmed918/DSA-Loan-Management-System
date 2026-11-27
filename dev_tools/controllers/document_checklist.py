# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.document_data import check_checklist


class DocumentChecklist(Document):
	def validate(self):
		owner, self.dsa_branch = frappe.db.get_value("Loan Application", self.loan_application, ["loan_customer", "dsa_branch"])
		co = frappe.get_all("Co-Applicant", {"parent": self.loan_application, "parenttype": "Loan Application"}, pluck="applicant")
		if self.applicant not in [owner] + co:
			frappe.throw(_("{0} is not an applicant on {1}.").format(self.applicant, self.loan_application))
		if self.is_new() and frappe.db.exists(
			"Document Checklist", {"loan_application": self.loan_application, "applicant": self.applicant}
		):
			frappe.throw(_("{0} already has a document checklist for {1}.").format(self.applicant, self.loan_application))
		if not self.is_new():
			check_checklist(self)
