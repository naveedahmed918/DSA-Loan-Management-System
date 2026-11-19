"""Date ranges for the dashboard. Only the presets below are accepted from the browser; a custom
range is checked for valid dates, order and length."""

from datetime import datetime, time, timedelta

import frappe
from frappe import _
from frappe.utils import add_months, get_first_day, get_last_day, get_quarter_start, get_year_start, getdate, today

PRESETS = {
	"today": "Today",
	"this_week": "This Week",
	"this_month": "This Month",
	"last_month": "Last Month",
	"this_quarter": "This Quarter",
	"this_year": "This Year",
	"custom": "Custom Range",
}
DEFAULT_PRESET = "this_month"
MAX_DAYS = 366 * 5


def resolve(preset=None, from_date=None, to_date=None):
	"""(start, end) as dates for a preset or a validated custom range."""
	preset = preset or DEFAULT_PRESET
	if preset not in PRESETS:
		frappe.throw(_("Unknown date range"), frappe.ValidationError)
	now = getdate(today())
	if preset == "today":
		return now, now
	if preset == "this_week":
		start = now - timedelta(days=now.weekday())
		return start, start + timedelta(days=6)
	if preset == "this_month":
		return get_first_day(now), get_last_day(now)
	if preset == "last_month":
		prev = add_months(now, -1)
		return get_first_day(prev), get_last_day(prev)
	if preset == "this_quarter":
		start = getdate(get_quarter_start(now))
		return start, get_last_day(add_months(start, 2))
	if preset == "this_year":
		start = getdate(get_year_start(now))
		return start, getdate(f"{start.year}-12-31")

	if not from_date or not to_date:
		frappe.throw(_("Enter both From and To dates"), frappe.ValidationError)
	try:
		start, end = getdate(from_date), getdate(to_date)
	except Exception:
		frappe.throw(_("Enter valid From and To dates"), frappe.ValidationError)
	if start > end:
		frappe.throw(_("From date must be on or before To date"), frappe.ValidationError)
	if (end - start).days > MAX_DAYS:
		frappe.throw(_("Choose a range of five years or less"), frappe.ValidationError)
	return start, end


def previous(start, end):
	"""The equally long period immediately before (start, end)."""
	days = (end - start).days + 1
	p_end = start - timedelta(days=1)
	return p_end - timedelta(days=days - 1), p_end


def between(start, end):
	return ["between", [str(start), str(end)]]


def day_start(d):
	return datetime.combine(d, time.min)


def day_end(d):
	return datetime.combine(d, time.max)


def buckets(start, end):
	"""Chart buckets: one per day for a month or less, otherwise one per month.
	Returns (granularity, [(key, label)])."""
	if (end - start).days <= 31:
		out, d = [], start
		while d <= end:
			out.append((str(d), d.strftime("%d %b")))
			d += timedelta(days=1)
		return "day", out
	out, d = [], get_first_day(start)
	while d <= end:
		out.append((d.strftime("%Y-%m"), d.strftime("%b %y")))
		d = add_months(d, 1)
	return "month", out


def bucket_key(value, granularity):
	if not value:
		return None
	value = getdate(value)
	return str(value) if granularity == "day" else value.strftime("%Y-%m")
