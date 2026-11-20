"""Remove what the consolidated field spec (Nov 2026) replaced: legacy DocTypes, their tables,
old columns left in reused tables, and the old dashboard pages.

`bench migrate` deletes orphan DocType records but keeps their tables, and never drops columns of
fields that were removed. This patch cleans both up, but only where nothing is lost: a table or
column that still holds data is kept and listed in the Error Log for manual migration.
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

# DocTypes whose names were kept but whose fields changed, so old columns may remain.
REUSED_DOCTYPES = ["Lender", "Lender Branch", "DSA Branch", "Lender Document Rule", "Loan Customer", "Franchise Settlement"]

LEGACY_PAGES = ["dsa-admin-dashboard", "dsa-admin-dashboard-v2"]

STANDARD_COLUMNS = {
	"name", "creation", "modified", "modified_by", "owner", "docstatus", "idx", "parent", "parentfield",
	"parenttype", "_user_tags", "_comments", "_assign", "_liked_by", "_seen", "amended_from",
}


def execute():
	kept = remove_legacy_doctypes() + trim_old_columns()
	for page in LEGACY_PAGES:
		frappe.delete_doc("Page", page, force=True, ignore_permissions=True, ignore_missing=True)
	if kept:
		frappe.log_error(
			title="dsa_loan: legacy data kept",
			message="These still hold data. Move it to the new DocTypes/fields, then remove them:\n" + "\n".join(kept),
		)


def remove_legacy_doctypes():
	kept = []
	for doctype in LEGACY_DOCTYPES:
		has_table = frappe.db.table_exists(doctype)
		if has_table and frappe.db.count(doctype):
			kept.append(f"table tab{doctype}")
			continue
		if frappe.db.exists("DocType", doctype):
			frappe.delete_doc("DocType", doctype, force=True, ignore_permissions=True, ignore_missing=True)
		if frappe.db.table_exists(doctype):
			frappe.db.sql_ddl(f"DROP TABLE `tab{doctype}`")
	return kept


def trim_old_columns():
	"""Drop columns of the reused DocTypes that no current field uses and that hold no values."""
	kept = []
	for doctype in REUSED_DOCTYPES:
		if not frappe.db.table_exists(doctype):
			continue
		frappe.clear_cache(doctype=doctype)
		meta = frappe.get_meta(doctype)
		current = {df.fieldname for df in meta.fields} | STANDARD_COLUMNS
		for column in frappe.db.get_table_columns(doctype):
			if column in current:
				continue
			if column_has_values(doctype, column):
				kept.append(f"column tab{doctype}.{column}")
				continue
			frappe.db.sql_ddl(f"ALTER TABLE `tab{doctype}` DROP COLUMN `{column}`")
	return kept


def column_has_values(doctype, column):
	"""True when any row has something other than NULL, an empty string or zero."""
	return bool(
		frappe.db.sql(
			f"""SELECT 1 FROM `tab{doctype}`
			WHERE `{column}` IS NOT NULL
				AND CAST(`{column}` AS CHAR) <> ''
				AND CAST(`{column}` AS CHAR) NOT REGEXP '^-?0+([.]0+)?$'
			LIMIT 1"""
		)
	)
