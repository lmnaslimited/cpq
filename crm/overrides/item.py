# import frappe
from frappe import _
from erpnext.stock.doctype.item.item import Item


class CustomItem(Item):
	@staticmethod
	def default_list_data():
		columns = [
			{
				'label': 'Item Code',
				'type': 'Data',
				'key': 'item_code',
				'width': '17rem',
			},
            {
				'label': 'Item Group',
				'type': 'Data',
				'key': 'item_group',
				'width': '17rem',
			},
			{
				'label': 'Variant Of',
				'type': 'Data',
				'key': 'variant_of',
				'width': '17rem',
			},
            
			
		]
		rows = [
			"name",
            "item_group"
            "variant_of",
			
			
		]
		return {'columns': columns, 'rows': rows}