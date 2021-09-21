
frappe.listview_settings['Order Tracking'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["Pending","Waiting","In Production","Packing","Ready for Shipment","Waiting for Shipment", "Receiving to Store", "Dispatching to Store"].includes(doc.status)) {
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (["Shipped","Completed"].includes(doc.status)) {
			return [__(doc.status), "green", "status,=," + doc.status];
		}

	},
};