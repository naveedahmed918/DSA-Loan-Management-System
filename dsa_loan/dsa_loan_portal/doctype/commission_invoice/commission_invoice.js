// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Commission Invoice", {
	setup(frm) {
		frm.set_query("commission_calculation", "items", () => ({
			filters: {
				lender: frm.doc.lender,
				status: ["in", ["Calculated", "Approved"]],
				commission_invoice: ["is", "not set"],
			},
		}));
	},
	refresh(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.lender && frm.doc.status === "Draft") {
			frm.add_custom_button(__("Get Commissions"), () => {
				frappe
					.call("dsa_loan.dsa_loan_portal.doctype.commission_invoice.commission_invoice.get_invoiceable_commissions", {
						lender: frm.doc.lender,
						period_from: frm.doc.period_from,
						period_to: frm.doc.period_to,
					})
					.then((r) => {
						const have = new Set((frm.doc.items || []).map((d) => d.commission_calculation));
						(r.message || [])
							.filter((c) => !have.has(c.name))
							.forEach((c) =>
								frm.add_child("items", {
									commission_calculation: c.name,
									loan_application: c.loan_application,
									taxable_amount: c.gross_commission,
									gst_amount: c.gst_amount,
								})
							);
						frm.refresh_field("items");
						frm.dirty();
					});
			});
		}
	},
});
