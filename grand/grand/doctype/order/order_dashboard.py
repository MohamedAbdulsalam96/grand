from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'order',
		'transactions': [
			{
				'label': _('Linked Forms'),
				'items': ['Purchase Order', 'Payment Entry']
			}
		]
	}