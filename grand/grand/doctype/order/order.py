# Copyright (c) 2021, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Order(Document):
	def validate(self):
		for i in self.order_items:
			if i.new_sku:
				self.with_sku = 1
	@frappe.whitelist()
	def change_status(self, status):
		frappe.db.sql(""" UPDATE `tabOrder` SET status=%s, workflow_state=%s WHERE name=%s """, (status, status, self.name))
		frappe.db.commit()

	def create_items(self):
		if not self.reorder:
			for i in self.order_items:

				obj = {
					"doctype": "Item",
					"item_code": i.item_name,
					"description": i.item_description,
					"item_group": "All Item Groups"
				}
				try:
					new_item = frappe.get_doc(obj).insert()
					frappe.db.sql(""" UPDATE `tabOrder Item` SET item = %s WHERE name = %s""",(new_item.name, i.name))
					frappe.db.commit()
				except:
					frappe.log_error(frappe.get_traceback(), "Item Creation Failed")
					return False
		return True
	def generate_po(self):
		obj = {
			"doctype": "Purchase Order",
			"supplier": self.supplier_master if self.existing_supplier else self.supplier,
			"items": self.get_po_items()
		}
		new_po = frappe.get_doc(obj).insert()
		frappe.db.sql(""" UPDATE `tabOrder` SET purchase_order=%s WHERE name=%s """,(new_po.name, self.name))
		frappe.db.commit()
	def get_po_items(self):
		items = []
		for i in self.order_items:
			items.append({
				"item_code": i.item if not self.reorder else i.item_name_master,
				"qty": i.moq,
				"rate": i.price,

			})
	def generate_payment_entry(self):
		items = []
		obj = {
			"doctype": "Payment Entry",
			"items": self.get_items()
		}
		for i in self.order_items:
			if self.check_item():
				items.append({
					"item_code": i.item if not self.reorder else i.item_name_master,
					"qty": i.moq,
					"rate": i.price,

				})
	@frappe.whitelist()
	def add_item(self):
		items = frappe.db.sql(""" SELECT * FROM `tabRequirement Item` WHERE parent=%s """, self.requirement, as_dict=1)
		for i in items:
			self.append("order_items",{
				"item_name": i.item_name,
				"item_description": i.item_description,
			})
	@frappe.whitelist()
	def create_supplier(self):
		obj = {
			"doctype": "Supplier",
			"supplier_name": self.supplier,
			"supplier_group": "All Supplier Groups",
		}
		try:
			frappe.get_doc(obj).insert()
			return True
		except:
			frappe.log_error(frappe.get_traceback(), "Supplier Creation Failed")
			return False