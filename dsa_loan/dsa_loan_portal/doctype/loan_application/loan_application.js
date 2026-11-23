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
		if (frm.doc.final_status === "Disbursed") {
			const call = (method, label) =>
				frappe.call({
					method: "dsa_loan.dsa_loan_portal.invoicing." + method,
					args: { application: frm.doc.name },
					freeze: true,
					freeze_message: label,
					callback: () => frm.reload_doc(),
				});
			if (!frm.doc.sales_invoice) {
				frm.add_custom_button(__("Create & Email Invoice"), () => call("create_and_send", __("Raising invoice...")), __("Lender Invoice"));
			} else {
				frm.add_custom_button(__("Send Invoice Email"), () => call("resend_email", __("Sending...")), __("Lender Invoice"));
				frm.add_custom_button(__("Open Sales Invoice"), () => frappe.set_route("Form", "Sales Invoice", frm.doc.sales_invoice), __("Lender Invoice"));
			}
			if (frm.doc.invoice_status) {
				const colour = { Emailed: "green", "Invoice Created": "blue", "Email Pending": "orange", "Awaiting Commission": "orange", Failed: "red" };
				frm.dashboard.add_indicator(__("Invoice: {0}", [__(frm.doc.invoice_status)]), colour[frm.doc.invoice_status] || "gray");
			}
		}
	},
	lender(frm) {
		frm.set_value({ lender_branch: "", loan_product: "", loan_scheme: "" });
	},
	loan_product(frm) {
		frm.set_value("loan_scheme", "");
	},
});
