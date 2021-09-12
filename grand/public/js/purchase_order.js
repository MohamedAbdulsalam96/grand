cur_frm.cscript.refresh = function () {
    cur_frm.set_query('order', 'orders', () => {
    return {
        filters: {
            supplier_master: cur_frm.doc.supplier,
            status: 'Approved'
        }
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
                            } else if(cur_frm.doc.items[xxx].item_code === final_item_name && cur_frm.doc.items[xxx].qty === doc.order_items[x].moq){
                                cur_frm.doc.items[xxx].qty -= doc.order_items[x].moq
                                 cur_frm.get_field("items").grid.grid_rows[x].remove();
                                cur_frm.refresh_field('items');
                            }
                        }
                    }
                }
            })
    }
}