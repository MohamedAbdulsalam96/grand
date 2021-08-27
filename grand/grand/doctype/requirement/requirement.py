# Copyright (c) 2021, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Requirement(Document):
	@frappe.whitelist()
	def validate(self):
		if self.status == "Quotation Sent":
			country_moq_fields = ['country_based_moq_1', 'country_based_moq_2', 'country_based_moq_3',
								  'country_based_moq_4', 'country_based_moq_5']
			for i in self.requirement_items:
				total_moq = 0
				for x in range(0, len(country_moq_fields)):
					if i.__dict__[country_moq_fields[x]]:
						total_moq += i.__dict__[country_moq_fields[x]]
				if total_moq != i.final_moq:
					frappe.throw("Total MOQ is not equal to Final MOQ in row " + str(i.idx))
	@frappe.whitelist()
	def check_for_quotation(self):
		country_moq_fields = ['country_based_moq_1', 'country_based_moq_2', 'country_based_moq_3',
							  'country_based_moq_4', 'country_based_moq_5']
		country_fields = ['country_1','country_2','country_3','country_4','country_5']
		not_set = False
		for i in self.requirement_items:
			if not i.final_moq or not i.final_price:
				not_set = True
		total_moq = 0
		for x in self.requirement_items:
			for xx in range(0,len(country_moq_fields)):
				total_moq += x.__dict__[country_moq_fields[xx]]

			if total_moq != x.final_moq:
				not_set = True

		if not self.supplier_id:
			not_set = True
		frappe.db.sql(""" UPDATE `tabRequirement` SET for_quotation_sent=%s WHERE name=%s""", (not not_set, self.name))
		frappe.db.commit()
		self.reload()
	@frappe.whitelist()
	def on_update_after_submit(self):
		self.check_for_quotation()
		country_moq_fields = ['country_based_moq_1', 'country_based_moq_2', 'country_based_moq_3',
							  'country_based_moq_4', 'country_based_moq_5']
		for i in self.requirement_items:
			total_moq = 0
			for x in range(0, len(country_moq_fields)):
				if i.__dict__[country_moq_fields[x]]:
					total_moq += i.__dict__[country_moq_fields[x]]

			if total_moq != i.final_moq:
				frappe.throw("Total MOQ is not equal to Final MOQ in row " + str(i.idx))


	@frappe.whitelist()
	def on_submit(self):
		self.add_status("Identifying Supplier")
	@frappe.whitelist()
	def change_status(self, status):
		frappe.db.sql(""" UPDATE `tabRequirement` SET status=%s WHERE name=%s """, (status, self.name))
		frappe.db.commit()
		self.add_status(status)

	@frappe.whitelist()
	def create_supplier(self):
		obj = {
			"doctype": "Supplier",
			"supplier_name": self.supplier,
			"supplier_group": "All Supplier Groups",
		}
		try:
			supplier = frappe.get_doc(obj).insert()
			frappe.db.sql(""" UPDATE `tabRequirement` SET supplier_id=%s WHERE name=%s """, (supplier.name, self.name))
			frappe.db.commit()
			return True
		except:
			frappe.log_error(frappe.get_traceback(), "Supplier Creation Failed")
			return False
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
		country_fields = ['country_1','country_2','country_3','country_4','country_5']
		country_moq_fields = ['country_based_moq_1','country_based_moq_2','country_based_moq_3','country_based_moq_4','country_based_moq_5']
		for i in self.requirement_items:
			for x in range(0,len(country_fields)):
				existing_order = frappe.db.sql(""" SELECT * FROM `tabOrder` WHERE country=%s and requirement=%s """, (i.__dict__[country_fields[x]],self.name),as_dict=1)
				if len(existing_order) > 0:
					order_exist = frappe.get_doc("Order", existing_order[0].name)
					order_exist.append("order_items",{
						"item_name": i.item_name,
						"item_description": i.item_description,
						"moq": i.__dict__[country_moq_fields[x]],
						"uom": i.uom,
					})
					order_exist.save()
					print("EXISTING ORDER")
				else:
					obj = {
						"doctype": "Order",
						"requirement": self.name,
						"date_of_requirement": self.date_of_requirement,
						"priority": self.priority,
						"country": i.__dict__[country_fields[x]],
						"supplier_master": self.supplier_id,
						"order_items": [
							{
								"item_name": i.item_name,
								"item_description": i.item_description,
								"moq": i.__dict__[country_moq_fields[x]],
								"uom": i.uom,
							}
						]
					}
					order = frappe.get_doc(obj).insert()
					print("NEW ORDER")
					print(order.name)

	@frappe.whitelist()
	def check_order(self):
		order = frappe.db.sql(""" SELECT COUNT(*) as count from `tabOrder` WHERE requirement=%s """, self.name, as_dict=1)

		return order[0].count > 0