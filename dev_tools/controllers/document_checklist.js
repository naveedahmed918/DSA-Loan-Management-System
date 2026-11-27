// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Document Checklist", {
	refresh(frm) {
		if (frm.is_new()) return;
		const rows = (frm.doc.documents || []).filter((r) => r.document_status !== "Not Applicable");
		const verified = rows.filter((r) => r.document_status === "Verified").length;
		const received = rows.filter((r) => r.document_status === "Received").length;
		frm.set_intro(__("{0} of {1} documents verified, {2} received and waiting to be verified. "
			+ "Attach each file to its row (the row becomes Received), check it, then mark it Verified.",
			[verified, rows.length, received]), verified === rows.length ? "green" : "blue");
		frm.add_custom_button(__("Back to Loan Application"), () =>
			frappe.set_route("Form", "Loan Application", frm.doc.loan_application));
		frm.add_custom_button(__("Applicant"), () => frappe.set_route("Form", "Loan Customer", frm.doc.applicant), __("Go to"));
		if (received) {
			frm.add_custom_button(__("Mark Received as Verified"), () =>
				frappe.call("dsa_loan.dsa_loan_portal.flow.verify_received", { checklist: frm.doc.name }).then((r) => {
					frappe.show_alert({ message: __("{0} rows verified", [r.message]), indicator: "green" });
					frm.reload_doc();
				}, () => frm.reload_doc())).addClass("btn-primary");
		}
	},
});

frappe.ui.form.on("Document Checklist Item", {
	document_file(frm, cdt, cdn) {
		// attaching a file marks a pending document as received
		const row = locals[cdt][cdn];
		if (row.document_file && row.document_status === "Pending") {
			frappe.model.set_value(cdt, cdn, "document_status", "Received");
		}
	},
});
