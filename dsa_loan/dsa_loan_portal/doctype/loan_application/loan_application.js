// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Loan Application", {
	setup(frm) {
		frm.set_query("lender_branch", () => ({ filters: { lender: frm.doc.lender, is_active: 1 } }));
		frm.set_query("loan_product", () => ({ filters: { lender: frm.doc.lender, is_active: 1 } }));
		frm.set_query("loan_scheme", () => ({
			filters: { loan_product: frm.doc.loan_product, scheme_status: "Active" },
		}));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Document Checklist"), () =>
			frappe.set_route("List", "Document Checklist", { loan_application: frm.doc.name })
		);
		if (["Sanctioned", "Partially Disbursed"].includes(frm.doc.final_status)) {
			frm.add_custom_button(__("New Disbursement"), () =>
				frappe.new_doc("Loan Disbursement", { loan_application: frm.doc.name })
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
