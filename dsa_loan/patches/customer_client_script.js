frappe.ui.form.on("DSA Customer", {
    validate(frm) {
        const raw = (frm.doc.mobile_number || "").trim();
        const mobile = raw.replace(/\D/g, "");
        if (mobile && !/^[6-9]\d{9}$/.test(mobile)) {
            frappe.throw(__("Enter a valid 10-digit Indian mobile number."));
        }
        const email = (frm.doc.email_address || "").trim();
        if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            frappe.throw(__("Enter a valid email address."));
        }
    },
    refresh(frm) {
        if (frm.is_new() && !frm.doc.assigned_dsa &&
            frappe.session.user && frappe.session.user !== "Administrator") {
            frm.set_value("assigned_dsa", frappe.session.user);
        }
    }
});