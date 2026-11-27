"""Loan types are now Home Loan, Loan Against Property, Balance Transfer, Plot and Plot + Construction, and the Loan
Purpose depends on the Loan Type. Move existing leads, products and applications onto the new values."""

import frappe

TYPE_MAP = {"Home Purchase": "Home Loan", "Home Improvement": "Home Loan", "Plot Purchase": "Plot"}
PURPOSE_MAP = {"Purchase": "Purchase - Ready Property", "Construction": "Self Construction",
               "Renovation": "Extension / Renovation", "Top-up": "Balance Transfer + Top-up",
               "Plot + Construction": "Plot Purchase + Construction"}


def execute():
	from dsa_loan.dsa_loan_portal.doctype.loan_application.loan_application import LOAN_PURPOSES

	for doctype, field in (("Loan Lead", "loan_type"), ("Loan Product", "loan_category"), ("Loan Application", "loan_type")):
		for old, new in TYPE_MAP.items():
			frappe.db.sql(f"update `tab{doctype}` set `{field}` = %s where `{field}` = %s", (new, old))
	for app in frappe.get_all("Loan Application", ["name", "loan_type", "loan_purpose"]):
		allowed = LOAN_PURPOSES.get(app.loan_type) or []
		if allowed and app.loan_purpose not in allowed:
			new = PURPOSE_MAP.get(app.loan_purpose)
			frappe.db.set_value("Loan Application", app.name, "loan_purpose", new if new in allowed else allowed[0],
			                    update_modified=False)
