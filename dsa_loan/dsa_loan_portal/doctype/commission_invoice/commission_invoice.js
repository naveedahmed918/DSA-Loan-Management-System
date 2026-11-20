// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Commission Invoice", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Included Commissions"), () =>
				frappe.set_route("List", "Commission Calculation", { commission_invoice: frm.doc.name })
			);
		}
	},
});
