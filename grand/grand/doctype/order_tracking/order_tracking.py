# Copyright (c) 2021, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
class OrderTracking(Document):
	@frappe.whitelist()
	def validate(self):
		self.add_predefined_status()

	def add_predefined_status(self):
		if not self.order_tracking_status:
			statuses = [
				{'status': "Waiting", "days": 5},
				{'status': "In Production", "days": 5},
				{'status': "Packing", "days": 5},
				{'status': "Ready for Shipment", "days": 5},
				{'status': "Waiting for Shipment", "days": 5},
				{'status': "Shipped", "days": 5},
				{'status': "Receiving to Store", "days": 5},
				{'status': "Dispatching to Store", "days": 5}
			]
			start_date = self.eta
			for status in statuses:
				end_date = (
				datetime.datetime.strptime(str(start_date), "%Y-%m-%d") + datetime.timedelta(days=5)).date()
				obj = {
					"status": status['status'],
					"start_date": str(start_date),
					"days": status['days'],
					"end_date": str(end_date),
				}
				print(obj)
				self.append("order_status", obj)
				start_date = (
					datetime.datetime.strptime(str(start_date), "%Y-%m-%d") + datetime.timedelta(days=5)).date()
	@frappe.whitelist()
	def change_status(self, status):
		frappe.db.sql(""" UPDATE `tabOrder Tracking` SET status=%s WHERE name=%s """, (status, self.name))
		frappe.db.commit()

		# self.add_status(status)

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