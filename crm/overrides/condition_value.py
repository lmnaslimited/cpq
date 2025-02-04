# import frappe
from frappe import _
from crm.cpq.doctype.condition_value.condition_value import ConditionValue


class CustomConditionValue(ConditionValue):
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
				'label': 'Condition Type',
				'type': 'Data',
				'key': 'condition_type',
				'width': '17rem',
			},
            
		]
		rows = [
			"name",
            "condition_type"
		]
		return {'columns': columns, 'rows': rows}