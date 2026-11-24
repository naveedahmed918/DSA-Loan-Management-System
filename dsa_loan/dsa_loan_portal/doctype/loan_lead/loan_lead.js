// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Loan Lead", {
	refresh(frm) {
		if (frm.is_new() || ["Converted", "Not Interested", "Lost"].includes(frm.doc.lead_status)) return;
		frm.add_custom_button(__("Convert to Customer"), () => {
			frappe
				.call("dsa_loan.dsa_loan_portal.doctype.loan_lead.loan_lead.convert_to_customer", { lead: frm.doc.name })
				.then((r) =>
					frappe.new_doc("Loan Application", {
						loan_lead: frm.doc.name,
						primary_customer: r.message,
						loan_type: frm.doc.loan_type,
						requested_loan_amount: frm.doc.estimated_loan_amount,
						company: frm.doc.assigned_company,
						dsa_branch: frm.doc.dsa_branch,
						assigned_agent: frm.doc.assigned_agent,
						branch_manager: frm.doc.branch_manager,
					})
				);
		}).addClass("btn-primary");
	},
});
