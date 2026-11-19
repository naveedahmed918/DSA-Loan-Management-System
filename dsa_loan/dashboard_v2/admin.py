"""Admin dashboard numbers.

Every function returns plain JSON-able data, or None when the section is unavailable (no read
permission, or a field is missing). Nothing here writes to the database.

Date basis per module (inspected from the schema):
  Loan Application      -> application_date          (customer's loan request)
  Lender Application    -> submission_date           (a submission to one lender)
  Lender Disbursement   -> disbursement_date         (only disbursement_status = Processed counts as money out)
  Lender Commission Rec -> commission_date           (Cancelled records never count)
  Sales / Payment Entry -> posting_date              (submitted documents of the selected company)

Double counting: a Loan Application can be sent to several lenders, so pipeline counts use
count(distinct customer_loan_application). Commission operational figures (Lender Commission
Record) are kept apart from accounting figures (Sales Invoice / Payment Entry).
"""

from collections import defaultdict
from datetime import timedelta

import frappe
from frappe.utils import add_days, flt, get_fullname, getdate, today

from dsa_loan.dashboard_v2 import core as C
from dsa_loan.dashboard_v2 import filters as F
from dsa_loan.dashboard_v2 import schema as S

route = C.route
LIVE_COMM = [["commission_status", "!=", S.COMM_CANCELLED]]


def kpi(key, label, value, fmt="Int", rt=None, note=None, delta=None):
	return {"key": key, "label": label, "value": value, "format": fmt, "route": rt, "note": note, "delta": delta}


def pct_change(cur, prev):
	if cur is None or prev is None or not prev:
		return None
	return round((cur - prev) * 100.0 / prev, 1)


def _int(v):
	return None if v is None else int(v)


def _creation_between(start, end):
	return [["creation", ">=", F.day_start(start)], ["creation", "<=", F.day_end(end)]]


# ====================================================================== finance (ERPNext)

def finance_overview(start, end, company):
	"""Accounting view for one company: submitted documents only, credit notes netted."""
	if not C.can(S.SALES_INVOICE) or not company:
		return None
	rng = F.between(start, end)
	base = [["docstatus", "=", 1], ["company", "=", company]]
	period = base + [["posting_date", "between", rng[1]]]
	td = str(getdate(today()))

	inv = C.aggregate(S.SALES_INVOICE, period + [["is_return", "=", 0]], c=("count", "name"), g=("sum", "base_grand_total"))
	ret = C.aggregate(S.SALES_INVOICE, period + [["is_return", "=", 1]], g=("sum", "base_grand_total"))
	net = C.aggregate(S.SALES_INVOICE, period, n=("sum", "base_net_total"))
	paid = C.scalar(S.SALES_INVOICE, period + [["is_return", "=", 0], ["status", "=", "Paid"]])
	out_all = C.aggregate(S.SALES_INVOICE, base + [["outstanding_amount", ">", 0]], c=("count", "name"), o=("sum", "outstanding_amount"))
	overdue = C.aggregate(S.SALES_INVOICE, base + [["outstanding_amount", ">", 0], ["due_date", "<", td]], c=("count", "name"), o=("sum", "outstanding_amount"))
	rec = C.aggregate(S.PAYMENT_ENTRY, period + [["payment_type", "=", "Receive"]], c=("count", "name"), s=("sum", "base_received_amount"))
	made = C.aggregate(S.PAYMENT_ENTRY, period + [["payment_type", "=", "Pay"]], c=("count", "name"), s=("sum", "base_paid_amount"))
	payables = C.aggregate(S.PURCHASE_INVOICE, base + [["outstanding_amount", ">", 0]], c=("count", "name"), o=("sum", "outstanding_amount"))

	s_inv = C.series(S.SALES_INVOICE, base + [["is_return", "=", 0]], "posting_date", start, end, s=("sum", "base_grand_total"))
	s_ret = C.series(S.SALES_INVOICE, base + [["is_return", "=", 1]], "posting_date", start, end, s=("sum", "base_grand_total"))
	s_rec = C.series(S.PAYMENT_ENTRY, base + [["payment_type", "=", "Receive"]], "posting_date", start, end, s=("sum", "base_received_amount"))
	keys = F.buckets(start, end)[1]
	g = lambda s, k: (s[1][k]["s"] if s else 0.0)

	def val(a, k):
		return None if a is None else a[k]

	return {
		"company": company,
		"totals": {
			"invoices": _int(val(inv, "c")),
			"invoiced": val(inv, "g"),
			"credit_notes": val(ret, "g"),
			"net_revenue": val(net, "n"),
			"paid_invoices": _int(paid),
			"outstanding": val(out_all, "o"),
			"unpaid_count": _int(val(out_all, "c")),
			"overdue": val(overdue, "o"),
			"overdue_count": _int(val(overdue, "c")),
			"received": val(rec, "s"),
			"received_count": _int(val(rec, "c")),
			"paid_out": val(made, "s"),
			"payables": val(payables, "o"),
		},
		"labels": [l for _k, l in keys],
		"datasets": [
			{"name": "Invoiced (net of credit notes)", "values": [g(s_inv, k) + g(s_ret, k) for k, _l in keys]},
			{"name": "Payments received", "values": [g(s_rec, k) for k, _l in keys]},
		],
	}


# ====================================================================== commission linkage

def _linked_invoice_totals(record_filters):
	"""Distinct submitted Sales Invoices linked from commission records -> (grand_total, outstanding).
	Distinct so one invoice covering several records is counted once. Includes GST."""
	if not C.usable(S.COMM, "sales_invoice") or not C.usable(S.SALES_INVOICE, "grand_total", "outstanding_amount", "docstatus"):
		return None
	names = C.pluck_distinct(S.COMM, list(record_filters) + [["sales_invoice", "is", "set"]], "sales_invoice")
	if names is None:
		return None
	grand = out = 0.0
	for chunk in C.chunks([n for n in names if n], 400):
		a = C.aggregate(S.SALES_INVOICE, [["name", "in", chunk], ["docstatus", "=", 1]], g=("sum", "grand_total"), o=("sum", "outstanding_amount"))
		if a is None:
			return None
		grand += a["g"]
		out += a["o"]
	return grand, out


# ====================================================================== KPIs

def kpis(start, end, company, fin=None):
	rng = F.between(start, end)
	ps, pe = F.previous(start, end)
	prng = F.between(ps, pe)

	la_all = C.grouped(S.LOAN_APP, [], "application_status", c=("count", "name"))
	la_per = C.grouped(S.LOAN_APP, [["application_date", "between", rng[1]]], "application_status", c=("count", "name"), s=("sum", "loan_amount"))
	apps_p = C.total(la_per)
	approved_p = C.pick(la_per, S.LOAN_APPROVED)
	rejected_p = C.pick(la_per, ["Rejected"])
	pending_now = C.pick(la_all, S.LOAN_PENDING)
	prev_apps = C.scalar(S.LOAN_APP, [["application_date", "between", prng[1]]])
	prev_appr = C.scalar(S.LOAN_APP, [["application_date", "between", prng[1]], ["application_status", "in", S.LOAN_APPROVED]])

	cust_total = C.scalar(S.CUSTOMER, [])
	cust_new = C.scalar(S.CUSTOMER, _creation_between(start, end))

	lenders = C.grouped(S.LENDER, [], "lender_status", c=("count", "name"))
	prod = C.grouped(S.PRODUCT, [], "is_active", c=("count", "name"))
	lapp_all = C.grouped(S.LENDER_APP, [], "application_status", c=("count", "name"))
	lapp_per = C.grouped(S.LENDER_APP, [["submission_date", "between", rng[1]]], "application_status", c=("count", "name"), sub=("sum", "submitted_amount"), ap=("sum", "approved_amount"))

	d_all = C.grouped(S.DISB, [], "disbursement_status", c=("count", "name"), s=("sum", "disbursement_amount"))
	d_per = C.grouped(S.DISB, [["disbursement_date", "between", rng[1]]], "disbursement_status", c=("count", "name"), s=("sum", "disbursement_amount"))
	d_cnt_p = C.pick(d_per, [S.DISB_DONE])
	d_amt_p = C.pick(d_per, [S.DISB_DONE], "s")
	prev_d = C.scalar(S.DISB, [["disbursement_status", "=", S.DISB_DONE], ["disbursement_date", "between", prng[1]]], "sum", "disbursement_amount")

	c_per = C.grouped(S.COMM, [["commission_date", "between", rng[1]]], "commission_status", c=("count", "name"), s=("sum", "commission_amount"))
	c_all = C.grouped(S.COMM, [], "commission_status", c=("count", "name"), s=("sum", "commission_amount"))
	earned_p = None if c_per is None else sum(v["s"] for k, v in c_per.items() if k != S.COMM_CANCELLED)
	prev_c = C.scalar(S.COMM, LIVE_COMM + [["commission_date", "between", prng[1]]], "sum", "commission_amount")
	not_invoiced = C.pick(c_all, ["Pending"], "s")
	recv_inv = _linked_invoice_totals(LIVE_COMM + [["commission_date", "between", rng[1]]])
	wait_inv = _linked_invoice_totals([["commission_status", "in", S.COMM_INVOICED]])

	if fin is None:
		fin = finance_overview(start, end, company)
	ft = (fin or {}).get("totals", {})

	avg_disb = None if d_cnt_p is None or d_amt_p is None else (d_amt_p / d_cnt_p if d_cnt_p else 0.0)
	active_lenders = C.pick(lenders, [S.LENDER_ACTIVE])
	products_active = C.pick(prod, [1])
	products_total = C.total(prod)

	headline = [
		kpi("applications", "Loan applications", _int(apps_p), "Int", route(S.LOAN_APP, application_date=rng), "Created in period", pct_change(apps_p, prev_apps)),
		kpi("approved", "Approved", _int(approved_p), "Int", route(S.LOAN_APP, application_date=rng, application_status=["in", S.LOAN_APPROVED]), "Approved or disbursed", pct_change(approved_p, prev_appr)),
		kpi("disbursed", "Disbursed", d_amt_p, "Currency", route(S.DISB, disbursement_date=rng, disbursement_status=S.DISB_DONE), None if d_cnt_p is None else f"{int(d_cnt_p)} processed in period", pct_change(d_amt_p, prev_d)),
		kpi("commission", "Commission earned", earned_p, "Currency", route(S.COMM, commission_date=rng, commission_status=["!=", S.COMM_CANCELLED]), "Excl. cancelled", pct_change(earned_p, prev_c)),
	]
	tiles = [
		kpi("customers", "Customers", _int(cust_total), "Int", route(S.CUSTOMER), "All time"),
		kpi("pending", "Pending applications", _int(pending_now), "Int", route(S.LOAN_APP, application_status=["in", S.LOAN_PENDING]), "Draft, submitted, under review"),
		kpi("rejected", "Rejected", _int(rejected_p), "Int", route(S.LOAN_APP, application_date=rng, application_status="Rejected"), "In period"),
		kpi("lenders", "Lenders", _int(C.total(lenders)), "Int", route(S.LENDER), "All time"),
		kpi("active_lenders", "Active lenders", _int(active_lenders), "Int", route(S.LENDER, lender_status=S.LENDER_ACTIVE), "Status Active"),
		kpi("products", "Loan products", _int(products_total), "Int", route(S.PRODUCT), None if products_active is None else f"{int(products_active)} active"),
	]
	sections = [
		{"key": "customers", "label": "Customers", "kpis": [
			kpi("c_total", "Total customers", _int(cust_total), "Int", route(S.CUSTOMER)),
			kpi("c_new", "New customers", _int(cust_new), "Int", route(S.CUSTOMER, creation=rng), "Registered in period"),
		]},
		{"key": "applications", "label": "Loan applications", "kpis": [
			kpi("a_all", "All applications", _int(C.total(la_all)), "Int", route(S.LOAN_APP)),
			kpi("a_draft", "Draft", _int(C.pick(la_all, ["Draft"])), "Int", route(S.LOAN_APP, application_status="Draft"), "Right now"),
			kpi("a_sub", "Submitted", _int(C.pick(la_all, ["Submitted"])), "Int", route(S.LOAN_APP, application_status="Submitted"), "Right now"),
			kpi("a_rev", "Under review", _int(C.pick(la_all, ["Under Review"])), "Int", route(S.LOAN_APP, application_status="Under Review"), "Right now"),
			kpi("a_appr", "Approved", _int(approved_p), "Int", route(S.LOAN_APP, application_date=rng, application_status=["in", S.LOAN_APPROVED]), "In period, incl. disbursed"),
			kpi("a_rej", "Rejected", _int(rejected_p), "Int", route(S.LOAN_APP, application_date=rng, application_status="Rejected"), "In period"),
		]},
		{"key": "lenders", "label": "Lenders & submissions", "kpis": [
			kpi("l_total", "Lenders", _int(C.total(lenders)), "Int", route(S.LENDER)),
			kpi("l_active", "Active lenders", _int(active_lenders), "Int", route(S.LENDER, lender_status=S.LENDER_ACTIVE)),
			kpi("l_prod", "Loan products", _int(products_total), "Int", route(S.PRODUCT)),
			kpi("l_prod_a", "Active products", _int(products_active), "Int", route(S.PRODUCT, is_active=1)),
			kpi("l_subs", "Lender submissions", _int(C.total(lapp_per)), "Int", route(S.LENDER_APP, submission_date=rng), "Submitted in period"),
			kpi("l_wait", "Awaiting lender response", _int(C.pick(lapp_all, S.LAPP_AWAITING)), "Int", route(S.LENDER_APP, application_status=["in", S.LAPP_AWAITING]), "Submitted or under review"),
			kpi("l_docs", "Documents required", _int(C.pick(lapp_all, ["Documents Required"])), "Int", route(S.LENDER_APP, application_status="Documents Required"), "Right now"),
			kpi("l_sanc", "Sanctioned", _int(C.pick(lapp_per, ["Sanctioned"])), "Int", route(S.LENDER_APP, submission_date=rng, application_status="Sanctioned"), "Submitted in period"),
		]},
		{"key": "disbursements", "label": "Disbursements", "kpis": [
			kpi("d_cnt", "Processed (all time)", _int(C.pick(d_all, [S.DISB_DONE])), "Int", route(S.DISB, disbursement_status=S.DISB_DONE)),
			kpi("d_amt", "Disbursed (all time)", C.pick(d_all, [S.DISB_DONE], "s"), "Currency", route(S.DISB, disbursement_status=S.DISB_DONE)),
			kpi("d_cnt_p", "Processed in period", _int(d_cnt_p), "Int", route(S.DISB, disbursement_date=rng, disbursement_status=S.DISB_DONE)),
			kpi("d_avg", "Average disbursement", avg_disb, "Currency", None, "In period"),
			kpi("d_pend", "Pending disbursements", _int(C.pick(d_all, ["Pending"])), "Int", route(S.DISB, disbursement_status="Pending"), "Right now"),
			kpi("d_fail", "Failed", _int(C.pick(d_all, ["Failed"])), "Int", route(S.DISB, disbursement_status="Failed"), "Right now"),
		]},
		{"key": "commission", "label": "Commission", "kpis": [
			kpi("m_earned", "Earned", earned_p, "Currency", route(S.COMM, commission_date=rng, commission_status=["!=", S.COMM_CANCELLED]), "In period, excl. cancelled"),
			kpi("m_notinv", "Not yet invoiced", not_invoiced, "Currency", route(S.COMM, commission_status="Pending"), "Status Pending"),
			kpi("m_recv", "Received", None if recv_inv is None else recv_inv[0] - recv_inv[1], "Currency", route(S.COMM, commission_date=rng, commission_status=["!=", S.COMM_CANCELLED]), "Paid share of linked invoices, incl. GST"),
			kpi("m_wait", "Awaiting payment", None if wait_inv is None else wait_inv[1], "Currency", route(S.COMM, commission_status=["in", S.COMM_INVOICED]), "Outstanding on linked invoices, incl. GST"),
		]},
		{"key": "finance", "label": "Accounts (selected company)", "kpis": [
			kpi("f_inv", "Sales invoices", ft.get("invoices"), "Int", route(S.SALES_INVOICE, company=company, docstatus=1, posting_date=rng, is_return=0), "Submitted, in period"),
			kpi("f_amt", "Invoiced", ft.get("invoiced"), "Currency", route(S.SALES_INVOICE, company=company, docstatus=1, posting_date=rng, is_return=0), "Incl. GST"),
			kpi("f_net", "Net revenue", ft.get("net_revenue"), "Currency", route(S.SALES_INVOICE, company=company, docstatus=1, posting_date=rng), "Before GST, after credit notes"),
			kpi("f_out", "Outstanding receivables", ft.get("outstanding"), "Currency", route(S.SALES_INVOICE, company=company, docstatus=1, outstanding_amount=[">", 0]), "All unpaid invoices"),
			kpi("f_over", "Overdue", ft.get("overdue"), "Currency", route(S.SALES_INVOICE, company=company, docstatus=1, outstanding_amount=[">", 0], due_date=["<", str(getdate(today()))])),
			kpi("f_rec", "Payments received", ft.get("received"), "Currency", route(S.PAYMENT_ENTRY, company=company, docstatus=1, payment_type="Receive", posting_date=rng), "In period"),
			kpi("f_made", "Payments made", ft.get("paid_out"), "Currency", route(S.PAYMENT_ENTRY, company=company, docstatus=1, payment_type="Pay", posting_date=rng), "In period"),
			kpi("f_pay", "Outstanding payables", ft.get("payables"), "Currency", route(S.PURCHASE_INVOICE, company=company, docstatus=1, outstanding_amount=[">", 0])),
		]},
	]
	undated = {
		"applications": _int(C.scalar(S.LOAN_APP, [["application_date", "is", "not set"]])),
		"commission": _int(C.scalar(S.COMM, [["commission_date", "is", "not set"]])),
	}
	return {"headline": headline, "tiles": tiles, "sections": sections, "undated": undated}


# ====================================================================== customers

def customers(start, end):
	if not C.can(S.CUSTOMER):
		return None
	gran, keys = F.buckets(start, end)
	created = C.rows(S.CUSTOMER, _creation_between(start, end), ["creation"], "creation asc", 5000) or []
	per = defaultdict(int)
	for r in created:
		k = F.bucket_key(r.get("creation"), gran)
		if k:
			per[k] += 1
	cities = C.grouped(S.CUSTOMER, [], "city", c=("count", "name")) or {}
	top = sorted(((k or "Not set", v["c"]) for k, v in cities.items()), key=lambda x: -x[1])[:6]
	return {
		"total": _int(C.scalar(S.CUSTOMER, [])),
		"new": _int(C.scalar(S.CUSTOMER, _creation_between(start, end))),
		"labels": [l for _k, l in keys],
		"values": [per.get(k, 0) for k, _l in keys],
		"cities": [{"label": k, "count": int(c)} for k, c in top],
		"route": route(S.CUSTOMER),
	}


# ====================================================================== loan applications

def application_trends(start, end):
	if not C.usable(S.LOAN_APP, "application_date", "application_status"):
		return None
	_g, keys = F.buckets(start, end)

	def per_bucket(statuses):
		s = C.series(S.LOAN_APP, [["application_status", "in", statuses]], "application_date", start, end, c=("count", "name"))
		return [0 if s is None else int(s[1][k]["c"]) for k, _l in keys]

	created = C.series(S.LOAN_APP, [], "application_date", start, end, c=("count", "name"))
	if created is None:
		return None
	return {
		"labels": [l for _k, l in keys],
		"datasets": [
			{"name": "Created", "values": [int(created[1][k]["c"]) for k, _l in keys]},
			{"name": "Approved", "values": per_bucket(S.LOAN_APPROVED)},
			{"name": "Rejected", "values": per_bucket(["Rejected"])},
			{"name": "Pending", "values": per_bucket(S.LOAN_PENDING)},
		],
	}


def application_status(start, end):
	g = C.grouped(S.LOAN_APP, [["application_date", "between", [str(start), str(end)]]], "application_status", c=("count", "name"))
	if g is None:
		return None
	order = S.LOAN_STATUS_ORDER + [k for k in g if k not in S.LOAN_STATUS_ORDER]
	items = [(k or "No status", g[k]["c"]) for k in order if g.get(k, {}).get("c")]
	return {"labels": [k for k, _c in items], "values": [int(c) for _k, c in items], "total": int(sum(c for _k, c in items))}


def loan_types(start, end):
	rng = F.between(start, end)
	g = C.grouped(S.LOAN_APP, [["application_date", "between", rng[1]]], "loan_type", c=("count", "name"), s=("sum", "loan_amount"))
	if g is None:
		return None
	items = sorted(g.items(), key=lambda kv: -kv[1]["c"])
	return {"rows": [{"label": k or "Not set", "count": int(v["c"]), "amount": v["s"], "route": route(S.LOAN_APP, application_date=rng, loan_type=k) if k else None} for k, v in items]}


def amounts(start, end):
	"""Submitted vs approved amount per bucket, from lender submissions."""
	if not C.usable(S.LENDER_APP, "submission_date", "submitted_amount", "approved_amount", "application_status"):
		return None
	_g, keys = F.buckets(start, end)
	sub = C.series(S.LENDER_APP, [["application_status", "not in", S.LAPP_NOT_SUBMITTED]], "submission_date", start, end, s=("sum", "submitted_amount"))
	app = C.series(S.LENDER_APP, [["application_status", "in", S.LAPP_APPROVED]], "submission_date", start, end, s=("sum", "approved_amount"))
	if sub is None or app is None:
		return None
	return {
		"labels": [l for _k, l in keys],
		"datasets": [
			{"name": "Submitted", "values": [sub[1][k]["s"] for k, _l in keys]},
			{"name": "Approved", "values": [app[1][k]["s"] for k, _l in keys]},
		],
	}


# ====================================================================== lenders

def _is_bank(name):
        return "bank" in (name or "").lower()
def lender_performance(start, end):
        if not C.usable(S.LENDER, "lender_name", "lender_type", "lender_status"):
                return None

        rng = [str(start), str(end)]

        lenders = C.rows(
                S.LENDER, [],
                ["name", "lender_name", "lender_type", "lender_status"],
                "lender_name asc", 500
        ) or []

        # Resolve internal Lender Type IDs into readable names.
        lender_type_labels = {
                row["name"]: row["type_name"]
                for row in frappe.get_all(
                        "Lender Type",
                        fields=["name", "type_name"],
                        limit_page_length=500
                )
        }

        prod = C.grouped(S.PRODUCT, [], "lender", c=("count", "name"), a=("sum", "is_active")) or {}
        subs = C.grouped(S.LENDER_APP, [["submission_date", "between", rng], ["application_status", "not in", S.LAPP_NOT_SUBMITTED]], "lender", c=("count", "name"), s=("sum", "submitted_amount")) or {}
        appr = C.grouped(S.LENDER_APP, [["submission_date", "between", rng], ["application_status", "in", S.LAPP_APPROVED]], "lender", c=("count", "name"), s=("sum", "approved_amount")) or {}
        disb = C.grouped(S.DISB, [["disbursement_status", "=", S.DISB_DONE], ["disbursement_date", "between", rng]], "lender", c=("count", "name"), s=("sum", "disbursement_amount")) or {}
        comm = C.grouped(S.COMM, LIVE_COMM + [["commission_date", "between", rng]], "lender", s=("sum", "commission_amount")) or {}

        table = []

        for l in lenders:
                n = l.get("name")
                type_id = l.get("lender_type")
                table.append({
                        "lender": n,
                        "lender_name": l.get("lender_name") or n,
                        "lender_type": type_id,
                        "lender_type_label": lender_type_labels.get(type_id, type_id),
                        "status": l.get("lender_status"),
                        "products": int(prod.get(n, {}).get("c", 0)),
                        "active_products": int(prod.get(n, {}).get("a", 0)),
                        "submissions": int(subs.get(n, {}).get("c", 0)),
                        "submitted_amount": subs.get(n, {}).get("s", 0.0),
                        "approved": int(appr.get(n, {}).get("c", 0)),
                        "approved_amount": appr.get(n, {}).get("s", 0.0),
                        "disbursements": int(disb.get(n, {}).get("c", 0)),
                        "disbursed": disb.get(n, {}).get("s", 0.0),
                        "commission": comm.get(n, {}).get("s", 0.0),
                })

        table.sort(key=lambda r: (-r["submissions"], -r["disbursed"], (r["lender_name"] or "").lower()))

        by_type = C.grouped(S.LENDER, [], "lender_type", c=("count", "name")) or {}
        active_by_type = C.grouped(S.LENDER, [["lender_status", "=", S.LENDER_ACTIVE]], "lender_type", c=("count", "name")) or {}

        types = sorted(
                ({
                        "type": lender_type_labels.get(k, k) if k else "Not set",
                        "type_id": k,
                        "count": int(v["c"]),
                        "active": int(active_by_type.get(k, {}).get("c", 0)),
                        "bank": _is_bank(lender_type_labels.get(k, k)),
                } for k, v in by_type.items()),
                key=lambda x: -x["count"],
        )

        total = sum(t["count"] for t in types)
        banks = sum(t["count"] for t in types if t["bank"])
        active = C.pick(C.grouped(S.LENDER, [], "lender_status", c=("count", "name")), [S.LENDER_ACTIVE])

        return {
                "rows": table[:25],
                "row_count": len(table),
                "types": types,
                "groups": {"banks": banks, "others": total - banks},
                "totals": {
                        "lenders": total,
                        "active": _int(active),
                        "products": _int(C.scalar(S.PRODUCT, [])),
                        "active_products": _int(C.scalar(S.PRODUCT, [["is_active", "=", 1]])),
                },
                "range": rng,
        }



# ====================================================================== disbursements / commission

def disbursement_analytics(start, end):
	flt_ = [["disbursement_status", "=", S.DISB_DONE]]
	s = C.series(S.DISB, flt_, "disbursement_date", start, end, c=("count", "name"), s=("sum", "disbursement_amount"))
	if s is None:
		return None
	keys, data = s
	cnt = [int(data[k]["c"]) for k, _l in keys]
	amt = [data[k]["s"] for k, _l in keys]
	rng = F.between(start, end)
	by_lender = C.grouped(S.DISB, flt_ + [["disbursement_date", "between", rng[1]]], "lender", c=("count", "name"), s=("sum", "disbursement_amount")) or {}
	top = sorted(by_lender.items(), key=lambda kv: -kv[1]["s"])[:5]
	tc, ta = sum(cnt), sum(amt)
	return {
		"labels": [l for _k, l in keys], "count": cnt, "amount": amt,
		"average": [round(a / c, 2) if c else 0 for a, c in zip(amt, cnt)],
		"totals": {"count": tc, "amount": ta, "average": round(ta / tc, 2) if tc else 0},
		"by_lender": [{"lender": k, "count": int(v["c"]), "amount": v["s"]} for k, v in top],
		"pending": _int(C.scalar(S.DISB, [["disbursement_status", "=", "Pending"]])),
		"route": route(S.DISB, disbursement_date=rng, disbursement_status=S.DISB_DONE),
	}


def commission_analytics(start, end):
	base = [["commission_status", "!=", S.COMM_CANCELLED]]
	earned = C.series(S.COMM, base, "commission_date", start, end, s=("sum", "commission_amount"))
	if earned is None:
		return None
	paid = C.series(S.COMM, [["commission_status", "=", "Paid"]], "commission_date", start, end, s=("sum", "commission_amount"))
	openc = C.series(S.COMM, [["commission_status", "in", S.COMM_OPEN]], "commission_date", start, end, s=("sum", "commission_amount"))
	keys = earned[0]
	rng = F.between(start, end)
	by_lender = C.grouped(S.COMM, base + [["commission_date", "between", rng[1]]], "lender", s=("sum", "commission_amount")) or {}
	top = sorted(by_lender.items(), key=lambda kv: -kv[1]["s"])[:5]
	vals = lambda s: [0.0 if s is None else s[1][k]["s"] for k, _l in keys]
	return {
		"labels": [l for _k, l in keys],
		"datasets": [
			{"name": "Earned", "values": vals(earned)},
			{"name": "Marked paid", "values": vals(paid)},
			{"name": "Pending / invoiced", "values": vals(openc)},
		],
		"by_lender": [{"lender": k, "amount": v["s"]} for k, v in top],
		"route": route(S.COMM, commission_date=rng, commission_status=["!=", S.COMM_CANCELLED]),
	}


# ====================================================================== pipeline

def _avg_days(pairs):
	days = [(getdate(b) - getdate(a)).days for a, b in pairs if a and b and getdate(b) >= getdate(a)]
	return round(sum(days) / len(days), 1) if days else None


def pipeline(start, end):
	"""Funnel of activity in the period. Counts are distinct Loan Applications, so a loan sent to
	three lenders is one application. Stages after 'Applications created' are measured by the
	lender submission date, so conversion % compares activity within the same period."""
	if not C.can(S.LOAN_APP):
		return None
	rng = F.between(start, end)
	sub_f = [["submission_date", "between", rng[1]]]
	created = C.scalar(S.LOAN_APP, [["application_date", "between", rng[1]]])
	drafts = C.scalar(S.LOAN_APP, [["application_date", "between", rng[1]], ["application_status", "=", "Draft"]])
	submitted = C.distinct_count(S.LENDER_APP, sub_f + [["application_status", "not in", S.LAPP_NOT_SUBMITTED]], "customer_loan_application")
	review = C.distinct_count(S.LENDER_APP, sub_f + [["application_status", "in", S.LAPP_REVIEW]], "customer_loan_application")
	approved = C.distinct_count(S.LENDER_APP, sub_f + [["application_status", "in", S.LAPP_APPROVED]], "customer_loan_application")
	disbursed = C.distinct_count(S.DISB, [["disbursement_status", "=", S.DISB_DONE], ["disbursement_date", "between", rng[1]]], "lender_application")
	rejected = C.distinct_count(S.LENDER_APP, sub_f + [["application_status", "=", "Rejected"]], "customer_loan_application")
	withdrawn = C.distinct_count(S.LENDER_APP, sub_f + [["application_status", "=", "Withdrawn"]], "customer_loan_application")
	customers_new = C.scalar(S.CUSTOMER, _creation_between(start, end))

	stages = [
		{"key": "created", "label": "Applications created", "count": _int(created), "now": _int(drafts), "now_label": "still draft", "route": route(S.LOAN_APP, application_date=rng)},
		{"key": "submitted", "label": "Submitted to lenders", "count": _int(submitted), "now": None, "now_label": None, "route": route(S.LENDER_APP, submission_date=rng, application_status=["not in", S.LAPP_NOT_SUBMITTED])},
		{"key": "review", "label": "With lender / reviewing", "count": _int(review), "now": None, "now_label": None, "route": route(S.LENDER_APP, submission_date=rng, application_status=["in", S.LAPP_REVIEW])},
		{"key": "approved", "label": "Approved or sanctioned", "count": _int(approved), "now": None, "now_label": None, "route": route(S.LENDER_APP, submission_date=rng, application_status=["in", S.LAPP_APPROVED])},
		{"key": "disbursed", "label": "Disbursed", "count": _int(disbursed), "now": None, "now_label": None, "route": route(S.DISB, disbursement_date=rng, disbursement_status=S.DISB_DONE)},
	]
	prev = None
	for st in stages:
		c = st["count"]
		st["conversion"] = round(100.0 * c / prev, 1) if (c is not None and prev) else None
		prev = c if c is not None else prev

	timing = {"application_to_submission": None, "submission_to_sanction": None}
	la_rows = C.rows(S.LENDER_APP, sub_f + [["application_status", "not in", S.LAPP_NOT_SUBMITTED]], ["customer_loan_application", "submission_date", "sanction_date"], "submission_date asc", 3000)
	if la_rows:
		timing["submission_to_sanction"] = _avg_days([(r.get("submission_date"), r.get("sanction_date")) for r in la_rows])
		apps = sorted({r.get("customer_loan_application") for r in la_rows if r.get("customer_loan_application")})
		dates = {}
		for chunk in C.chunks(apps, 400):
			for r in C.rows(S.LOAN_APP, [["name", "in", chunk]], ["name", "application_date"], None, 400) or []:
				dates[r["name"]] = r.get("application_date")
		timing["application_to_submission"] = _avg_days([(dates.get(r.get("customer_loan_application")), r.get("submission_date")) for r in la_rows])

	return {
		"stages": stages, "timing": timing,
		"customers_new": _int(customers_new),
		"side": {
			"rejected": _int(rejected), "withdrawn": _int(withdrawn),
			"route_rejected": route(S.LENDER_APP, submission_date=rng, application_status="Rejected"),
			"route_withdrawn": route(S.LENDER_APP, submission_date=rng, application_status="Withdrawn"),
		},
	}


# ====================================================================== activity

ACTIVITY = [
	# doctype, label, timestamp field, extra filters, title field (or "@customer"), status field
	(S.CUSTOMER, "Customer registered", "creation", [], "customer_name", None),
	(S.LOAN_APP, "Application created", "creation", [], "@customer", "application_status"),
	(S.LOAN_APP, "Application updated", "modified", [], "@customer", "application_status"),
	(S.LENDER_APP, "Lender submission", "modified", [["application_status", "not in", S.LAPP_NOT_SUBMITTED]], "lender", "application_status"),
	(S.LENDER_APP, "Application approved", "modified", [["application_status", "in", S.LAPP_APPROVED]], "lender", "application_status"),
	(S.DISB, "Loan disbursed", "modified", [["disbursement_status", "=", S.DISB_DONE]], "lender", "disbursement_status"),
	(S.COMM, "Commission recorded", "creation", LIVE_COMM, "lender", "commission_status"),
	(S.SALES_INVOICE, "Invoice raised", "creation", [["docstatus", "=", 1]], "customer_name", "status"),
	(S.PAYMENT_ENTRY, "Payment entry", "creation", [["docstatus", "=", 1]], "party_name", "payment_type"),
]


def recent_activities(company, limit=14):
	items, seen = [], set()
	names = {}
	user_names = {}
	for doctype, label, ts, extra, title, status in ACTIVITY:
		f = list(extra)
		if doctype in (S.SALES_INVOICE, S.PAYMENT_ENTRY) and company:
			f.append(["company", "=", company])
		tfield = "customer" if title == "@customer" else title
		fields = ["name", ts, tfield, "modified_by", "owner", "creation", "modified"] + ([status] if status else [])
		fields = list(dict.fromkeys(fields))
		for r in C.rows(doctype, f, fields, f"{ts} desc", 6) or []:
			if label == "Application updated" and r.get("modified") and r.get("creation") and abs((r["modified"] - r["creation"]).total_seconds()) < 5:
				continue  # never edited after creation; already listed as created
			key = (doctype, r["name"], label)
			if key in seen:
				continue
			seen.add(key)
			uid = r.get("modified_by") if ts == "modified" else r.get("owner")
			if uid not in user_names:
				user_names[uid] = get_fullname(uid) if uid else None
			items.append({
				"doctype": doctype, "name": r["name"], "activity": label,
				"title": r.get(tfield) or r["name"], "title_is_customer_id": title == "@customer",
				"status": r.get(status) if status else None, "timestamp": r.get(ts), "user": user_names[uid],
			})
	cust_ids = list({i["title"] for i in items if i["title_is_customer_id"]})
	if cust_ids:
		for r in C.rows(S.CUSTOMER, [["name", "in", cust_ids]], ["name", "customer_name"], None, len(cust_ids)) or []:
			names[r["name"]] = r.get("customer_name")
	for i in items:
		if i.pop("title_is_customer_id"):
			i["title"] = names.get(i["title"]) or i["title"]
	items.sort(key=lambda x: x["timestamp"] or 0, reverse=True)
	return items[:limit]


# ====================================================================== pending tasks

def pending_tasks(company):
	td = str(getdate(today()))
	soon = str(add_days(getdate(today()), 30))
	tasks = []

	def add(key, label, priority, doctype, filters, rt, amount_field=None):
		a = C.aggregate(doctype, filters, c=("count", "name"), **({"s": ("sum", amount_field)} if amount_field else {}))
		if not a or not a["c"]:
			return
		tasks.append({"key": key, "label": label, "priority": priority, "count": int(a["c"]), "amount": a.get("s") if amount_field else None, "route": rt})

	inv = [["docstatus", "=", 1], ["company", "=", company], ["outstanding_amount", ">", 0]] if company else None
	add("review", "Applications awaiting review", "High", S.LOAN_APP, [["application_status", "in", ["Submitted", "Under Review"]]], route(S.LOAN_APP, application_status=["in", ["Submitted", "Under Review"]]), "loan_amount")
	add("docs", "Lenders asking for documents", "High", S.LENDER_APP, [["application_status", "=", "Documents Required"]], route(S.LENDER_APP, application_status="Documents Required"))
	add("await_disb", "Approved, awaiting disbursement", "High", S.LENDER_APP, [["application_status", "in", ["Approved", "Sanctioned"]]], route(S.LENDER_APP, application_status=["in", ["Approved", "Sanctioned"]]), "approved_amount")
	add("disb_failed", "Failed disbursements", "High", S.DISB, [["disbursement_status", "=", "Failed"]], route(S.DISB, disbursement_status="Failed"), "disbursement_amount")
	if inv:
		add("overdue", "Overdue invoices", "High", S.SALES_INVOICE, inv + [["due_date", "<", td]], route(S.SALES_INVOICE, company=company, docstatus=1, outstanding_amount=[">", 0], due_date=["<", td]), "outstanding_amount")
	add("lender_wait", "Awaiting lender decision", "Medium", S.LENDER_APP, [["application_status", "in", S.LAPP_AWAITING]], route(S.LENDER_APP, application_status=["in", S.LAPP_AWAITING]), "submitted_amount")
	add("disb_pending", "Disbursements pending", "Medium", S.DISB, [["disbursement_status", "=", "Pending"]], route(S.DISB, disbursement_status="Pending"), "disbursement_amount")
	add("comm_pending", "Commission not yet invoiced", "Medium", S.COMM, [["commission_status", "=", "Pending"]], route(S.COMM, commission_status="Pending"), "commission_amount")
	add("agreements", "Agreements ending within 30 days", "Medium", S.AGREEMENT, [["agreement_status", "=", "Active"], ["end_date", "between", [td, soon]]], route(S.AGREEMENT, agreement_status="Active", end_date=["between", [td, soon]]))
	add("drafts", "Draft applications to submit", "Low", S.LOAN_APP, [["application_status", "=", "Draft"]], route(S.LOAN_APP, application_status="Draft"), "loan_amount")
	if inv:
		add("unpaid", "Invoices awaiting payment", "Low", S.SALES_INVOICE, inv + [["due_date", ">=", td]], route(S.SALES_INVOICE, company=company, docstatus=1, outstanding_amount=[">", 0], due_date=[">=", td]), "outstanding_amount")
	order = {"High": 0, "Medium": 1, "Low": 2}
	tasks.sort(key=lambda t: (order[t["priority"]], -t["count"]))
	return tasks
