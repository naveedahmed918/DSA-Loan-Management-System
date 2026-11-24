
# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime

from dsa_loan.dsa_loan_portal.utils import check_belongs, check_range


class CommissionSlabStructure(Document):
    """Commission structure for a lender, product and scheme."""

    def validate(self):
        check_range(self, "effective_from", "effective_to")

        check_belongs(
            "Loan Product",
            self.loan_product,
            "lender",
            self.lender,
            "Lender"
        )

        check_belongs(
            "Loan Scheme",
            self.loan_scheme,
            "loan_product",
            self.loan_product,
            "Loan Product"
        )

        self.validate_commission_slabs()
        self.validate_approval()

        if self.slab_status == "Active":
            self.validate_no_overlap()

    def validate_approval(self):
        """Enforce lender agreement and approval requirements."""

        if self.approval_status == "Approved":
            if not self.agreement_reference:
                frappe.throw(_("Agreement Reference is mandatory for approval."))

            if not self.agreement_document:
                frappe.throw(_("Agreement Document is mandatory for approval."))

            if not self.approved_by:
                self.approved_by = frappe.session.user

            if not self.approval_date:
                self.approval_date = now_datetime()

        else:
            if self.slab_status == "Active":
                frappe.throw(
                    _("Only an Approved commission structure can be Active.")
                )

            self.approved_by = None
            self.approval_date = None

    def validate_commission_slabs(self):
        """Validate amount ranges and commission values."""

        slabs = self.get("commission_slabs") or []

        if not slabs:
            frappe.throw(
                _("Please add at least one Commission Slab Detail.")
            )

        ordered_slabs = sorted(
            slabs,
            key=lambda row: flt(row.minimum_amount)
        )

        previous_slab = None

        for index, row in enumerate(ordered_slabs, start=1):

            minimum = flt(row.minimum_amount)
            maximum = flt(row.maximum_amount)
            percentage = flt(row.commission_percentage)
            fixed = flt(row.fixed_commission)

            if minimum < 0:
                frappe.throw(
                    _("Row {0}: Minimum Amount cannot be negative.").format(index)
                )

            if row.maximum_amount is not None and row.maximum_amount != "":
                if maximum <= minimum:
                    frappe.throw(
                        _("Row {0}: Maximum Amount must be greater than Minimum Amount.").format(index)
                    )
            else:
                maximum = None

            if percentage <= 0:
                frappe.throw(
                    _("Row {0}: Commission Percentage must be greater than zero.").format(index)
                )

            if previous_slab:
                previous_maximum = (
                    flt(previous_slab.maximum_amount)
                    if previous_slab.maximum_amount not in (None, "")
                    else None
                )

                if previous_maximum is None:
                    frappe.throw(
                        _("An unlimited slab must be the final amount range.")
                    )

                if minimum <= previous_maximum:
                    frappe.throw(
                        _("Commission amount ranges must not overlap. Check row {0}.").format(index)
                    )

            previous_slab = row

    def validate_no_overlap(self):
        """Prevent overlapping active structures for the same lender/product/scheme."""

        others = frappe.get_all(
            "Commission Slab Structure",
            filters={
                "slab_status": "Active",
                "lender": self.lender,
                "loan_product": self.loan_product or ("is", "not set"),
                "loan_scheme": self.loan_scheme or ("is", "not set"),
                "name": ("!=", self.name),
            },
            fields=["name", "effective_from", "effective_to"],
        )

        start = getdate(self.effective_from)
        end = getdate(self.effective_to) if self.effective_to else None

        for other in others:
            other_start = getdate(other.effective_from)
            other_end = (
                getdate(other.effective_to)
                if other.effective_to
                else None
            )

            if (
                (end is None or other_start <= end)
                and (other_end is None or start <= other_end)
            ):
                frappe.throw(
                    _("Active slab {0} already covers these dates for the same lender, product and scheme.").format(
                        other.name
                    )
                )


def find_structure(lender, loan_product, loan_scheme, on_date):
    """Find the most specific Active structure on a date."""

    scopes = []

    if loan_scheme:
        scopes.append({
            "loan_product": loan_product,
            "loan_scheme": loan_scheme
        })

    scopes.append({
        "loan_product": loan_product,
        "loan_scheme": ("is", "not set")
    })

    scopes.append({
        "loan_product": ("is", "not set"),
        "loan_scheme": ("is", "not set")
    })

    for scope in scopes:
        rows = frappe.get_all(
            "Commission Slab Structure",
            filters=dict(
                scope,
                slab_status="Active",
                approval_status="Approved",
                lender=lender,
                effective_from=("<=", on_date)
            ),
            or_filters=[
                ["effective_to", "is", "not set"],
                ["effective_to", ">=", on_date]
            ],
            pluck="name",
            order_by="effective_from desc",
            limit=1,
        )

        if rows:
            return rows[0]

    return None

