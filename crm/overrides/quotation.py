# import frappe
from frappe import _
from erpnext.selling.doctype.quotation.quotation import Quotation


class CustomQuotation(Quotation):
	@staticmethod
	def default_list_data():
		columns = [
			{
				'label': 'Title',
				'type': 'Data',
				'key': 'title',
				'width': '17rem',
			},
			{
				'label': 'Status',
				'type': 'Data',
				'key': 'status',
				'width': '17rem',
				'color': 'green',
			},
			{
				'label': 'Date',
				'type': 'Date',
				'key': 'transaction_date',
				'width': '17rem',
			},
			{
				'label': 'Grand Total',
				'type': 'Data',
				'key': 'base_grand_total',
				'width': '17rem',
			},
			{
				'label': 'Id',
				'type': 'Data',
				'key': 'name',
				'width': '17rem',
			},
			
		]
		rows = [
			'customer_name',
			'status',
			'transaction_date',
			'base_grand_total',
			'name'
			
		]
		return {'columns': columns, 'rows': rows}