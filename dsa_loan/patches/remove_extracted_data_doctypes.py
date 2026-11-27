"""The 7 extracted-data DocTypes (Aadhaar / PAN / Address Proof / Bank Statement / Salary Slip / ITR / Form 16 Data)
are removed; checklist rows keep only the document name, file and status."""

import frappe

REMOVED = ("Aadhaar Card Data", "PAN Card Data", "Address Proof Data", "Bank Statement Data",
           "Salary Slip Data", "ITR Data", "Form 16 Data")


def execute():
	for dt in REMOVED:
		if frappe.db.exists("DocType", dt):
			frappe.delete_doc("DocType", dt, force=True, ignore_permissions=True)
		frappe.db.sql_ddl(f"drop table if exists `tab{dt}`")
		frappe.db.delete("DocType Link", {"link_doctype": dt})
		frappe.db.delete("User Permission", {"allow": dt})
