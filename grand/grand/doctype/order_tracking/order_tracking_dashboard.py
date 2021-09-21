from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'order_tracking',
		'transactions': [
			{
				'label': _('Linked Forms'),
				'items': ['Order Tracking']
			}
		]
	}