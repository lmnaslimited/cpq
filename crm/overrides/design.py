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
				'width': '12rem',
			},
			{
				'label': 'Total Cost',
				'type': 'Data',
				'key': 'total_cost',
				'width': '12rem',
			},
		]
		rows = [
			"name",
			"status",
			"design_template",
			"total_cost"
		]
		return {'columns': columns, 'rows': rows}