// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Franchise Settlement", {
	refresh(frm) {
		if (frm.doc.franchise && ["Draft", "Pending Approval"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Get Eligible Commissions"), () => {
				frappe
					.call("dsa_loan.dsa_loan_portal.doctype.franchise_settlement.franchise_settlement.get_settleable", {
						franchise: frm.doc.franchise,
					})
					.then((r) => {
						const have = new Set(
							(frm.doc.items || []).map((d) => d.commission_calculation || d.commission_clawback)
						);
						(r.message.calculations || [])
							.filter((c) => !have.has(c.name))
							.forEach((c) =>
								frm.add_child("items", { commission_calculation: c.name, gross_share: c.franchise_share_amount })
							);
						(r.message.clawbacks || [])
							.filter((c) => !have.has(c.name))
							.forEach((c) =>
								frm.add_child("items", { commission_clawback: c.name, deduction: c.franchise_recovery_amount })
							);
						frm.refresh_field("items");
						frm.dirty();
					});
			});
		}
	},
});
