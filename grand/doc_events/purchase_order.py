import frappe

def validate_po(doc, method):
    if len(doc.orders) > 0:
        for i in doc.items:
            if i.qty != i.final_moq:
                frappe.throw("Final MOQ (" + str(i.final_moq) + ") for item " + i.item_name + " is not equal to Order Qty (" + str(i.qty) + ")")

def on_submit_po(doc, method):
    obj = {
        "doctype": "Order Tracking",
        "supplier": doc.supplier,
        "purchase_order_ref": doc.name,
        "order_tracking_location": get_order_tracking_location(doc),
        "order_tracking_items": get_order_tracking_items(doc),
    }
    frappe.get_doc(obj).insert()


def get_order_tracking_items(doc):
    items = []
    for i in doc.items:
        items.append({
            "item_code": i.item_code,
            "delivery_date": i.schedule_date,
            "quantity": i.qty,
            "rate": i.rate,
            "amount": i.amount,
        })
    return items
def get_order_tracking_location(doc):
    status = [{
        "status": "Waiting",
    }]
    return status


def on_trash_po(doc, method):
    for i in doc.orders:
        frappe.db.sql(""" UPDATE `tabOrder` SET purchase_order='' WHERE name=%s """, (i.order))
        frappe.db.commit()