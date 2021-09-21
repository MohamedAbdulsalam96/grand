var existing_order = false

cur_frm.cscript.refresh = function () {
    cur_frm.trigger("filter_order")
        frappe.call({
                    method: "grand.doc_events.purchase_order.check_order_tracking",
                    args:{
                        name: cur_frm.doc.name
                    },
                    async: false,
                    callback: function (r) {
                        if (cur_frm.doc.docstatus && !r.message) {
                            cur_frm.add_custom_button(__("Order Tracking"), () => {
                                frappe.call({
                                method: "grand.doc_events.purchase_order.create_order_tracking",
                                args: {
                                    doc: cur_frm.doc
                                },
                                callback: function (rr) {
                                    cur_frm.reload_doc()
                                                                        frappe.set_route("Form", "Order Tracking", rr.message);

                                }
                                })
                        }).css({'color': 'white', 'font-weight': 'bold', 'background-color': 'blue'});
                        }
                    }
                })

        }
cur_frm.cscript.supplier = function () {
    cur_frm.trigger("filter_order")
}
cur_frm.cscript.filter_order = function () {
    var names=[]
    if(cur_frm.doc.orders){
        names = cur_frm.doc.orders.map(x => "order" in x ? x.order:"")
    }
    cur_frm.set_query('order', 'orders', () => {
    return {
        filters: [
            ["supplier_master", "=", cur_frm.doc.supplier],
            ["status","=", "Approved"],
            ["name", "not in", names]
        ]
    }
    })
}

cur_frm.cscript.order = function (frm, cdt, cdn) {
    var d = locals[cdt][cdn]
    if(d.order) {
        frappe.db.get_doc('Order', d.order)
            .then(doc => {
            if(cur_frm.doc.items.length === 1 && !cur_frm.doc.items[0].item_code){
                cur_frm.clear_table("items")
                cur_frm.refresh_field("items")
                for (var x = 0; x < doc.order_items.length; x += 1) {
                    cur_frm.add_child('items', {
                        item_code: doc.order_items[x].item_name_master ? doc.order_items[x].item_name_master : doc.order_items[x].item,
                        item_name: doc.order_items[x].item_description,
                        description: doc.order_items[x].item_description,
                        qty: doc.order_items[x].moq,
                        rate: doc.order_items[x].price,
                        schedule_date: doc.date_of_requirement,
                        uom: doc.order_items[x].uom,
                        final_moq: doc.order_items[x].final_moq
                    });

                    cur_frm.refresh_field('items');
                    cur_frm.trigger("qty")
                    cur_frm.trigger("filter_order")

                }
            } else {

                for (var x = 0; x < doc.order_items.length; x += 1) {
                    var final_item_name = doc.order_items[x].item_name_master ? doc.order_items[x].item_name_master : doc.order_items[x].item
                    if((cur_frm.doc.items.filter(item => (item.item_code === final_item_name))).length > 0){
                        for(var xxx=0;xxx<cur_frm.doc.items.length;xxx+=1){
                            if(cur_frm.doc.items[xxx].item_code === final_item_name){
                                cur_frm.doc.items[xxx].qty += doc.order_items[x].moq
                                cur_frm.refresh_field('items');
cur_frm.trigger("qty")
    cur_frm.trigger("filter_order")

                            }
                        }
                    } else {
                         cur_frm.add_child('items', {
                            item_code: doc.order_items[x].item_name_master ? doc.order_items[x].item_name_master : doc.order_items[x].item,
                            item_name: doc.order_items[x].item_description,
                            qty: doc.order_items[x].moq,
                            rate: doc.order_items[x].price,
                            description: doc.order_items[x].item_description,
                            schedule_date: doc.date_of_requirement,
                            uom: doc.order_items[x].uom,
                             final_moq: doc.order_items[x].final_moq
                        });

                        cur_frm.refresh_field('items');
                        cur_frm.trigger("qty")
                        cur_frm.trigger("filter_order")

                    }


                }
            }
        })
    }
}

cur_frm.cscript.before_orders_remove = function(frm, cdt, cdn){
    var d = locals[cdt][cdn]
    if(d.order) {
        frappe.db.get_doc('Order', d.order)
            .then(doc => {
               for (var x = 0; x < doc.order_items.length; x += 1) {
                    var final_item_name = doc.order_items[x].item_name_master ? doc.order_items[x].item_name_master : doc.order_items[x].item
                    if((cur_frm.doc.items.filter(item => (item.item_code === final_item_name))).length > 0){
                        for(var xxx=0;xxx<cur_frm.doc.items.length;xxx+=1){
                            if(cur_frm.doc.items[xxx].item_code === final_item_name && cur_frm.doc.items[xxx].qty > doc.order_items[x].moq){
                                cur_frm.doc.items[xxx].qty -= doc.order_items[x].moq
                                cur_frm.refresh_field('items');
                                cur_frm.trigger("qty")
                                cur_frm.trigger("filter_order")

                            } else if(cur_frm.doc.items[xxx].item_code === final_item_name && cur_frm.doc.items[xxx].qty === doc.order_items[x].moq){
                                cur_frm.doc.items[xxx].qty -= doc.order_items[x].moq
                                 cur_frm.get_field("items").grid.grid_rows[x].remove();
                                cur_frm.refresh_field('items');
                                cur_frm.trigger("filter_order")

                            }
                        }
                    }
                }
            })
    }
}