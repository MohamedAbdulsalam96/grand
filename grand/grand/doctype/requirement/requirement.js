// Copyright (c) 2021, sammish and contributors
// For license information, please see license.txt
var existing_order = false
frappe.ui.form.on('Requirement', {
    onload_post_render: function(){
        if(!cur_frm.is_new()) {
            document.querySelectorAll("[data-doctype='Order']")[2].style.display = "none";
        }
    },
    create_supplier: function(frm) {
	    if(cur_frm.doc.supplier){
	       cur_frm.call({
                doc: cur_frm.doc,
                method: 'create_supplier',
                args: {},
                freeze: true,
                freeze_message: "Creating Supplier....",
                async: false,
                callback: (r) => {
                    if(r.message){
                        cur_frm.reload_doc()
                         frappe.show_alert({
                            message:__('Supplier Created'),
                            indicator:'green'
                        }, 3);
                    }

                }
            })
        }

    },
	refresh: function(frm) {
	     cur_frm.call({
            doc: cur_frm.doc,
            method: 'check_order',
            args: {},
            freeze: true,
            freeze_message: "Changing Status...",
            async: false,
            callback: (r) => {
                existing_order = r.message
             }
        })
	    if(cur_frm.doc.docstatus && cur_frm.doc.status === "Identifying Supplier"){
	        cur_frm.add_custom_button(__("Checking Quality"), () => {
                cur_frm.call({
                    doc: cur_frm.doc,
                    method: 'change_status',
                    args: {
                      status: "Checking Quality"
                    },
                    freeze: true,
                    freeze_message: "Changing Status...",
                    async: false,
                    callback: (r) => {
                        cur_frm.reload_doc()
                    }
                })
            }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
        } else  if(cur_frm.doc.docstatus && cur_frm.doc.status === "Checking Quality"){
	        cur_frm.add_custom_button(__("Waiting for Quote"), () => {
                cur_frm.call({
                    doc: cur_frm.doc,
                    method: 'change_status',
                    args: {
                      status: "Waiting for Quote"
                    },
                    freeze: true,
                    freeze_message: "Changing Status...",
                    async: false,
                    callback: (r) => {
                        cur_frm.reload_doc()
                    }
                })
            }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
        } else  if(cur_frm.doc.docstatus && cur_frm.doc.status === "Waiting for Quote"){
	        cur_frm.add_custom_button(__("Negotiating Price & MOQ"), () => {
                cur_frm.call({
                    doc: cur_frm.doc,
                    method: 'change_status',
                    args: {
                      status: "Negotiating Price & MOQ"
                    },
                    freeze: true,
                    freeze_message: "Changing Status...",
                    async: false,
                    callback: (r) => {
                        cur_frm.reload_doc()
                    }
                })
            }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
        } else  if(cur_frm.doc.docstatus && cur_frm.doc.status === "Negotiating Price & MOQ"){
	        cur_frm.add_custom_button(__("Quotation Sent"), () => {
                cur_frm.call({
                    doc: cur_frm.doc,
                    method: 'change_status',
                    args: {
                      status: "Quotation Sent"
                    },
                    freeze: true,
                    freeze_message: "Changing Status...",
                    async: false,
                    callback: (r) => {
                        cur_frm.reload_doc()
                    }
                })
            }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
        } else  if(cur_frm.doc.docstatus && cur_frm.doc.status === "Quotation Sent"){
	        cur_frm.add_custom_button(__("Approve"), () => {
                cur_frm.call({
                    doc: cur_frm.doc,
                    method: 'change_status',
                    args: {
                      status: "Approved"
                    },
                    freeze: true,
                    freeze_message: "Changing Status...",
                    async: false,
                    callback: (r) => {
                        cur_frm.reload_doc()
                    }
                })
            }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});

	        cur_frm.add_custom_button(__("Reject"), () => {
                cur_frm.call({
                    doc: cur_frm.doc,
                    method: 'change_status',
                    args: {
                      status: "Rejected"
                    },
                    freeze: true,
                    freeze_message: "Changing Status...",
                    async: false,
                    callback: (r) => {
                        cur_frm.reload_doc()
                    }
                })
            }).css({'color':'white','font-weight': 'bold', 'background-color': 'red'});
        }
        else  if(cur_frm.doc.docstatus && cur_frm.doc.status === "Approved" && !existing_order){
	        cur_frm.add_custom_button(__("Create Orders"), () => {
                cur_frm.call({
                    doc: cur_frm.doc,
                    method: 'create_order',
                    args: {},
                    freeze: true,
                    freeze_message: "Creating Orders...",
                    async: false,
                    callback: (r) => {
                        cur_frm.reload_doc()
                         frappe.show_alert({
                            message:__('Orders Created'),
                            indicator:'green'
                        }, 3);
                    }
                })
            }).css({'color':'white','font-weight': 'bold', 'background-color': 'blue'});
        }

	}
});
