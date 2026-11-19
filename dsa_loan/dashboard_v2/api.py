"""Whitelisted methods for the Admin dashboard. All are read-only and need a logged-in user. What
each returns is limited by that user's permissions (see core.py). The page needs two calls:
get_context once, then get_overview on every filter change."""

import re

import frappe
from frappe import _
from frappe.utils import cint, now_datetime, strip_html

from dsa_loan.dashboard_v2 import admin as M
from dsa_loan.dashboard_v2 import core as C
from dsa_loan.dashboard_v2 import filters as F
from dsa_loan.dashboard_v2 import navigation
from dsa_loan.dashboard_v2 import schema as S


def _login():
	if frappe.session.user == "Guest":
		frappe.throw(_("Please log in"), frappe.PermissionError)


def _companies():
	if not C.can("Company"):
		return []
	return C.rows("Company", [], ["name", "default_currency"], "name asc", 50) or []


def _company(requested, companies=None):
	"""Validated company: must be one the user may read. Falls back to DSA Loan Services, then the user default."""
	companies = companies if companies is not None else _companies()
	names = [c["name"] for c in companies]
	if requested:
		if requested not in names:
			frappe.throw(_("Unknown or inaccessible company"), frappe.PermissionError)
		return requested
	for cand in (S.DEFAULT_COMPANY, frappe.defaults.get_user_default("Company")):
		if cand in names:
			return cand
	return names[0] if names else None


def _currency(company, companies):
	for c in companies:
		if c["name"] == company:
			return c.get("default_currency") or "INR"
	return "INR"


@frappe.whitelist()
def get_context():
	"""Everything the shell needs once: user, companies, sidebar, quick actions, presets."""
	_login()
	user = frappe.session.user
	full_name = frappe.utils.get_fullname(user)
	companies = _companies()
	company = _company(None, companies)
	return {
		"user": user,
		"full_name": full_name,
		"first_name": (frappe.db.get_value("User", user, "first_name") or full_name or "").split(" ")[0],
		"image": frappe.db.get_value("User", user, "user_image"),
		"companies": [c["name"] for c in companies],
		"company": company,
		"currency": _currency(company, companies),
		"is_system_manager": "System Manager" in frappe.get_roles(),
		"presets": [{"value": k, "label": v} for k, v in F.PRESETS.items()],
		"default_preset": F.DEFAULT_PRESET,
		"sidebar": navigation.sidebar(),
		"quick_actions": navigation.quick_actions(),
		"page": S.PAGE,
	}


def _section(fn, *args):
	"""One failing section must not blank the whole dashboard."""
	try:
		return fn(*args)
	except frappe.PermissionError:
		return None
	except Exception:
		frappe.logger("dsa_dashboard").exception(f"section {getattr(fn, '__name__', fn)} failed")
		return None


@frappe.whitelist()
def get_overview(preset=None, from_date=None, to_date=None, company=None):
	"""Every dashboard section in one call, so a filter change is a single round trip."""
	_login()
	start, end = F.resolve(preset, from_date, to_date)
	companies = _companies()
	co = _company(company, companies)
	fin = _section(M.finance_overview, start, end, co)
	return {
		"from_date": str(start),
		"to_date": str(end),
		"company": co,
		"currency": _currency(co, companies),
		"generated_at": str(now_datetime()),
		"data": {
			"kpis": _section(M.kpis, start, end, co, fin),
			"customers": _section(M.customers, start, end),
			"trends": _section(M.application_trends, start, end),
			"status": _section(M.application_status, start, end),
			"loan_types": _section(M.loan_types, start, end),
			"amounts": _section(M.amounts, start, end),
			"lenders": _section(M.lender_performance, start, end),
			"disbursements": _section(M.disbursement_analytics, start, end),
			"commission": _section(M.commission_analytics, start, end),
			"finance": fin,
			"pipeline": _section(M.pipeline, start, end),
			"activities": _section(M.recent_activities, co),
			"tasks": _section(M.pending_tasks, co) or [],
		},
	}


# Individual endpoints (same logic, one section each) for reuse by other dashboards or tests.
@frappe.whitelist()
def get_dashboard_kpis(preset=None, from_date=None, to_date=None, company=None):
	_login()
	s, e = F.resolve(preset, from_date, to_date)
	return M.kpis(s, e, _company(company))


@frappe.whitelist()
def get_loan_application_trends(preset=None, from_date=None, to_date=None):
	_login()
	s, e = F.resolve(preset, from_date, to_date)
	return M.application_trends(s, e)


@frappe.whitelist()
def get_application_status_distribution(preset=None, from_date=None, to_date=None):
	_login()
	s, e = F.resolve(preset, from_date, to_date)
	return M.application_status(s, e)


@frappe.whitelist()
def get_lender_performance(preset=None, from_date=None, to_date=None):
	_login()
	s, e = F.resolve(preset, from_date, to_date)
	return M.lender_performance(s, e)


@frappe.whitelist()
def get_disbursement_analytics(preset=None, from_date=None, to_date=None):
	_login()
	s, e = F.resolve(preset, from_date, to_date)
	return M.disbursement_analytics(s, e)


@frappe.whitelist()
def get_commission_analytics(preset=None, from_date=None, to_date=None):
	_login()
	s, e = F.resolve(preset, from_date, to_date)
	return M.commission_analytics(s, e)


@frappe.whitelist()
def get_financial_overview(preset=None, from_date=None, to_date=None, company=None):
	_login()
	s, e = F.resolve(preset, from_date, to_date)
	return M.finance_overview(s, e, _company(company))


@frappe.whitelist()
def get_recent_activities(company=None):
	_login()
	return M.recent_activities(_company(company))


@frappe.whitelist()
def get_pending_tasks(company=None):
	_login()
	return M.pending_tasks(_company(company))


# ------------------------------------------------------------------ search

# doctype, title field (None = use the record name), subtitle field
SEARCH = [
	(S.CUSTOMER, "customer_name", "city"),
	(S.LOAN_APP, None, "application_status"),
	(S.LENDER_APP, None, "application_status"),
	(S.DISB, None, "lender"),
	(S.LENDER, "lender_name", "lender_type"),
	(S.PRODUCT, "product_name", "loan_type"),
	(S.COMM, None, "commission_status"),
	("Lender Branch", "branch_name", "city"),
	(S.SALES_INVOICE, "customer_name", "status"),
]


@frappe.whitelist()
def search(txt=None):
	"""Records the user may read whose ID or name matches txt, a few per type.
	Never searches or returns PAN, Aadhaar, mobile numbers or attachments."""
	_login()
	txt = re.sub(r"[%_\\]", "", strip_html(txt or "")).strip()[:60]
	if len(txt) < 2:
		return []
	out = []
	for doctype, title, sub in SEARCH:
		if not C.usable(doctype, title, sub):
			continue
		fields = ["name"] + ([f"{title} as title"] if title else []) + ([f"{sub} as sub"] if sub else [])
		like = [["name", "like", f"%{txt}%"]] + ([[title, "like", f"%{txt}%"]] if title else [])
		try:
			rows = frappe.get_list(doctype, fields=fields, or_filters=like, order_by="modified desc", limit_page_length=4)
		except Exception:
			frappe.logger("dsa_dashboard").exception("search failed for " + doctype)
			continue
		for r in rows:
			out.append({"doctype": doctype, "name": r.get("name"), "title": r.get("title") or r.get("name"), "sub": r.get("sub")})
	return out[:24]


# ------------------------------------------------------------------ notifications

@frappe.whitelist()
def get_notifications():
	"""The signed-in user's own Notification Log entries (read-only; nothing is marked as read)."""
	_login()
	user = frappe.session.user
	if not C.exists("Notification Log"):
		return {"unread": 0, "items": []}
	rows = frappe.get_all(
		"Notification Log", filters={"for_user": user}, fields=["name", "subject", "document_type", "document_name", "read", "creation"],
		order_by="creation desc", limit=8,
	)
	for r in rows:
		r["subject"] = strip_html(r.get("subject") or "")[:140]
	return {"unread": cint(frappe.db.count("Notification Log", {"for_user": user, "read": 0})), "items": rows}
