"""The DSA Commission Statement email now goes out with the lender's Sales Invoice PDF attached; add the
"invoice attached" line to the Email Template already installed (other edits to the template are kept)."""

import frappe

ANCHOR = "as per our agreed payout terms.</p>"
LINE = ('\n    {% if invoice_number %}<p style="margin:12px 0 0 0;">Our tax invoice <b>{{ invoice_number }}</b>'
        '{% if invoice_date %} dated {{ invoice_date }}{% endif %} for this commission is attached to this email as a PDF.</p>{% endif %}')


def execute():
	name = "DSA Commission Statement"
	if not frappe.db.exists("Email Template", name):
		return  # installed fresh from the HTML file, which already has the line
	html = frappe.db.get_value("Email Template", name, "response_html") or ""
	if "invoice_number" in html or ANCHOR not in html:
		return
	frappe.db.set_value("Email Template", name, "response_html", html.replace(ANCHOR, ANCHOR + LINE, 1))
