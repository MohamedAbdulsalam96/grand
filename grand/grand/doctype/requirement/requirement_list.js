frappe.listview_settings['Requirement'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["Identifying Supplier", "Checking Quality","Waiting for Quote", "Negotiating Price & MOQ", "Quotation Sent"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "orange", "status,=," + doc.status];
		}

	},
};