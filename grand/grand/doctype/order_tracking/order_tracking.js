// Copyright (c) 2021, sammish and contributors
// For license information, please see license.txt
var existing_order_tracking = false
frappe.ui.form.on('Order Tracking', {
	refresh: function(frm) {
	   cur_frm.call({
            doc: cur_frm.doc,
            method: 'check_ot',
            args: {},
            freeze: true,
            freeze_message: "Checking...",
            async: false,
            callback: (r) => {
                existing_order_tracking = r.message
            }
        })
	    var statuses = []
        var last_status = ""
	    if(!cur_frm.doc.order_tracking){
	        statuses = ["Waiting", "In Production", "Packing", "Ready for Shipment", "Waiting for Shipment", "Shipped"]
            last_status = "Shipped"
	    } else {
	        statuses = ["Receiving to Store", "Dispatching to Store", "Completed"]
            last_status = "Completed"
        }

	        if(cur_frm.doc.docstatus  && cur_frm.doc.status !== last_status){
                cur_frm.add_custom_button(__(statuses[statuses.indexOf(cur_frm.doc.status) + 1]), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'change_status',
                        args: {
                          status: statuses[statuses.indexOf(cur_frm.doc.status) + 1]
                        },
                        freeze: true,
                        freeze_message: "Changing Status...",
                        async: false,
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
            }

            if(cur_frm.doc.docstatus && cur_frm.doc.status === "Shipped" && !existing_order_tracking){
	            cur_frm.add_custom_button(__("Order Tracking"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'change_status',
                        args: {
                          status: "Order Tracking"
                        },
                        freeze: true,
                        freeze_message: "Changing Status...",
                        async: false,
                        callback: (r) => {
                            cur_frm.reload_doc()
                        }
                    })
                }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
            }
	},
    purchase_order_ref: function () {
	        cur_frm.clear_table("order_tracking_items")
        cur_frm.refresh_field("order_tracking_items")
         cur_frm.call({
                doc: cur_frm.doc,
                method: 'add_order',
                args: {},
                freeze: true,
                freeze_message: "Adding Order",
                async: false,
                callback: (r) => {
                    cur_frm.refresh_field("order_tracking_items")
                }
            })
    }
});
