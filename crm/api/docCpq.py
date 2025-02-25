import frappe
import json
from frappe import _
from frappe.model.document import get_controller, Document
from frappe.model import no_value_fields
from pypika import Criterion
from frappe.utils import make_filter_tuple, get_url_to_list
from crm.api.views import get_views
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_fields_layout.crm_fields_layout import get_sidepanel_sections as get_sidebar_fields

from functools import lru_cache

from sql_metadata import Parser

from frappe.core.doctype.access_log.access_log import make_access_log
from frappe.model import child_table_fields, default_fields, get_permitted_fields, optional_fields
from frappe.model.base_document import get_controller
from frappe.model.db_query import DatabaseQuery
from frappe.model.utils import is_virtual_doctype
from frappe.utils import add_user_info, cint, format_duration
from frappe.utils.data import sbool

@frappe.whitelist()
def fn_get_sidebar_fields_with_table(doctype, name):
    """
    Retrieves the sidebar fields and their corresponding child table data for a given doctype and document name.

    This function extends the functionality of the original `get_sidebar_fields` method by enriching 
    fields of type "Table" with additional data. For each "Table" field, child records are fetched 
    from the corresponding child doctype, and relevant field attributes such as type, options, and values 
    are added to the field definition.

    Parameters:
    - doctype (str): The name of the doctype for which the sidebar fields are fetched.
    - name (str): The name of the document instance from which the sidebar fields are derived.

    Returns:
    - list: A list of dictionaries representing the sections and their fields, with child table data 
            included for fields of type "Table". Each field will include an additional "children" key, 
            which contains the relevant child records for that table.
    """
    # Call the original get_sidebar_fields function to get the layout
    la_layout = get_sidebar_fields(doctype, name)

    # Loop through each section in the layout
    for ld_section in la_layout:
        # Iterate over fields in the section
        for ld_field in ld_section.get("fields", []):
            
            # If the field type is Table
             if isinstance(ld_field, dict) and ld_field.get("type") == "Table":
                l_child_doctype = ld_field.get("options")  # Get the child doctype from options
 
                # Query the child doctype where parent matches the name
                la_child_records = frappe.get_all(l_child_doctype, filters={"parent": name}, fields=["*"], order_by="idx ASC")
              
                ld_field["children"] = []

                # Loop through each child record
                for ld_record in la_child_records:
                   
                    # Determine field type based on numeric_values
                    #mostly the type is "data" or "select"
                    if ld_record.get("numeric_values") == 1:
                        l_field_type = "data"
                    else:
                        l_field_type = "select"

                    # In order to get option for the non numeric field
                    # query the doctype mentioned in the link key
                    if ld_field.get("link"):
            
                        l_attribute_value = ld_record.get("attribute")
                        la_options = frappe.get_all(ld_field.get("link"), filters={"parent": l_attribute_value}, fields=["attribute_value"])
                        
                        # Extracting the attribute_value into an array
                        la_options = [ld_option.get("attribute_value") for ld_option in la_options]

                    else:
                        la_options = None

                    # Push properties into children maintaining structure for front-end
                    ld_field["children"].append({
                        "label": ld_record.get("attribute", ''),
                        "type": l_field_type,
                        "name": "attribute_value",
                        "from_range": ld_record.get("from_range"),
                        "to_range": ld_record.get("to_range"),
                        "increment": ld_record.get("increment"),
                        "value": ld_record.get("attribute_value", ''),
                        "hidden": ld_record.get("hidden", False),
                        "reqd": ld_record.get("reqd", False),
                        "read_only": ld_record.get("read_only", False),
                        "placeholder": ld_record.get("placeholder", ''),
                        "options": la_options,
                        "doctype": ld_field.get("options"),
                        "parent": ld_record.get("parent"),
                        "default_value": ld_record.get("custom_default_value")
                    })

    return la_layout

@frappe.whitelist()
def fn_update_child_table(doctype, doc_name, field_name, new_value, target_fieldname):
    """
    Updates the 'attribute_value' field for a specific attribute in a child doctype linked to a parent document.

    This function searches for a child record in the specified 'doctype' where the 'parent' matches the 
    provided 'doc_name' and the 'attribute' matches the 'field_name'. If such a record is found, it updates 
    the 'attribute_value' to the new value specified. 

    Parameters:
    - doctype (str): The name of the child doctype to search for.
    - doc_name (str): The name of the parent document to look for in the child records.
    - field_name (str): The name of the field in the child record that identifies the attribute to be updated.
    - new_value (str): The new value to set for the 'attribute_value' field.
    - target_filename(str): the child table field your are updating the value
    Returns:
    - dict: A dictionary with a success message if the update was successful, or an error message if it failed.
    """
    try:
        # get the attribute detail from child doctype
        la_child_docs = frappe.get_all(doctype,
            filters={
                "parent": doc_name,
                "attribute": field_name
            },
            limit=1 
        )
        if not la_child_docs:
            return {"error": _("Attribute not found for the specified parent.")}

        try:
            # Update the attribute_value directly
            frappe.db.set_value(doctype, la_child_docs[0].name, target_fieldname, new_value)

            return {"message": _("Updated successfully")}
        except frappe.exceptions.ValidationError as ve:
            return {"error": _("Validation Error: {}".format(str(ve)))}
    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        return {"error": _("Failed to update: {}".format(str(e)))}


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

@frappe.whitelist()
def get_navigate_url(doctype, name):
    url = get_url_to_list(doctype)
    return f"{url}/{name}"


@frappe.whitelist()
def get_item(name):
    Item = frappe.qb.DocType("Item")
    query = frappe.qb.from_(Item).select("*").where(Item.name == name).limit(1)
    item = query.run(as_dict=True)
    if not len(item):
        frappe.throw(_("Item not found"), frappe.DoesNotExistError)
    item = item.pop()
    item["doctype"] = "Item"
    item["fields_meta"] = get_fields_meta("Item")
    item["_form_script"] = get_form_script('Item')
    item["_assign"] = get_assigned_users("Item", item.name, item.owner)
    return item

@frappe.whitelist()
def get_quotation(name):
    Quotation = frappe.qb.DocType("Quotation")
    query = frappe.qb.from_(Quotation).select("*").where(Quotation.name == name).limit(1)
    quotation = query.run(as_dict=True)
    if not len(quotation):
        frappe.throw(_("Quotation not found"), frappe.DoesNotExistError)
    quotation = quotation.pop()
    quotation["doctype"] = "Quotation"
    quotation["fields_meta"] = get_fields_meta("Quotation")
    quotation["_form_script"] = get_form_script('Quotation')
    quotation["_assign"] = get_assigned_users("Quotation", quotation.name, quotation.owner)
    return quotation

@frappe.whitelist()
def fn_get_table_rows_columns(doctype, docname):
    """
    Fetches the metadata and rows for all table fields in a specified parent document.
    The function identifies fields of type "Table" in the parent doctype, retrieves their metadata 
    from the child doctype, and returns both the metadata (column structure) and the rows (data) 
    from the child tables linked to the parent document.

    Parameters:
    - doctype (str): The name of the parent doctype (e.g., 'Sales Order').
    - docname (str): The name of the specific parent document (e.g., 'SO-0001').

    Returns:
    - dict: A dictionary containing:
        - 'columns': A list of metadata for fields in child doctypes (columns). 
          Each entry includes fieldname, label, fieldtype, options, etc.
        - 'rows': A dictionary where each key is the fieldname of a table field, and 
          the corresponding value is a list of child records (rows) for that table.
    """
    # Fetch metadata of the parent doctype
    ld_parent_meta = frappe.get_meta(doctype)
    la_table_fields = []

    # Identify fields of type "Table"
    for ld_field in ld_parent_meta.fields:
        if ld_field.fieldtype == "Table":
            la_table_fields.append({
                "fieldname": ld_field.fieldname,
                "options": ld_field.options  # Child table doctype
            })

    # Prepare the response
    ld_result = {
        "columns": [],
        "rows": {}
    }

    # Iterate through the table fields to fetch child metadata and rows
    for ld_table_field in la_table_fields:
        l_child_doctype = ld_table_field["options"]
        ld_child_meta = frappe.get_meta(l_child_doctype)

        # Append child metadata to columns
        ld_result["columns"].append({
            "fieldname": ld_table_field["fieldname"],
            "fields": [
                {
                    "fieldname": field.fieldname,
                    "label": field.label,
                    "fieldtype": field.fieldtype,
                    "options": field.options if hasattr(field, "options") else None,
                    "hidden": field.hidden,
                    "read_only": field.read_only
                }
                for field in ld_child_meta.fields
            ]
        })

        # Fetch rows for the child table
        la_rows = frappe.get_all(
            l_child_doctype,
            filters={"parent" : docname},
            fields="*"
        )
        ld_result["rows"][ld_table_field["fieldname"]] = la_rows

    return ld_result

@frappe.whitelist()
def fn_update_child_table_row(doctype, docname, child_field, values):
    """
    Updates or adds rows in a child table field of a specified document.

    This function updates the child table records based on a list of dictionaries provided in `values`.
    If the row exists, it is updated with the new values. If the row does not exist, a new row is added.
    Additionally, rows not included in the incoming data will be removed.

    Parameters:
    - doctype (str): The name of the parent document (e.g., 'Quotation').
    - docname (str): The name of the specific document to update (e.g., 'QTN-0001').
    - child_field (str): The name of the child table field in the parent document (e.g., 'items').
    - values (list of dict): A list of dictionaries where each dictionary represents a row to update or add. Each dictionary should contain the row's field values, including the unique 'name' field if updating existing rows.

    Returns:
    - dict: A dictionary containing the status of the operation and a message.
      Example: 
      {
          "status": "success", 
          "message": "Updated successfully.", 
          "doc": <updated document object>
      }
    """
    try:
        # Fetch the document
        ld_doc = frappe.get_doc(doctype, docname)

        # Ensure items are passed in the correct format
        if not isinstance(values, list):
            frappe.throw("Items must be a list of dictionaries.")

        # Get existing rows in the child table as a list
        ld_existing_rows = {row.name: row for row in getattr(ld_doc, child_field)}

        # Create a set of incoming names
        la_incoming_names = {value.get("name") for value in values}

        # Remove rows in the child table that are not in the incoming data
        ld_doc.set(child_field, [
            row for row in getattr(ld_doc, child_field) if row.name in la_incoming_names
        ])

        # Add or update rows
        for ld_value in values:
            l_existing_row = ld_existing_rows.get(ld_value.get("name"))

            if l_existing_row:
                # Update the existing row
                for field, field_value in ld_value.items():
                    setattr(l_existing_row, field, field_value)
            else:
                # If it's a new row (no name exists in the document), append it
                ld_doc.append(child_field, ld_value)
        
        # Save the updated document
        ld_doc.save()
        frappe.db.commit()
        ld_doc.reload()

        return {"status": "success", "message": "updated successfully.", "doc": ld_doc}

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Update Error")
        return {"status": "error", "message": str(e)}

# @frappe.whitelist()
# def fn_get_variant_attributes(name):
#     """
#     Fetch attributes of an Item variant.

#     Args:
#         item_name (str): The name of the Item.

#     Returns:
#         list: List of attributes from the Item's attribute child table.
#     """
#     try:
#         # Fetch the Item document
#         item = frappe.get_doc("Item", name)
#         return item.attributes

#     except frappe.DoesNotExistError:
#         return 'DoesNotExistError'
#         frappe.throw(_("Item with name '{0}' does not exist").format(name))
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Error in fn_get_variant_attributes api")
#         frappe.throw(_("An unexpected error occurred while fetching the item attributes."))

@frappe.whitelist()
def fn_get_item_attribute_record():
    la_attributes = frappe.get_all("Item Attribute", fields=["*"], filters={"custom_is_group": 0})
    for ld_attribute in la_attributes:
        
        ld_attribute["item_attribute_values"] = [
            la_value["attribute_value"] for la_value in frappe.get_all(
                "Item Attribute Value",
                filters={"parent": ld_attribute["name"]},
                fields=["attribute_value"]
            )
        ]
    return la_attributes


'''
This API is replicated version of original delete_items
'''

@frappe.whitelist()
def delete_items():
    """delete selected items"""
    import json

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


"""
    Process condition types for a given document and update target fields based on predefined conditions.

    This function retrieves applicable "Condition Type" records linked to the given document's Doctype.
    It evaluates whether conditions are met based on input sequences, and if so, updates the document's
    target fields with corresponding values.

    Parameters:
    doc (dict or str): The document object or its JSON string representation.

    Returns:
    list: A list of dictionaries containing the source and target field mappings applied.
"""
@frappe.whitelist()
def condition_type(doc):
    # If the doc is coming as a string, try converting it back to a dictionary
    if isinstance(doc, str):
        ld_doc = frappe.parse_json(doc)

    # Then you can safely call frappe.get_doc(doc)
    ld_doc = frappe.get_doc(doc)
    la_condition_types = frappe.get_list('Condition Type', filters={'document_reference': ld_doc.doctype})
    
    if not la_condition_types:
        return []
    
    la_result = []

    def fn_get_fieldname_from_label(doctype, label):
        """Get fieldname from label for a given DocType"""
        ld_meta = frappe.get_meta(doctype)
        for ld_field in ld_meta.fields:
            if ld_field.label == label:
                return ld_field.fieldname
        return None

    for ld_condition_type in la_condition_types:
        ld_condition_type_detail = frappe.get_doc('Condition Type', ld_condition_type.name)
        
        if not ld_condition_type_detail.enable:
            continue
        
        if ld_condition_type_detail.is_value_based:
            la_input_sequence = ld_condition_type_detail.input_sequence
            la_output_sequence = ld_condition_type_detail.output_sequence
            ld_condition_value = frappe.get_doc('Condition Value', {'condition_type': ld_condition_type_detail.name})
            
            access_key = ld_condition_value.access_key
            la_input_value = ld_condition_value.input_value
            la_output_value = ld_condition_value.output_value
            
            la_source_labels = access_key.split('/')
            la_source_fields = [fn_get_fieldname_from_label(ld_doc.doctype, label) for label in la_source_labels]
            la_source_fields_value = []
            input_index = 0
            
            for field in la_source_labels:
                la_matching_rows = [row for row in la_input_sequence if row.field_name == field]
                
                if la_matching_rows:
                    row_length = la_matching_rows[0].length                   
                    if input_index + row_length <= len(la_input_value):
                        extracted_value = la_input_value[input_index:input_index + row_length]
                    else:
                        extracted_value = la_input_value[input_index:].strip()
                    
                    extracted_value = extracted_value.strip()
                    la_source_fields_value.append(extracted_value)
                    input_index += row_length
            
            la_source = [{field: value} for field, value in zip(la_source_fields, la_source_fields_value)]
            
            # **Check if doc's source fields match expected values**
            source_conditions_met = all(str(ld_doc.get(field)) == str(value) for field, value in zip(la_source_fields, la_source_fields_value))
            
            if not source_conditions_met:
                continue  # Skip setting target values if conditions are not met
            
            la_target_labels = [field.field_name for field in la_output_sequence]
            la_target_fields = [fn_get_fieldname_from_label(ld_doc.doctype, label) for label in la_target_labels]
            la_target_fields_value = []
            output_index = 0
            
            for ld_field in la_output_sequence:
                row_length = ld_field.length
                
                if output_index + row_length <= len(la_output_value):
                    extracted_value = la_output_value[output_index:output_index + row_length]
                else:
                    extracted_value = la_output_value[output_index:].strip()
                
                extracted_value = extracted_value.strip()
                la_target_fields_value.append(extracted_value)
                output_index += row_length
            
            la_target = [{field: value} for field, value in zip(la_target_fields, la_target_fields_value)]
            
            # **Update doc's target fields using frappe.db.set_value**
            for field, value in zip(la_target_fields, la_target_fields_value):
                if field:  # Ensure fieldname exists before updating
                    frappe.db.set_value(ld_doc.doctype, ld_doc.name, field, value)
                    # ld_doc.set(field, value)

            # frappe.db.commit()
            
            la_result.append({'source': la_source, 'target': la_target})
        
        elif ld_condition_type_detail.is_api_based:
            pass
        
        elif ld_condition_type_detail.is_formula_based:
            pass
    
    return la_result
