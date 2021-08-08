import frappe

def on_submit_po(doc, method):
    obj = {
        "doctype": "Order Tracking",
        "supplier": doc.supplier,
        "purchase_order_ref": doc.name,
        "order_tracking_items": get_order_tracking_items(doc),
    }
    frappe.get_doc(obj).insert()
def get_order_tracking_items(doc):
    items = []
    for i in doc.items:
        items.append({
            "item_code": i.item_code,
            "delivery_date": i.expected_delivery_date,
            "quantity": i.qty,
            "rate": i.rate,
            "amount": i.amount,
        })
    return items