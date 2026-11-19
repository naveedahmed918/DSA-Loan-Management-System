import frappe
from frappe import _
from frappe.utils import getdate
from . import filters as date_filters
from . import admin
from .navigation import sidebar

def _guard():
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in"), frappe.PermissionError)
    if "System Manager" not in frappe.get_roles():
        frappe.throw(_("You are not permitted to access the DSA Admin Dashboard."), frappe.PermissionError)

@frappe.whitelist()
def get_context():
    _guard()
    companies = frappe.get_list("Company", fields=["name", "default_currency"], order_by="name")
    default_company = "DSA Loan Services" if any(c.name == "DSA Loan Services" for c in companies) else (companies[0].name if companies else None)
    user = frappe.get_doc("User", frappe.session.user)
    return {
        "full_name": user.full_name or frappe.session.user,
        "user": frappe.session.user,
        "currency": frappe.db.get_default("currency") or "INR",
        "companies": companies,
        "default_company": default_company,
        "sidebar": sidebar(),
        "presets": ["today", "this_week", "this_month", "last_month", "this_quarter", "this_year", "custom"],
    }

@frappe.whitelist()
def get_overview(preset="this_month", from_date=None, to_date=None, company=None):
    _guard()
    start, end = date_filters.resolve(preset, from_date, to_date)
    allowed_companies = set(frappe.get_list("Company", pluck="name"))
    if company and company not in allowed_companies:
        frappe.throw(_("Invalid company selection"), frappe.PermissionError)
    return admin.overview(start, end, company)
