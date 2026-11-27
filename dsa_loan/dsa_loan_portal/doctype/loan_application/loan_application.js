// Copyright (c) 2026
// For license information, please see license.txt

// Guided flow: a progress bar at the top, one primary "next step" button (with a dialog for the fields that
// step needs), the other outcomes under "Set Status", and direct links to checklists, customers and disbursements.
const FLOW = "dsa_loan.dsa_loan_portal.flow.";
// Loan Purpose choices per Loan Type (same as LOAN_PURPOSES in loan_application.py)
const PURPOSES = {
	"Home Loan": ["Purchase - Ready Property", "Purchase - Under Construction", "Self Construction", "Extension / Renovation"],
	"Loan Against Property": ["Business Expansion", "Working Capital", "Education", "Medical", "Marriage",
		"Debt Consolidation", "Other Personal Need"],
	"Balance Transfer": ["Balance Transfer", "Balance Transfer + Top-up"],
	"Plot": ["Plot Purchase"],
	"Plot + Construction": ["Plot Purchase + Construction"],
};

function set_purposes(frm) {
	frm.set_df_property("loan_purpose", "options", [""].concat(PURPOSES[frm.doc.loan_type] || []));
}

const PATH = ["Draft", "Documents Pending", "Ready for Submission", "Submitted", "Under Review", "Sanctioned",
	"Partially Disbursed", "Disbursed"];

frappe.ui.form.on("Loan Application", {
	setup(frm) {
		frm.set_query("lender_branch", () => ({ filters: { lender: frm.doc.lender, is_active: 1 } }));
		frm.set_query("loan_product", () => ({ filters: { lender: frm.doc.lender, is_active: 1 } }));
		frm.set_query("loan_scheme", () => ({
			filters: { loan_product: frm.doc.loan_product, scheme_status: "Active" },
		}));
		// DSA Owned -> DSA branches (no franchise); franchise channels -> that franchise's branches
		frm.set_query("dsa_branch", () => ({
			filters: frm.doc.business_channel === "DSA Owned"
				? { franchise: ["is", "not set"], branch_status: "Active" }
				: { franchise: frm.doc.franchise || "-", branch_status: "Active" },
		}));
		frm.set_query("franchise", () => ({ filters: { franchise_status: "Active" } }));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		frappe.call({ method: FLOW + "application_flow", args: { application: frm.doc.name } }).then((r) => {
			const info = r.message || {};
			show_progress(frm, info);
			add_next_step(frm, info);
			add_documents(frm, info);
			add_other_outcomes(frm);
		});
	},
	lender(frm) {
		frm.set_value({ lender_branch: "", loan_product: "", loan_scheme: "" });
	},
	loan_product(frm) {
		frm.set_value("loan_scheme", "");
	},
	onload(frm) {
		set_purposes(frm);
	},
	loan_type(frm) {
		set_purposes(frm);
		if (!(PURPOSES[frm.doc.loan_type] || []).includes(frm.doc.loan_purpose)) frm.set_value("loan_purpose", "");
	},
	dsa_branch(frm) {
		// Branch Manager and Assigned Agent follow the branch (its Branch Manager / Branch Agent)
		if (!frm.doc.dsa_branch) return;
		frappe.db.get_value("DSA Branch", frm.doc.dsa_branch, ["branch_manager", "default_agent"]).then((r) => {
			const b = r.message || {};
			frm.set_value({ branch_manager: b.branch_manager || "", assigned_agent: b.default_agent || "" });
		});
	},
	business_channel(frm) {
		frm.set_value({ franchise: "", dsa_branch: "" });
	},
	franchise(frm) {
		frm.set_value("dsa_branch", "");
	},
});

function money(v) {
	return format_currency(v || 0, "INR", 0);
}

function show_progress(frm, info) {
	const at = PATH.indexOf(frm.doc.final_status);
	const steps = PATH.map((s, i) => {
		const style = i < at ? "color: var(--green-600)" : i === at ? "font-weight: 700; color: var(--text-color)" : "color: var(--text-muted)";
		return `<span style="${style}">${i < at ? "&#10003; " : ""}${__(s)}</span>`;
	}).join(' <span class="text-muted">&rsaquo;</span> ');
	const lines = [at >= 0 ? steps : `<b>${__(frm.doc.final_status)}</b>`];

	const docs = (info.checklists || []).map((c) => {
		const done = c.total && c.verified === c.total;
		const flag = c.attention ? ` <span style="color: var(--red-500)">(${c.attention} to fix)</span>` : "";
		return `<a href="/app/document-checklist/${c.name}">${frappe.utils.escape_html(c.customer_name)}</a>: `
			+ `<span style="color: var(--${done ? "green-600" : "orange-500"})">${c.verified}/${c.total} verified</span>${flag}`;
	});
	if (docs.length) lines.push(`<b>${__("Documents")}</b> &nbsp;${docs.join(" &nbsp;|&nbsp; ")}`);

	if (frm.doc.sanctioned_amount) {
		const comm = (info.commissions || []).reduce((t, c) => t + (c.gross_commission || 0), 0);
		lines.push(`<b>${__("Money")}</b> &nbsp;${__("Sanctioned")} ${money(frm.doc.sanctioned_amount)} &nbsp;|&nbsp; `
			+ `${__("Disbursed")} ${money(info.disbursed)} &nbsp;|&nbsp; ${__("Commission")} ${money(comm)}`);
	}
	frm.set_intro(lines.join("<br>"), "blue");
}

function set_status(frm, status, values) {
	// Saved on the server through the controller, so every rule still applies. Unsaved edits are saved first.
	const go = () => frappe.db.set_value("Loan Application", frm.doc.name, Object.assign({}, values || {}, { final_status: status }))
		.then(() => frm.reload_doc(), () => frm.reload_doc());
	return frm.is_dirty() ? frm.save().then(go) : go();
}

// Move to `status` using the values already on the form. `fields` are the details that step needs: the ones still
// empty get their default; only the required ones that are still empty are asked for, once, in a small dialog.
function step_using_form(frm, title, fields, status, primary) {
	const values = {};
	const missing = [];
	fields.forEach((f) => {
		if (frm.doc[f.fieldname]) return;
		if (f.reqd) missing.push(f);
		else if (f.default !== undefined && f.default !== null && f.default !== "") values[f.fieldname] = f.default;
	});
	if (!missing.length) return set_status(frm, status, values);
	const d = new frappe.ui.Dialog({
		title,
		fields: [{ fieldtype: "HTML", options: `<p class="text-muted">${__(
			"Fill this once here (or in the Lender Processing section of the form); it will not be asked again.")}</p>` }]
			.concat(missing),
		primary_action_label: primary || __("Save"),
		primary_action(v) {
			d.hide();
			set_status(frm, status, Object.assign(values, v));
		},
	});
	d.show();
}

function ask(frm, title, fields, status, primary) {
	const d = new frappe.ui.Dialog({
		title,
		fields,
		primary_action_label: primary || __("Save"),
		primary_action(values) {
			d.hide();
			if (status) set_status(frm, status, values);
		},
	});
	d.show();
	return d;
}

function add_next_step(frm, info) {
	const s = frm.doc.final_status;
	const today = frappe.datetime.get_today();
	const steps = {
		"Draft": [__("Next: Documents Pending"), () => set_status(frm, "Documents Pending")],
		"Documents Pending": [__("Next: Ready for Submission"), () => set_status(frm, "Ready for Submission")],
		"Ready for Submission": [__("Next: Submit to Lender"), () => step_using_form(frm, __("Submit to {0}", [frm.doc.lender]), [
			{ fieldname: "lender_application_number", label: __("Lender Application Number"), fieldtype: "Data", reqd: 1 },
			{ fieldname: "lender_submission_date", label: __("Lender Submission Date"), fieldtype: "Date", default: today },
		], "Submitted", __("Submit"))],
		"Submitted": [__("Next: Under Review"), () => set_status(frm, "Under Review")],
		"Query Raised": [__("Query answered: back to Under Review"), () => set_status(frm, "Under Review")],
		"On Hold": [__("Resume: back to Under Review"), () => set_status(frm, "Under Review")],
		"Under Review": [__("Next: Sanctioned"), () => step_using_form(frm, __("Sanction details"), [
			{ fieldname: "sanction_date", label: __("Sanction Date"), fieldtype: "Date", reqd: 1, default: today },
			{ fieldname: "sanctioned_amount", label: __("Sanctioned Amount"), fieldtype: "Currency", reqd: 1,
				default: frm.doc.requested_loan_amount },
			{ fieldname: "sanctioned_interest_rate", label: __("Sanctioned Interest Rate"), fieldtype: "Percent",
				default: frm.doc.expected_interest_rate },
			{ fieldname: "sanctioned_tenure_months", label: __("Sanctioned Tenure (Months)"), fieldtype: "Int",
				default: frm.doc.requested_tenure_months },
			{ fieldname: "sanction_valid_until", label: __("Sanction Valid Until"), fieldtype: "Date",
				default: frappe.datetime.add_days(today, 90) },
		], "Sanctioned", __("Sanction"))],
		"Sanctioned": [__("Record Disbursement"), () => disburse(frm, info)],
		"Partially Disbursed": [__("Record Next Disbursement"), () => disburse(frm, info)],
	};
	const step = steps[s];
	if (step) frm.add_custom_button(step[0], step[1]).addClass("btn-primary");
}

function disburse(frm, info) {
	const d = ask(frm, __("Record disbursement {0}", [info.next_number]), [
		{ fieldname: "help", fieldtype: "HTML", options: `<p class="text-muted">${__(
			"Saved as Confirmed: the bank has released this money. The commission is created now; when the loan is fully "
			+ "disbursed (nothing left of the sanctioned amount) the GST invoice is raised and emailed to the lender's invoice "
			+ "email group.")}</p>` },
		{ fieldname: "amount", label: __("Amount Released"), fieldtype: "Currency", reqd: 1, default: info.balance },
		{ fieldname: "disbursement_date", label: __("Disbursement Date"), fieldtype: "Date", reqd: 1,
			default: frappe.datetime.get_today() },
		{ fieldname: "payment_mode", label: __("Payment Mode"), fieldtype: "Select",
			options: ["", "NEFT", "RTGS", "IMPS", "Cheque", "Other"], default: "RTGS" },
		{ fieldname: "payment_reference", label: __("Payment Reference (UTR)"), fieldtype: "Data" },
		{ fieldname: "beneficiary_name", label: __("Beneficiary Name"), fieldtype: "Data" },
	], null, __("Record"));
	d.set_primary_action(__("Record"), (values) => {
		d.hide();
		frappe.call({
			method: FLOW + "record_disbursement",
			args: { application: frm.doc.name, values },
			freeze: true,
			freeze_message: __("Recording disbursement, commission and invoice..."),
		}).then((r) => {
			frappe.show_alert({ message: __("Disbursement {0} recorded", [r.message]), indicator: "green" });
			frm.reload_doc();
		}, () => frm.reload_doc());
	});
}

function add_documents(frm, info) {
	const lists = info.checklists || [];
	if (lists.length === 1) {
		frm.add_custom_button(__("Document Checklist"), () => frappe.set_route("Form", "Document Checklist", lists[0].name));
	} else {
		lists.forEach((c) => frm.add_custom_button(c.customer_name, () =>
			frappe.set_route("Form", "Document Checklist", c.name), __("Documents")));
	}
	if (frm.doc.loan_lead) {
		frm.add_custom_button(__("Loan Lead"), () => frappe.set_route("Form", "Loan Lead", frm.doc.loan_lead), __("Go to"));
	}
	frm.add_custom_button(__("Loan Customer"), () => frappe.set_route("Form", "Loan Customer", frm.doc.loan_customer),
		__("Go to"));
	if (frm.doc.franchise) {
		frm.add_custom_button(__("Franchise"), () => frappe.set_route("Form", "Franchise", frm.doc.franchise), __("Go to"));
	}
	(info.tranches || []).forEach((t) => frm.add_custom_button(__("Disbursement {0} ({1})", [t.disbursement_number, __(t.disbursement_status)]),
		() => frappe.set_route("Form", "Loan Disbursement", t.name), __("Go to")));
	(info.commissions || []).forEach((c) => frm.add_custom_button(__("Commission {0}", [c.name]),
		() => frappe.set_route("Form", "Commission Calculation", c.name), __("Go to")));
}

function add_other_outcomes(frm) {
	const s = frm.doc.final_status;
	const confirm = (question, status) => frappe.confirm(question, () => set_status(frm, status));
	const group = __("Set Status");
	if (["Submitted", "Under Review"].includes(s)) {
		frm.add_custom_button(__("Query Raised"), () => confirm(__("Mark this application Query Raised?"), "Query Raised"), group);
	}
	if (["Documents Pending", "Ready for Submission", "Submitted", "Under Review", "Query Raised", "Sanctioned"].includes(s)) {
		frm.add_custom_button(__("On Hold"), () => confirm(__("Put this application On Hold?"), "On Hold"), group);
		frm.add_custom_button(__("Rejected"), () => step_using_form(frm, __("Rejected by lender"), [
			{ fieldname: "rejection_reason", label: __("Rejection Reason"), fieldtype: "Small Text", reqd: 1 }], "Rejected"), group);
		frm.add_custom_button(__("Withdrawn"), () => confirm(__("Mark this application Withdrawn by the customer?"), "Withdrawn"), group);
	}
	if (s === "Disbursed") {
		frm.add_custom_button(__("Closed (loan repaid / foreclosed)"), () => ask(frm, __("Close the loan"), [
			{ fieldname: "help", fieldtype: "HTML", options: `<p class="text-muted">${__(
				"If this is within the lender's clawback window, a Commission Clawback and a Credit Note are created.")}</p>` },
			], "Closed", __("Close Loan")), group);
	}
}
