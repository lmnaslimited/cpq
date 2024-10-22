# import frappe
from frappe import _
from crm.fcrm.doctype.design.design import Design


class CustomDesign(Design):
	@staticmethod
	def default_list_data():
		columns = [
			{
				'label': 'Name',
				'type': 'Data',
				'key': 'name',
				'width': '17rem',
			},
			{
				'label': 'Status',
				'type': 'Data',
				'key': 'status',
				'width': '12rem',
			},
			{
				'label': 'Last Modified',
				'type': 'Datetime',
				'key': 'modified',
				'width': '8rem',
			},
		]
		rows = [
			"name",
			"status",
			"modified",
		]
		return {'columns': columns, 'rows': rows}
