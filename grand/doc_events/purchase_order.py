import frappe, json

@frappe.whitelist()
def check_order_tracking(name):
    order_tracking = frappe.db.sql(""" SELECT COUNT(*) as count FROM `tabOrder Tracking` WHERE purchase_order_ref=%s """,name, as_dict=1 )

    return order_tracking[0].count > 0

def validate_po(doc, method):
    if len(doc.orders) > 0:
        for i in doc.items:
            if i.qty != i.final_moq:
                frappe.throw("Final MOQ (" + str(i.final_moq) + ") for item " + i.item_name + " is not equal to Order Qty (" + str(i.qty) + ")")

@frappe.whitelist()
def create_order_tracking(doc):
    data = json.loads(doc)
    print(data['orders'])

    obj = {
        "doctype": "Order Tracking",
        "supplier": data['supplier'],
        "purchase_order_ref": data['name'],
        "order_tracking_items": get_order_tracking_items(data),
        "purchase_order_date": data['transaction_date'],
    }
    ot = frappe.get_doc(obj).insert()
    return ot.name

def get_order_tracking_items(doc):
    items = []
    for i in doc['orders']:
        items.append({
            "order": i['order'],
        })
    return items
def get_order_tracking_location():
    status = [{
        "status": "Waiting",
    }]
    return status


def on_trash_po(doc, method):
    for i in doc.orders:
        frappe.db.sql(""" UPDATE `tabOrder` SET purchase_order='' WHERE name=%s """, (i.order))
        frappe.db.commit()