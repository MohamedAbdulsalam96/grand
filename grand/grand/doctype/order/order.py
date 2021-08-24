# Copyright (c) 2021, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Order(Document):
    def validate(self):
        self.with_sku = 0
        for i in self.order_items:
            if i.new_sku:
               self.with_sku = 1

    @frappe.whitelist()
    def change_status(self, status):
        frappe.db.sql(""" UPDATE `tabOrder` SET status=%s WHERE name=%s """, (status, self.name))
        frappe.db.commit()

        self.add_status(status)

    @frappe.whitelist()
    def add_status(self, status):
        status_length = frappe.db.sql(""" SELECT COUNT(*) as count FROM `tabOrder Status` WHERE parent=%s""",
                                      self.name, as_dict=1)
        obj = {
            "doctype": "Order Status",
            "status": status,
            "parent": self.name,
            "parenttype": "Order",
            "parentfield": "order_status",
            "idx": status_length[0].count + 1
        }
        frappe.get_doc(obj).insert()

    @frappe.whitelist()
    def create_items(self):
        if not self.reorder:
            for i in self.order_items:
                obj = {
                    "doctype": "Item",
                    "item_code": i.item_name,
                    "item_name": i.item_name,
                    "description": i.item_description,
                    "item_group": "All Item Groups",
                    "stock_uom": i.uom
                }
                try:
                    new_item = frappe.get_doc(obj).insert()
                    frappe.db.sql(""" UPDATE `tabOrder Item` SET item = %s WHERE name = %s""",(new_item.name, i.name))
                    frappe.db.commit()
                    if self.requirement:
                        other_orders = frappe.db.sql(""" SELECT * FROM `tabOrder` WHERE requirement=%s """, self.requirement, as_dict=1)
                        for iii in other_orders:
                            frappe.db.sql(""" UPDATE `tabOrder Item` SET item = %s WHERE parent = %s and item_name=%s""",
                                          (new_item.name, iii.name, i.item_name))
                            frappe.db.sql(""" UPDATE `tabOrder` SET created_items=1 WHERE name=%s """, iii.name)
                            frappe.db.commit()

                except:
                    frappe.log_error(frappe.get_traceback(), "Item Creation Failed")
                    return False
        frappe.db.sql(""" UPDATE `tabOrder` SET created_items=1 WHERE name=%s """, self.name)
        frappe.db.commit()
        return True
    @frappe.whitelist()
    def check_po(self):
        po = frappe.db.sql(""" SELECT COUNT(*) as count from `tabPurchase Order Orders` WHERE order=%s """, self.name,
                              as_dict=1)

        return po[0].count > 0


    @frappe.whitelist()
    def generate_po(self):
        if not self.supplier_master:
            frappe.throw("Please create the supplier through Create Supplier Button in Linked Requirement")
        if self.requirement:
            po_name = self.create_po_requirements()
            return po_name
        else:
            obj = {
                "doctype": "Purchase Order",
                "supplier": self.supplier_master,
                "schedule_date": self.date_of_requirement,
                "order": self.name,
                "items": self.get_po_items(),
                "orders": [{"order": self.name}]
            }
            new_po = frappe.get_doc(obj).insert()
            frappe.db.sql(""" UPDATE `tabOrder` SET purchase_order=%s WHERE name=%s """,(new_po.name, self.name))
            frappe.db.commit()
            return new_po.name
    @frappe.whitelist()
    def create_po_requirements(self):

        orders = frappe.db.sql(""" SELECT * FROM `tabOrder` WHERE requirement=%s and (purchase_order is null or purchase_order='') and status='Approved' """, self.requirement, as_dict=1)
        items = []
        orders_po = []
        for i in orders:
            orders_po.append({"order": i.name})
            order_items = frappe.db.sql(""" SELECT * FROM `tabOrder Item` WHERE parent=%s """, i.name, as_dict=1)
            for ii in order_items:
                items.append({
                    "item_code": ii.item,
                    "item_name": ii.item_description,
                    "qty": ii.moq,
                    "rate": ii.price,
                    "schedule_date": self.date_of_requirement,
                })
        obj = {
            "doctype": "Purchase Order",
            "supplier": self.supplier_master,
            "schedule_date": self.date_of_requirement,
            "order": self.name,
            "items": items,
            "orders": orders_po
        }
        print("POOOOOOOOOOOOOOOOOOOOOOOOOO")
        print(obj)
        new_po = frappe.get_doc(obj).insert()
        for order in orders:
            frappe.db.sql(""" UPDATE `tabOrder` SET purchase_order=%s WHERE name=%s""",(new_po.name,order.name))
            frappe.db.commit()
        return new_po.name
    def get_po_items(self):
        items = []
        for i in self.order_items:
            items.append({
                "item_code": i.item_name_master,
                "item_name": i.item_description,
                "qty": i.moq,
                "rate": i.price,
                "schedule_date": self.date_of_requirement,

            })

        return items
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
        country_fields = ['country_1', 'country_2', 'country_3', 'country_4', 'country_5']
        country_moq_fields = ['country_based_moq_1', 'country_based_moq_2', 'country_based_moq_3',
                              'country_based_moq_4', 'country_based_moq_5']
        for i in items:
            for x in range(0, len(country_fields)):
                if i[country_fields[x]] == self.country:
                    self.append("order_items",{
                        "item_name": i.item_name,
                        "item_description": i.item_description,
                        "moq": i[country_moq_fields[x]],
                    })
    @frappe.whitelist()
    def create_supplier(self):
        obj = {
            "doctype": "Supplier",
            "supplier_name": self.supplier,
            "supplier_group": "All Supplier Groups",
        }
        try:
            supplier = frappe.get_doc(obj).insert()
            frappe.db.sql(""" UPDATE `tabOrder` SET supplier_id=%s WHERE name=%s """,(supplier.name,self.name))
            frappe.db.commit()
            return True
        except:
            frappe.log_error(frappe.get_traceback(), "Supplier Creation Failed")
            return False