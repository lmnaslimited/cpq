from frappe import _
from crm.cpq.doctype.design.design import Design


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
				'label': 'Design Template',
				'type': 'Data',
				'key': 'design_template',
				'width': '8rem',
			},
		]
		rows = [
			"name",
			"status",
			"design_template",
		]
		return {'columns': columns, 'rows': rows}