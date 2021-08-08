frappe.listview_settings['Order'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (["Identifying Competitor Product",
                "Checking Requirement",
                "Finalizing Order Quantity",
                "Negotiating Price"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "orange", "status,=," + doc.status];
		} else if (["Rejected"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "red", "status,=," + doc.status];
		}else if (["Approved"].includes(doc.status)) {
			// Closed
			return [__(doc.status), "green", "status,=," + doc.status];
		}

	},
};