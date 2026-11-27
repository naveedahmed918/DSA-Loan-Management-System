"""Nov 2026 field changes: drop Lender Login / Lender Document Rule, move Loan Application.primary_customer to
loan_customer, fill business_channel and the co-applicant name on existing records."""

import frappe


def execute():
	for dt in ("Lender Login", "Lender Document Rule"):
		if frappe.db.exists("DocType", dt):
			frappe.delete_doc("DocType", dt, force=True, ignore_permissions=True)
		frappe.db.sql_ddl(f"drop table if exists `tab{dt}`")
		frappe.db.delete("DocType Link", {"link_doctype": dt})

	columns = frappe.db.get_table_columns("Loan Application")
	if "primary_customer" in columns:
		frappe.db.sql("""update `tabLoan Application` set loan_customer = primary_customer
			where ifnull(loan_customer, '') = '' and ifnull(primary_customer, '') != ''""")
	frappe.db.sql("""update `tabLoan Application` a join `tabLoan Customer` c on c.name = a.loan_customer
		set a.customer_name = c.customer_name where ifnull(a.customer_name, '') = ''""")
	# existing franchise loans are assumed franchise-owned; change any that are franchise-operated by hand
	frappe.db.sql("""update `tabLoan Application` set business_channel = if(ifnull(franchise, '') = '', 'DSA Owned', 'Franchise Owned')
		where ifnull(business_channel, '') = ''""")
	frappe.db.sql("""update `tabCo-Applicant` r join `tabLoan Customer` c on c.name = r.applicant
		set r.applicant_name = c.customer_name where ifnull(r.applicant_name, '') = ''""")
