import frappe
import json
from frappe import _
from crm.api.doc import get_assigned_users, get_fields_meta
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script


@frappe.whitelist()
def get_doc_details(doctype, name):
    id_doc = frappe.get_doc(doctype, name)
    id_doc.check_permission("read")

    id_doc = id_doc.as_dict()
    id_doc["fields_meta"] = get_fields_meta(doctype)
    id_doc["_form_script"] = get_form_script(doctype)
    id_doc["_assign"] = get_assigned_users(doctype, id_doc["name"])

    return id_doc

'''
This API is replicated version of original delete_items
'''

@frappe.whitelist()
def delete_items():
    """delete selected items"""

    items = sorted(json.loads(frappe.form_dict.get("items")), reverse=True)
    doctype = frappe.form_dict.get("doctype")

    if len(items) > 10:
        frappe.enqueue("frappe.desk.reportview.delete_bulk", doctype=doctype, items=items)
    else:
        return delete_bulk(doctype, items)
    
def delete_bulk(doctype, items):
    undeleted_items = []
    for i, d in enumerate(items):
        try:
            frappe.delete_doc(doctype, d)
            if len(items) >= 5:
                frappe.publish_realtime(
                    "progress",
                    dict(
                        progress=[i + 1, len(items)],
                        title=_("Deleting {0}").format(doctype),
                        description=d
                    ),
                    user=frappe.session.user,
                )
            # Commit after successful deletion
            frappe.db.commit()
        except Exception:
            # Rollback if any record failed to delete
            undeleted_items.append(d)
            frappe.db.rollback()

    if undeleted_items and len(items) != len(undeleted_items):
        frappe.clear_messages()
        return delete_bulk(doctype, undeleted_items)
    elif undeleted_items:
        error_message = _("Failed to delete {0} documents: {1}").format(len(undeleted_items), ", ".join(undeleted_items))
        frappe.msgprint(
            error_message,
            realtime=True,
            title=_("Bulk Operation Failed"),
        )
        return {"status": "error", "message": error_message}
    else:
        success_message = _("Deleted all documents successfully")
        frappe.msgprint(
            success_message, realtime=True, title=_("Bulk Operation Successful")
        )
        return {"status": "success", "message": success_message}

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
                    "fieldname": ld_attribute.attribute_name.replace(" ", "_").lower(),
                    "fieldtype": "Range",
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
                    "fieldname": ld_attribute.attribute_name.replace(" ", "_").lower(),
                    "fieldtype": "Select",
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

@frappe.whitelist()
def fn_create_item_from_design(design_name):
    """
    Creates a new item variant based on the details from the specified design document. 
    This function uses the design template to fetch the item template and associated attributes, 
    creates a new item variant, and updates it with the relevant attributes from the design document. 
    It also creates a standard selling price for the new item based on the design's total cost.

    Parameters:
    - design_name (str): The name of the design document to fetch the item details from.

    Returns:
    - str: The item code of the newly created item variant.
    
    Raises:
    - frappe.exceptions.ValidationError: If the design template is not specified in the design document.
    """

    #get the details of the design
    ld_design_doc = frappe.get_doc("Design", design_name)

    if not ld_design_doc.design_template:
        frappe.throw(__('Design Template is not specified in the design document.'))

    #get the details of the item template
    ld_template_item = frappe.get_doc("Item", ld_design_doc.design_template)

    #Forming a dictionary with key as variant's name and value as is_numeric
    ld_template_attributes = {
        attr.attribute: attr.numeric_values for attr in ld_template_item.attributes
    }

    #replacing space with - for item name and code formation
    la_attribute_values = [
        attribute.attribute_value.replace(" ", "-")
        for attribute in ld_design_doc.design_attributes
        if attribute.attribute in ld_template_attributes
    ]
    l_item_code = f"{ld_design_doc.design_template}-" + "-".join(la_attribute_values)

    ld_item_variant = frappe.new_doc("Item")
    ld_item_variant.item_code = l_item_code
    ld_item_variant.item_name = l_item_code
    ld_item_variant.item_group = ld_template_item.item_group
    ld_item_variant.is_stock_item = ld_template_item.is_stock_item
    ld_item_variant.variant_of = ld_design_doc.design_template
    ld_item_variant.stock_uom = ld_template_item.stock_uom
    ld_item_variant.include_item_in_manufacturing = 0

    for ld_attribute in ld_design_doc.design_attributes:
        if ld_attribute.attribute in ld_template_attributes:

            l_numeric_value = ld_template_attributes[ld_attribute.attribute]
            
            ld_item_variant.append("attributes", {
                "attribute": ld_attribute.attribute,
                "attribute_value": ld_attribute.attribute_value,
                "numeric_values": l_numeric_value
            })

    ld_item_variant.insert()
    frappe.db.commit()

    # Create a "Standard Selling" price list for this item
    ld_item_price = frappe.new_doc("Item Price")
    ld_item_price.item_code = ld_item_variant.item_code
    ld_item_price.price_list = "Standard Selling"
    ld_item_price.price_list_rate = ld_design_doc.total_cost
    ld_item_price.insert()
    return ld_item_variant.item_code
