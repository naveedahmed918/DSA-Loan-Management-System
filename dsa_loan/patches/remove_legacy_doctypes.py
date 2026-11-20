"""Remove DocTypes and pages replaced by the consolidated field spec (Nov 2026).

Renamed DocTypes (e.g. Customer Loan Application -> Loan Application) leave their old DocType
record and table behind, because `bench migrate` never deletes DocTypes. This patch deletes each
legacy DocType only when its table is empty, so no site loses data. Non-empty ones are skipped
and reported in the Error Log so they can be migrated by hand.
"""

import frappe

LEGACY_DOCTYPES = [
	# children / dependents first
	"Lender Application Document",
	"Lender Application Status Log",
	"Lender Document Checklist Item",
	"Lender Query",
	"Loan Sanction Condition",
	"Lender Commission Tier",
	"Lender Commission Record",
	"Lender Disbursement",
	"Lender Application",
	"Loan Co-applicant",
	"Customer Loan Application",
	"Lender Commission Slab",
	"Lender Scheme Rate Card",
	"Lender Loan Product",
	"Lender Agreement",
	"Franchise Commission Share",
	"Franchise Sub-DSA Partner",
]

LEGACY_PAGES = ["dsa-admin-dashboard", "dsa-admin-dashboard-v2"]


def execute():
	skipped = []
	for doctype in LEGACY_DOCTYPES:
		if not frappe.db.exists("DocType", doctype):
			continue
		if frappe.db.table_exists(doctype) and frappe.db.count(doctype):
			skipped.append(doctype)
			continue
		frappe.delete_doc("DocType", doctype, force=True, ignore_permissions=True, ignore_missing=True)

	for page in LEGACY_PAGES:
		frappe.delete_doc("Page", page, force=True, ignore_permissions=True, ignore_missing=True)

	if skipped:
		frappe.log_error(
			title="dsa_loan: legacy DocTypes kept because they contain data",
			message="Migrate these records to the new DocTypes, then delete them:\n" + "\n".join(skipped),
		)
