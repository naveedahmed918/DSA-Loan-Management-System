// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("DSA Branch", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("New Loan Lead"), () => frappe.new_doc("Loan Lead")).addClass("btn-primary");
		if (frm.doc.franchise) {
			frm.add_custom_button(__("Franchise"), () => frappe.set_route("Form", "Franchise", frm.doc.franchise), __("Go to"));
		}
	},
});
