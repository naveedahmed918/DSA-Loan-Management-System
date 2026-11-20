// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Franchise Settlement", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Included Commissions"), () =>
			frappe.set_route("List", "Commission Calculation", { franchise_settlement: frm.doc.name })
		);
		frm.add_custom_button(__("Included Clawbacks"), () =>
			frappe.set_route("List", "Commission Clawback", { franchise_settlement: frm.doc.name })
		);
	},
});
