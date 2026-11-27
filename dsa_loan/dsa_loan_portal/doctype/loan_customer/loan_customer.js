// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Loan Customer", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (frm.doc.loan_lead) {
			frm.add_custom_button(__("Loan Lead"), () => frappe.set_route("Form", "Loan Lead", frm.doc.loan_lead), __("Go to"));
		}
		frm.add_custom_button(__("New Loan Application"), () =>
			(frm.doc.loan_lead
				? frappe.db.get_value("Loan Lead", frm.doc.loan_lead, ["loan_type", "estimated_loan_amount"])
				: Promise.resolve({ message: {} })).then((r) => {
				const lead = r.message || {};
				frappe.new_doc("Loan Application", {
					loan_customer: frm.doc.name,
					dsa_branch: frm.doc.dsa_branch,
					loan_type: lead.loan_type,
					requested_loan_amount: lead.estimated_loan_amount,
				});
			}));
	},
});
