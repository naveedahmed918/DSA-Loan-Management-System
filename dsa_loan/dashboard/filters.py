import frappe
from frappe.utils import add_days, add_months, getdate, get_first_day, get_last_day, today

PRESETS = ("today", "this_week", "this_month", "last_month", "this_quarter", "this_year", "custom")

def resolve(preset="this_month", from_date=None, to_date=None):
    if preset not in PRESETS:
        frappe.throw("Invalid date range", frappe.ValidationError)
    end = getdate(today())
    if preset == "today":
        start = end
    elif preset == "this_week":
        start = add_days(end, -end.weekday())
    elif preset == "this_month":
        start = get_first_day(end)
    elif preset == "last_month":
        end = add_days(get_first_day(end), -1)
        start = get_first_day(end)
    elif preset == "this_quarter":
        month = ((end.month - 1) // 3) * 3 + 1
        start = getdate(f"{end.year}-{month:02d}-01")
    elif preset == "this_year":
        start = getdate(f"{end.year}-01-01")
    else:
        if not from_date or not to_date:
            frappe.throw("Choose both dates for a custom range", frappe.ValidationError)
        start, end = getdate(from_date), getdate(to_date)
        if start > end:
            frappe.throw("From date cannot be after To date", frappe.ValidationError)
        if (end - start).days > 1825:
            frappe.throw("Custom date range cannot exceed five years", frappe.ValidationError)
    return start, end
