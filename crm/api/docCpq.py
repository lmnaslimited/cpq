import frappe
import json
from frappe import _
from frappe.model.document import get_controller, Document
from frappe.model import no_value_fields
from pypika import Criterion
from frappe.utils import make_filter_tuple, get_url_to_list
from crm.api.views import get_views
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from crm.api.doc import get_sidebar_fields, get_fields_meta, get_assigned_users, get_field_obj


@frappe.whitelist()
def get_sidebar_fields_with_table(doctype, name):
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
                        "value": ld_record.get("attribute_value", ''),
                        "hidden": ld_field.get("hidden", False),
                        "reqd": ld_field.get("reqd", False),
                        "read_only": ld_field.get("read_only", False),
                        "placeholder": ld_field.get("placeholder", ''),
                        "options": la_options,
                        "doctype": ld_field.get("options"),
                        "parent": ld_record.get("parent")
                    })

    return la_layout

@frappe.whitelist()
def update_item_attribute(child_doctype, parent_docName, target_field, new_value):
    """
    Updates the 'attribute_value' field for a specific attribute in a child doctype linked to a parent document.

    This function searches for a child record in the specified 'child_doctype' where the 'parent' matches the 
    provided 'parent_docname' and the 'attribute' matches the 'target_field'. If such a record is found, it updates 
    the 'attribute_value' to the new value specified. 

    Parameters:
    - child_doctype (str): The name of the child doctype to search for.
    - parent_docname (str): The name of the parent document to look for in the child records.
    - target_field (str): The name of the field in the child record that identifies the attribute to be updated.
    - new_value (str): The new value to set for the 'attribute_value' field.

    Returns:
    - dict: A dictionary with a success message if the update was successful, or an error message if it failed.
    """
    try:
        # get the attribute detail from child doctype
        la_child_docs = frappe.get_all(child_doctype,
            filters={
                "parent": parent_docName,
                "attribute": target_field
            },
            limit=1 
        )
        if not la_child_docs:
            return {"error": _("Attribute not found for the specified parent.")}

        # Update the attribute_value directly
        frappe.db.set_value(child_doctype, la_child_docs[0].name, "attribute_value", new_value)

        return {"message": _("Updated successfully")}
    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        return {"error": _("Failed to update: {}".format(str(e)))}

@frappe.whitelist()
def create_item_from_design(design_name):
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
def get_table_rows_columns(doctype, docname):
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
def update_child_table_row(doctype, docname, child_field, values):
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

@frappe.whitelist()
def get_variant_attributes(name):
    """
    Fetch attributes of an Item variant.

    Args:
        item_name (str): The name of the Item.

    Returns:
        list: List of attributes from the Item's attribute child table.
    """
    try:
        # Fetch the Item document
        item = frappe.get_doc("Item", name)
        return item.attributes

    except frappe.DoesNotExistError:
        return 'DoesNotExistError'
        frappe.throw(_("Item with name '{0}' does not exist").format(name))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_variant_attributes")
        frappe.throw(_("An unexpected error occurred while fetching the item attributes."))

@frappe.whitelist()
def get_item_attribute_record():
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

