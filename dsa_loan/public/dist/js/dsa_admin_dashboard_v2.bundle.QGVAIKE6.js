(() => {
  // ../dsa_loan/dsa_loan/public/js/dsa_admin_dashboard_v2/util.js
  var P = {
    grid: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9"/><path d="M16 3.1a4 4 0 0 1 0 7.8"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>',
    "user-plus": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6M22 11h-6"/>',
    bank: '<path d="M3 21h18"/><path d="M5 21V10M10 21V10M14 21V10M19 21V10"/><path d="M12 3 21 8H3z"/>',
    file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    "file-plus": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M12 12v6M9 15h6"/>',
    send: '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
    wallet: '<path d="M20 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    percent: '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    mail: '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    chart: '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>',
    settings: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    bell: '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a2 2 0 0 0 3.4 0"/>',
    tasks: '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
    help: '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/>',
    chevron: '<path d="m6 9 6 6 6-6"/>',
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
    panel: '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M9 3v18"/>',
    box: '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
    receipt: '<path d="M4 2v20l3-2 3 2 2-2 2 2 3-2 3 2V2l-3 2-3-2-2 2-2-2-3 2z"/><path d="M8 9h8M8 13h6"/>',
    rupee: '<path d="M6 3h12M6 8h12M6 13l8.5 8M6 13h3a5 5 0 0 0 0-10"/>',
    logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5M21 12H9"/>',
    refresh: '<path d="M21 12a9 9 0 1 1-2.6-6.4L21 8"/><path d="M21 3v5h-5"/>',
    calendar: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    alert: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>',
    clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    x: '<path d="M18 6 6 18M6 6l12 12"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V2H6.5A2.5 2.5 0 0 0 4 4.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
    keyboard: '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M7 14h10"/>',
    inbox: '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.5 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.7 1.1z"/>',
    lock: '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    trend: '<path d="m22 7-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>',
    building: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>'
  };
  function icon(name, cls = "") {
    return `<svg class="dl-i ${cls}" viewBox="0 0 24 24" aria-hidden="true">${P[name] || P.grid}</svg>`;
  }
  var LOGO = `<svg viewBox="0 0 32 32" aria-hidden="true">
	<defs><linearGradient id="dl-lg" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#0F766E"/><stop offset="1" stop-color="#6FD3B4"/></linearGradient></defs>
	<circle cx="16" cy="16" r="14" fill="#E3F3EC"/>
	<path d="M6.5 21.5c4-.5 6.5-3.2 8-7 1.2-3 3.4-5 7.5-5.5" fill="none" stroke="url(#dl-lg)" stroke-width="3.2" stroke-linecap="round"/>
	<circle cx="22.8" cy="9.2" r="2.6" fill="#123C3A"/>
</svg>`;
  var COLORS = ["#0F766E", "#34A88A", "#D97706", "#71817B", "#123C3A", "#9AD4C0", "#DC2626", "#B7791F"];
  var esc = (v) => frappe.utils.escape_html(v == null ? "" : String(v));
  var currency = "INR";
  function set_currency(c) {
    currency = c || "INR";
  }
  var trim = (x) => x.toFixed(2).replace(/\.?0+$/, "");
  var SYM = { INR: "\u20B9", USD: "$", EUR: "\u20AC", GBP: "\xA3" };
  function money(v, compact = true) {
    if (v == null)
      return "\u2014";
    const n = Number(v) || 0;
    const sym = SYM[currency] || currency + " ";
    const a = Math.abs(n);
    const sign = n < 0 ? "-" : "";
    if (compact && currency === "INR") {
      if (a >= 1e7)
        return `${sign}${sym}${trim(a / 1e7)} Cr`;
      if (a >= 1e5)
        return `${sign}${sym}${trim(a / 1e5)} L`;
    }
    if (compact && currency !== "INR" && a >= 1e6)
      return `${sign}${sym}${trim(a / 1e6)}M`;
    return `${sign}${sym}${a.toLocaleString(currency === "INR" ? "en-IN" : void 0, { maximumFractionDigits: 0 })}`;
  }
  function money_full(v) {
    if (v == null)
      return "\u2014";
    const n = Number(v) || 0;
    return `${SYM[currency] || currency + " "}${n.toLocaleString(currency === "INR" ? "en-IN" : void 0, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
  function num(v) {
    if (v == null)
      return "\u2014";
    return (Number(v) || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 });
  }
  var fmt = (v, format) => format === "Currency" ? money(v) : num(v);
  var full = (v, format) => v == null ? "" : format === "Currency" ? money_full(v) : num(v);
  function clone(o) {
    return o ? JSON.parse(JSON.stringify(o)) : o;
  }
  function go(spec) {
    if (!spec)
      return;
    if (spec.doctype && !spec.route) {
      frappe.route_options = clone(spec.filters || {});
      frappe.set_route("List", spec.doctype);
      return;
    }
    if (spec.filters)
      frappe.route_options = clone(spec.filters);
    frappe.set_route(...spec.route);
  }
  var open_doc = (doctype, name) => frappe.set_route("Form", doctype, name);
  function pill(status) {
    if (!status)
      return "";
    const s = String(status);
    let c = "dl-info";
    if (/^(Disbursed|Paid|Processed|Approved|Sanctioned|Active|Completed|Receive)$/.test(s))
      c = "dl-ok";
    else if (/(Reject|Cancel|Fail|Overdue|Suspend|Terminat|Withdraw)/.test(s))
      c = "dl-bad";
    else if (/(Pending|Draft|Unpaid|Partial|Invoiced|Required|On Hold|Inactive|Expired|Review|Submitted)/.test(s))
      c = "dl-warn";
    return `<span class="dl-pill ${c}">${esc(__(s))}</span>`;
  }
  function store(key, value) {
    try {
      if (value === void 0)
        return JSON.parse(localStorage.getItem("dsa_dash_" + key));
      localStorage.setItem("dsa_dash_" + key, JSON.stringify(value));
    } catch (e) {
      return null;
    }
  }
  function initials(name) {
    const parts = String(name || "?").trim().split(/\s+/);
    return (esc(((parts[0] || "")[0] || "") + ((parts[1] || "")[0] || "")) || "?").toUpperCase();
  }
  function debounce(fn, ms) {
    let t;
    return (...a) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...a), ms);
    };
  }
  var empty = (msg, ic = "inbox") => `<div class="dl-empty">${icon(ic)}<span>${esc(msg)}</span></div>`;
  var unavailable = () => `<div class="dl-empty dl-locked">${icon("lock")}<span>${__("Unavailable")}</span><small>${__("You may not have access, or this module is not set up yet.")}</small></div>`;
  var allzero = (arrs) => arrs.every((a) => (a || []).every((v) => !v));
  function when(ts) {
    if (!ts)
      return "";
    try {
      return frappe.datetime.prettyDate(ts, true);
    } catch (e) {
      return String(ts);
    }
  }
  function spark(values, color = "#0F766E") {
    const v = (values || []).map((x) => Number(x) || 0);
    if (v.length < 2 || v.every((x) => !x))
      return `<svg class="dl-spark" viewBox="0 0 100 28" preserveAspectRatio="none"><line x1="0" y1="26" x2="100" y2="26" stroke="${color}" stroke-opacity=".25" stroke-width="1.5" stroke-dasharray="3 3"/></svg>`;
    const max = Math.max(...v);
    const pts = v.map((x, i) => `${(i / (v.length - 1) * 100).toFixed(1)},${(25 - x / max * 22).toFixed(1)}`);
    return `<svg class="dl-spark" viewBox="0 0 100 28" preserveAspectRatio="none"><polygon points="0,28 ${pts.join(" ")} 100,28" fill="${color}" fill-opacity=".12"/><polyline points="${pts.join(" ")}" fill="none" stroke="${color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>`;
  }

  // ../dsa_loan/dsa_loan/public/js/dsa_admin_dashboard_v2/shell.js
  var API = "dsa_loan.dashboard_v2.api.";
  var Shell = class {
    constructor(root, ctx, hooks) {
      this.root = root;
      this.ctx = ctx;
      this.hooks = hooks;
      this.expanded = new Set(store("expanded") || ["overview", "loans"]);
      this.active = "top";
      this.render_top();
      this.render_side();
      this.bind_global();
      this.refresh_notification_badge();
      if (store("collapsed"))
        this.set_collapsed(true);
    }
    render_top() {
      const c = this.ctx;
      const avatar = c.image ? `<img src="${esc(c.image)}" alt="">` : initials(c.full_name);
      this.top = this.root.querySelector(".dl-top");
      const pop = (name, label, ic, extra = "") => `<div class="dl-anchor ${extra}"><button class="dl-top-btn" data-toggle="${name}" title="${esc(label)}" aria-label="${esc(label)}">${icon(ic)}<span class="dl-badge" data-badge="${name}" hidden></span></button><div class="dl-pop" data-pop="${name}"></div></div>`;
      this.top.innerHTML = `
			<button class="dl-top-btn dl-burger" data-act="drawer" aria-label="${__("Menu")}">${icon("menu")}</button>
			<a class="dl-brand" href="/app/${esc(c.page)}" aria-label="DSA Loan Portal">
				<span class="dl-logo">${LOGO}</span>
				<span class="dl-brand-text"><b>DSA Loan Portal</b><small>${__("Admin console")}</small></span>
			</a>
			<div class="dl-search">
				<label class="dl-search-box">${icon("search")}
					<input type="search" placeholder="${__("Search customers, applications, lenders, products\u2026")}" aria-label="${__("Search")}" autocomplete="off">
					<kbd>Ctrl K</kbd>
				</label>
				<div class="dl-pop dl-pop-wide" data-pop="search" role="listbox"></div>
			</div>
			<div class="dl-top-actions">
				<div class="dl-anchor"><button class="dl-quick" data-toggle="quick">${icon("plus")}<span>${__("Quick create")}</span></button><div class="dl-pop" data-pop="quick"></div></div>
				${pop("tasks", __("Pending tasks"), "tasks")}
				${pop("notif", __("Notifications"), "bell")}
				${pop("help", __("Help and support"), "help", "dl-hide-sm")}
				${pop("settings", __("Settings"), "settings", "dl-hide-sm")}
				<div class="dl-anchor"><button class="dl-user" data-toggle="user" aria-label="${__("Account")}"><span class="dl-avatar">${avatar}</span><span class="dl-user-name">${esc(c.full_name)}</span></button><div class="dl-pop" data-pop="user"></div></div>
			</div>`;
      this.fill_static_pops();
      const input = this.search_input = this.top.querySelector(".dl-search input");
      input.addEventListener("input", debounce(() => this.search(input.value), 220));
      input.addEventListener("focus", () => input.value.trim().length >= 2 && this.search(input.value));
      input.addEventListener("keydown", (e) => this.search_keys(e));
      this.top.addEventListener("click", (e) => {
        const t = e.target.closest("[data-toggle]");
        if (t) {
          e.stopPropagation();
          this.toggle(t.dataset.toggle);
          return;
        }
        const a = e.target.closest('[data-act="drawer"]');
        if (a) {
          e.stopPropagation();
          this.root.classList.toggle("dl-drawer");
        }
      });
    }
    pop(name) {
      return this.top.querySelector(`[data-pop="${name}"]`);
    }
    menu(name, title, items) {
      const el = this.pop(name);
      el.innerHTML = (title ? `<div class="dl-pop-head">${esc(title)}</div>` : "") + items.map((it, i) => `<button class="dl-pop-item" data-mi="${i}">${icon(it[0])}${esc(it[1])}</button>`).join("");
      el.addEventListener("click", (e) => {
        const b = e.target.closest("[data-mi]");
        if (b) {
          this.close_pops();
          items[b.dataset.mi][2]();
        }
      });
    }
    fill_static_pops() {
      const c = this.ctx;
      const q = this.pop("quick");
      q.innerHTML = `<div class="dl-pop-head">${__("Create new")}</div>` + (c.quick_actions.length ? c.quick_actions.map((a, i) => `<button class="dl-pop-item" data-qa="${i}">${icon(a.icon)}${esc(__(a.label))}</button>`).join("") : `<div class="dl-pop-empty">${__("You cannot create records here")}</div>`);
      q.addEventListener("click", (e) => {
        const b = e.target.closest("[data-qa]");
        if (!b)
          return;
        this.close_pops();
        const a = c.quick_actions[b.dataset.qa];
        if (a.doctype)
          frappe.new_doc(a.doctype);
        else
          go({ route: a.route });
      });
      this.menu("help", __("Help & support"), [
        ["keyboard", __("Keyboard shortcuts"), () => frappe.ui.keys && frappe.ui.keys.show_keyboard_shortcut_dialog && frappe.ui.keys.show_keyboard_shortcut_dialog()],
        ["book", __("ERPNext documentation"), () => window.open("https://docs.erpnext.com", "_blank", "noopener")],
        ["help", __("About"), () => frappe.ui.misc && frappe.ui.misc.about && frappe.ui.misc.about()]
      ]);
      const st = [["user", __("My settings"), () => frappe.set_route("Form", "User", c.user)], ["moon", __("Switch theme"), () => new frappe.ui.ThemeSwitcher().show()]];
      if (c.is_system_manager) {
        st.push(["building", __("Companies"), () => frappe.set_route("List", "Company")]);
        st.push(["settings", __("System settings"), () => frappe.set_route("Form", "System Settings")]);
      }
      this.menu("settings", __("Settings"), st);
      this.menu("user", c.full_name, [
        ["user", __("My profile"), () => frappe.set_route("Form", "User", c.user)],
        ["grid", __("Desk home"), () => frappe.set_route("")],
        ["logout", __("Log out"), () => frappe.app.logout()]
      ]);
    }
    toggle(name) {
      const el = this.pop(name);
      const open = el.classList.contains("dl-open");
      this.close_pops();
      if (open)
        return;
      el.classList.add("dl-open");
      if (name === "notif")
        this.load_notifications();
      if (name === "tasks")
        this.draw_tasks();
    }
    close_pops() {
      this.top.querySelectorAll(".dl-pop.dl-open").forEach((p) => p.classList.remove("dl-open"));
    }
    async search(txt) {
      const el = this.pop("search");
      txt = (txt || "").trim();
      if (txt.length < 2)
        return el.classList.remove("dl-open");
      this.close_pops();
      el.classList.add("dl-open");
      el.innerHTML = `<div class="dl-pop-empty">${__("Searching\u2026")}</div>`;
      const seq = this.sseq = (this.sseq || 0) + 1;
      let rows = [];
      try {
        rows = await frappe.xcall(API + "search", { txt });
      } catch (e) {
        el.innerHTML = `<div class="dl-pop-empty">${__("Search failed")}</div>`;
        return;
      }
      if (seq !== this.sseq)
        return;
      this.results = rows;
      if (!rows.length) {
        el.innerHTML = `<div class="dl-pop-empty">${__("No matching records you can open")}</div>`;
        return;
      }
      let last = "";
      el.innerHTML = rows.map((r, i) => {
        const head = r.doctype !== last ? `<div class="dl-pop-head">${esc(__(r.doctype))}</div>` : "";
        last = r.doctype;
        return `${head}<button class="dl-pop-item dl-res" data-res="${i}"><span><b>${esc(r.title)}</b>${r.title !== r.name ? `<small>${esc(r.name)}</small>` : ""}</span>${r.sub ? `<em>${esc(r.sub)}</em>` : ""}</button>`;
      }).join("");
      this.sel = -1;
    }
    search_keys(e) {
      const items = [...this.pop("search").querySelectorAll("[data-res]")];
      if (e.key === "Escape") {
        this.close_pops();
        e.target.blur();
      } else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        if (!items.length)
          return;
        e.preventDefault();
        this.sel = (this.sel + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items.forEach((b, i) => b.classList.toggle("dl-sel", i === this.sel));
        items[this.sel].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter") {
        const r = this.results && this.results[items[this.sel] ? items[this.sel].dataset.res : 0];
        if (r)
          this.open_result(r);
      }
    }
    open_result(r) {
      this.close_pops();
      this.search_input.value = "";
      open_doc(r.doctype, r.name);
    }
    async load_notifications() {
      const el = this.pop("notif");
      el.innerHTML = `<div class="dl-pop-head">${__("Notifications")}</div><div class="dl-pop-empty">${__("Loading\u2026")}</div>`;
      try {
        const n = await frappe.xcall(API + "get_notifications");
        this.badge("notif", n.unread);
        el.innerHTML = `<div class="dl-pop-head">${__("Notifications")}</div>` + (n.items.length ? n.items.map((i) => `<button class="dl-pop-item dl-note ${i.read ? "" : "dl-unread"}" data-dt="${esc(i.document_type)}" data-dn="${esc(i.document_name)}"><span>${esc(i.subject)}<small>${esc(when(i.creation))}</small></span></button>`).join("") : `<div class="dl-pop-empty">${__("You are all caught up")}</div>`);
        el.onclick = (e) => {
          const b = e.target.closest("[data-dt]");
          if (b && b.dataset.dt && b.dataset.dn) {
            this.close_pops();
            open_doc(b.dataset.dt, b.dataset.dn);
          }
        };
      } catch (e) {
        el.innerHTML = `<div class="dl-pop-empty">${__("Could not load notifications")}</div>`;
      }
    }
    async refresh_notification_badge() {
      try {
        const n = await frappe.xcall(API + "get_notifications");
        this.badge("notif", n.unread);
      } catch (e) {
      }
    }
    badge(name, n) {
      const b = this.top.querySelector(`[data-badge="${name}"]`);
      if (!b)
        return;
      b.textContent = n > 99 ? "99+" : n;
      b.hidden = !n;
    }
    set_tasks(tasks) {
      this.tasks = tasks || [];
      this.badge("tasks", this.tasks.length);
      const b = this.top.querySelector('[data-badge="tasks"]');
      if (b)
        b.classList.toggle("dl-hot", this.tasks.some((t) => t.priority === "High"));
    }
    draw_tasks() {
      const el = this.pop("tasks");
      const t = this.tasks || [];
      el.innerHTML = `<div class="dl-pop-head">${__("Pending tasks")}</div>` + (t.length ? t.map((x, i) => `<button class="dl-pop-item" data-task="${i}"><i class="dl-dot dl-p-${x.priority.toLowerCase()}"></i><span>${esc(__(x.label))}</span><em>${x.count}</em></button>`).join("") : `<div class="dl-pop-empty">${__("Nothing needs attention")}</div>`);
      el.onclick = (e) => {
        const b = e.target.closest("[data-task]");
        if (b) {
          this.close_pops();
          go(t[b.dataset.task].route);
        }
      };
    }
    render_side() {
      this.side = this.root.querySelector(".dl-side");
      this.side.innerHTML = `
			<div class="dl-side-head"><label class="dl-find">${icon("search")}<input type="search" placeholder="${__("Find a page\u2026")}" aria-label="${__("Find a page")}"></label>
			<button class="dl-collapse" data-act="collapse" title="${__("Collapse sidebar")}" aria-label="${__("Collapse sidebar")}">${icon("panel")}</button></div>
			<nav class="dl-nav"></nav>`;
      this.nav = this.side.querySelector(".dl-nav");
      this.find = this.side.querySelector(".dl-find input");
      this.find.addEventListener("input", debounce(() => this.draw_nav(), 120));
      this.draw_nav();
      this.side.addEventListener("click", (e) => {
        if (e.target.closest('[data-act="collapse"]'))
          return this.set_collapsed(!this.root.classList.contains("dl-collapsed"));
        const g = e.target.closest("[data-group]");
        if (g) {
          if (this.root.classList.contains("dl-collapsed"))
            this.set_collapsed(false);
          const k = g.dataset.group;
          this.expanded.has(k) ? this.expanded.delete(k) : this.expanded.add(k);
          store("expanded", [...this.expanded]);
          return this.draw_nav();
        }
        const it = e.target.closest("[data-item]");
        if (!it)
          return;
        const [gi, ii] = it.dataset.item.split(":").map(Number);
        const item = this.ctx.sidebar[gi].items[ii];
        this.root.classList.remove("dl-drawer");
        if (item.anchor) {
          this.active = item.anchor;
          this.draw_nav();
          this.hooks.scroll_to(item.anchor);
        } else
          go(item);
      });
    }
    draw_nav() {
      const q = (this.find ? this.find.value : "").trim().toLowerCase();
      this.nav.innerHTML = this.ctx.sidebar.map((g, gi) => {
        const items = g.items.map((it, ii) => ({ it, ii })).filter(({ it }) => !q || it.label.toLowerCase().includes(q) || g.label.toLowerCase().includes(q));
        if (!items.length)
          return "";
        const open = q || this.expanded.has(g.key);
        return `<div class="dl-group ${open ? "dl-open" : ""}">
					<button class="dl-group-btn" data-group="${esc(g.key)}" title="${esc(__(g.label))}">${icon(g.icon)}<span>${esc(__(g.label))}</span>${icon("chevron", "dl-chev")}</button>
					<div class="dl-group-items">${items.map(({ it, ii }) => `<button class="dl-item ${it.anchor && it.anchor === this.active ? "dl-on" : ""}" data-item="${gi}:${ii}">${esc(__(it.label))}</button>`).join("")}</div></div>`;
      }).join("");
      if (!this.nav.innerHTML)
        this.nav.innerHTML = `<div class="dl-pop-empty">${__("No pages match")}</div>`;
    }
    set_collapsed(on) {
      this.root.classList.toggle("dl-collapsed", !!on);
      store("collapsed", !!on);
    }
    bind_global() {
      this.root.querySelector(".dl-scrim").addEventListener("click", () => this.root.classList.remove("dl-drawer"));
      this.top.querySelector(".dl-pop[data-pop=search]").addEventListener("click", (e) => {
        const b = e.target.closest("[data-res]");
        if (b)
          this.open_result(this.results[b.dataset.res]);
      });
      this.on_doc_click = (e) => {
        if (!this.root.isConnected)
          return document.removeEventListener("click", this.on_doc_click);
        if (!e.target.closest(".dl-anchor, .dl-search"))
          this.close_pops();
      };
      document.addEventListener("click", this.on_doc_click);
      this.on_key = (e) => {
        if (!this.root.isConnected)
          return document.removeEventListener("keydown", this.on_key);
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k" && document.body.classList.contains("dl-active")) {
          e.preventDefault();
          this.search_input.focus();
          this.search_input.select();
        } else if (e.key === "Escape")
          this.close_pops();
      };
      document.addEventListener("keydown", this.on_key);
    }
  };

  // ../dsa_loan/dsa_loan/public/js/dsa_admin_dashboard_v2/overview.js
  var KPI_STYLE = {
    applications: ["file", "#0F766E"],
    approved: ["check", "#16A34A"],
    disbursed: ["send", "#0F766E"],
    commission: ["percent", "#34A88A"],
    customers: ["users", "#0F766E"],
    pending: ["clock", "#D97706"],
    rejected: ["x", "#DC2626"],
    lenders: ["bank", "#123C3A"],
    active_lenders: ["bank", "#16A34A"],
    products: ["box", "#34A88A"]
  };
  var ACT_ICON = {
    "DSA Customer": "user-plus",
    "Loan Application": "file",
    "Lender Application": "send",
    "Lender Disbursement": "wallet",
    "Lender Commission Record": "percent",
    "Sales Invoice": "receipt",
    "Payment Entry": "rupee"
  };
  var PRESET_SHORT = { today: "Today", this_week: "Week", this_month: "Month", last_month: "Last month", this_quarter: "Quarter", this_year: "Year", custom: "Custom" };
  var dstr = (s) => new Date(s + "T00:00:00").toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
  var Overview = class {
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
        company: ctx.companies.includes(saved.company) ? saved.company : ctx.company
      };
      if (this.state.preset === "custom" && !(this.state.from && this.state.to))
        this.state.preset = ctx.default_preset;
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
    render_frame() {
      const c = this.ctx;
      const today = new Date();
      const long = today.toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
      const month = today.toLocaleDateString("en-IN", { month: "long", year: "numeric" });
      const seg = c.presets.map((p) => `<button class="${p.value === this.state.preset ? "dl-on" : ""}" data-preset="${p.value}">${esc(__(PRESET_SHORT[p.value] || p.label))}</button>`).join("");
      const comp = c.companies.length ? `<label class="dl-select" title="${__("Company for accounting figures")}">${icon("building")}<select data-company>${c.companies.map((n) => `<option ${n === this.state.company ? "selected" : ""}>${esc(n)}</option>`).join("")}</select></label>` : "";
      this.main.innerHTML = `
			<div class="dl-wrap">
			<section class="dl-head" data-anchor="top">
				<div>
					<div class="dl-eyebrow">${esc(long)} \xB7 ${esc(month)}</div>
					<h1>${__("Welcome back, {0}!", [esc(c.first_name || c.full_name)])}</h1>
					<p>${__("Here's an overview of your DSA business operations.")}</p>
				</div>
				<div class="dl-controls">
					${comp}
					<div class="dl-seg" role="group" aria-label="${__("Date range")}">${seg}</div>
					<div class="dl-custom" hidden>
						<input type="date" data-from value="${esc(this.state.from)}" aria-label="${__("From")}"><span>\u2192</span><input type="date" data-to value="${esc(this.state.to)}" aria-label="${__("To")}">
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
      if (on)
        this.main.querySelector("[data-error]").hidden = true;
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
      if (el)
        el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    render_quick() {
      const qa = this.ctx.quick_actions.slice(0, 5);
      this.main.querySelector("[data-quickrow]").innerHTML = qa.length ? `<span class="dl-quick-label">${__("Quick actions")}</span>` + qa.map((a, i) => `<button class="dl-chip" data-qa="${i}">${icon(a.icon)}${esc(__(a.label))}</button>`).join("") : "";
    }
    on_click(e) {
      const b = (sel) => {
        const el2 = e.target.closest(sel);
        return el2 && this.main.contains(el2) ? el2 : null;
      };
      let el;
      if (el = b("[data-preset]")) {
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
        if (!f || !t)
          return frappe.show_alert({ message: __("Choose both From and To dates"), indicator: "orange" });
        if (f > t)
          return frappe.show_alert({ message: __("From date must be on or before To date"), indicator: "red" });
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
      if (b("[data-refresh]"))
        return this.on_change();
      if (el = b("[data-qa]")) {
        const a = this.ctx.quick_actions[el.dataset.qa];
        return a.doctype ? frappe.new_doc(a.doctype) : go({ route: a.route });
      }
      if (el = b("[data-tab]")) {
        const [group, key] = el.dataset.tab.split(":");
        el.parentElement.querySelectorAll("button").forEach((x) => x.classList.toggle("dl-on", x === el));
        this.tab[group] = key;
        return this.render_tab(group);
      }
      if (el = b("[data-route]")) {
        try {
          return go(JSON.parse(el.dataset.route));
        } catch (err) {
          return;
        }
      }
      if (el = b("[data-open]"))
        return open_doc(el.dataset.open, el.dataset.name);
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
    render(resp) {
      this.resp = resp;
      this.tab = this.tab || { disb: "amount", ledger: null };
      const d = resp.data;
      this.d = d;
      this.set_loading(false);
      this.main.querySelector("[data-range]").innerHTML = `${icon("calendar")}<span>${dstr(resp.from_date)} \u2013 ${dstr(resp.to_date)}</span><i></i><span>${esc(resp.company || "")}</span>`;
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
      if (u && u.applications)
        notes.push(__("{0} loan application(s) have no application date and are not counted in date-filtered figures.", [u.applications]));
      if (u && u.commission)
        notes.push(__("{0} commission record(s) have no commission date and are not counted in date-filtered figures.", [u.commission]));
      this.main.querySelector("[data-foot]").innerHTML = notes.map((n) => `<p>${icon("alert")}${esc(n)}</p>`).join("") + `<p class="dl-muted">${__("Read-only view of live records. Figures respect your permissions.")}</p>`;
    }
    chart(key, el, cfg) {
      if (this.charts[key] && this.charts[key].destroy) {
        try {
          this.charts[key].destroy();
        } catch (e) {
        }
      }
      const n = cfg.data.labels.length;
      if (cfg.type === "bar" && n && n <= 3)
        cfg.barOptions = Object.assign({ spaceRatio: n === 1 ? 0.8 : 0.65 }, cfg.barOptions);
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
      if (!k)
        return el.innerHTML = unavailable();
      const sp = {
        applications: d.trends && d.trends.datasets[0].values,
        approved: d.trends && d.trends.datasets[1].values,
        disbursed: d.disbursements && d.disbursements.amount,
        commission: d.commission && d.commission.datasets[0].values
      };
      el.innerHTML = k.headline.map((x) => {
        const [ic, color] = KPI_STYLE[x.key] || ["chart", "#0F766E"];
        const na = x.value == null;
        const dl = x.delta;
        return `<button class="dl-hero-cell" ${na ? "disabled" : this.rt(x.route)}>
					<div class="dl-hero-top"><span class="dl-ico" style="--c:${color}">${icon(ic)}</span><span class="dl-hero-label">${esc(__(x.label))}</span></div>
					<div class="dl-hero-value" title="${esc(full(x.value, x.format))}">${na ? `<span class="dl-na">${__("Unavailable")}</span>` : esc(fmt(x.value, x.format))}</div>
					<div class="dl-hero-meta">${dl == null ? "" : `<span class="dl-delta ${dl >= 0 ? "dl-up" : "dl-down"}">${dl >= 0 ? "\u25B2" : "\u25BC"} ${Math.abs(dl)}%</span>`}<span>${esc(x.note || "")}</span></div>
					${spark(sp[x.key], color)}
				</button>`;
      }).join("");
    }
    render_tiles(k) {
      const el = this.sec("tiles");
      if (!k)
        return el.innerHTML = "";
      el.innerHTML = k.tiles.map((x) => {
        const [ic, color] = KPI_STYLE[x.key] || ["chart", "#0F766E"];
        const na = x.value == null;
        return `<button class="dl-tile" ${na ? "disabled" : this.rt(x.route)} style="--c:${color}">
					<span class="dl-ico">${icon(ic)}</span>
					<span class="dl-tile-body"><span class="dl-tile-label">${esc(__(x.label))}</span><b>${na ? "\u2014" : esc(fmt(x.value, x.format))}</b><small>${esc(na ? __("Unavailable") : x.note || "")}</small></span>
				</button>`;
      }).join("");
    }
    render_pipeline(p) {
      const el = this.sec("pipeline");
      if (!p)
        return el.innerHTML = unavailable();
      const first = (p.stages.find((s) => s.count) || {}).count || 0;
      const max = Math.max(1, ...p.stages.map((s) => s.count || 0));
      const t = p.timing || {};
      el.innerHTML = `
			<div class="dl-rail">${p.stages.map((s, i) => {
        const w = s.count == null ? 0 : Math.max(s.count ? 6 : 0, Math.round(s.count / max * 100));
        return `${i ? `<div class="dl-conv" title="${__("Conversion from previous stage")}">${s.conversion == null ? "\u2013" : s.conversion + "%"}</div>` : ""}
					<button class="dl-stage" ${s.count == null ? "disabled" : this.rt(s.route)}>
						<span class="dl-stage-n">${s.count == null ? "\u2014" : num(s.count)}</span>
						<span class="dl-stage-l">${esc(__(s.label))}</span>
						<span class="dl-track"><span style="width:${w}%"></span></span>
						<small>${s.now_label && s.now != null ? `${num(s.now)} ${esc(__(s.now_label))}` : "&nbsp;"}</small>
					</button>`;
      }).join("")}</div>
			<div class="dl-pipe-foot">
				<button class="dl-link" ${this.rt(p.side.route_rejected)}>${num(p.side.rejected)} ${__("rejected by lenders")}</button>
				<button class="dl-link" ${this.rt(p.side.route_withdrawn)}>${num(p.side.withdrawn)} ${__("withdrawn")}</button>
				<span>${icon("clock")}${t.application_to_submission == null ? "\u2014" : t.application_to_submission + " " + __("days")} ${__("application \u2192 submission")}</span>
				<span>${icon("clock")}${t.submission_to_sanction == null ? "\u2014" : t.submission_to_sanction + " " + __("days")} ${__("submission \u2192 sanction")}</span>
			</div>
			<p class="dl-note">${__("Counts are distinct loan applications; lender stages use the submission date, so a loan sent to several lenders counts once.")}</p>`;
      this.main.querySelector('[data-sub="pipeline"]').textContent = first ? __("{0} applications in period", [num(first)]) : "";
    }
    render_tasks(t) {
      const el = this.sec("tasks");
      const sub = this.main.querySelector('[data-sub="tasks"]');
      if (!t || !t.length) {
        sub.textContent = "";
        return el.innerHTML = empty(__("Nothing needs attention right now"), "check");
      }
      sub.textContent = __("{0} items", [t.length]);
      el.innerHTML = `<ul class="dl-tasks">${t.map((x) => `<li><button ${this.rt(x.route)}><i class="dl-dot dl-p-${x.priority.toLowerCase()}" title="${esc(__(x.priority))}"></i><span class="dl-task-l">${esc(__(x.label))}<small>${esc(__(x.priority))}${x.amount ? " \xB7 " + money(x.amount) : ""}</small></span><b>${num(x.count)}</b></button></li>`).join("")}</ul>`;
    }
    render_trends(t) {
      const el = this.sec("trends");
      if (!t)
        return el.innerHTML = unavailable();
      if (allzero(t.datasets.map((d) => d.values)))
        return el.innerHTML = empty(__("No applications in this period"));
      this.chart_card("trends", "trends", t, "bar", { colors: ["#0F766E", "#34A88A", "#DC2626", "#D97706"], axisOptions: { xIsSeries: 1 }, barOptions: { spaceRatio: 0.4 } });
    }
    render_status(s) {
      const el = this.sec("status");
      if (!s)
        return el.innerHTML = unavailable();
      if (!s.total)
        return el.innerHTML = empty(__("No applications in this period"));
      const colors = { Draft: "#9AD4C0", Submitted: "#34A88A", "Under Review": "#D97706", Approved: "#0F766E", Rejected: "#DC2626", Disbursed: "#123C3A" };
      el.innerHTML = `<div class="dl-donut"><div data-chart></div><ul class="dl-legend">${s.labels.map((l, i) => `<li><button ${this.rt({ doctype: "Loan Application", filters: { application_status: l, application_date: ["between", [this.resp.from_date, this.resp.to_date]] } })}><i style="background:${colors[l] || COLORS[i % COLORS.length]}"></i>${esc(__(l))}<b>${num(s.values[i])}</b></button></li>`).join("")}</ul></div>`;
      this.chart("status", el.querySelector("[data-chart]"), { type: "donut", height: 190, data: { labels: s.labels, datasets: [{ values: s.values }] }, colors: s.labels.map((l, i) => colors[l] || COLORS[i % COLORS.length]) });
    }
    render_types(t) {
      const el = this.sec("types");
      if (!t)
        return el.innerHTML = unavailable();
      if (!t.rows.length)
        return el.innerHTML = empty(__("No applications in this period"));
      const max = Math.max(...t.rows.map((r) => r.count));
      el.innerHTML = `<ul class="dl-bars">${t.rows.map((r, i) => `<li><button ${this.rt(r.route)}><span class="dl-bar-l">${esc(__(r.label))}<small>${r.amount ? money(r.amount) + " " + __("requested") : ""}</small></span><span class="dl-bar"><span style="width:${r.count / max * 100}%;background:${COLORS[i % COLORS.length]}"></span></span><b>${num(r.count)}</b></button></li>`).join("")}</ul>`;
    }
    render_lenders(L) {
      const el = this.sec("lenders");
      const sub = this.main.querySelector('[data-sub="lenders"]');
      if (!L)
        return el.innerHTML = unavailable();
      const T = L.totals;
      const rng = { between: ["between", L.range] };
      const maxS = Math.max(1, ...L.rows.map((r) => r.submissions));
      const typeChips = L.types.map((t) => `<button class="dl-chip dl-chip-static" ${this.rt({ doctype: "Lender", filters: t.type_id ? { lender_type: t.type_id } : {} })}>${esc(t.type)} <b>${t.count}</b></button>`).join("");
      sub.textContent = L.row_count > L.rows.length ? __("Top {0} of {1} lenders", [L.rows.length, L.row_count]) : "";
      el.innerHTML = `
			<div class="dl-lender-top">
				<div class="dl-mini"><b>${num(T.lenders)}</b><span>${__("Lenders")}</span></div>
				<div class="dl-mini"><b>${T.active == null ? "\u2014" : num(T.active)}</b><span>${__("Active")}</span></div>
				<div class="dl-mini"><b>${num(L.groups.banks)}</b><span>${__("Banks")}</span></div>
				<div class="dl-mini"><b>${num(L.groups.others)}</b><span>${__("NBFC & others")}</span></div>
				<div class="dl-mini"><b>${T.products == null ? "\u2014" : num(T.products)}</b><span>${__("Products")}${T.active_products != null ? ` \xB7 ${num(T.active_products)} ${__("active")}` : ""}</span></div>
				<div class="dl-types">${typeChips}</div>
			</div>
			${L.rows.length ? `<div class="dl-table-wrap"><table class="dl-table"><thead><tr><th>${__("Lender")}</th><th>${__("Type")}</th><th class="r">${__("Products")}</th><th class="r">${__("Submissions")}</th><th class="r">${__("Approved")}</th><th class="r">${__("Disbursed")}</th><th class="r">${__("Commission")}</th></tr></thead><tbody>${L.rows.map((r) => {
        const f = (extra) => ({ doctype: "Lender Application", filters: Object.assign({ lender: r.lender, submission_date: ["between", L.range] }, extra) });
        return `<tr>
								<td><button class="dl-link dl-strong" data-open="Lender" data-name="${esc(r.lender)}">${esc(r.lender_name)}</button>${r.status ? `<small>${pill(r.status)}</small>` : ""}</td>
								<td>${esc(r.lender_type_label || "\u2014")}</td>
								<td class="r"><button class="dl-link" ${this.rt({ doctype: "Lender Loan Product", filters: { lender: r.lender } })}>${num(r.products)}</button></td>
								<td class="r dl-barcell" style="--w:${r.submissions / maxS * 100}%"><button class="dl-link" ${this.rt(f({ application_status: ["not in", ["Draft", "Withdrawn"]] }))}>${num(r.submissions)}</button></td>
								<td class="r"><button class="dl-link" ${this.rt(f({ application_status: ["in", ["Approved", "Sanctioned", "Disbursed"]] }))}>${num(r.approved)}</button>${r.approved_amount ? `<small>${money(r.approved_amount)}</small>` : ""}</td>
								<td class="r"><button class="dl-link" ${this.rt({ doctype: "Lender Disbursement", filters: { lender: r.lender, disbursement_status: "Processed", disbursement_date: ["between", L.range] } })}>${money(r.disbursed)}</button><small>${num(r.disbursements)} ${__("loans")}</small></td>
								<td class="r">${money(r.commission)}</td></tr>`;
      }).join("")}</tbody></table></div>` : empty(__("No lenders yet"), "bank")}`;
    }
    render_tab(group) {
      if (group === "disb")
        this.render_disb(this.d.disbursements);
    }
    render_disb(dsb) {
      const el = this.sec("disb");
      if (!dsb)
        return el.innerHTML = unavailable();
      const mode = this.tab && this.tab.disb || "amount";
      const T = dsb.totals;
      const head = `<div class="dl-statline"><div><b>${money(T.amount)}</b><span>${__("disbursed")}</span></div><div><b>${num(T.count)}</b><span>${__("processed")}</span></div><div><b>${money(T.average)}</b><span>${__("average")}</span></div><div><b>${dsb.pending == null ? "\u2014" : num(dsb.pending)}</b><span>${__("pending now")}</span></div></div>`;
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
      if (!c)
        return el.innerHTML = unavailable();
      if (allzero(c.datasets.map((d) => d.values)))
        return el.innerHTML = empty(__("No commission recorded in this period"), "percent");
      el.innerHTML = `<div class="dl-chart-host" data-chart></div>${c.by_lender.length ? `<ul class="dl-rank">${c.by_lender.map((l) => `<li><span>${esc(l.lender)}</span><b>${money(l.amount)}</b></li>`).join("")}</ul>` : ""}`;
      this.chart("commission", el.querySelector("[data-chart]"), { type: "bar", height: 220, colors: ["#0F766E", "#16A34A", "#D97706"], data: { labels: c.labels, datasets: c.datasets }, barOptions: { spaceRatio: 0.4 } });
    }
    render_amounts(a) {
      const el = this.sec("amounts");
      if (!a)
        return el.innerHTML = unavailable();
      if (allzero(a.datasets.map((d) => d.values)))
        return el.innerHTML = empty(__("No lender submissions in this period"), "send");
      this.chart_card("amounts", "amounts", a, "bar", { colors: ["#9AD4C0", "#0F766E"], height: 240, barOptions: { spaceRatio: 0.4 } });
    }
    render_finance(f) {
      const el = this.sec("finance");
      const sub = this.main.querySelector('[data-sub="finance"]');
      if (!f)
        return el.innerHTML = unavailable();
      sub.textContent = f.company;
      const t = f.totals;
      const cell = (label, v, note) => `<div class="dl-fin-cell"><span>${esc(label)}</span><b>${v == null ? "\u2014" : money(v)}</b><small>${esc(note || "")}</small></div>`;
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
      if (host)
        this.chart("finance", host, { type: "bar", height: 200, colors: ["#0F766E", "#9AD4C0"], data: { labels: f.labels, datasets: f.datasets }, barOptions: { spaceRatio: 0.4 } });
    }
    render_activity(a) {
      const el = this.sec("activity");
      if (!a)
        return el.innerHTML = unavailable();
      if (!a.length)
        return el.innerHTML = empty(__("No activity yet"));
      el.innerHTML = `<ul class="dl-feed">${a.map((x) => `<li><button data-open="${esc(x.doctype)}" data-name="${esc(x.name)}"><span class="dl-ico dl-ico-sm">${icon(ACT_ICON[x.doctype] || "file")}</span><span class="dl-feed-b"><b>${esc(x.title)}</b><small>${esc(__(x.activity))} \xB7 ${esc(x.name)}${x.user ? " \xB7 " + esc(x.user) : ""}</small></span><span class="dl-feed-r">${pill(x.status)}<small>${esc(when(x.timestamp))}</small></span></button></li>`).join("")}</ul>`;
    }
    render_customers(c) {
      const el = this.sec("customers");
      if (!c)
        return el.innerHTML = unavailable();
      el.innerHTML = `<div class="dl-statline"><button class="dl-stat-btn" ${this.rt(c.route)}><b>${num(c.total)}</b><span>${__("total")}</span></button><button class="dl-stat-btn" ${this.rt({ doctype: "DSA Customer", filters: { creation: ["between", [this.resp.from_date, this.resp.to_date]] } })}><b>${num(c.new)}</b><span>${__("new in period")}</span></button></div>
			${allzero([c.values]) ? empty(__("No customers registered in this period"), "users") : `<div class="dl-chart-host" data-chart></div>`}
			${c.cities.length ? `<div class="dl-cities">${c.cities.map((x) => `<span>${esc(x.label)} <b>${num(x.count)}</b></span>`).join("")}</div>` : ""}`;
      const host = el.querySelector("[data-chart]");
      if (host)
        this.chart("customers", host, { type: "bar", height: 150, colors: ["#34A88A"], data: { labels: c.labels, datasets: [{ name: __("New customers"), values: c.values }] }, barOptions: { spaceRatio: 0.45 } });
    }
    render_ledger(k) {
      const el = this.sec("ledger");
      const tabs = this.main.querySelector('[data-tabs="ledger"]');
      if (!k) {
        tabs.innerHTML = "";
        return el.innerHTML = unavailable();
      }
      if (!this.tab.ledger || !k.sections.some((s) => s.key === this.tab.ledger))
        this.tab.ledger = k.sections[0].key;
      tabs.innerHTML = k.sections.map((s) => `<button class="${s.key === this.tab.ledger ? "dl-on" : ""}" data-tab="ledger:${s.key}">${esc(__(s.label))}</button>`).join("");
      this.render_tab_ledger();
    }
    render_tab_ledger() {
      const k = this.d.kpis;
      const sec = k.sections.find((s) => s.key === this.tab.ledger);
      this.sec("ledger").innerHTML = `<div class="dl-ledger">${sec.kpis.map((x) => {
        const na = x.value == null;
        return `<button class="dl-led" ${na || !x.route ? "disabled" : this.rt(x.route)}><span class="dl-led-l">${esc(__(x.label))}<small>${esc(na ? __("Unavailable") : x.note || "")}</small></span><b title="${esc(full(x.value, x.format))}">${na ? "\u2014" : esc(fmt(x.value, x.format))}</b></button>`;
      }).join("")}</div>`;
    }
  };
  var _render_tab = Overview.prototype.render_tab;
  Overview.prototype.render_tab = function(group) {
    if (group === "ledger")
      return this.render_tab_ledger();
    return _render_tab.call(this, group);
  };

  // ../dsa_loan/dsa_loan/public/js/dsa_admin_dashboard_v2.bundle.js
  var API2 = "dsa_loan.dashboard_v2.api.";
  var Dashboard = class {
    constructor(wrapper) {
      this.root = document.createElement("div");
      this.root.className = "dl-app";
      this.root.innerHTML = `
			<header class="dl-top"></header>
			<aside class="dl-side"></aside>
			<div class="dl-scrim"></div>
			<main class="dl-main"><div class="dl-boot"><span class="dl-spin"></span>${__("Loading dashboard\u2026")}</div></main>`;
      $(wrapper).empty().append(this.root);
      this.init();
    }
    async init() {
      try {
        this.ctx = await frappe.xcall(API2 + "get_context");
      } catch (e) {
        this.root.querySelector(".dl-main").innerHTML = `<div class="dl-fatal">${__("The dashboard could not start. Check that you are allowed to open it, then reload.")}</div>`;
        return;
      }
      set_currency(this.ctx.currency);
      this.overview = new Overview(this.root.querySelector(".dl-main"), this.ctx, () => this.load());
      this.shell = new Shell(this.root, this.ctx, { scroll_to: (a) => this.overview.scroll_to(a) });
      await this.load();
    }
    async load() {
      const seq = this.seq = (this.seq || 0) + 1;
      this.overview.set_loading(true);
      try {
        const resp = await frappe.xcall(API2 + "get_overview", this.overview.args());
        if (seq !== this.seq)
          return;
        set_currency(resp.currency);
        this.overview.render(resp);
        this.shell.set_tasks(resp.data.tasks || []);
        this.loaded_at = Date.now();
      } catch (e) {
        if (seq !== this.seq)
          return;
        this.overview.set_error();
      }
    }
    on_show() {
      if (this.loaded_at && Date.now() - this.loaded_at > 60 * 1e3)
        this.load();
      this.shell && this.shell.refresh_notification_badge();
    }
  };
  frappe.provide("dsa_loan.dashboard_v2");
  dsa_loan.dashboard_v2.Dashboard = Dashboard;
})();
//# sourceMappingURL=dsa_admin_dashboard_v2.bundle.QGVAIKE6.js.map
