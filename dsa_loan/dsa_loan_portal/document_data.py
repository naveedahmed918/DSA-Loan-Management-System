"""Document checklists.

Each applicant gets one Document Checklist per Loan Application. Its rows are the documents to collect: each row
has the document name, the attached file and a status, and is checked and marked Verified by hand.
"""

import frappe
from frappe import _

# The separate extracted-data DocTypes (Aadhaar / PAN / ... Data) were removed; kept empty for old patches.
EXTRACTED_DOCTYPES = ()

# (document name, needed for salaried applicants only), in checklist order: 13 rows for a salaried applicant.
STANDARD_DOCUMENTS = [
	("Aadhaar Card", False),
	("PAN Card", False),
	("Address Proof", False),
	("Bank Statement – Last 6 Months", False),
	("Salary Slip – Month 1", True),
	("Salary Slip – Month 2", True),
	("Salary Slip – Month 3", True),
	("ITR – Year 1", False),
	("ITR – Year 2", False),
	("ITR – Year 3", False),
	("Form 16 – Year 1", True),
	("Form 16 – Year 2", True),
	("Form 16 – Year 3", True),
]


def standard_rows(employment_type):
	"""Checklist rows for one applicant. Salary slips and Form 16 apply to salaried applicants only."""
	salaried = employment_type in (None, "", "Salaried")
	return [
		{"document_name": name, "document_status": "Pending" if salaried or not salaried_only else "Not Applicable"}
		for name, salaried_only in STANDARD_DOCUMENTS
	]


def check_checklist(doc):
	"""Checks across a Document Checklist's rows."""
	for row in doc.documents:
		if row.document_status == "Verified" and not row.document_file:
			frappe.throw(_("Row {0}: attach the {1} before marking it Verified.").format(row.idx, row.document_name))


def make_checklists(app):
	"""One Document Checklist per applicant (loan customer + co-applicants) with the standard rows.
	Returns how many were created."""
	applicants = [app.loan_customer] + [r.applicant for r in app.co_applicants]
	created = 0
	for applicant in applicants:
		if frappe.db.exists("Document Checklist", {"loan_application": app.name, "applicant": applicant}):
			continue
		employment = frappe.db.get_value("Loan Customer", applicant, "employment_type")
		frappe.get_doc(
			{"doctype": "Document Checklist", "loan_application": app.name, "applicant": applicant,
			 "documents": standard_rows(employment)}
		).insert(ignore_permissions=True)
		created += 1
	return created
