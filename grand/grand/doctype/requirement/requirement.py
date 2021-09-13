# Copyright (c) 2021, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime

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
		self.add_predefined_status()
	def add_predefined_status(self):
		if not self.requirement_status:
			statuses = [
				{'status': "Identifying Supplier", "days": 5},
				{'status': "Checking Quality", "days": 5},
				{'status': "Waiting for Quote", "days": 5},
				{'status': "Negotiating Price & MOQ", "days": 5},
				{'status': "Quotation Sent", "days": 5}
			 ]
			start_date = self.posting_date
			for status in statuses:
				end_date = (datetime.datetime.strptime(str(start_date), "%Y-%m-%d") + datetime.timedelta(days=5)).date()
				obj = {
					"status": status['status'],
					"start_date": str(start_date),
					"days": status['days'],
					"end_date": str(end_date),
				}
				print(obj)
				self.append("requirement_status",obj)
				start_date = (datetime.datetime.strptime(str(start_date), "%Y-%m-%d") + datetime.timedelta(days=5)).date()

	@frappe.whitelist()
	def check_for_quotation(self):
		country_moq_fields = ['country_based_moq_1', 'country_based_moq_2', 'country_based_moq_3',
							  'country_based_moq_4', 'country_based_moq_5']
		country_fields = ['country_1','country_2','country_3','country_4','country_5']
		if not self.supplier_id:
			frappe.throw("Supplier is not created")

		for i in self.requirement_items:
			if (not i.final_moq or not i.final_price) and not i.no_required_moq:
				frappe.throw("Final MOQ or Final Price is not set for row " + str(i.idx))

		for x in self.requirement_items:
			total_moq = 0
			for xx in range(0,len(country_moq_fields)):
				if x.__dict__[country_moq_fields[xx]]:
					total_moq += x.__dict__[country_moq_fields[xx]]

			if total_moq != x.final_moq and not i.no_required_moq:
				frappe.throw("Total MOQ is not equal to Final MOQ in row " + str(x.idx))

		# frappe.db.sql(""" UPDATE `tabRequirement` SET for_quotation_sent=%s WHERE name=%s""", (not not_set, self.name))
		# frappe.db.commit()
		self.reload()
	@frappe.whitelist()
	def on_update_after_submit(self):
		# self.check_for_quotation()
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
	def change_status(self, status):
		if status == "Quotation Sent":
			self.check_for_quotation()
		frappe.db.sql(""" UPDATE `tabRequirement` SET status=%s WHERE name=%s """, (status, self.name))
		frappe.db.commit()
		# self.add_status(status)

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
	def check_country(self, country):
		country_fields = ['country_1', 'country_2', 'country_3', 'country_4', 'country_5']
		approve_fields = ['approved_country_1', 'approved_country_2', 'approved_country_3', 'approved_country_4', 'approved_country_5']
		country_moq_fields = ['country_based_moq_1', 'country_based_moq_2', 'country_based_moq_3',
							  'country_based_moq_4', 'country_based_moq_5']
		country_order_fields = ['order_1', 'order_2', 'order_3', 'order_4', 'order_5']

		for i in self.requirement_items:
			for x in range(0, len(country_fields)):
				print(i.__dict__[approve_fields[x]])
				print(i.__dict__[country_fields[x]] and \
						i.__dict__[country_fields[x]] == country and \
						not i.__dict__[country_order_fields[x]] and  \
						(i.__dict__[country_moq_fields[x]] <= 0 or i.__dict__[approve_fields[x]] == "Rejected" or not i.__dict__[approve_fields[x]] or i.__dict__[approve_fields[x]] == ''))
				if i.__dict__[country_fields[x]] and \
						i.__dict__[country_fields[x]] == country and \
						not i.__dict__[country_order_fields[x]] and  \
						(i.__dict__[country_moq_fields[x]] <= 0 or i.__dict__[approve_fields[x]] == "Rejected" or not i.__dict__[approve_fields[x]] or i.__dict__[approve_fields[x]] == ''):
					return False
		return True
	# @frappe.whitelist()
	# def create_order(self):
	# 	country_fields = ['country_1','country_2','country_3','country_4','country_5']
	# 	approve_fields = ['approve_1','approve_2','approve_3','approve_4','approve_5']
	# 	country_moq_fields = ['country_based_moq_1','country_based_moq_2','country_based_moq_3','country_based_moq_4','country_based_moq_5']
	# 	country_order_fields = ['order_1','order_2','order_3','order_4','order_5']
    #
	# 	items = {}
	# 	for i in self.requirement_items:
	# 		for x in range(0,len(country_fields)):
	# 			if i.__dict__[country_fields[x]] and self.check_country(i.__dict__[country_fields[x]]):
	# 				if i.__dict__[country_fields[x]] not in items:
	# 					items[i.__dict__[country_fields[x]]] = [i]
	# 				else:
	# 					items[i.__dict__[country_fields[x]]].append(i)
    #
	# 	for item in items:
	# 		order_items = []
	# 		for yyy in items[item]:
	# 			order_items.append({
	# 				"item_name": yyy.item_name,
	# 				"item_description": yyy.item_description,
	# 				"moq": yyy.__dict__[country_moq_fields[x]],
	# 				"uom": yyy.uom,
	# 			})
	# 		obj = {
	# 			"doctype": "Order",
	# 			"requirement": self.name,
	# 			"date_of_requirement": self.date_of_requirement,
	# 			"priority": self.priority,
	# 			"country": item,
	# 			"supplier_master": self.supplier_id,
	# 			"order_items": order_items
	# 		}
	# 		order = frappe.get_doc(obj).insert()
	# 		for yyy in items[item]:
	# 			for xxx in  range(0, len(country_fields)):
	# 				if yyy.__dict__[country_fields[xxx]] == item:
	# 					query1 = """ UPDATE `tabRequirement Item` SET {0}='{1}' WHERE name='{2}'""".format(country_order_fields[xxx],order.name, yyy.name)
	# 					frappe.db.sql(query1)
	# 					frappe.db.commit()

	@frappe.whitelist()
	def create_order(self):
		country_fields = ['country_1', 'country_2', 'country_3', 'country_4', 'country_5']
		country_moq_fields = ['country_based_moq_1', 'country_based_moq_2', 'country_based_moq_3',
							  'country_based_moq_4', 'country_based_moq_5']
		country_order_fields = ['order_1', 'order_2', 'order_3', 'order_4', 'order_5']
		for i in self.requirement_items:
			if i.no_required_moq:
				obj = {
					"doctype": "Order",
					"requirement": self.name,
					"date_of_requirement": self.date_of_requirement,
					"priority": self.priority,
					"country": self.requested_country,
					"supplier_master": self.supplier_id,
					"order_items": [
						{
							"item_name": i.item_name,
							"item_description": i.item_description,
							"moq": i.qty_required,
							"uom": i.uom,
							"price": i.final_price,
							"final_moq": i.qty_required
						}
					]
				}
				order = frappe.get_doc(obj).insert()
				query1 = """ UPDATE `tabRequirement Item` SET order_name='{0}' WHERE name='{1}'""".format(order.name,i.name)
				frappe.db.sql(query1)
				frappe.db.commit()

			for x in range(0, len(country_fields)):
				if i.__dict__[country_moq_fields[x]] > 0:
					existing_order = frappe.db.sql(
						""" SELECT * FROM `tabOrder` WHERE country=%s and requirement=%s """,
						(i.__dict__[country_fields[x]], self.name), as_dict=1)
					if len(existing_order) > 0:
						order_exist = frappe.get_doc("Order", existing_order[0].name)
						order_exist.append("order_items", {
							"item_name": i.item_name,
							"item_description": i.item_description,
							"moq": i.__dict__[country_moq_fields[x]],
							"uom": i.uom,
							"price": i.final_price,
							"final_moq": i.final_moq
						})
						order_exist.save()
						query = """ UPDATE `tabRequirement Item` SET {0}='{1}' WHERE name='{2}'""".format(
							country_order_fields[x], existing_order[0].name, i.name)
						frappe.db.sql(query)
						frappe.db.commit()
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
									"price": i.final_price,
									"final_moq": i.final_moq
								}
							]
						}
						order = frappe.get_doc(obj).insert()
						query1 = """ UPDATE `tabRequirement Item` SET {0}='{1}' WHERE name='{2}'""".format(
							country_order_fields[x], order.name, i.name)

						frappe.db.sql(query1)
						frappe.db.commit()
	@frappe.whitelist()
	def check_order(self):
		order = frappe.db.sql(""" SELECT COUNT(*) as count from `tabOrder` WHERE requirement=%s """, self.name, as_dict=1)

		return order[0].count > 0