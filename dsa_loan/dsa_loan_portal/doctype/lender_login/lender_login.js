// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Lender Login", {
	setup(frm) {
		frm.set_query("lender_branch", () => ({ filters: { lender: frm.doc.lender, status: "Active" } }));
		frm.set_query("loan_product", () => ({ filters: { lender: frm.doc.lender, status: "Active" } }));
		frm.set_query("loan_scheme", () => ({
			filters: { loan_product: frm.doc.loan_product, status: "Active" },
		}));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Document Checklist"), () =>
			frappe.set_route("List", "Document Checklist", { lender_login: frm.doc.name })
		);
		frm.add_custom_button(__("Regenerate Checklist"), () =>
			frappe
				.call("dsa_loan.dsa_loan_portal.doctype.lender_login.lender_login.regenerate_checklist", {
					lender_login: frm.doc.name,
				})
				.then((r) => frappe.show_alert(__("{0} checklist items added", [r.message || 0])))
		);
		if (frm.doc.status === "Sanctioned") {
			frm.add_custom_button(__("New Disbursement"), () =>
				frappe.new_doc("Loan Disbursement", { lender_login: frm.doc.name })
			);
		}
	},
	lender(frm) {
		frm.set_value({ lender_branch: "", loan_product: "", loan_scheme: "" });
	},
	loan_product(frm) {
		frm.set_value("loan_scheme", "");
	},
});
