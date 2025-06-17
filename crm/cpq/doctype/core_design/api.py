import frappe
import json
from frappe import _

@frappe.whitelist()
def get_formated_item_variants(item_template):

    item = frappe.get_all(
        "Item", 
        filters={"item_code":item_template}, 
        fields=[
            "`tabItem Variant Attribute`.attribute",
            "`tabItem Variant Attribute`.attribute_value",
            "`tabItem Variant Attribute`.numeric_values",
            "`tabItem Variant Attribute`.from_range",
            "`tabItem Variant Attribute`.increment",
            "`tabItem Variant Attribute`.to_range",
        ])
        
    non_numeric = [record.attribute for record in item if not record.numeric_values]
    non_numeric_options_map = {}
    if non_numeric:
        all_options = frappe.get_all(
            "Item Attribute Value",
            filters={"parent": ["in", non_numeric]},
            fields=["parent", "attribute_value"],
            order_by="idx ASC"
        )
        for row in all_options:
            #setdefault is a python build in method for grouping
            non_numeric_options_map.setdefault(row.parent, []).append({
                "label": row.attribute_value,
                "value": row.attribute_value
            })
            
    la_fields = []

    for ld_attribute in item:
        if ld_attribute.numeric_values:
            ld_field = {
                "label": ld_attribute.attribute,
                "fieldname": ld_attribute.attribute.replace(" ", "_").lower(),
                "fieldtype": "range",
                "numeric_values": 1,
                "min": ld_attribute.from_range,
                "max": ld_attribute.to_range,
                "step": ld_attribute.increment,
                "from_range": ld_attribute.from_range,
                "to_range": ld_attribute.to_range,
                "increment": ld_attribute.increment,
                "default": ld_attribute.attribute_value
            }
        else:
            ld_field = {
                "label": ld_attribute.attribute,
                "fieldname": ld_attribute.attribute.replace(" ", "_").lower(),
                "fieldtype": "select",
                "numeric_values": 0,
                "default": ld_attribute.attribute_value,
                "from_range": ld_attribute.from_range,
                "to_range": ld_attribute.to_range,
                "increment": ld_attribute.increment,
                "options": non_numeric_options_map[ld_attribute.attribute]
            }
        la_fields.append(ld_field)


    return la_fields