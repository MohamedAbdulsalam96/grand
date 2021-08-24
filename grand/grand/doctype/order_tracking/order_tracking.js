// Copyright (c) 2021, sammish and contributors
// For license information, please see license.txt

frappe.ui.form.on('Order Tracking', {
	refresh: function(frm) {
	    var statuses = [
	        "Waiting",
            "In Production",
            "Packing",
            "Ready for Shipment",
            "Waiting for Shipment",
            "Shipped",
            "Receiving to Store",
            "Dispatching to Store"]

	        if(cur_frm.doc.docstatus  && cur_frm.doc.status !== "Dispatching to Store"){
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
	}
});
