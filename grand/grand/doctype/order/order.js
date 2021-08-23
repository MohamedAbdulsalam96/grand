// Copyright (c) 2021, sammish and contributors
// For license information, please see license.txt

function change_status(cur_frm,status) {
    cur_frm.call({
        doc: cur_frm.doc,
        method: 'change_status',
        args: {
          status: status
        },
        freeze: true,
        freeze_message: "Changing Status...",
        async: false,
        callback: (r) => {
            cur_frm.reload_doc()
        }
    })

}
var existing_po = false
frappe.ui.form.on('Order', {
    onload_post_render: function(){
        if(!cur_frm.is_new()) {
            document.querySelectorAll("[data-doctype='Purchase Order']")[2].style.display = "none";
            document.querySelectorAll("[data-doctype='Payment Entry']")[2].style.display = "none";
        }
    },
    onload: function(){
        var item_name_master = frappe.meta.get_docfield("Order Item", "item_name_master", cur_frm.doc.name);
        var item_name = frappe.meta.get_docfield("Order Item", "item_name", cur_frm.doc.name);
        var item_description = frappe.meta.get_docfield("Order Item", "item_description", cur_frm.doc.name);

        item_name_master.read_only = !cur_frm.doc.reorder
        item_name.read_only = cur_frm.doc.reorder
        item_description.read_only = cur_frm.doc.reorder
    },
    refresh: function () {
        if(!cur_frm.doc.docstatus && !cur_frm.is_new() && cur_frm.doc.with_sku > 0){
            cur_frm.page.add_action_item(__("Approve SKU"), function() {
               change_status(cur_frm,"SKU Approved")

            });
            cur_frm.page.add_action_item(__("Reject SKU"), function() {
               change_status(cur_frm,"SKU Rejected")

            });
        }
         cur_frm.call({
            doc: cur_frm.doc,
            method: 'check_po',
            args: {},
            freeze: true,
            freeze_message: "Check PO...",
            async: false,
            callback: (r) => {
                existing_po = r.message
             }
        })
       cur_frm.set_query('requirement', () => {
            return {
                filters: [
                        ["docstatus", "=", 1]
                    ]
            }
        })
        var item_name_master = frappe.meta.get_docfield("Order Item", "item_name_master", cur_frm.doc.name);
        var item_name = frappe.meta.get_docfield("Order Item", "item_name", cur_frm.doc.name);
        var item_description = frappe.meta.get_docfield("Order Item", "item_description", cur_frm.doc.name);

        item_name_master.read_only = !cur_frm.doc.reorder
        item_name.read_only = cur_frm.doc.reorder
        item_description.read_only = cur_frm.doc.reorder
            if(!cur_frm.doc.docstatus && !cur_frm.is_new() && cur_frm.doc.status === "Pending" && cur_frm.doc.with_sku < 1){
                var button1 = cur_frm.add_custom_button(__("Identifying Competitor Product"), () => {
                    change_status(cur_frm,"Identifying Competitor Product")
                }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
            } else if(cur_frm.doc.status === "SKU Approved"){
                cur_frm.page.clear_actions_menu()
                cur_frm.disable_save()

                 var button1 = cur_frm.add_custom_button(__("Identifying Competitor Product"), () => {
                    change_status(cur_frm,"Identifying Competitor Product")
                }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
            } else if(cur_frm.doc.status === "Approved" && !existing_po){
                 cur_frm.page.clear_actions_menu()
                cur_frm.disable_save()
                      var button4 = cur_frm.add_custom_button(__("Purchase Order"), () => {
                            cur_frm.call({
                                doc: cur_frm.doc,
                                method: 'generate_po',
                                args: {},
                                freeze: true,
                                freeze_message: "Generating Purchase Order...",
                                async: false,
                                callback: (r) => {
                                    cur_frm.reload_doc()
                                    frappe.set_route("Form", "Purchase Order", r.message);
                                }
                            })
                        }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});

            } else if(cur_frm.doc.status === "Approved" && existing_po){
                 cur_frm.page.clear_actions_menu()
                cur_frm.disable_save()


            } else if(cur_frm.doc.status === "Rejected"){
                 cur_frm.page.clear_actions_menu()
                cur_frm.enable_save()

            } else if(cur_frm.doc.status === "SKU Rejected"){
                 cur_frm.page.clear_actions_menu()
                cur_frm.enable_save()

            } else if(cur_frm.doc.status === "Identifying Competitor Product"){

                cur_frm.page.clear_actions_menu()
                cur_frm.disable_save()
                var button1 = cur_frm.add_custom_button(__("Checking Requirement"), () => {
                    change_status(cur_frm,"Checking Requirement")
                }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
            } else  if( cur_frm.doc.status === "Checking Requirement"){

                cur_frm.page.clear_actions_menu()
                cur_frm.disable_save()
                var button2 = cur_frm.add_custom_button(__("Finalizing Order Quantity"), () => {
                        change_status(cur_frm,"Finalizing Order Quantity")
                }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
            } else  if(cur_frm.doc.status === "Finalizing Order Quantity"){
                cur_frm.page.clear_actions_menu()
                cur_frm.disable_save()

                var button3 = cur_frm.add_custom_button(__("Negotiating Price"), () => {
                    change_status(cur_frm,"Negotiating Price")
                }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});

            } else if (cur_frm.doc.status === "Negotiating Price"){
                cur_frm.page.clear_actions_menu()
                cur_frm.disable_save()

                cur_frm.page.add_action_item(__("Approve"), function() {
                    change_status(cur_frm,"Approved")

                });
                cur_frm.page.add_action_item(__("Reject"), function() {
                   change_status(cur_frm,"Rejected")

                });

            }

        if(cur_frm.doc.advance_payment){
           cur_frm.add_custom_button(__("Payment Entry"), () => {
                cur_frm.call({
                    doc: cur_frm.doc,
                    method: 'generate_payment_entry',
                    args: {},
                    freeze: true,
                    freeze_message: "Generating Payment Entry...",
                    async: false,
                    callback: (r) => {
                        cur_frm.reload_doc()
                    }
                })
            }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
        }
    },
	reorder: function(frm) {
        cur_frm.clear_table("order_items")
        cur_frm.doc.requirement = ""
        cur_frm.refresh_field("order_items")
        cur_frm.refresh_field("requirement")
        var item_name_master = frappe.meta.get_docfield("Order Item", "item_name_master", cur_frm.doc.name);
        var item_name = frappe.meta.get_docfield("Order Item", "item_name", cur_frm.doc.name);
        var item_description = frappe.meta.get_docfield("Order Item", "item_description", cur_frm.doc.name);
        item_name_master.read_only = !cur_frm.doc.reorder
        item_name.read_only = cur_frm.doc.reorder
        item_description.read_only = cur_frm.doc.reorder
    },
    requirement: function(frm) {
	    cur_frm.clear_table("order_items")
        cur_frm.refresh_field("order_items")
	    if(cur_frm.doc.requirement && cur_frm.doc.country){
	       cur_frm.call({
                doc: cur_frm.doc,
                method: 'add_item',
                args: {},
                freeze: true,
                freeze_message: "Adding Items",
                async: false,
                callback: (r) => {
                    cur_frm.refresh_field("order_items")
                }
            })
        }

    },
    country: function(frm) {
	    cur_frm.clear_table("order_items")
        cur_frm.refresh_field("order_items")
	    if(cur_frm.doc.requirement && cur_frm.doc.country){
	       cur_frm.call({
                doc: cur_frm.doc,
                method: 'add_item',
                args: {},
                freeze: true,
                freeze_message: "Adding Items",
                async: false,
                callback: (r) => {
                    cur_frm.refresh_field("order_items")
                }
            })
        }

    },
    create_items: function(frm) {
	    if(!cur_frm.doc.reorder){
	       cur_frm.call({
                doc: cur_frm.doc,
                method: 'create_items',
                args: {},
                freeze: true,
                freeze_message: "Creating Items....",
                async: false,
                callback: (r) => {
                    if(r.message){
                                                cur_frm.reload_doc()

                         frappe.show_alert({
                            message:__('Items Created'),
                            indicator:'green'
                        }, 3);
                    }

                }
            })
        }

    },
    existing_supplier: function(frm) {
            cur_frm.doc.supplier_master = ""
            cur_frm.doc.supplier = ""
            cur_frm.doc.supplier_name = ""
            cur_frm.refresh_field("supplier_master")
            cur_frm.refresh_field("supplier")
            cur_frm.refresh_field("supplier_name")
    }
});

