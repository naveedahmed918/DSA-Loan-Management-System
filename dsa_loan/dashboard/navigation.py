import frappe

GROUPS = [
    ("Customers", ["Loan Customer"]),
    ("Loan Management", ["Customer Loan Application", "Lender Application", "Lender Disbursement"]),
    ("Lender Management", ["Lender", "Lender Type", "Lender Status", "Lender Loan Product", "Lender Branch", "Lender Agreement", "Lender Commission Slab"]),
    ("Commissions & Settlements", ["Lender Commission Record", "Lender Receivable", "Lender Payable", "Lender Payment", "Lender Adjustment"]),
    ("Accounts", ["Sales Invoice", "Payment Entry", "Purchase Invoice", "Journal Entry"]),
]

def sidebar():
    result = []
    for label, doctypes in GROUPS:
        items = []
        for dt in doctypes:
            if frappe.db.exists("DocType", dt) and frappe.has_permission(dt, "read"):
                items.append({"label": dt, "route": ["List", dt]})
        if items:
            result.append({"label": label, "items": items})
    return result
