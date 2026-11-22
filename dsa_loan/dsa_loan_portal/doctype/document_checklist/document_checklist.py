# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate, now_datetime, nowdate


class DocumentChecklist(Document):
	def validate(self):
		if self.document_file and self.verification_status == "Pending":
			self.verification_status = "Received"
		if self.document_file and not self.received_date:
			self.received_date = nowdate()
		if self.issue_date and self.expiry_date and getdate(self.expiry_date) < getdate(self.issue_date):
			frappe.throw(_("Expiry Date cannot be before Issue Date."))
		self.check_validity_period()
		if self.verification_status == "Rejected" and not self.rejection_reason:
			frappe.throw(_("Enter the Rejection Reason before rejecting the document."))
		if self.has_value_changed("verification_status") and self.verification_status in ("Verified", "Rejected"):
			self.verification_date = now_datetime()
			if not self.verified_by:
				self.verified_by = frappe.db.get_value("Employee", {"user_id": frappe.session.user})

	def check_validity_period(self):
		"""Warn when a document is older than the lender rule allows (e.g. bank statement > 90 days)."""
		if not (self.lender_document_rule and self.issue_date):
			return
		days = frappe.db.get_value("Lender Document Rule", self.lender_document_rule, "validity_period_days")
		if days and getdate(add_days(self.issue_date, days)) < getdate(nowdate()):
			frappe.msgprint(_("{0} is older than the {1} days the lender accepts.").format(self.document_name, days), indicator="orange")
