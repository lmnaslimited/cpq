from frappe import _
from crm.cpq.doctype.condition_type.condition_type import ConditionType


class CustomConditionType(ConditionType):
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
				'label': 'Document Reference',
				'type': 'Data',
				'key': 'document_reference',
				'width': '17rem',
			},
            
		]
		rows = [
			"name",
            "document_reference"
		]
		return {'columns': columns, 'rows': rows}