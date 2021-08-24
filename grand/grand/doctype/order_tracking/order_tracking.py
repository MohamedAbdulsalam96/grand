# Copyright (c) 2021, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OrderTracking(Document):
	@frappe.whitelist()
	def on_submit(self):
		self.add_status("Waiting")
		self.reload()
	@frappe.whitelist()
	def change_status(self, status):
		frappe.db.sql(""" UPDATE `tabOrder Tracking` SET status=%s WHERE name=%s """, (status, self.name))
		frappe.db.commit()

		self.add_status(status)

	@frappe.whitelist()
	def add_status(self, status):
		status_length = frappe.db.sql(""" SELECT COUNT(*) as count FROM `tabOrder Tracking Location` WHERE parent=%s""",
									  self.name, as_dict=1)
		obj = {
			"doctype": "Order Tracking Location",
			"status": status,
			"parent": self.name,
			"parenttype": "Order Tracking",
			"parentfield": "order_tracking_location",
			"idx": status_length[0].count + 1
		}
		frappe.get_doc(obj).insert()