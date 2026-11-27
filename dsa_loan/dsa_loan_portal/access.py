"""Roles and branch / franchise data separation.

Roles (9)
---------
DSA side
  DSA Admin                 head office: masters (lenders, products, schemes, branches, franchises); sees every branch
    DSA Operations Manager  runs loan operations across every branch (DSA and franchise): leads, customers,
                            applications, documents and disbursements; reads commission, payouts and settlements
    DSA Accounts           disbursements, commissions, invoices, payouts and franchise settlements; every branch
    Document Verifier       verifies document checklists and extracted document data
    DSA Branch Manager      runs a DSA branch: leads, customers, applications, documents; sends loans to the lender
      DSA Agent             creates leads, customers, applications and uploads documents in a DSA branch
Franchise side
  Franchise Partner         franchise owner: works and watches all of their franchise's branches; reads their settlements
    Franchise Branch Manager  runs one franchise branch (same work as a DSA Branch Manager, no lender commission)
      Franchise Agent         creates leads, customers, applications and uploads documents in a franchise branch

Which role can do what on each DocType is set in the DocType permissions (tools/generate_doctypes.py, ACCESS).

Data separation
---------------
A user only sees records of the DSA Branches they are given (a User Permission on DSA Branch). Every
customer-facing DocType carries a dsa_branch link, so Frappe filters lists, reports and links automatically.
Franchise users also get a User Permission on their Franchise, so they see only their franchise and settlements.
DSA branch roles may only be given DSA branches; franchise roles only their franchise's branches.
Users without any DSA Branch User Permission (e.g. head office) see every branch.
"""

import frappe
from frappe import _

ROLES = [
	"DSA Admin", "DSA Operations Manager", "DSA Accounts", "Document Verifier", "DSA Branch Manager", "DSA Agent",
	"Franchise Partner", "Franchise Branch Manager", "Franchise Agent",
]
DSA_BRANCH_ROLES = ("DSA Branch Manager", "DSA Agent")
FRANCHISE_ROLES = ("Franchise Partner", "Franchise Branch Manager", "Franchise Agent")
RETIRED_ROLES = ("Branch Manager",)  # replaced by DSA Branch Manager / Franchise Branch Manager


def create_roles():
	"""Make sure the app's 8 roles exist and the retired ones are gone. Runs on install and before every migrate."""
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)
	for role in RETIRED_ROLES:
		if frappe.db.exists("Role", role) and not frappe.db.exists("Has Role", {"role": role, "parenttype": "User"}):
			frappe.db.delete("Custom DocPerm", {"role": role})
			frappe.delete_doc("Role", role, force=True, ignore_permissions=True)


def _allow(user, doctype, value):
	if not frappe.db.exists("User Permission", {"user": user, "allow": doctype, "for_value": value}):
		frappe.get_doc(
			{"doctype": "User Permission", "user": user, "allow": doctype, "for_value": value, "apply_to_all_doctypes": 1}
		).insert(ignore_permissions=True)


@frappe.whitelist()
def grant_branch_access(user, dsa_branch=None, franchise=None):
	"""Limit `user` to one DSA Branch, or to a Franchise and all of its branches. Can be called again to add more."""
	frappe.only_for(("System Manager", "DSA Admin"))
	if not (dsa_branch or franchise):
		frappe.throw(_("Give a DSA Branch or a Franchise."))
	roles = set(frappe.get_roles(user))
	branch_franchise = frappe.db.get_value("DSA Branch", dsa_branch, "franchise") if dsa_branch else None
	if roles & set(DSA_BRANCH_ROLES) and (franchise or branch_franchise):
		frappe.throw(_("{0} has a DSA branch role; give a DSA-owned branch, not a franchise's.").format(user))
	if roles & set(FRANCHISE_ROLES):
		if dsa_branch and not branch_franchise:
			frappe.throw(_("{0} has a franchise role; give one of the franchise's branches.").format(user))
		if dsa_branch:  # one franchise branch (e.g. Franchise Branch Manager / Agent): also limit them to that franchise
			_allow(user, "Franchise", branch_franchise)
	branches = [dsa_branch] if dsa_branch else []
	if franchise:
		_allow(user, "Franchise", franchise)
		branches += frappe.get_all("DSA Branch", {"franchise": franchise}, pluck="name")
		if not branches:
			frappe.throw(_("Franchise {0} has no DSA Branch yet; create its branch first.").format(franchise))
	for branch in set(branches):
		_allow(user, "DSA Branch", branch)
	return sorted(set(branches))


def sync_franchise_branch(doc, method=None):
	"""DSA Branch hook: users of a franchise automatically get access to its new branches."""
	if not doc.franchise:
		return
	for user in frappe.get_all("User Permission", {"allow": "Franchise", "for_value": doc.franchise}, pluck="user"):
		_allow(user, "DSA Branch", doc.name)
