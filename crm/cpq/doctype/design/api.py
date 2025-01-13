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
def fn_get_item_variant():
    '''
    This api return item template name in an array
    '''
    la_item_variant = frappe.get_list("Item", filters={"has_variants": 1})
    la_item_names = [ld_item['name'] for ld_item in la_item_variant]
    return la_item_names


@frappe.whitelist()
def fn_get_formatted_item_details(item_name):
    """
    Fetches and formats the attributes for a given item.

    This API retrieves attributes associated with an item and returns them as a structured list. 
    Each attribute is represented as a field configuration, specifying whether it is a range-based 
    field or a select-type field. The configuration includes default values, options, and range specifications where applicable.

    Parameters:
        item_name (str): The name of the item for which attributes need to be fetched.

    Returns:
        list[dict]: A list of dictionaries representing attribute field configurations. 
        Each dictionary includes:
            - `label`, `name` ,`type` ,`numeric_values` ,`min` ,`max` ,`step` ,`default` ,`options` 

    Raises:
        DoesNotExistError: If the specified item does not exist.
        Exception: If any other error occurs, the error is logged and a user-friendly message is thrown.
    """
    try:
        # Fetch the item document to get the list of attributes
        ld_item = frappe.get_doc("Item", item_name)
        # Prepare a list of attributes and their default values
        la_attribute_names = []
        ld_attribute_defaults = {}  # Dictionary to hold custom default values for each attribute

        for ld_attribute in ld_item.attributes:
            la_attribute_names.append(ld_attribute.attribute)
            ld_attribute_defaults[ld_attribute.attribute] = ld_attribute.attribute_value  # Store default value for each attribute
        
        
        l_sql = f"""
        SELECT `name`, `attribute_name`, `numeric_values`, `from_range`, `to_range`, `increment`
        FROM `tabItem Attribute`
        WHERE `name` IN ({','.join(['%s']*len(la_attribute_names))})
        ORDER BY FIELD(`name`, {','.join(['%s']*len(la_attribute_names))})
        """

        la_attributes = frappe.db.sql(l_sql, tuple(la_attribute_names + la_attribute_names), as_dict=True)

        # Prepare list to store fields
        la_fields = []
        
        # Loop over attributes and fetch options if needed
        for ld_attribute in la_attributes:
            # Get the custom default value for the current attribute
            l_default_value = ld_attribute_defaults.get(ld_attribute.attribute_name, None)

            if ld_attribute.numeric_values:
                # Range type field setup
                ld_field = {
                    "label": ld_attribute.attribute_name,
                    "name": ld_attribute.attribute_name.replace(" ", "_").lower(),
                    "type": "Range",
                    "numeric_values": 1,
                    "min": ld_attribute.from_range,
                    "max": ld_attribute.to_range,
                    "step": ld_attribute.increment,
                    "from_range": ld_attribute.from_range,
                    "to_range": ld_attribute.to_range,
                    "increment": ld_attribute.increment,
                    "default": l_default_value
                }
            else:
                # Select type field setup with options
                la_options = frappe.get_all("Item Attribute Value",
                                         filters={"parent": ld_attribute.name},
                                         fields=["attribute_value"],
                                         order_by="idx ASC")
                
                ld_field = {
                    "label": ld_attribute.attribute_name,
                    "name": ld_attribute.attribute_name.replace(" ", "_").lower(),
                    "type": "Select",
                    "numeric_values": 0,
                    "default": l_default_value,
                    "from_range": ld_attribute.from_range,
                    "to_range": ld_attribute.to_range,
                    "increment": ld_attribute.increment,
                    "options": [{"label": ld_option.attribute_value, "value": ld_option.attribute_value} for ld_option in la_options]
                }
            
            la_fields.append(ld_field)
        
        return la_fields

    except frappe.DoesNotExistError:
        frappe.throw(_("Item not found"))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching item details"))
        frappe.throw(_("Could not fetch item details"))
