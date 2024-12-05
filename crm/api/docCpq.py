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
    # Call the original get_sidebar_fields function to get the layout
    layout = get_sidebar_fields(doctype, name)

    # Fetch field metadata for the doctype
    fields = frappe.get_meta(doctype).fields

    # Loop through each section in the layout
    for section in layout:
        # Iterate over fields in the section
        for field in section.get("fields", []):
            
            # If the field type is Table
             if isinstance(field, dict) and field.get("type") == "Table":
                child_doctype = field.get("options")  # Get the child doctype from options
 
                # Query the child doctype where parent matches the name
                child_records = frappe.get_all(child_doctype, filters={"parent": name}, fields=["*"])
              
                field["children"] = []

                # Loop through each child record
                for record in child_records:
                   
                    # Determine field type based on numeric_values
                    #mostly the type is "data" or "select"
                    if record.get("numeric_values") == 1:
                        field_type = "data"
                    else:
                        field_type = "select"

                    # In order to get option for the non numeric field
                    # query the doctype mentioned in the link key
                    if field.get("link"):
            
                        attribute_value = record.get("attribute")
                        options = frappe.get_all(field.get("link"), filters={"parent": attribute_value}, fields=["attribute_value"])
                        
                        # Extracting the attribute_value into an array
                        options = [opt.get("attribute_value") for opt in options]

                    else:
                        options = None

                    # Push properties into children maintaining structure for front-end
                    field["children"].append({
                        "label": record.get("attribute", ''),
                        "type": field_type,
                        "name": "attribute_value",
                        "value": record.get("attribute_value", ''),
                        "hidden": field.get("hidden", False),
                        "reqd": field.get("reqd", False),
                        "read_only": field.get("read_only", False),
                        "placeholder": field.get("placeholder", ''),
                        "options": options, # Add options as an array
                        "doctype": field.get("options"),
                        "parent": record.get("parent")
                    })

    return layout

@frappe.whitelist()
def update_item_attribute(child_doctype, parent_docName, target_field, new_value):
    try:
        # get the attribute detail from child doctype
        child_docs = frappe.get_all(child_doctype,
            filters={
                "parent": parent_docName,
                "attribute": target_field
            },
            limit=1 
        )
        if not child_docs:
            return {"error": _("Attribute not found for the specified parent.")}

        #commented this code to replace with set_value
        # child_doc_name = child_docs[0].name
        # child_doc = frappe.get_doc(child_doctype, child_doc_name)
        
        # child_doc.attribute_value = new_value
        # child_doc.save() 

        # Update the attribute_value directly
        frappe.db.set_value(child_doctype, child_docs[0].name, "attribute_value", new_value)

        return {"message": _("Updated successfully")}
    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        return {"error": _("Failed to update: {}".format(str(e)))}

@frappe.whitelist()
def create_item_from_design(design_name):

    #get the details of the design
    design_doc = frappe.get_doc("Design", design_name)

    if not design_doc.design_template:
        frappe.throw(__('Design Template is not specified in the design document.'))

    #get the details of the item template
    template_item = frappe.get_doc("Item", design_doc.design_template)

    #Forming a dictionary with key as variant's name and value as is_numeric
    template_attributes = {
        attr.attribute: attr.numeric_values for attr in template_item.attributes
    }

    #replacing space with - for item name and code formation
    attribute_values = [
        attribute.attribute_value.replace(" ", "-")
        for attribute in design_doc.design_attributes
        if attribute.attribute in template_attributes
    ]
    item_code = f"{design_doc.design_template}-" + "-".join(attribute_values)

    item_variant = frappe.new_doc("Item")
    item_variant.item_code = item_code
    item_variant.item_name = item_code
    item_variant.item_group = template_item.item_group
    item_variant.is_stock_item = template_item.is_stock_item
    item_variant.variant_of = design_doc.design_template
    item_variant.include_item_in_manufacturing = 0

    for attribute in design_doc.design_attributes:
        if attribute.attribute in template_attributes:

            numeric_value = template_attributes[attribute.attribute]
            
            item_variant.append("attributes", {
                "attribute": attribute.attribute,
                "attribute_value": attribute.attribute_value,
                "numeric_values": numeric_value
            })

    item_variant.insert()
    frappe.db.commit()

    # Create a "Standard Selling" price list for this item
    item_price = frappe.new_doc("Item Price")
    item_price.item_code = item_variant.item_code
    item_price.price_list = "Standard Selling"
    item_price.price_list_rate = design_doc.total_cost
    item_price.insert()
    frappe.db.commit()
    return item_variant.item_code

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
    # Fetch metadata of the parent doctype
    parent_meta = frappe.get_meta(doctype)
    table_fields = []

    # Identify fields of type "Table"
    for field in parent_meta.fields:
        if field.fieldtype == "Table":
            table_fields.append({
                "fieldname": field.fieldname,
                "options": field.options  # Child table doctype
            })

    # Prepare the response
    result = {
        "columns": [],
        "rows": {}
    }

    # Iterate through the table fields to fetch child metadata and rows
    for table_field in table_fields:
        child_doctype = table_field["options"]
        child_meta = frappe.get_meta(child_doctype)

        # Append child metadata to columns
        result["columns"].append({
            "fieldname": table_field["fieldname"],
            "fields": [
                {
                    "fieldname": f.fieldname,
                    "label": f.label,
                    "fieldtype": f.fieldtype,
                    "options": f.options if hasattr(f, "options") else None,
                    "hidden": f.hidden,
                    "read_only": f.read_only
                }
                for f in child_meta.fields
            ]
        })

        # Fetch rows for the child table
        rows = frappe.get_all(
            child_doctype,
            filters={"parent" : docname},
            fields="*"
        )
        result["rows"][table_field["fieldname"]] = rows

    return result

@frappe.whitelist()
def update_child_table_row(doctype, docname, child_field, values):
    """
    :param doctype: The doctype to be updated
    :param docname: The name of the document to update.
    :param child_field: The child table fieldname in the Quotation.
    :param values: A list of dictionaries with item details to update.
    :return: Success message or error.
    """
    try:
        # Fetch the document
        doc = frappe.get_doc(doctype, docname)

        # Ensure items are passed in the correct format
        if not isinstance(values, list):
            frappe.throw("Items must be a list of dictionaries.")

        # Get existing rows in the child table as a list
        existing_rows = {row.name: row for row in getattr(doc, child_field)}

        # Create a set of incoming names
        incoming_names = {value.get("name") for value in values}

        # Remove rows in the child table that are not in the incoming data
        doc.set(child_field, [
            row for row in getattr(doc, child_field) if row.name in incoming_names
        ])

        # Add or update rows
        for value in values:
            existing_row = existing_rows.get(value.get("name"))

            if existing_row:
                # Update the existing row
                for field, field_value in value.items():
                    setattr(existing_row, field, field_value)
            else:
                # If it's a new row (no name exists in the document), append it
                doc.append(child_field, value)
        
        # Save the updated document
        doc.save()
        frappe.db.commit()
        doc.reload()

        return {"status": "success", "message": "updated successfully.", "doc": doc}

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
        # frappe.throw(_("Item with name '{0}' does not exist").format(name))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_variant_attributes")
        frappe.throw(_("An unexpected error occurred while fetching the item attributes."))
