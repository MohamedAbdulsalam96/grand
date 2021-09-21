# Copyright (c) 2021, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
class OrderTracking(Document):
	@frappe.whitelist()
	def check_ot(self):
		ot = frappe.db.sql(""" SELECT COUNT(*) as count FROm `tabOrder Tracking` WHERE order_tracking = %s """, self.name, as_dict=1)

		return ot[0].count > 0
	@frappe.whitelist()
	def add_order(self):
		orders = frappe.db.sql(""" SELECT * FROM `tabPurchase Order Orders` WHERE parent=%s """, self.purchase_order_ref, as_dict=1)
		for i in orders:
			self.append("order_tracking_items", {
				"order": i.order,
			})
	@frappe.whitelist()
	def validate(self):
		self.add_predefined_status()

	def add_predefined_status(self):
		if not self.order_tracking_location:
			if self.order_tracking:
				statuses = [
					{'status': "Receiving to Store", "days": 30},
					{'status': "Dispatching to Store", "days": 2}
				]
				self.status = "Pending"
			else:
				statuses = [
					{'status': "Waiting", "days": 5},
					{'status': "In Production", "days": 10},
					{'status': "Packing", "days": 5},
					{'status': "Ready for Shipment", "days": 5},
					{'status': "Waiting for Shipment", "days": 5},
					{'status': "Shipped", "days": 2}
				]
			start_date = self.purchase_order_date if self.purchase_order_date else self.order_tracking_date
			for status in statuses:
				end_date = (
				datetime.datetime.strptime(str(start_date), "%Y-%m-%d") + datetime.timedelta(days=status['days'])).date()
				obj = {
					"status": status['status'],
					"start_date": str(start_date),
					"days": status['days'],
					"end_date": str(end_date),
				}
				print(obj)
				self.append("order_tracking_location", obj)
				start_date = (
					datetime.datetime.strptime(str(start_date), "%Y-%m-%d") + datetime.timedelta(days=status['days'])).date()
	@frappe.whitelist()
	def change_status(self, status):
		if status == "Order Tracking":
			self.generate_sub_order_trackings()
			status = "Shipped"

		frappe.db.sql(""" UPDATE `tabOrder Tracking` SET status=%s WHERE name=%s """, (status, self.name))
		frappe.db.commit()
		if status == "Completed":
			ot = frappe.db.sql(""" SELECT COUNT(*) as count from `tabOrder Tracking` where order_tracking=%s and status != 'Completed' """, self.order_tracking, as_dict=1)
			if ot[0].count == 0:
				frappe.db.sql(""" UPDATE `tabOrder Tracking` SET status='Completed'  WHERE name=%s""", self.order_tracking)
				frappe.db.commit()
		# self.add_status(status)

	def generate_sub_order_trackings(self):
		for i in self.order_tracking_items:
			obj = {
				"doctype": "Order Tracking",
				"supplier": self.supplier,
				"order_tracking": self.name,
				"order_tracking_items": [{
					"order": i.order
				}],
				"order_tracking_date": self.purchase_order_date,
			}
			ot = frappe.get_doc(obj).insert()
			ot.submit()
	# @frappe.whitelist()
	# def add_status(self, status):
	# 	status_length = frappe.db.sql(""" SELECT COUNT(*) as count FROM `tabOrder Tracking Location` WHERE parent=%s""",
	# 								  self.name, as_dict=1)
	# 	obj = {
	# 		"doctype": "Order Tracking Location",
	# 		"status": status,
	# 		"parent": self.name,
	# 		"parenttype": "Order Tracking",
	# 		"parentfield": "order_tracking_location",
	# 		"idx": status_length[0].count + 1
	# 	}
	# 	frappe.get_doc(obj).insert()