import frappe
from frappe import _

DOCTYPE = "DSA Customer"

def execute():
    """Idempotently simplify DSA Customer without deleting existing fields or records."""
    if not frappe.db.exists("DocType", DOCTYPE):
        frappe.throw(_("DocType {0} does not exist").format(DOCTYPE))

    doc = frappe.get_doc("DocType", DOCTYPE)
    existing = {f.fieldname for f in doc.fields}
    additions = [
        {"fieldname":"lead_management_section","label":"Lead Management","fieldtype":"Section Break"},
        {"fieldname":"customer_source","label":"Customer Source","fieldtype":"Select",
         "options":"Direct\nReferral\nWebsite\nSocial Media\nCampaign\nWalk-in\nOther",
         "default":"Direct"},
        {"fieldname":"customer_status","label":"Customer Status","fieldtype":"Select",
         "options":"Lead\nContacted\nQualified\nConverted\nLost","default":"Lead"},
        {"fieldname":"assigned_dsa","label":"Assigned DSA","fieldtype":"Link","options":"User"},
        {"fieldname":"profile_section","label":"Additional Customer Profile",
         "fieldtype":"Section Break","collapsible":1},
    ]
    for field in additions:
        if field["fieldname"] not in existing:
            doc.append("fields", field)

    for f in doc.fields:
        if f.fieldname in ("customer_name", "mobile_number"):
            f.reqd = 1
        elif f.fieldname in ("date_of_birth","gender","marital_status","address","city","pin_code"):
            f.reqd = 0

    preferred = [
        "customer_name","mobile_number","email_address",
        "lead_management_section","customer_source","customer_status","assigned_dsa",
        "profile_section","date_of_birth","gender","marital_status","address","city","pin_code"
    ]
    by_name = {f.fieldname:f for f in doc.fields}
    doc.fields = [by_name[n] for n in preferred if n in by_name] + [
        f for f in doc.fields if f.fieldname not in preferred
    ]
    doc.title_field = "customer_name"
    doc.track_changes = 1
    doc.save(ignore_permissions=True)

    script_path = frappe.get_app_path("dsa_loan", "patches", "customer_client_script.js")
    with open(script_path, encoding="utf-8") as handle:
        script = handle.read()
    client_name = "DSA Customer - Quick Registration"
    if frappe.db.exists("Client Script", client_name):
        cs = frappe.get_doc("Client Script", client_name)
        cs.script = script
        cs.enabled = 1
        cs.dt = DOCTYPE
        cs.save(ignore_permissions=True)
    else:
        frappe.get_doc({
            "doctype":"Client Script","name":client_name,"dt":DOCTYPE,
            "view":"Form","enabled":1,"script":script
        }).insert(ignore_permissions=True)

    frappe.clear_cache(doctype=DOCTYPE)
    frappe.db.commit()
    print("DSA Customer quick-registration patch applied; existing fields and records preserved.")
