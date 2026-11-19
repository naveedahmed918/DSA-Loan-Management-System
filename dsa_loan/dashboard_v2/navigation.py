"""Sidebar groups and quick actions. Built on the server so only targets that exist and that the
current user may open are sent to the browser. (Hiding a link is a convenience; the APIs and the
Frappe forms enforce permissions on their own.)

Only DocTypes, Reports and Pages that exist in this site are listed. Nothing is shown for modules
that have not been built (franchise, leads, KYC, customer documents).
"""

import frappe

from dsa_loan.dashboard_v2 import schema as S

# item: (label, kind, target, extra)
#   doctype -> list view of target; extra = list filters (dict) or "my_todos"
#   report  -> query / script report
#   page    -> desk page
#   anchor  -> a section of this dashboard (target = section id)
GROUPS = [
	("overview", "Overview", "grid", [
		("Business overview", "anchor", "top", None),
		("Loan pipeline", "anchor", "pipeline", None),
		("Lender performance", "anchor", "lenders", None),
		("Disbursements & commission", "anchor", "money", None),
		("Financial overview", "anchor", "finance", None),
		("Recent activity", "anchor", "activity", None),
		("My tasks", "doctype", "ToDo", "my_todos"),
	]),
	("customers", "Customers", "users", [
		("DSA Customers", "doctype", S.CUSTOMER, None),
		("Contacts", "doctype", "Contact", None),
	]),
	("loans", "Loan management", "file", [
		("Loan Applications", "doctype", S.LOAN_APP, None),
		("Draft", "doctype", S.LOAN_APP, {"application_status": "Draft"}),
		("Under review", "doctype", S.LOAN_APP, {"application_status": ["in", ["Submitted", "Under Review"]]}),
		("Approved", "doctype", S.LOAN_APP, {"application_status": ["in", S.LOAN_APPROVED]}),
		("Rejected", "doctype", S.LOAN_APP, {"application_status": "Rejected"}),
		("Lender Applications", "doctype", S.LENDER_APP, None),
	]),
	("lenders", "Lender management", "bank", [
		("Lenders", "doctype", S.LENDER, None),
		("Lender Types", "doctype", S.LENDER_TYPE, None),
		("Lender Statuses", "doctype", "Lender Status", None),
		("Loan Products", "doctype", S.PRODUCT, None),
		("Lender Branches", "doctype", "Lender Branch", None),
		("Lender Agreements", "doctype", S.AGREEMENT, None),
		("Commission Slabs", "doctype", "Lender Commission Slab", None),
	]),
	("disbursement", "Disbursements", "send", [
		("All disbursements", "doctype", S.DISB, None),
		("Pending", "doctype", S.DISB, {"disbursement_status": "Pending"}),
		("Processed", "doctype", S.DISB, {"disbursement_status": S.DISB_DONE}),
		("Failed", "doctype", S.DISB, {"disbursement_status": "Failed"}),
	]),
	("commission", "Commission", "percent", [
		("Commission Records", "doctype", S.COMM, None),
		("Pending commission", "doctype", S.COMM, {"commission_status": "Pending"}),
		("Lender Receivables", "doctype", "Lender Receivable", None),
		("Lender Payables", "doctype", "Lender Payable", None),
		("Lender Payments", "doctype", "Lender Payment", None),
		("Lender Adjustments", "doctype", "Lender Adjustment", None),
	]),
	("accounts", "Accounts & finance", "wallet", [
		("Sales Invoices", "doctype", S.SALES_INVOICE, None),
		("Payment Entries", "doctype", S.PAYMENT_ENTRY, None),
		("Journal Entries", "doctype", "Journal Entry", None),
		("Purchase Invoices", "doctype", S.PURCHASE_INVOICE, None),
		("Customers (billing)", "doctype", "Customer", None),
		("Suppliers", "doctype", "Supplier", None),
		("Accounts Receivable", "report", "Accounts Receivable", None),
		("Accounts Payable", "report", "Accounts Payable", None),
		("General Ledger", "report", "General Ledger", None),
	]),
	("communication", "Communication", "mail", [
		("Email Queue", "doctype", "Email Queue", None),
		("Email Templates", "doctype", "Email Template", None),
		("Notification Log", "doctype", "Notification Log", None),
	]),
	("reports", "Reports", "chart", [
		("Accounts Receivable", "report", "Accounts Receivable", None),
		("Profit and Loss", "report", "Profit and Loss Statement", None),
		("Balance Sheet", "report", "Balance Sheet", None),
		("Trial Balance", "report", "Trial Balance", None),
	]),
	("settings", "Settings", "settings", [
		("Companies", "doctype", "Company", None),
		("Users", "doctype", "User", None),
		("Role Permissions", "page", "permission-manager", None),
		("Workflows", "doctype", "Workflow", None),
		("System Settings", "doctype", "System Settings", None),
	]),
]

QUICK_ACTIONS = [
	("New customer", S.CUSTOMER, "user-plus"),
	("New loan application", S.LOAN_APP, "file-plus"),
	("New lender application", S.LENDER_APP, "send"),
	("New disbursement", S.DISB, "wallet"),
	("Add lender", S.LENDER, "bank"),
	("Add loan product", S.PRODUCT, "box"),
	("New sales invoice", S.SALES_INVOICE, "receipt"),
	("New payment entry", S.PAYMENT_ENTRY, "rupee"),
]


def _role_gate(doctype, names, my_roles):
	"""Same rule Frappe uses for Report/Page access, for many records in two queries:
	allowed when the record lists no roles or shares a role with the user."""
	names = list(set(names))
	if not names:
		return {}
	existing = set(frappe.get_all(doctype, filters={"name": ["in", names]}, pluck="name"))
	if "Administrator" == frappe.session.user:
		return {n: n in existing for n in names}
	roles = {}
	if existing:
		for r in frappe.get_all("Has Role", filters={"parenttype": doctype, "parent": ["in", list(existing)]}, fields=["parent", "role"]):
			roles.setdefault(r.parent, set()).add(r.role)
	return {n: n in existing and (not roles.get(n) or bool(roles[n] & my_roles)) for n in names}


def _build_gates():
	my_roles = set(frappe.get_roles())
	reports = [t for _k, _l, _i, items in GROUPS for _lab, kind, t, _x in items if kind == "report"]
	pages = [t for _k, _l, _i, items in GROUPS for _lab, kind, t, _x in items if kind == "page"]
	return {"Report": _role_gate("Report", reports, my_roles), "Page": _role_gate("Page", pages, my_roles)}


def _item(label, kind, target, extra, gates, doc_ok):
	if kind == "anchor":
		return {"label": label, "anchor": target}
	if kind == "doctype":
		if not doc_ok(target):
			return None
		filters = extra
		if extra == "my_todos":
			filters = {"allocated_to": frappe.session.user, "status": "Open"}
		single = frappe.get_meta(target).issingle
		return {"label": label, "route": ["Form", target, target] if single else ["List", target], "filters": filters or None}
	if kind == "report":
		if not gates["Report"].get(target):
			return None
		ref = frappe.get_cached_value("Report", target, "ref_doctype")
		if ref and not frappe.has_permission(ref, "read"):
			return None
		return {"label": label, "route": ["query-report", target]}
	if kind == "page":
		if not gates["Page"].get(target):
			return None
		return {"label": label, "route": [target]}
	return None


def sidebar():
	gates = _build_gates()  # request-local on purpose: never share permission results between users
	seen = {}

	def doc_ok(dt):
		if dt not in seen:
			seen[dt] = bool(frappe.db.exists("DocType", dt)) and bool(frappe.has_permission(dt, "read"))
		return seen[dt]

	out = []
	for key, label, icon, items in GROUPS:
		built = [i for i in (_item(*it, gates, doc_ok) for it in items) if i]
		if built:
			out.append({"key": key, "label": label, "icon": icon, "items": built})
	return out


def quick_actions():
	out = []
	for label, doctype, icon in QUICK_ACTIONS:
		if frappe.db.exists("DocType", doctype) and frappe.has_permission(doctype, "create"):
			out.append({"label": label, "doctype": doctype, "icon": icon})
	if frappe.db.exists("DocType", S.COMM) and frappe.has_permission(S.COMM, "read"):
		out.append({"label": "View commission", "route": ["List", S.COMM], "icon": "percent"})
	return out
