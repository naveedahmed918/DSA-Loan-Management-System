import frappe
from frappe.utils import flt

def exists(doctype):
    return bool(frappe.db.exists("DocType", doctype))

def can_read(doctype):
    return exists(doctype) and frappe.has_permission(doctype, "read")

def has_field(doctype, fieldname):
    try:
        return bool(frappe.get_meta(doctype).has_field(fieldname))
    except Exception:
        return False

def aggregate(doctype, filters=None, expression="count(name)", alias="value"):
    if not can_read(doctype):
        return None
    try:
        rows = frappe.get_list(
            doctype, filters=filters or [], fields=[f"{expression} as {alias}"],
            order_by=None, limit_page_length=1
        )
        return flt(rows[0].get(alias)) if rows else 0
    except (frappe.PermissionError, frappe.ValidationError):
        return None
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"DSA dashboard aggregate: {doctype}")
        return None

def grouped(doctype, filters, field, expression="count(name)", alias="value"):
    if not can_read(doctype) or not has_field(doctype, field):
        return None
    try:
        rows = frappe.get_list(
            doctype, filters=filters or [],
            fields=[field, f"{expression} as {alias}"],
            group_by=field, order_by=None, limit_page_length=100
        )
        return [{"label": r.get(field) or "Unspecified", "value": flt(r.get(alias))} for r in rows]
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"DSA dashboard grouped: {doctype}")
        return None

def recent(doctype, fields, filters=None, limit=6):
    if not can_read(doctype):
        return None
    safe_fields = [f for f in fields if has_field(doctype, f)]
    if "name" not in safe_fields:
        safe_fields.insert(0, "name")
    try:
        return frappe.get_list(
            doctype, filters=filters or [], fields=safe_fields,
            order_by="modified desc", limit_page_length=limit
        )
    except Exception:
        return None
