# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

from dsa_loan.dsa_loan_portal.doctype.commission_slab_structure.commission_slab_structure import find_structure


class CommissionCalculation(Document):

    def validate(self):
        disb = frappe.db.get_value(
            "Loan Disbursement",
            self.loan_disbursement,
            [
                "loan_application",
                "disbursement_status",
                "current_disbursement_amount",
                "disbursement_date"
            ],
            as_dict=True,
        )

        if not disb:
            frappe.throw(_("Loan Disbursement does not exist."))

        if disb.loan_application != self.loan_application:
            frappe.throw(
                _("Disbursement {0} belongs to {1}, not {2}.").format(
                    self.loan_disbursement,
                    disb.loan_application,
                    self.loan_application
                )
            )

        if disb.disbursement_status != "Confirmed":
            frappe.throw(
                _("Commission can only be calculated on a Confirmed disbursement.")
            )

        dup = frappe.db.get_value(
            "Commission Calculation",
            {
                "loan_disbursement": self.loan_disbursement,
                "calculation_status": ("!=", "Reversed"),
                "name": ("!=", self.name or "")
            },
        )

        if dup:
            frappe.throw(
                _("Disbursement {0} already has Commission Calculation {1}.").format(
                    self.loan_disbursement,
                    dup
                )
            )

        app = frappe.db.get_value(
            "Loan Application",
            self.loan_application,
            [
                "lender",
                "company",
                "franchise",
                "dsa_branch",
                "assigned_agent",
                "loan_product",
                "loan_scheme"
            ],
            as_dict=True,
        )

        if not app:
            frappe.throw(_("Loan Application does not exist."))

        self.lender = app.lender
        self.company = app.company
        self.franchise = app.franchise
        self.dsa_branch = app.dsa_branch
        self.assigned_agent = app.assigned_agent

        if not self.commission_slab:
            self.commission_slab = find_structure(
                app.lender,
                app.loan_product,
                app.loan_scheme,
                disb.disbursement_date
            )

        if not self.commission_slab:
            frappe.throw(
                _("No approved and active Commission Slab Structure found for {0} on {1}.").format(
                    app.lender,
                    disb.disbursement_date
                )
            )

        slab = frappe.get_doc(
            "Commission Slab Structure",
            self.commission_slab
        )

        if slab.lender != app.lender:
            frappe.throw(
                _("Selected Commission Structure belongs to another lender.")
            )

        if slab.slab_status != "Active":
            frappe.throw(_("Selected Commission Structure is not Active."))

        if slab.approval_status != "Approved":
            frappe.throw(_("Selected Commission Structure is not Approved."))

        if slab.calculation_basis != "Disbursed Amount":
            frappe.throw(
                _("Only Disbursed Amount calculation basis is supported.")
            )

        disbursement_date = getdate(disb.disbursement_date)

        if getdate(slab.effective_from) > disbursement_date:
            frappe.throw(
                _("Commission Structure is not effective on the disbursement date.")
            )

        if slab.effective_to and getdate(slab.effective_to) < disbursement_date:
            frappe.throw(
                _("Commission Structure has expired on the disbursement date.")
            )

        if slab.loan_product and slab.loan_product != app.loan_product:
            frappe.throw(
                _("Selected Commission Structure belongs to another Loan Product.")
            )

        if slab.loan_scheme and slab.loan_scheme != app.loan_scheme:
            frappe.throw(
                _("Selected Commission Structure belongs to another Loan Scheme.")
            )

        self.commission_basis_amount = flt(
            disb.current_disbursement_amount
        )

        if self.commission_basis_amount <= 0:
            frappe.throw(_("Disbursement amount must be greater than zero."))

        matching_slab = find_matching_commission_slab(
            slab,
            self.commission_basis_amount
        )

        if not matching_slab:
            frappe.throw(
                _("No commission amount slab matches the disbursement amount {0}.").format(
                    self.commission_basis_amount
                )
            )

        self.commission_percentage = flt(
            matching_slab.commission_percentage
        )

        if self.commission_percentage <= 0:
            frappe.throw(
                _("The selected commission slab must have a positive percentage.")
            )

        # Fixed commission is intentionally ignored.
        self.fixed_commission = 0

        self.calculate()

        if self.calculation_status == "Draft":
            self.calculation_status = "Calculated"





    def calculate(self):
        gross = (
            self.commission_basis_amount
            * self.commission_percentage
            / 100
        )

        self.gross_commission = flt(gross, 2)

        self.gst_amount = flt(
            self.gross_commission * flt(self.gst_rate) / 100,
            2
        )

        self.tds_amount = flt(
            self.gross_commission * flt(self.tds_rate) / 100,
            2
        )

        self.net_commission = flt(
            self.gross_commission
            + self.gst_amount
            - self.tds_amount
            - flt(self.other_deductions),
            2
        )

def find_matching_commission_slab(structure, amount):
    """Return the amount-based commission slab matching the full amount."""

    amount = flt(amount)

    for row in structure.commission_slabs:
        minimum = flt(row.minimum_amount)
        maximum_value = flt(row.maximum_amount)

        # Frappe stores an empty Currency value as 0.0.
        # Treat zero as an unlimited upper range.
        maximum = maximum_value if maximum_value > 0 else None

        if amount >= minimum and (
            maximum is None or amount <= maximum
        ):
            return row

    return None

