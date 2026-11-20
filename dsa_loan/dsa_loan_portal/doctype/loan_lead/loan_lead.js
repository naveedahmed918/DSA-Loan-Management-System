// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Loan Lead", {
	refresh(frm) {
		if (!frm.is_new() && !["Converted", "Lost"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Convert to Application"), () => {
				frappe
					.call("dsa_loan.dsa_loan_portal.doctype.loan_lead.loan_lead.convert_to_application", {
						lead: frm.doc.name,
					})
					.then((r) => frappe.set_route("Form", "Loan Application", r.message));
			}).addClass("btn-primary");
		}
	},
});
