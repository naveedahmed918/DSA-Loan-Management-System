"""Permission-aware read helpers shared by every dashboard.

Rules this module enforces:
- Business numbers are read with frappe.get_list, so role permissions and User Permissions apply.
- A DocType the user cannot read, or a field that does not exist, returns None ("unavailable").
  The dashboard shows that as a clear state instead of crashing or showing a made-up zero.
- Totals are computed by the database (count / sum / group by), never by loading records.
"""

import frappe
from frappe.utils import flt

from dsa_loan.dashboard_v2 import filters as F


def _log():
	return frappe.logger("dsa_dashboard")


def _cache():
	store = getattr(frappe.local, "dsa_dash_cache", None)
	if store is None:
		store = {"cols": {}, "exists": {}}
		frappe.local.dsa_dash_cache = store
	return store


def exists(doctype):
	c = _cache()["exists"]
	if doctype not in c:
		c[doctype] = bool(frappe.db.exists("DocType", doctype))
	return c[doctype]


def can(doctype, ptype="read"):
	return exists(doctype) and bool(frappe.has_permission(doctype, ptype))


def _cols(doctype):
	c = _cache()["cols"]
	if doctype not in c:
		c[doctype] = set(frappe.get_meta(doctype).get_valid_columns())
	return c[doctype]


def usable(doctype, *fields):
	"""True when the user can read the DocType and every named field exists on it."""
	if not can(doctype):
		return False
	cols = _cols(doctype)
	return all(f in cols for f in fields if f)


def _safe(fn):
	try:
		return fn()
	except frappe.PermissionError:
		return None
	except Exception:
		_log().exception("dashboard query failed")
		return None


def _need(filters, extra):
	s = {f[0] for f in (filters or []) if isinstance(f, (list, tuple)) and f}
	s.update(x for x in extra if x and x != "name")
	return s


def _expr(spec):
	fn, field = spec
	if fn == "count_distinct":
		return f"count(distinct {field})"
	return f"{fn}({field})"


def aggregate(doctype, filters, **aggs):
	"""One row of aggregates: aggregate("Lender", [], c=("count","name"), s=("sum","x")) -> {c, s} or None."""
	filters = filters or []
	if not usable(doctype, *_need(filters, [v[1] for v in aggs.values()])):
		return None

	def go():
		rows = frappe.get_list(
			doctype, filters=filters, fields=[f"{_expr(v)} as {k}" for k, v in aggs.items()], order_by=None, limit_page_length=0
		)
		r = rows[0] if rows else {}
		return {k: flt(r.get(k)) for k in aggs}

	return _safe(go)


def scalar(doctype, filters, agg="count", field="name"):
	a = aggregate(doctype, filters, v=(agg, field))
	return None if a is None else a["v"]


def distinct_count(doctype, filters, field):
	"""Number of distinct values of `field`. Falls back to grouping if the database refuses count(distinct)."""
	a = aggregate(doctype, filters, v=("count_distinct", field))
	if a is not None:
		return a["v"]
	if not usable(doctype, field, *_need(filters, [])):
		return None
	return _safe(
		lambda: float(len(frappe.get_list(doctype, filters=filters, fields=[f"{field} as k"], group_by=field, order_by=None, limit_page_length=5000)))
	)


def grouped(doctype, filters, by, **aggs):
	"""{group value: {agg name: value}} with the grouping done in SQL."""
	filters = filters or []
	if not usable(doctype, by, *_need(filters, [v[1] for v in aggs.values()])):
		return None

	def go():
		fields = [f"{by} as k"] + [f"{_expr(v)} as {k}" for k, v in aggs.items()]
		out = {}
		for r in frappe.get_list(doctype, filters=filters, fields=fields, group_by=by, order_by=None, limit_page_length=5000):
			out[r.get("k")] = {k: flt(r.get(k)) for k in aggs}
		return out

	return _safe(go)


def series(doctype, filters, date_field, start, end, **aggs):
	"""Per-bucket aggregates over a date range. SQL groups by day; days are rolled into chart buckets here.
	Returns (keys, {bucket: {agg: value}}) or None."""
	granularity, keys = F.buckets(start, end)
	per_day = grouped(doctype, list(filters or []) + [[date_field, "between", [str(start), str(end)]]], date_field, **aggs)
	if per_day is None:
		return None
	out = {k: {n: 0.0 for n in aggs} for k, _l in keys}
	for day, vals in per_day.items():
		k = F.bucket_key(day, granularity)
		if k in out:
			for n, v in vals.items():
				out[k][n] += v
	return keys, out


def rows(doctype, filters, fields, order_by=None, limit=20):
	"""A short, bounded list of records (plain field names only)."""
	filters = filters or []
	if not usable(doctype, *_need(filters, fields)):
		return None
	return _safe(lambda: frappe.get_list(doctype, filters=filters, fields=list(fields), order_by=order_by, limit_page_length=limit))


def pluck_distinct(doctype, filters, field, limit=2000):
	filters = filters or []
	if not usable(doctype, field, *_need(filters, [])):
		return None
	return _safe(
		lambda: [r.get("k") for r in frappe.get_list(doctype, filters=filters, fields=[f"{field} as k"], group_by=field, order_by=None, limit_page_length=limit)]
	)


def chunks(seq, n):
	seq = list(seq)
	for i in range(0, len(seq), n):
		yield seq[i : i + n]


def pick(g, keys, field="c"):
	"""Sum one aggregate over several group values; None when the group query was unavailable."""
	if g is None:
		return None
	return sum(g.get(k, {}).get(field, 0.0) for k in keys)


def total(g, field="c"):
	if g is None:
		return None
	return sum(v.get(field, 0.0) for v in g.values())


def route(doctype, **filters):
	"""A list view to open on click; the browser applies the filters."""
	return {"doctype": doctype, "filters": filters}
