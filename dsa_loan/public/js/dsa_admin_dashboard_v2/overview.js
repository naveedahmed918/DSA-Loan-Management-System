// Main content of the DSA Admin Dashboard: filters, key figures, pipeline, charts, tables, activity.
import { icon, esc, go, open_doc, store, fmt, full, money, num, pill, when, empty, unavailable, allzero, spark, COLORS, clone } from "./util";

const KPI_STYLE = {
	applications: ["file", "#0F766E"], approved: ["check", "#16A34A"], disbursed: ["send", "#0F766E"], commission: ["percent", "#34A88A"],
	customers: ["users", "#0F766E"], pending: ["clock", "#D97706"], rejected: ["x", "#DC2626"],
	lenders: ["bank", "#123C3A"], active_lenders: ["bank", "#16A34A"], products: ["box", "#34A88A"],
};
const ACT_ICON = {
	"DSA Customer": "user-plus", "Loan Application": "file", "Lender Application": "send", "Lender Disbursement": "wallet",
	"Lender Commission Record": "percent", "Sales Invoice": "receipt", "Payment Entry": "rupee",
};
const PRESET_SHORT = { today: "Today", this_week: "Week", this_month: "Month", last_month: "Last month", this_quarter: "Quarter", this_year: "Year", custom: "Custom" };

const dstr = (s) => new Date(s + "T00:00:00").toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });

export class Overview {
	constructor(main, ctx, on_change) {
		this.main = main;
		this.ctx = ctx;
		this.on_change = on_change;
		this.charts = {};
		const saved = store("range") || {};
		this.state = {
			preset: ctx.presets.some((p) => p.value === saved.preset) ? saved.preset : ctx.default_preset,
			from: saved.from || "",
			to: saved.to || "",
			company: ctx.companies.includes(saved.company) ? saved.company : ctx.company,
		};
		if (this.state.preset === "custom" && !(this.state.from && this.state.to)) this.state.preset = ctx.default_preset;
		this.render_frame();
		this.main.addEventListener("click", (e) => this.on_click(e));
		this.main.addEventListener("change", (e) => this.on_input(e));
	}

	args() {
		const a = { preset: this.state.preset, company: this.state.company };
		if (this.state.preset === "custom") {
			a.from_date = this.state.from;
			a.to_date = this.state.to;
		}
		return a;
	}

	// ------------------------------------------------------------------ frame
	render_frame() {
		const c = this.ctx;
		const today = new Date();
		const long = today.toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
		const month = today.toLocaleDateString("en-IN", { month: "long", year: "numeric" });
		const seg = c.presets.map((p) => `<button class="${p.value === this.state.preset ? "dl-on" : ""}" data-preset="${p.value}">${esc(__(PRESET_SHORT[p.value] || p.label))}</button>`).join("");
		const comp = c.companies.length
			? `<label class="dl-select" title="${__("Company for accounting figures")}">${icon("building")}<select data-company>${c.companies.map((n) => `<option ${n === this.state.company ? "selected" : ""}>${esc(n)}</option>`).join("")}</select></label>`
			: "";
		this.main.innerHTML = `
			<div class="dl-wrap">
			<section class="dl-head" data-anchor="top">
				<div>
					<div class="dl-eyebrow">${esc(long)} · ${esc(month)}</div>
					<h1>${__("Welcome back, {0}!", [esc(c.first_name || c.full_name)])}</h1>
					<p>${__("Here's an overview of your DSA business operations.")}</p>
				</div>
				<div class="dl-controls">
					${comp}
					<div class="dl-seg" role="group" aria-label="${__("Date range")}">${seg}</div>
					<div class="dl-custom" hidden>
						<input type="date" data-from value="${esc(this.state.from)}" aria-label="${__("From")}"><span>→</span><input type="date" data-to value="${esc(this.state.to)}" aria-label="${__("To")}">
						<button class="dl-btn" data-apply>${__("Apply")}</button>
					</div>
					<button class="dl-icon-btn" data-reset title="${__("Reset to this month")}" aria-label="${__("Reset filters")}">${icon("x")}</button>
					<button class="dl-icon-btn" data-refresh title="${__("Refresh")}" aria-label="${__("Refresh")}">${icon("refresh")}</button>
				</div>
			</section>
			<div class="dl-range-line" data-range></div>
			<div class="dl-alert" data-error hidden></div>
			<div class="dl-quick-row" data-quickrow></div>
			<section class="dl-hero" data-sec="hero">${this.skeleton(4)}</section>
			<section class="dl-tiles" data-sec="tiles">${this.skeleton(6, "dl-sk-sm")}</section>

			<div class="dl-grid dl-g-pipe" data-anchor="pipeline">
				<section class="dl-card"><header><h2>${__("Loan pipeline")}</h2><span class="dl-sub" data-sub="pipeline"></span></header><div data-sec="pipeline">${this.skeleton(1, "dl-sk-lg")}</div></section>
				<section class="dl-card"><header><h2>${__("Needs attention")}</h2><span class="dl-sub" data-sub="tasks"></span></header><div data-sec="tasks">${this.skeleton(1, "dl-sk-lg")}</div></section>
			</div>

			<div class="dl-grid dl-g-3">
				<section class="dl-card"><header><h2>${__("Application trend")}</h2></header><div data-sec="trends" class="dl-chart">${this.skeleton(1, "dl-sk-lg")}</div></section>
				<section class="dl-card"><header><h2>${__("Status mix")}</h2></header><div data-sec="status">${this.skeleton(1, "dl-sk-lg")}</div></section>
				<section class="dl-card"><header><h2>${__("Loan types")}</h2></header><div data-sec="types">${this.skeleton(1, "dl-sk-lg")}</div></section>
			</div>

			<section class="dl-card" data-anchor="lenders"><header><h2>${__("Lender performance")}</h2><span class="dl-sub" data-sub="lenders"></span></header><div data-sec="lenders">${this.skeleton(1, "dl-sk-lg")}</div></section>

			<div class="dl-grid dl-g-2" data-anchor="money">
				<section class="dl-card"><header><h2>${__("Disbursements")}</h2><div class="dl-tabs" data-tabs="disb"><button class="dl-on" data-tab="disb:amount">${__("Amount")}</button><button data-tab="disb:count">${__("Count")}</button><button data-tab="disb:average">${__("Average")}</button></div></header><div data-sec="disb">${this.skeleton(1, "dl-sk-lg")}</div></section>
				<section class="dl-card"><header><h2>${__("Commission")}</h2><span class="dl-sub">${__("Operational records")}</span></header><div data-sec="commission">${this.skeleton(1, "dl-sk-lg")}</div></section>
			</div>

			<div class="dl-grid dl-g-2">
				<section class="dl-card"><header><h2>${__("Submitted vs approved")}</h2><span class="dl-sub">${__("Lender submissions")}</span></header><div data-sec="amounts">${this.skeleton(1, "dl-sk-lg")}</div></section>
				<section class="dl-card" data-anchor="finance"><header><h2>${__("Financial overview")}</h2><span class="dl-sub" data-sub="finance"></span></header><div data-sec="finance">${this.skeleton(1, "dl-sk-lg")}</div></section>
			</div>

			<div class="dl-grid dl-g-act" data-anchor="activity">
				<section class="dl-card"><header><h2>${__("Recent activity")}</h2></header><div data-sec="activity">${this.skeleton(1, "dl-sk-lg")}</div></section>
				<section class="dl-card"><header><h2>${__("Customer overview")}</h2></header><div data-sec="customers">${this.skeleton(1, "dl-sk-lg")}</div></section>
			</div>

			<section class="dl-card"><header><h2>${__("All figures")}</h2><div class="dl-tabs" data-tabs="ledger"></div></header><div data-sec="ledger"></div></section>
			<footer class="dl-foot" data-foot></footer>
			</div>`;
		this.sync_custom();
		this.render_quick();
	}

	skeleton(n, cls = "") {
		return Array.from({ length: n }, () => `<div class="dl-sk ${cls}"></div>`).join("");
	}

	sec(name) {
		return this.main.querySelector(`[data-sec="${name}"]`);
	}

	set_loading(on) {
		this.main.classList.toggle("dl-loading", !!on);
		if (on) this.main.querySelector("[data-error]").hidden = true;
	}

	set_error() {
		this.set_loading(false);
		const e = this.main.querySelector("[data-error]");
		e.hidden = false;
		e.innerHTML = `${icon("alert")}<span>${__("Could not load the dashboard data.")}</span><button class="dl-btn" data-refresh>${__("Retry")}</button>`;
	}

	sync_custom() {
		this.main.querySelector(".dl-custom").hidden = this.state.preset !== "custom";
		this.main.querySelectorAll("[data-preset]").forEach((b) => b.classList.toggle("dl-on", b.dataset.preset === this.state.preset));
	}

	scroll_to(anchor) {
		const el = this.main.querySelector(`[data-anchor="${anchor}"]`);
		if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
	}

	render_quick() {
		const qa = this.ctx.quick_actions.slice(0, 5);
		this.main.querySelector("[data-quickrow]").innerHTML = qa.length
			? `<span class="dl-quick-label">${__("Quick actions")}</span>` + qa.map((a, i) => `<button class="dl-chip" data-qa="${i}">${icon(a.icon)}${esc(__(a.label))}</button>`).join("")
			: "";
	}

	// ------------------------------------------------------------------ events
	on_click(e) {
		const b = (sel) => {
			const el = e.target.closest(sel);
			return el && this.main.contains(el) ? el : null;
		};
		let el;
		if ((el = b("[data-preset]"))) {
			this.state.preset = el.dataset.preset;
			this.sync_custom();
			if (this.state.preset !== "custom") {
				this.persist();
				this.on_change();
			}
			return;
		}
		if (b("[data-apply]")) {
			const f = this.main.querySelector("[data-from]").value;
			const t = this.main.querySelector("[data-to]").value;
			if (!f || !t) return frappe.show_alert({ message: __("Choose both From and To dates"), indicator: "orange" });
			if (f > t) return frappe.show_alert({ message: __("From date must be on or before To date"), indicator: "red" });
			this.state.from = f;
			this.state.to = t;
			this.persist();
			return this.on_change();
		}
		if (b("[data-reset]")) {
			this.state = { preset: this.ctx.default_preset, from: "", to: "", company: this.ctx.company };
			this.main.querySelector("[data-company]") && (this.main.querySelector("[data-company]").value = this.ctx.company);
			this.sync_custom();
			this.persist();
			return this.on_change();
		}
		if (b("[data-refresh]")) return this.on_change();
		if ((el = b("[data-qa]"))) {
			const a = this.ctx.quick_actions[el.dataset.qa];
			return a.doctype ? frappe.new_doc(a.doctype) : go({ route: a.route });
		}
		if ((el = b("[data-tab]"))) {
			const [group, key] = el.dataset.tab.split(":");
			el.parentElement.querySelectorAll("button").forEach((x) => x.classList.toggle("dl-on", x === el));
			this.tab[group] = key;
			return this.render_tab(group);
		}
		if ((el = b("[data-route]"))) {
			try {
				return go(JSON.parse(el.dataset.route));
			} catch (err) {
				return;
			}
		}
		if ((el = b("[data-open]"))) return open_doc(el.dataset.open, el.dataset.name);
	}

	on_input(e) {
		if (e.target.matches("[data-company]")) {
			this.state.company = e.target.value;
			this.persist();
			this.on_change();
		}
	}

	persist() {
		store("range", { preset: this.state.preset, from: this.state.from, to: this.state.to, company: this.state.company });
	}

	rt(spec) {
		return spec ? ` data-route='${esc(JSON.stringify(spec))}'` : "";
	}

	// ------------------------------------------------------------------ render
	render(resp) {
		this.resp = resp;
		this.tab = this.tab || { disb: "amount", ledger: null };
		const d = resp.data;
		this.d = d;
		this.set_loading(false);
		this.main.querySelector("[data-range]").innerHTML = `${icon("calendar")}<span>${dstr(resp.from_date)} – ${dstr(resp.to_date)}</span><i></i><span>${esc(resp.company || "")}</span>`;
		this.render_hero(d.kpis, d);
		this.render_tiles(d.kpis);
		this.render_pipeline(d.pipeline);
		this.render_tasks(d.tasks);
		this.render_trends(d.trends);
		this.render_status(d.status);
		this.render_types(d.loan_types);
		this.render_lenders(d.lenders);
		this.render_tab("disb");
		this.render_commission(d.commission);
		this.render_amounts(d.amounts);
		this.render_finance(d.finance);
		this.render_activity(d.activities);
		this.render_customers(d.customers);
		this.render_ledger(d.kpis);
		const u = d.kpis && d.kpis.undated;
		const notes = [];
		if (u && u.applications) notes.push(__("{0} loan application(s) have no application date and are not counted in date-filtered figures.", [u.applications]));
		if (u && u.commission) notes.push(__("{0} commission record(s) have no commission date and are not counted in date-filtered figures.", [u.commission]));
		this.main.querySelector("[data-foot]").innerHTML = notes.map((n) => `<p>${icon("alert")}${esc(n)}</p>`).join("") + `<p class="dl-muted">${__("Read-only view of live records. Figures respect your permissions.")}</p>`;
	}

	chart(key, el, cfg) {
		if (this.charts[key] && this.charts[key].destroy) {
			try {
				this.charts[key].destroy();
			} catch (e) {
				/* ignore */
			}
		}
		const n = cfg.data.labels.length;
		if (cfg.type === "bar" && n && n <= 3) cfg.barOptions = Object.assign({ spaceRatio: n === 1 ? 0.8 : 0.65 }, cfg.barOptions);
		try {
			this.charts[key] = new frappe.Chart(el, Object.assign({ height: 250, animate: 0, truncateLegends: 1 }, cfg));
		} catch (err) {
			el.innerHTML = empty(__("The chart could not be drawn"));
		}
	}

	chart_card(sec, key, data, type = "bar", opts = {}) {
		const el = this.sec(sec);
		el.innerHTML = `<div class="dl-chart-host" data-chart></div>`;
		this.chart(key, el.querySelector("[data-chart]"), Object.assign({ type, data: { labels: data.labels, datasets: data.datasets }, colors: COLORS }, opts));
	}

	render_hero(k, d) {
		const el = this.sec("hero");
		if (!k) return (el.innerHTML = unavailable());
		const sp = {
			applications: d.trends && d.trends.datasets[0].values,
			approved: d.trends && d.trends.datasets[1].values,
			disbursed: d.disbursements && d.disbursements.amount,
			commission: d.commission && d.commission.datasets[0].values,
		};
		el.innerHTML = k.headline
			.map((x) => {
				const [ic, color] = KPI_STYLE[x.key] || ["chart", "#0F766E"];
				const na = x.value == null;
				const dl = x.delta;
				return `<button class="dl-hero-cell" ${na ? "disabled" : this.rt(x.route)}>
					<div class="dl-hero-top"><span class="dl-ico" style="--c:${color}">${icon(ic)}</span><span class="dl-hero-label">${esc(__(x.label))}</span></div>
					<div class="dl-hero-value" title="${esc(full(x.value, x.format))}">${na ? `<span class="dl-na">${__("Unavailable")}</span>` : esc(fmt(x.value, x.format))}</div>
					<div class="dl-hero-meta">${dl == null ? "" : `<span class="dl-delta ${dl >= 0 ? "dl-up" : "dl-down"}">${dl >= 0 ? "▲" : "▼"} ${Math.abs(dl)}%</span>`}<span>${esc(x.note || "")}</span></div>
					${spark(sp[x.key], color)}
				</button>`;
			})
			.join("");
	}

	render_tiles(k) {
		const el = this.sec("tiles");
		if (!k) return (el.innerHTML = "");
		el.innerHTML = k.tiles
			.map((x) => {
				const [ic, color] = KPI_STYLE[x.key] || ["chart", "#0F766E"];
				const na = x.value == null;
				return `<button class="dl-tile" ${na ? "disabled" : this.rt(x.route)} style="--c:${color}">
					<span class="dl-ico">${icon(ic)}</span>
					<span class="dl-tile-body"><span class="dl-tile-label">${esc(__(x.label))}</span><b>${na ? "—" : esc(fmt(x.value, x.format))}</b><small>${esc(na ? __("Unavailable") : x.note || "")}</small></span>
				</button>`;
			})
			.join("");
	}

	render_pipeline(p) {
		const el = this.sec("pipeline");
		if (!p) return (el.innerHTML = unavailable());
		const first = (p.stages.find((s) => s.count) || {}).count || 0;
		const max = Math.max(1, ...p.stages.map((s) => s.count || 0));
		const t = p.timing || {};
		el.innerHTML = `
			<div class="dl-rail">${p.stages
				.map((s, i) => {
					const w = s.count == null ? 0 : Math.max(s.count ? 6 : 0, Math.round((s.count / max) * 100));
					return `${i ? `<div class="dl-conv" title="${__("Conversion from previous stage")}">${s.conversion == null ? "–" : s.conversion + "%"}</div>` : ""}
					<button class="dl-stage" ${s.count == null ? "disabled" : this.rt(s.route)}>
						<span class="dl-stage-n">${s.count == null ? "—" : num(s.count)}</span>
						<span class="dl-stage-l">${esc(__(s.label))}</span>
						<span class="dl-track"><span style="width:${w}%"></span></span>
						<small>${s.now_label && s.now != null ? `${num(s.now)} ${esc(__(s.now_label))}` : "&nbsp;"}</small>
					</button>`;
				})
				.join("")}</div>
			<div class="dl-pipe-foot">
				<button class="dl-link" ${this.rt(p.side.route_rejected)}>${num(p.side.rejected)} ${__("rejected by lenders")}</button>
				<button class="dl-link" ${this.rt(p.side.route_withdrawn)}>${num(p.side.withdrawn)} ${__("withdrawn")}</button>
				<span>${icon("clock")}${t.application_to_submission == null ? "—" : t.application_to_submission + " " + __("days")} ${__("application → submission")}</span>
				<span>${icon("clock")}${t.submission_to_sanction == null ? "—" : t.submission_to_sanction + " " + __("days")} ${__("submission → sanction")}</span>
			</div>
			<p class="dl-note">${__("Counts are distinct loan applications; lender stages use the submission date, so a loan sent to several lenders counts once.")}</p>`;
		this.main.querySelector('[data-sub="pipeline"]').textContent = first ? __("{0} applications in period", [num(first)]) : "";
	}

	render_tasks(t) {
		const el = this.sec("tasks");
		const sub = this.main.querySelector('[data-sub="tasks"]');
		if (!t || !t.length) {
			sub.textContent = "";
			return (el.innerHTML = empty(__("Nothing needs attention right now"), "check"));
		}
		sub.textContent = __("{0} items", [t.length]);
		el.innerHTML = `<ul class="dl-tasks">${t
			.map((x) => `<li><button ${this.rt(x.route)}><i class="dl-dot dl-p-${x.priority.toLowerCase()}" title="${esc(__(x.priority))}"></i><span class="dl-task-l">${esc(__(x.label))}<small>${esc(__(x.priority))}${x.amount ? " · " + money(x.amount) : ""}</small></span><b>${num(x.count)}</b></button></li>`)
			.join("")}</ul>`;
	}

	render_trends(t) {
		const el = this.sec("trends");
		if (!t) return (el.innerHTML = unavailable());
		if (allzero(t.datasets.map((d) => d.values))) return (el.innerHTML = empty(__("No applications in this period")));
		this.chart_card("trends", "trends", t, "bar", { colors: ["#0F766E", "#34A88A", "#DC2626", "#D97706"], axisOptions: { xIsSeries: 1 }, barOptions: { spaceRatio: 0.4 } });
	}

	render_status(s) {
		const el = this.sec("status");
		if (!s) return (el.innerHTML = unavailable());
		if (!s.total) return (el.innerHTML = empty(__("No applications in this period")));
		const colors = { Draft: "#9AD4C0", Submitted: "#34A88A", "Under Review": "#D97706", Approved: "#0F766E", Rejected: "#DC2626", Disbursed: "#123C3A" };
		el.innerHTML = `<div class="dl-donut"><div data-chart></div><ul class="dl-legend">${s.labels
			.map((l, i) => `<li><button ${this.rt({ doctype: "Loan Application", filters: { application_status: l, application_date: ["between", [this.resp.from_date, this.resp.to_date]] } })}><i style="background:${colors[l] || COLORS[i % COLORS.length]}"></i>${esc(__(l))}<b>${num(s.values[i])}</b></button></li>`)
			.join("")}</ul></div>`;
		this.chart("status", el.querySelector("[data-chart]"), { type: "donut", height: 190, data: { labels: s.labels, datasets: [{ values: s.values }] }, colors: s.labels.map((l, i) => colors[l] || COLORS[i % COLORS.length]) });
	}

	render_types(t) {
		const el = this.sec("types");
		if (!t) return (el.innerHTML = unavailable());
		if (!t.rows.length) return (el.innerHTML = empty(__("No applications in this period")));
		const max = Math.max(...t.rows.map((r) => r.count));
		el.innerHTML = `<ul class="dl-bars">${t.rows
			.map((r, i) => `<li><button ${this.rt(r.route)}><span class="dl-bar-l">${esc(__(r.label))}<small>${r.amount ? money(r.amount) + " " + __("requested") : ""}</small></span><span class="dl-bar"><span style="width:${(r.count / max) * 100}%;background:${COLORS[i % COLORS.length]}"></span></span><b>${num(r.count)}</b></button></li>`)
			.join("")}</ul>`;
	}

	render_lenders(L) {
		const el = this.sec("lenders");
		const sub = this.main.querySelector('[data-sub="lenders"]');
		if (!L) return (el.innerHTML = unavailable());
		const T = L.totals;
		const rng = { between: ["between", L.range] };
		const maxS = Math.max(1, ...L.rows.map((r) => r.submissions));
		const typeChips = L.types.map((t) => `<button class="dl-chip dl-chip-static" ${this.rt({ doctype: "Lender", filters: t.type_id ? { lender_type: t.type_id } : {} })}>${esc(t.type)} <b>${t.count}</b></button>`).join("");
		sub.textContent = L.row_count > L.rows.length ? __("Top {0} of {1} lenders", [L.rows.length, L.row_count]) : "";
		el.innerHTML = `
			<div class="dl-lender-top">
				<div class="dl-mini"><b>${num(T.lenders)}</b><span>${__("Lenders")}</span></div>
				<div class="dl-mini"><b>${T.active == null ? "—" : num(T.active)}</b><span>${__("Active")}</span></div>
				<div class="dl-mini"><b>${num(L.groups.banks)}</b><span>${__("Banks")}</span></div>
				<div class="dl-mini"><b>${num(L.groups.others)}</b><span>${__("NBFC & others")}</span></div>
				<div class="dl-mini"><b>${T.products == null ? "—" : num(T.products)}</b><span>${__("Products")}${T.active_products != null ? ` · ${num(T.active_products)} ${__("active")}` : ""}</span></div>
				<div class="dl-types">${typeChips}</div>
			</div>
			${L.rows.length
				? `<div class="dl-table-wrap"><table class="dl-table"><thead><tr><th>${__("Lender")}</th><th>${__("Type")}</th><th class="r">${__("Products")}</th><th class="r">${__("Submissions")}</th><th class="r">${__("Approved")}</th><th class="r">${__("Disbursed")}</th><th class="r">${__("Commission")}</th></tr></thead><tbody>${L.rows
						.map((r) => {
							const f = (extra) => ({ doctype: "Lender Application", filters: Object.assign({ lender: r.lender, submission_date: ["between", L.range] }, extra) });
							return `<tr>
								<td><button class="dl-link dl-strong" data-open="Lender" data-name="${esc(r.lender)}">${esc(r.lender_name)}</button>${r.status ? `<small>${pill(r.status)}</small>` : ""}</td>
								<td>${esc(r.lender_type_label || "—")}</td>
								<td class="r"><button class="dl-link" ${this.rt({ doctype: "Lender Loan Product", filters: { lender: r.lender } })}>${num(r.products)}</button></td>
								<td class="r dl-barcell" style="--w:${(r.submissions / maxS) * 100}%"><button class="dl-link" ${this.rt(f({ application_status: ["not in", ["Draft", "Withdrawn"]] }))}>${num(r.submissions)}</button></td>
								<td class="r"><button class="dl-link" ${this.rt(f({ application_status: ["in", ["Approved", "Sanctioned", "Disbursed"]] }))}>${num(r.approved)}</button>${r.approved_amount ? `<small>${money(r.approved_amount)}</small>` : ""}</td>
								<td class="r"><button class="dl-link" ${this.rt({ doctype: "Lender Disbursement", filters: { lender: r.lender, disbursement_status: "Processed", disbursement_date: ["between", L.range] } })}>${money(r.disbursed)}</button><small>${num(r.disbursements)} ${__("loans")}</small></td>
								<td class="r">${money(r.commission)}</td></tr>`;
						})
						.join("")}</tbody></table></div>`
				: empty(__("No lenders yet"), "bank")}`;
	}

	render_tab(group) {
		if (group === "disb") this.render_disb(this.d.disbursements);
	}

	render_disb(dsb) {
		const el = this.sec("disb");
		if (!dsb) return (el.innerHTML = unavailable());
		const mode = (this.tab && this.tab.disb) || "amount";
		const T = dsb.totals;
		const head = `<div class="dl-statline"><div><b>${money(T.amount)}</b><span>${__("disbursed")}</span></div><div><b>${num(T.count)}</b><span>${__("processed")}</span></div><div><b>${money(T.average)}</b><span>${__("average")}</span></div><div><b>${dsb.pending == null ? "—" : num(dsb.pending)}</b><span>${__("pending now")}</span></div></div>`;
		if (!T.count) {
			el.innerHTML = head + empty(__("No processed disbursements in this period"), "send");
			return;
		}
		const color = mode === "count" ? "#34A88A" : mode === "average" ? "#D97706" : "#0F766E";
		el.innerHTML = head + `<div class="dl-chart-host" data-chart></div>${dsb.by_lender.length ? `<ul class="dl-rank">${dsb.by_lender.map((l) => `<li><span>${esc(l.lender)}</span><b>${money(l.amount)}</b><small>${num(l.count)}</small></li>`).join("")}</ul>` : ""}`;
		this.chart("disb", el.querySelector("[data-chart]"), { type: mode === "amount" ? "bar" : "line", height: 210, colors: [color], data: { labels: dsb.labels, datasets: [{ name: mode, values: dsb[mode] }] }, lineOptions: { regionFill: 1, hideDots: 0 }, barOptions: { spaceRatio: 0.45 } });
	}

	render_commission(c) {
		const el = this.sec("commission");
		if (!c) return (el.innerHTML = unavailable());
		if (allzero(c.datasets.map((d) => d.values))) return (el.innerHTML = empty(__("No commission recorded in this period"), "percent"));
		el.innerHTML = `<div class="dl-chart-host" data-chart></div>${c.by_lender.length ? `<ul class="dl-rank">${c.by_lender.map((l) => `<li><span>${esc(l.lender)}</span><b>${money(l.amount)}</b></li>`).join("")}</ul>` : ""}`;
		this.chart("commission", el.querySelector("[data-chart]"), { type: "bar", height: 220, colors: ["#0F766E", "#16A34A", "#D97706"], data: { labels: c.labels, datasets: c.datasets }, barOptions: { spaceRatio: 0.4 } });
	}

	render_amounts(a) {
		const el = this.sec("amounts");
		if (!a) return (el.innerHTML = unavailable());
		if (allzero(a.datasets.map((d) => d.values))) return (el.innerHTML = empty(__("No lender submissions in this period"), "send"));
		this.chart_card("amounts", "amounts", a, "bar", { colors: ["#9AD4C0", "#0F766E"], height: 240, barOptions: { spaceRatio: 0.4 } });
	}

	render_finance(f) {
		const el = this.sec("finance");
		const sub = this.main.querySelector('[data-sub="finance"]');
		if (!f) return (el.innerHTML = unavailable());
		sub.textContent = f.company;
		const t = f.totals;
		const cell = (label, v, note) => `<div class="dl-fin-cell"><span>${esc(label)}</span><b>${v == null ? "—" : money(v)}</b><small>${esc(note || "")}</small></div>`;
		el.innerHTML = `<div class="dl-fin">
			${cell(__("Invoiced"), t.invoiced, t.invoices == null ? "" : `${num(t.invoices)} ${__("invoices, incl. GST")}`)}
			${cell(__("Net revenue"), t.net_revenue, __("before GST, after credit notes"))}
			${cell(__("Payments received"), t.received, t.received_count == null ? "" : `${num(t.received_count)} ${__("entries")}`)}
			${cell(__("Outstanding receivables"), t.outstanding, t.unpaid_count == null ? "" : `${num(t.unpaid_count)} ${__("unpaid invoices")}`)}
			${cell(__("Overdue"), t.overdue, t.overdue_count == null ? "" : `${num(t.overdue_count)} ${__("invoices")}`)}
			${cell(__("Payables"), t.payables, __("unpaid purchase invoices"))}
			${cell(__("Payments made"), t.paid_out, "")}
			${cell(__("Credit notes"), t.credit_notes, __("in period"))}
		</div>
		${allzero(f.datasets.map((d) => d.values)) ? empty(__("No invoices or receipts in this period"), "receipt") : `<div class="dl-chart-host" data-chart></div>`}`;
		const host = el.querySelector("[data-chart]");
		if (host) this.chart("finance", host, { type: "bar", height: 200, colors: ["#0F766E", "#9AD4C0"], data: { labels: f.labels, datasets: f.datasets }, barOptions: { spaceRatio: 0.4 } });
	}

	render_activity(a) {
		const el = this.sec("activity");
		if (!a) return (el.innerHTML = unavailable());
		if (!a.length) return (el.innerHTML = empty(__("No activity yet")));
		el.innerHTML = `<ul class="dl-feed">${a
			.map((x) => `<li><button data-open="${esc(x.doctype)}" data-name="${esc(x.name)}"><span class="dl-ico dl-ico-sm">${icon(ACT_ICON[x.doctype] || "file")}</span><span class="dl-feed-b"><b>${esc(x.title)}</b><small>${esc(__(x.activity))} · ${esc(x.name)}${x.user ? " · " + esc(x.user) : ""}</small></span><span class="dl-feed-r">${pill(x.status)}<small>${esc(when(x.timestamp))}</small></span></button></li>`)
			.join("")}</ul>`;
	}

	render_customers(c) {
		const el = this.sec("customers");
		if (!c) return (el.innerHTML = unavailable());
		el.innerHTML = `<div class="dl-statline"><button class="dl-stat-btn" ${this.rt(c.route)}><b>${num(c.total)}</b><span>${__("total")}</span></button><button class="dl-stat-btn" ${this.rt({ doctype: "DSA Customer", filters: { creation: ["between", [this.resp.from_date, this.resp.to_date]] } })}><b>${num(c.new)}</b><span>${__("new in period")}</span></button></div>
			${allzero([c.values]) ? empty(__("No customers registered in this period"), "users") : `<div class="dl-chart-host" data-chart></div>`}
			${c.cities.length ? `<div class="dl-cities">${c.cities.map((x) => `<span>${esc(x.label)} <b>${num(x.count)}</b></span>`).join("")}</div>` : ""}`;
		const host = el.querySelector("[data-chart]");
		if (host) this.chart("customers", host, { type: "bar", height: 150, colors: ["#34A88A"], data: { labels: c.labels, datasets: [{ name: __("New customers"), values: c.values }] }, barOptions: { spaceRatio: 0.45 } });
	}

	render_ledger(k) {
		const el = this.sec("ledger");
		const tabs = this.main.querySelector('[data-tabs="ledger"]');
		if (!k) {
			tabs.innerHTML = "";
			return (el.innerHTML = unavailable());
		}
		if (!this.tab.ledger || !k.sections.some((s) => s.key === this.tab.ledger)) this.tab.ledger = k.sections[0].key;
		tabs.innerHTML = k.sections.map((s) => `<button class="${s.key === this.tab.ledger ? "dl-on" : ""}" data-tab="ledger:${s.key}">${esc(__(s.label))}</button>`).join("");
		this.render_tab_ledger();
	}

	render_tab_ledger() {
		const k = this.d.kpis;
		const sec = k.sections.find((s) => s.key === this.tab.ledger);
		this.sec("ledger").innerHTML = `<div class="dl-ledger">${sec.kpis
			.map((x) => {
				const na = x.value == null;
				return `<button class="dl-led" ${na || !x.route ? "disabled" : this.rt(x.route)}><span class="dl-led-l">${esc(__(x.label))}<small>${esc(na ? __("Unavailable") : x.note || "")}</small></span><b title="${esc(full(x.value, x.format))}">${na ? "—" : esc(fmt(x.value, x.format))}</b></button>`;
			})
			.join("")}</div>`;
	}
}

// ledger tab switching reuses the shared tab handler
const _render_tab = Overview.prototype.render_tab;
Overview.prototype.render_tab = function (group) {
	if (group === "ledger") return this.render_tab_ledger();
	return _render_tab.call(this, group);
};
