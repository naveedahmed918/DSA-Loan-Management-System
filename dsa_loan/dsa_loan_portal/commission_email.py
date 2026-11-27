"""Lender commission statement email: template + data.

The HTML lives in dsa_loan/templates/emails/lender_commission_statement.html and is installed (once, after migrate)
as the Email Template "DSA Commission Statement", so it can also be edited from Frappe (Email Template list).

get_context(commission_calculation) collects every placeholder from the system's own records: the Commission
Calculation (amounts and rates as calculated), its Loan Disbursement, Loan Application, Loan Customer, Lender,
Loan Product and Commission Slab, and the sending user's Employee record. Nothing is hard-coded; a value that is
not in the system is passed as None and the template leaves that row or line out.

Sending: when the lender's Sales Invoice is raised (invoicing.process), send_for_invoice emails one statement per
Commission Calculation on that invoice to the lender's Invoice Email Group, with the Sales Invoice PDF attached.
Each email is kept as a Communication on the Sales Invoice, linked to the Commission Calculation, Loan Application
and Lender. Without an outgoing Email Account (or recipients) the Communication is saved but not sent.
"""

import os
from decimal import ROUND_HALF_UP, Decimal

import frappe
from frappe import _
from frappe.utils import flt, formatdate, nowdate

TEMPLATE_NAME = "DSA Commission Statement"
SUBJECT = "DSA Commission Statement – {{ loan_application_id }} – {{ customer_name }}"
TEMPLATE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "templates", "emails", "lender_commission_statement.html")
DATE_FORMAT = "dd MMM yyyy"  # 27 Nov 2026


def install_template():
	"""after_migrate: create the Email Template from the HTML file if it does not exist yet (never overwrites edits)."""
	if frappe.db.exists("Email Template", TEMPLATE_NAME):
		return
	with open(TEMPLATE_FILE, encoding="utf-8") as f:
		html = f.read()
	frappe.get_doc({"doctype": "Email Template", "name": TEMPLATE_NAME, "subject": SUBJECT,
	                "use_html": 1, "response_html": html}).insert(ignore_permissions=True)


# ---------------------------------------------------------------- formatting

def inr(amount):
	"""Rupees with Indian digit grouping: 1234567.5 -> '₹12,34,567.50'. None -> None."""
	if amount is None:
		return None
	value = Decimal(str(flt(amount))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
	sign = "-" if value < 0 else ""
	whole, paise = f"{abs(value):.2f}".split(".")
	if len(whole) > 3:
		head, tail = whole[:-3], whole[-3:]
		groups = []
		while len(head) > 2:
			groups.insert(0, head[-2:])
			head = head[:-2]
		if head:
			groups.insert(0, head)
		whole = ",".join(groups + [tail])
	return f"{sign}₹{whole}.{paise}"


def pct(rate):
	"""0.35 -> '0.35%', 18 -> '18%'. Empty -> None."""
	if not flt(rate):
		return None
	return f"{flt(rate):.4f}".rstrip("0").rstrip(".") + "%"


def date(value):
	return formatdate(value, DATE_FORMAT) if value else None


# ---------------------------------------------------------------- data

def representative(user=None):
	"""Name, designation, email and phone of the person sending the statement (their Employee record if linked)."""
	user = user or frappe.session.user
	full_name, email = frappe.db.get_value("User", user, ["full_name", "email"]) or (None, None)
	emp = frappe.db.get_value("Employee", {"user_id": user, "status": "Active"},
	                          ["employee_name", "designation", "cell_number", "company_email"], as_dict=True) or {}
	return {
		"representative_name": emp.get("employee_name") or full_name,
		"representative_designation": emp.get("designation"),
		"representative_email": emp.get("company_email") or (email if email and "@" in email else None),
		"representative_phone": emp.get("cell_number"),
	}


def get_context(commission_calculation, user=None, **overrides):
	"""Every placeholder of the template, taken from the system's calculated data. `overrides` may set any key
	(for example representative_designation) when the system has no value for it."""
	calc = frappe.get_doc("Commission Calculation", commission_calculation)
	disb = frappe.db.get_value("Loan Disbursement", calc.loan_disbursement,
	                           ["disbursement_date", "current_disbursement_amount", "lender_reference_number"], as_dict=True)
	app = frappe.db.get_value("Loan Application", calc.loan_application,
	                          ["name", "loan_customer", "customer_name", "loan_product", "company", "sales_invoice"], as_dict=True)
	invoice = overrides.pop("invoice", None) or app.sales_invoice
	invoice_date = frappe.db.get_value("Sales Invoice", {"name": invoice, "docstatus": 1}, "posting_date") if invoice else None
	basis = frappe.db.get_value("Commission Slab Structure", calc.commission_slab, "calculation_basis") if calc.commission_slab else None
	fixed = flt(calc.fixed_commission) > 0

	ctx = {
		# loan disbursement details
		"dsa_company_name": app.company or calc.company,
		"lender_name": frappe.db.get_value("Lender", calc.lender, "lender_name") or calc.lender,
		"loan_application_id": app.name,
		"customer_name": app.customer_name or frappe.db.get_value("Loan Customer", app.loan_customer, "customer_name"),
		"loan_product": frappe.db.get_value("Loan Product", app.loan_product, "product_name") if app.loan_product else None,
		"loan_account_number": disb.lender_reference_number or None,  # the lender's loan account / reference, if recorded
		"disbursement_date": date(disb.disbursement_date),
		"disbursed_amount": inr(disb.current_disbursement_amount),
		# commission calculation details (as calculated and stored on the Commission Calculation)
		"commission_type": _("Fixed") if fixed else _("Percentage"),
		"commission_rate": None if fixed else pct(calc.commission_percentage),
		"commission_base": (f"{_(basis)} – {inr(calc.commission_basis_amount)}" if basis and basis != "Fixed Amount"
		                    else _("Fixed amount per disbursement") if fixed else inr(calc.commission_basis_amount)),
		"commission_base_label": (basis or "").lower() if basis and basis != "Fixed Amount" else None,
		"gross_commission": inr(calc.gross_commission),
		"gst_rate": pct(calc.gst_rate),
		"gst_amount": inr(calc.gst_amount),
		"tds_rate": pct(calc.tds_rate),
		"tds_amount": inr(calc.tds_amount),
		"other_adjustments": inr(calc.other_deductions),
		"net_commission": inr(calc.net_commission),
		"statement_date": date(nowdate()),
		# the lender's Sales Invoice (attached as PDF when the statement is sent)
		"invoice_number": invoice if invoice_date else None,
		"invoice_date": date(invoice_date),
		# raw values, for anyone reusing the context in another template
		"commission_calculation": calc.name,
		"loan_disbursement": calc.loan_disbursement,
	}
	ctx.update(representative(user))
	ctx.update(overrides)
	return ctx


def render(commission_calculation, user=None, **overrides):
	"""(subject, html) for one Commission Calculation, rendered from the Email Template."""
	install_template()
	template = frappe.get_doc("Email Template", TEMPLATE_NAME)
	ctx = get_context(commission_calculation, user, **overrides)
	body = template.response_html if template.use_html else template.response
	return frappe.render_template(template.subject, ctx), frappe.render_template(body or "", ctx)


@frappe.whitelist()
def preview(commission_calculation):
	"""Rendered subject and HTML for a Commission Calculation the user may read. Sends nothing."""
	frappe.has_permission("Commission Calculation", "read", commission_calculation, throw=True)
	subject, html = render(commission_calculation)
	return {"subject": subject, "html": html}


# ---------------------------------------------------------------- sending

def send_statement(commission_calculation, invoice):
	"""Email the statement for one Commission Calculation with the Sales Invoice `invoice` attached as PDF.
	Returns the Communication name."""
	from frappe.core.doctype.communication.email import _make

	from dsa_loan.dsa_loan_portal.invoicing import outgoing_account, recipients_for

	calc = frappe.db.get_value("Commission Calculation", commission_calculation,
	                           ["name", "lender", "loan_application"], as_dict=True)
	lender = frappe.get_doc("Lender", calc.lender)
	to, cc = recipients_for(lender)
	subject, html = render(calc.name, invoice=invoice)
	account = outgoing_account()
	comm = _make(
		doctype="Sales Invoice",  # the print of the reference document is what gets attached
		name=invoice,
		subject=subject,
		content=html,
		sender=account.email_id if account else None,
		recipients=to,
		cc=cc,
		send_email=bool(account and to),
		print_format=frappe.get_meta("Sales Invoice").default_print_format or "Standard",
		print_letterhead=True,
		email_template=TEMPLATE_NAME,
	)
	communication = frappe.get_doc("Communication", comm["name"])
	communication.add_link("Commission Calculation", calc.name)
	communication.add_link("Loan Application", calc.loan_application)
	communication.add_link("Lender", lender.name)
	communication.save(ignore_permissions=True)
	return communication.name


def send_for_invoice(app, invoice, lines):
	"""invoicing.process, right after the lender's Sales Invoice is raised: one statement per commission on it.
	A failure is logged and never stops the invoice."""
	sent = []
	for d in lines:
		try:
			sent.append(send_statement(d.calculation, invoice.name))
		except Exception:
			frappe.log_error(title=f"Commission statement email failed for {d.calculation}")
	if sent:
		frappe.msgprint(_("Commission statement emailed with invoice {0} attached.").format(invoice.name), alert=True)
	return sent
