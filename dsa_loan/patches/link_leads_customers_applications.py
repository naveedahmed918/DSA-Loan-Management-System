"""Lead -> Customer -> Application: fill the new loan_lead links on existing records.
A customer gets the latest Converted lead with the same mobile number; an application gets its customer's lead."""

import frappe


def execute():
	for cust in frappe.get_all("Loan Customer", {"loan_lead": ("is", "not set")}, ["name", "mobile_number"]):
		lead = frappe.db.get_value("Loan Lead", {"mobile_number": cust.mobile_number, "lead_status": "Converted"},
		                           order_by="creation desc")
		if lead:
			frappe.db.set_value("Loan Customer", cust.name, "loan_lead", lead, update_modified=False)
	frappe.db.sql("""update `tabLoan Application` a join `tabLoan Customer` c on c.name = a.loan_customer
		set a.loan_lead = c.loan_lead where ifnull(a.loan_lead, '') = '' and ifnull(c.loan_lead, '') != ''""")
