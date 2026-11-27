// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Loan Lead", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (frm.doc.lead_status === "Converted") {
			// Lead -> Customer -> Application(s)
			frappe.db.get_value("Loan Customer", { loan_lead: frm.doc.name }, "name").then((r) => {
				const cust = r.message && r.message.name;
				if (!cust) return;
				frm.add_custom_button(__("Open Loan Customer"), () => frappe.set_route("Form", "Loan Customer", cust)).addClass("btn-primary");
				frappe.db.get_list("Loan Application", { filters: { loan_lead: frm.doc.name }, fields: ["name"] }).then((apps) => {
					apps.forEach((a) => frm.add_custom_button(a.name, () => frappe.set_route("Form", "Loan Application", a.name),
						__("Loan Application")));
					if (!apps.length) {
						frm.add_custom_button(__("New Loan Application"), () => frappe.new_doc("Loan Application", {
							loan_customer: cust, loan_type: frm.doc.loan_type, requested_loan_amount: frm.doc.estimated_loan_amount }));
					}
				});
			});
			return;
		}
		if (["Not Interested", "Lost"].includes(frm.doc.lead_status)) return;
		frm.set_intro(__("Next: click <b>Convert to Customer</b>. It creates the customer and opens a new Loan Application filled from this lead."), "blue");
		frm.add_custom_button(__("Convert to Customer"), () => {
			frappe
				.call("dsa_loan.dsa_loan_portal.doctype.loan_lead.loan_lead.convert_to_customer", { lead: frm.doc.name })
				.then((r) => {
					frappe.show_alert({ message: __("Customer {0} ready - complete the loan application", [r.message]), indicator: "green" });
					frappe.new_doc("Loan Application", {
						loan_customer: r.message,
						loan_type: frm.doc.loan_type,
						requested_loan_amount: frm.doc.estimated_loan_amount,
					});
				});
		}).addClass("btn-primary");
	},
});
