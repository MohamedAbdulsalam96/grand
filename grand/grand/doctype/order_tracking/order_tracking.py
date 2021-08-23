# Copyright (c) 2021, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OrderTracking(Document):
	@frappe.whitelist()
	def on_update_after_submit(self):
		self.change_status()
		self.reload()

	@frappe.whitelist()
	def change_status(self):
		status = self.order_tracking_location[len(self.order_tracking_location) - 1].status
		frappe.db.sql(""" UPDATE `tabOrder Tracking` SET status=%s WHERE name=%s """, (status, self.name))
		frappe.db.commit()
