import frappe
from frappe.utils import flt
from .core import aggregate, grouped, recent, can_read, has_field

def _between(doctype, field, start, end):
    return [[field, "between", [str(start), str(end)]]] if has_field(doctype, field) else []

def _sum(doctype, field, filters=None):
    return aggregate(doctype, filters, f"sum({field})") if has_field(doctype, field) else None

def overview(start, end, company=None):
    period = {}
    period["customers"] = aggregate("Loan Customer")
    period["new_customers"] = aggregate("Loan Customer", _between("Loan Customer", "creation", start, end))
    period["applications"] = aggregate("Customer Loan Application")
    period["applications_period"] = aggregate("Customer Loan Application", _between("Customer Loan Application", "application_date", start, end))
    status = grouped("Customer Loan Application", [], "application_status")
    period["pending_applications"] = aggregate("Customer Loan Application", [["application_status", "in", ["Draft", "Submitted", "Under Review"]]])
    period["approved_applications"] = aggregate("Customer Loan Application", [["application_status", "in", ["Approved", "Disbursed"]]])
    period["rejected_applications"] = aggregate("Customer Loan Application", [["application_status", "=", "Rejected"]])
    period["requested_amount"] = _sum("Customer Loan Application", "loan_amount")

    period["lenders"] = aggregate("Lender")
    period["active_lenders"] = aggregate("Lender", [["lender_status", "=", "Active"]])
    period["products"] = aggregate("Lender Loan Product")
    period["active_products"] = aggregate("Lender Loan Product", [["is_active", "=", 1]])

    period["lender_submissions"] = aggregate("Lender Application")
    period["lender_approved"] = aggregate("Lender Application", [["application_status", "in", ["Approved", "Sanctioned", "Disbursed"]]])
    period["lender_pending"] = aggregate("Lender Application", [["application_status", "in", ["Submitted", "Under Review", "Documents Required"]]])

    period["disbursements"] = aggregate("Lender Disbursement", [["disbursement_status", "=", "Processed"]])
    period["disbursed_amount"] = _sum("Lender Disbursement", "disbursement_amount", [["disbursement_status", "=", "Processed"]])
    period["pending_disbursements"] = aggregate("Lender Disbursement", [["disbursement_status", "=", "Pending"]])

    period["commission_earned"] = _sum("Lender Commission Record", "commission_amount", [["commission_status", "!=", "Cancelled"]])
    period["commission_pending"] = _sum("Lender Commission Record", "commission_amount", [["commission_status", "in", ["Pending", "Invoiced", "Partially Paid"]]])
    period["commission_paid_records"] = aggregate("Lender Commission Record", [["commission_status", "=", "Paid"]])

    inv_filters = [["docstatus", "=", 1]]
    if company and frappe.db.exists("Company", company):
        inv_filters.append(["company", "=", company])
    period["sales_invoices"] = aggregate("Sales Invoice", inv_filters)
    period["invoice_total"] = _sum("Sales Invoice", "grand_total", inv_filters)
    period["invoice_outstanding"] = _sum("Sales Invoice", "outstanding_amount", inv_filters)

    pe_filters = [["docstatus", "=", 1], ["payment_type", "=", "Receive"]]
    if company and frappe.db.exists("Company", company):
        pe_filters.append(["company", "=", company])
    period["payments_received"] = _sum("Payment Entry", "paid_amount", pe_filters)

    lender_types = frappe.db.sql("""
    SELECT
        lt.type_name AS label,
        COUNT(l.name) AS value
    FROM `tabLender` l
    INNER JOIN `tabLender Type` lt
        ON l.lender_type = lt.name
    GROUP BY lt.type_name
    ORDER BY lt.type_name
""", as_dict=True)
    loan_types = grouped("Customer Loan Application", [], "loan_type")
    lender_status = grouped("Lender", [], "lender_status")
    lenders = recent("Lender", ["lender_name", "lender_type", "lender_status"], limit=8)
    activities = []
    for dt, fields in [
        ("Loan Customer", ["customer_name", "city", "creation"]),
        ("Customer Loan Application", ["customer", "loan_type", "application_status", "application_date"]),
        ("Lender Disbursement", ["lender", "disbursement_amount", "disbursement_status", "disbursement_date"]),
        ("Sales Invoice", ["customer", "grand_total", "status", "posting_date"]),
    ]:
        rows = recent(dt, fields, limit=4)
        if rows:
            for r in rows:
                activities.append({"doctype": dt, **r})
    activities.sort(key=lambda x: str(x.get("modified") or x.get("creation") or x.get("posting_date") or ""), reverse=True)

    return {
        "kpis": period, "application_status": status, "loan_types": loan_types,
        "lender_types": lender_types, "lender_status": lender_status,
        "lenders": lenders or [], "activities": activities[:10],
        "access": {dt: can_read(dt) for dt in [
            "Loan Customer", "Customer Loan Application", "Lender", "Lender Loan Product",
            "Lender Application", "Lender Disbursement", "Lender Commission Record",
            "Sales Invoice", "Payment Entry"
        ]},
        "range": {"from_date": str(start), "to_date": str(end)}
    }
