"""Read-only APIs for the internal DSA lender operations dashboard."""

from datetime import date, timedelta

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, nowdate, strip_html_tags

PAGE = "dsa-admin-dashboard-v2"
DEFAULT_PRESET = "this_month"
MAX_ROWS = 5000
PRESETS = [
    {"value": "today", "label": "Today"},
    {"value": "this_week", "label": "This Week"},
    {"value": "this_month", "label": "This Month"},
    {"value": "last_month", "label": "Last Month"},
    {"value": "this_quarter", "label": "This Quarter"},
    {"value": "this_year", "label": "This Year"},
    {"value": "custom", "label": "Custom Range"},
]


def _guard():
    """Keep APIs aligned with the existing System Manager-only dashboard page."""
    frappe.only_for("System Manager")


def _has_doctype(doctype):
    return bool(frappe.db.exists("DocType", doctype))


def _fields(doctype):
    return {df.fieldname for df in frappe.get_meta(doctype).fields} | {
        "name", "creation", "modified", "owner", "modified_by", "docstatus"
    }


def _read(doctype, fields, filters=None, order_by=None, limit=MAX_ROWS):
    """Read with Frappe list permissions; return [] for absent optional doctypes."""
    if not _has_doctype(doctype) or not frappe.has_permission(doctype, "read"):
        return []
    available = _fields(doctype)
    selected = [field for field in fields if field in available]
    if "name" not in selected:
        selected.insert(0, "name")
    for condition in filters or []:
        if condition[0] not in available:
            return []
    return frappe.get_list(
        doctype,
        fields=selected,
        filters=filters or None,
        order_by=order_by,
        limit_page_length=limit,
    )


def _count(doctype, filters=None):
    if not _has_doctype(doctype) or not frappe.has_permission(doctype, "read"):
        return 0
    available = _fields(doctype)
    if any(row[0] not in available for row in (filters or [])):
        return 0
    return cint(frappe.db.count(doctype, filters=filters or {}))


def _route(doctype, filters=None):
    return {"doctype": doctype, "filters": filters or {}}


def _period(preset, from_date=None, to_date=None):
    today = getdate(nowdate())
    if preset == "custom":
        if not from_date or not to_date:
            frappe.throw(_("Choose both From and To dates."))
        start, end = getdate(from_date), getdate(to_date)
        if start > end:
            frappe.throw(_("From date must be on or before To date."))
        return start, end
    if preset == "today":
        return today, today
    if preset == "this_week":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6)
    if preset == "last_month":
        end = today.replace(day=1) - timedelta(days=1)
        return end.replace(day=1), end
    if preset == "this_quarter":
        month = ((today.month - 1) // 3) * 3 + 1
        start = date(today.year, month, 1)
        next_quarter = (month + 3 - 1) % 12 + 1
        year = today.year + (1 if month > 9 else 0)
        end = date(year, next_quarter, 1) - timedelta(days=1)
        return start, end
    if preset == "this_year":
        return date(today.year, 1, 1), date(today.year, 12, 31)
    if preset == "this_month":
        start = today.replace(day=1)
        if today.month == 12:
            end = date(today.year, 12, 31)
        else:
            end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        return start, end
    frappe.throw(_("Unknown date range."))


def _date_filter(field, start, end):
    return [field, "between", [str(start), str(end)]]


def _lender_filter(lender):
    return [["lender", "=", lender]] if lender else []


def _safe_name(row, field):
    return row.get(field) or ""


@frappe.whitelist()
def get_context():
    _guard()
    user = frappe.get_cached_doc("User", frappe.session.user)
    lender_rows = _read("Lender", ["lender_name", "lender_status"], order_by="lender_name asc", limit=1000)
    lender_options = [{"value": "", "label": "All Lenders"}]
    lender_options.extend(
        {"value": row.name, "label": row.get("lender_name") or row.name}
        for row in lender_rows
    )

    sidebar = [
        {"key": "dashboard", "label": "Dashboard", "icon": "layout-dashboard", "items": [
            {"label": "Overview", "route": ["dsa-admin-dashboard-v2"]},
        ]},
        {"key": "lenders", "label": "Lender Management", "icon": "landmark", "items": [
            {"label": "Lenders", "doctype": "Lender", "route": ["List", "Lender"]},
            {"label": "Loan Products", "doctype": "Lender Loan Product", "route": ["List", "Lender Loan Product"]},
            {"label": "Lender Branches", "doctype": "Lender Branch", "route": ["List", "Lender Branch"]},
            {"label": "Agreements", "doctype": "Lender Agreement", "route": ["List", "Lender Agreement"]},
        ]},
        {"key": "operations", "label": "Operations", "icon": "briefcase-business", "items": [
            {"label": "Applications", "doctype": "Lender Application", "route": ["List", "Lender Application"]},
            {"label": "Documents", "doctype": "Lender Application Document", "route": ["List", "Lender Application Document"]},
            {"label": "Queries", "doctype": "Lender Query", "route": ["List", "Lender Query"]},
            {"label": "Sanction Conditions", "doctype": "Loan Sanction Condition", "route": ["List", "Loan Sanction Condition"]},
            {"label": "Disbursements", "doctype": "Lender Disbursement", "route": ["List", "Lender Disbursement"]},
        ]},
        {"key": "finance", "label": "Finance", "icon": "wallet", "items": [
            {"label": "Commissions", "doctype": "Lender Commission Record", "route": ["List", "Lender Commission Record"]},
        ]},
        {"key": "reports", "label": "Reports & Analytics", "icon": "chart-no-axes-combined", "items": [
            {"label": "Reports", "route": ["List", "Report"]},
        ]},
    ]

    quick_actions = []
    for label, icon_name, doctype in [
        ("New Lender", "plus", "Lender"),
        ("New Application", "file-plus", "Lender Application"),
        ("New Query", "message-circle", "Lender Query"),
        ("New Disbursement", "wallet", "Lender Disbursement"),
        ("New Commission", "percent", "Lender Commission Record"),
    ]:
        if _has_doctype(doctype) and frappe.has_permission(doctype, "create"):
            quick_actions.append({"label": label, "icon": icon_name, "doctype": doctype})

    return {
        "first_name": user.first_name or "",
        "full_name": user.full_name or "",
        "image": user.user_image or "",
        "user": frappe.session.user,
        "page": PAGE,
        "is_system_manager": "System Manager" in frappe.get_roles(),
        "presets": PRESETS,
        "default_preset": DEFAULT_PRESET,
        "lenders": lender_options,
        "default_lender": "",
        "quick_actions": quick_actions,
        "sidebar": sidebar,
        "currency": "INR",
    }


@frappe.whitelist()
def get_overview(preset=None, lender=None, from_date=None, to_date=None):
    _guard()
    start, end = _period(preset or DEFAULT_PRESET, from_date, to_date)
    date_range = [str(start), str(end)]
    selected_lender = lender if lender and frappe.db.exists("Lender", lender) else ""
    lender_filters = _lender_filter(selected_lender)

    lenders = _read("Lender", ["lender_name", "lender_status", "lender_type"], filters=( [["name", "=", selected_lender]] if selected_lender else [] ), order_by="lender_name asc", limit=1000)
    lender_count = len(lenders)
    active_lender_count = sum(1 for row in lenders if row.get("lender_status") == "Active")

    app_filters = lender_filters + [_date_filter("submission_date", start, end)]
    applications = _read("Lender Application", ["name", "lender", "application_status", "submitted_amount", "approved_amount", "submission_date", "sanction_date", "customer_loan_application", "loan_product"], app_filters, "submission_date desc")
    # Query, document and sanction-condition records link through Lender Application,
    # not directly to Lender. Resolve that relationship for the global lender filter.
    related_application_names = []
    if selected_lender:
        related_application_names = [row.name for row in _read(
            "Lender Application", ["name"], [["lender", "=", selected_lender]], limit=MAX_ROWS
        )]
    approved_states = {"Approved", "Sanctioned"}
    approved_count = sum(1 for row in applications if row.get("application_status") in approved_states)
    rejected_count = sum(1 for row in applications if row.get("application_status") == "Rejected")

    disb_filters = lender_filters + [["disbursement_status", "=", "Processed"], _date_filter("disbursement_date", start, end)]
    disbursements = _read("Lender Disbursement", ["name", "lender", "lender_application", "disbursement_amount", "disbursement_date", "disbursement_status"], disb_filters, "disbursement_date desc")
    disbursed_amount = flt(sum(flt(row.get("disbursement_amount")) for row in disbursements), 2)

    commission_filters = lender_filters + [["commission_status", "=", "Pending"], _date_filter("commission_date", start, end)]
    pending_commissions = _read("Lender Commission Record", ["name", "lender", "commission_amount", "commission_status", "commission_date"], commission_filters, "commission_date desc")
    pending_commission_amount = flt(sum(flt(row.get("commission_amount")) for row in pending_commissions), 2)

    query_filters = [["query_status", "in", ["Open", "In Progress", "Responded"]], ["raised_on", "between", [str(start) + " 00:00:00", str(end) + " 23:59:59"]]]
    if selected_lender:
        query_filters.append(["lender_application", "in", related_application_names or ["__no_matching_application__"]])
    queries = _read("Lender Query", ["name", "lender_application", "query_subject", "query_status", "due_date", "raised_on"], query_filters, "raised_on desc")

    pipeline_statuses = ["Draft", "Submitted", "Under Review", "Documents Required", "Approved", "Sanctioned", "Rejected", "Disbursed", "Withdrawn"]
    pipeline = []
    for status in pipeline_statuses:
        count = sum(1 for row in applications if row.get("application_status") == status)
        pipeline.append({
            "label": status,
            "count": count,
            "route": _route("Lender Application", {"application_status": status, **({"lender": selected_lender} if selected_lender else {}), "submission_date": ["between", date_range]}),
        })

    tasks = []
    document_filters = [["verification_status", "=", "Pending"]]
    if selected_lender:
        document_filters.append(["lender_application", "in", related_application_names or ["__no_matching_application__"]])
    pending_docs = _read("Lender Application Document", ["name", "lender_application", "verification_status"], document_filters, limit=1000)
    if pending_docs:
        tasks.append({"label": "Documents awaiting verification", "priority": "Medium", "count": len(pending_docs), "route": _route("Lender Application Document", {"verification_status": "Pending"})})
    overdue_queries = [row for row in queries if row.get("due_date") and getdate(row.due_date) < getdate(nowdate())]
    if overdue_queries:
        tasks.append({"label": "Overdue lender queries", "priority": "High", "count": len(overdue_queries), "route": _route("Lender Query", {"query_status": ["in", ["Open", "In Progress", "Responded"]], "due_date": ["<", nowdate()]})})
    condition_filters = [["condition_status", "in", ["Pending", "Submitted", "Rejected"]]]
    if selected_lender:
        condition_filters.append(["lender_application", "in", related_application_names or ["__no_matching_application__"]])
    pending_conditions = _read("Loan Sanction Condition", ["name", "lender_application", "condition_status", "due_date"], condition_filters, limit=1000)
    if pending_conditions:
        tasks.append({"label": "Sanction conditions requiring action", "priority": "Medium", "count": len(pending_conditions), "route": _route("Loan Sanction Condition", {"condition_status": ["in", ["Pending", "Submitted", "Rejected"]]})})
    pending_disbursements = _read("Lender Disbursement", ["name", "lender", "disbursement_amount"], _lender_filter(selected_lender) + [["disbursement_status", "=", "Pending"]], limit=1000)
    if pending_disbursements:
        tasks.append({"label": "Disbursements pending processing", "priority": "Medium", "count": len(pending_disbursements), "route": _route("Lender Disbursement", {"disbursement_status": "Pending", **({"lender": selected_lender} if selected_lender else {})})})

    performance = {}
    for row in lenders:
        key = row.name
        performance[key] = {
            "lender": key,
            "lender_name": row.get("lender_name") or key,
            "status": row.get("lender_status") or "",
            "lender_type": row.get("lender_type") or "",
            "applications": 0,
            "approved": 0,
            "disbursed": 0.0,
            "commission": 0.0,
        }
    for row in applications:
        item = performance.get(row.get("lender"))
        if item:
            item["applications"] += 1
            if row.get("application_status") in approved_states:
                item["approved"] += 1
    for row in disbursements:
        item = performance.get(row.get("lender"))
        if item:
            item["disbursed"] += flt(row.get("disbursement_amount"))
    for row in pending_commissions:
        item = performance.get(row.get("lender"))
        if item:
            item["commission"] += flt(row.get("commission_amount"))

    kpis = [
        {"key": "lenders", "label": "Total Lenders", "value": lender_count, "format": "Number", "route": _route("Lender", {"name": selected_lender} if selected_lender else {}), "preview": "Lender master records in the selected lender scope."},
        {"key": "active_lenders", "label": "Active Lenders", "value": active_lender_count, "format": "Number", "route": _route("Lender", {"lender_status": "Active", **({"name": selected_lender} if selected_lender else {})}), "preview": "Lenders whose master status is Active."},
        {"key": "applications", "label": "Applications", "value": len(applications), "format": "Number", "route": _route("Lender Application", {**({"lender": selected_lender} if selected_lender else {}), "submission_date": ["between", date_range]}), "preview": "Lender application submissions in the selected date range."},
        {"key": "approved", "label": "Approved / Sanctioned", "value": approved_count, "format": "Number", "route": _route("Lender Application", {"application_status": ["in", ["Approved", "Sanctioned"]], **({"lender": selected_lender} if selected_lender else {}), "submission_date": ["between", date_range]}), "preview": "Applications currently in Approved or Sanctioned status."},
        {"key": "rejected", "label": "Rejected", "value": rejected_count, "format": "Number", "route": _route("Lender Application", {"application_status": "Rejected", **({"lender": selected_lender} if selected_lender else {}), "submission_date": ["between", date_range]}), "preview": "Applications currently in Rejected status."},
        {"key": "disbursed", "label": "Disbursed Amount", "value": disbursed_amount, "format": "Currency", "route": _route("Lender Disbursement", {"disbursement_status": "Processed", **({"lender": selected_lender} if selected_lender else {}), "disbursement_date": ["between", date_range]}), "preview": "Sum of Processed disbursement amounts in the selected date range."},
        {"key": "commission", "label": "Pending Commission", "value": pending_commission_amount, "format": "Currency", "route": _route("Lender Commission Record", {"commission_status": "Pending", **({"lender": selected_lender} if selected_lender else {}), "commission_date": ["between", date_range]}), "preview": "Pending-status commission records only. Partially Paid balances are not inferred because the DocType has no outstanding-amount field."},
        {"key": "queries", "label": "Open Queries", "value": len(queries), "format": "Number", "route": _route("Lender Query", {"query_status": ["in", ["Open", "In Progress", "Responded"]], **({"lender": selected_lender} if selected_lender else {}), "raised_on": ["between", [str(start) + " 00:00:00", str(end) + " 23:59:59"]]}), "preview": "Queries not yet Resolved or Closed."},
    ]

    return {
        "from_date": str(start),
        "to_date": str(end),
        "lender": selected_lender,
        "currency": "INR",
        "data": {
            "kpis": kpis,
            "pipeline": pipeline,
            "tasks": tasks,
            "lenders": sorted(performance.values(), key=lambda item: (-item["applications"], item["lender_name"])),
            "disbursements": {"amount": disbursed_amount, "count": len(disbursements), "average": flt(disbursed_amount / len(disbursements), 2) if disbursements else 0},
            "commissions": {"pending_amount": pending_commission_amount, "pending_count": len(pending_commissions)},
            "query_count": len(queries),
        },
    }


@frappe.whitelist()
def search(txt=""):
    _guard()
    txt = (txt or "").strip().replace("%", "")[:60]
    if len(txt) < 2:
        return []
    like = f"%{txt}%"
    specs = [
        ("Lender", ["lender_name", "name"], "lender_name", "lender_status"),
        ("Lender Application", ["name", "lender_reference_number"], None, "application_status"),
        ("Lender Loan Product", ["product_name", "product_code"], "product_name", "lender"),
        ("Lender Query", ["name", "query_subject"], "query_subject", "query_status"),
    ]
    out = []
    for doctype, match_fields, title_field, sub_field in specs:
        if not _has_doctype(doctype) or not frappe.has_permission(doctype, "read"):
            continue
        available = _fields(doctype)
        columns = [field for field in match_fields if field in available]
        if not columns:
            continue
        selected = ["name"] + [field for field in (title_field, sub_field) if field and field in available]
        rows = frappe.get_list(doctype, fields=list(dict.fromkeys(selected)), or_filters=[[field, "like", like] for field in columns], order_by="modified desc", limit_page_length=5)
        for row in rows:
            out.append({"doctype": doctype, "name": row.name, "title": row.get(title_field) or row.name if title_field else row.name, "sub": row.get(sub_field) or "" if sub_field else ""})
    return out


@frappe.whitelist()
def get_notifications():
    _guard()
    if not _has_doctype("Notification Log") or not frappe.has_permission("Notification Log", "read"):
        return {"unread": 0, "items": []}
    user = frappe.session.user
    filters = {"for_user": user}
    rows = frappe.get_list("Notification Log", filters=filters, fields=["name", "subject", "read", "creation", "document_type", "document_name"], order_by="creation desc", limit_page_length=20)
    return {
        "unread": sum(1 for row in rows if not row.get("read")),
        "items": [{"subject": strip_html_tags(row.get("subject") or ""), "read": cint(row.get("read")), "creation": str(row.get("creation") or ""), "document_type": row.get("document_type") or "", "document_name": row.get("document_name") or ""} for row in rows],
    }
