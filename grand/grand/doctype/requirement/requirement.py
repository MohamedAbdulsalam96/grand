# Copyright (c) 2021, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Requirement(Document):
	@frappe.whitelist()
	def on_submit(self):
		self.add_status("Identifying Supplier")
	@frappe.whitelist()
	def change_status(self, status):
		frappe.db.sql(""" UPDATE `tabRequirement` SET status=%s WHERE name=%s """, (status, self.name))
		frappe.db.commit()
		self.add_status(status)

	@frappe.whitelist()
	def add_status(self,status):
		status_length = frappe.db.sql(""" SELECT COUNT(*) as count FROM `tabRequirement Status` WHERE parent=%s""", self.name, as_dict=1)
		obj ={
			"doctype": "Requirement Status",
			"status": status,
			"parent": self.name,
			"parenttype": "Requirement",
			"parentfield": "requirement_status",
			"idx": status_length[0].count + 1
		}
		frappe.get_doc(obj).insert()

	@frappe.whitelist()
	def create_order(self):
		obj = {
			"doctype": "Order",
			"requirement": self.name,
			"date_of_requirement": self.date_of_requirement,
			"priority": self.priority,
			"order_items": self.get_items()
		}
		order = frappe.get_doc(obj).insert()
		return order.name
	def get_items(self):
		items = []
		for i in self.requirement_items:
			items.append({
				"item_name": i.item_name,
				"item_description": i.item_description
			})
		return items
	@frappe.whitelist()
	def check_order(self):
		order = frappe.db.sql(""" SELECT COUNT(*) as count from `tabOrder` WHERE requirement=%s """, self.name, as_dict=1)

		return order[0].count > 0