import frappe
import json
from frappe import _
from frappe.model.document import get_controller
from frappe.model import no_value_fields
from pypika import Criterion
from frappe.utils import make_filter_tuple
from crm.api.views import get_views
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from crm.api.doc import get_sidebar_fields

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
            if field.get("type") == "Table":
                child_doctype = field.get("options")  # Get the child doctype from options
 
                # Query the child records where parent matches the name
                child_records = frappe.get_all(child_doctype, filters={"parent": name}, fields=["*"])
              
                # Initialize the children list if it doesn't exist
                field["children"] = []

                # # Loop through each child record and extract required properties
                # for record in child_records:
                #     if it record.numeric_values is o then get the attribute for that attribute in the field.get(link) and giv it to options
                #     print("record",record)
                #     # Push properties into children maintaining structure for front-end
                #     field["children"].append({
                #         "label": record.get("attribute", ''),
                #         "type": "data", if record[numeric_values] == 1 then it data or its select
                #         "name": "attribute_value",  
                #         "value": record.get("attribute_value", ''),
                #         "hidden": field.get("hidden", False),
                #         "reqd": field.get("reqd", False),
                #         "read_only": field.get("read_only", False),
                #         "placeholder": field.get("placeholder", '')
                #     })
                # Loop through each child record and extract required properties
                for record in child_records:
                   
                    # Determine field type based on numeric_values
                    if record.get("numeric_values") == 1:
                        field_type = "data"
                    else:
                        field_type = "select"

                    # Query the linked options based on the attribute_value
                    if field.get("link"):
                        # Assuming `attribute` is a field that links to the child doctype
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
def sync_fcrm_item_attribute(doc, method):
    """
    Create or update an Item Attribute whenever an Item Attribute is created or updated.
    """
    # Check if the Item Attribute already exists
    item_attribute = frappe.get_all(
        "FCRM Item Attribute",
        filters={"attribute_name": doc.attribute_name},
        limit=1
    )

    # Prepare data to sync
    data = {
        "attribute_name": doc.attribute_name,
        "numeric_values": doc.numeric_values,
        "from_range": doc.from_range,
        "increment": doc.increment,
        "to_range": doc.to_range,
    }

    if item_attribute:
        # Update existing Item Attribute
        # item_attribute_doc = frappe.get_doc("FCRM Item Attribute", item_attribute[0].name).as_dict()
        # print(f"Updating Item Attribute: {item_attribute_doc.name}")

        # # Update main fields
        # for field, value in data.items():
        #     setattr(item_attribute_doc, field, value)
        #     print(f"Set {field} to {value}")

        # # Retain existing child records and merge new values
        # existing_values = {item.attribute_value: item for item in item_attribute_doc.fcrm_item_attribute_values}
        # print(f"Existing Item Attribute Values: {existing_values}")

        # for item in doc.item_attribute_values:
        #     print(f"Item: {item_attribute_doc.fcrm_item_attribute_values}")
        #     if item.attribute_value in existing_values:
        #         # Update existing value
        #         existing_item = existing_values[item.attribute_value]
        #         existing_item.abbr = item.abbr
        #         print(f"Updated existing Item Attribute Value: {item.attribute_value}")
        #     else:
        #         # Append new value
        #         item_attribute_doc.append('fcrm_item_attribute_values', {
        #             "attribute_value": item.attribute_value,
        #             "abbr": item.abbr
        #         })
        #         print(f"Added new Item Attribute Value: {item.attribute_value}")

        # item_attribute_doc.save()
        # print(f"Saved updated Item Attribute: {item_attribute_doc.name}")
        # frappe.msgprint(f"Updated Item Attribute: {data['attribute_name']}")
        item_attribute_doc = frappe.get_doc("FCRM Item Attribute", item_attribute[0].name)  # Do not use .as_dict()

        # Ensure fcrm_item_attribute_values is initialized
        if not item_attribute_doc.fcrm_item_attribute_values:
            item_attribute_doc.fcrm_item_attribute_values = []

        # Update fields and append values
        for field, value in data.items():
            setattr(item_attribute_doc, field, value)

        existing_values = {item.attribute_value: item for item in item_attribute_doc.fcrm_item_attribute_values}

        for item in doc.item_attribute_values:
            if item.attribute_value in existing_values:
                existing_item = existing_values[item.attribute_value]
                existing_item.abbr = item.abbr
            else:
                item_attribute_doc.append('fcrm_item_attribute_values', {
                    "attribute_value": item.attribute_value,
                    "abbr": item.abbr
                })

        item_attribute_doc.save()
       
    else:
        # Create new Item Attribute
        item_attribute_doc = frappe.get_doc({
            "doctype": "FCRM Item Attribute",
            "attribute_name": doc.attribute_name,
            "numeric_values": doc.numeric_values,
            "from_range": doc.from_range,
            "increment": doc.increment,
            "to_range": doc.to_range,
        })

        # Add item_attribute_values if present
        if doc.item_attribute_values:
            for item in doc.item_attribute_values:
                item_attribute_doc.append('fcrm_item_attribute_values', {
                    "attribute_value": item.attribute_value,
                    "abbr": item.abbr
                })

        item_attribute_doc.insert()
       

@frappe.whitelist()
def update_child_table(doctype, parent, fieldName, value):
    try:
        print("incoming param", doctype + parent + fieldName + value)
        # Find the child document based on the provided doctype, parent, and attribute
        child_docs = frappe.get_all(doctype,
            filters={
                "parent": parent,
                "attribute": fieldName
            },
            limit=1  # Assuming you want to update only the first match
        )
        print("document name ", child_docs[0].name)
        if not child_docs:
            return {"error": _("Attribute not found for the specified parent.")}

        # Get the child document by its name (ID)
        child_doc_name = child_docs[0].name
        child_doc = frappe.get_doc(doctype, child_doc_name)
        
        # Update the attribute_value
        child_doc.attribute_value = value
        child_doc.save()  # Save the child document to apply changes

        return {"message": _("Updated successfully")}
    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        return {"error": _("Failed to update: {}".format(str(e)))}