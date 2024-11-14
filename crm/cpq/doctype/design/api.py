import frappe
from frappe import _

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script

@frappe.whitelist()
def get_design(name):
    Design = frappe.qb.DocType("Design")
    query = frappe.qb.from_(Design).select("*").where(Design.name == name).limit(1)
    design = query.run(as_dict=True)
    if not len(design):
        frappe.throw(_("Design not found"), frappe.DoesNotExistError)
    design = design.pop()
    design["doctype"] = "Design"
    design["fields_meta"] = get_fields_meta("Design")
    design["_form_script"] = get_form_script('Design')
    design["_assign"] = get_assigned_users("Design", design.name, design.owner)
    return design

@frappe.whitelist()
def get_item_variant():
  item_variant = frappe.get_list("Item", filters={"has_variants": 1})
  item_names = [item['name'] for item in item_variant]
  return item_names

@frappe.whitelist()
def get_formatted_item_details(item_name):
    try:
        # Fetch the item document to get the list of attributes
        item = frappe.get_doc("Item", item_name)
        attribute_names = [attr.attribute for attr in item.attributes]
        
        sql = f"""
        SELECT `name`, `attribute_name`, `numeric_values`, `from_range`, `to_range`, `increment`
        FROM `tabItem Attribute`
        WHERE `name` IN ({','.join(['%s']*len(attribute_names))})
        ORDER BY FIELD(`name`, {','.join(['%s']*len(attribute_names))})
        """

        attributes = frappe.db.sql(sql, tuple(attribute_names + attribute_names), as_dict=True)

        # Prepare list to store fields
        fields = []
        
        # Loop over attributes and fetch options if needed
        for attribute in attributes:
            if attribute.numeric_values:
                # Range type field setup
                field = {
                    "label": attribute.attribute_name,
                    "name": attribute.attribute_name.replace(" ", "_").lower(),
                    "type": "Range",
                    "numeric_values": 1,
                    "min": attribute.from_range,
                    "max": attribute.to_range,
                    "step": attribute.increment
                }
            else:
                # Select type field setup with options
                options = frappe.get_all("Item Attribute Value",
                                         filters={"parent": attribute.name},
                                         fields=["attribute_value"],
                                         order_by="idx ASC")
                
                field = {
                    "label": attribute.attribute_name,
                    "name": attribute.attribute_name.replace(" ", "_").lower(),
                    "type": "Select",
                    "numeric_values": 0,
                    "options": [{"label": val.attribute_value, "value": val.attribute_value} for val in options]
                }
            
            fields.append(field)
        
        return fields

    except frappe.DoesNotExistError:
        frappe.throw(_("Item not found"))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching item details"))
        frappe.throw(_("Could not fetch item details"))
