import frappe
import json
from frappe import _
from frappe.model.document import get_controller, Document
from frappe.model import no_value_fields
from pypika import Criterion
from frappe.utils import make_filter_tuple, get_url_to_list
from crm.api.views import get_views
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from crm.api.doc import get_sidebar_fields, get_fields_meta, get_assigned_users


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
 
                # Query the child records where parent matches the name
                child_records = frappe.get_all(child_doctype, filters={"parent": name}, fields=["*"])
              
                # Initialize the children list if it doesn't exist
                field["children"] = []

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
def update_child_table(child_doctype, parent_docName, target_field, new_value):
    try:
        child_docs = frappe.get_all(child_doctype,
            filters={
                "parent": parent_docName,
                "attribute": target_field
            },
            limit=1 
        )
        if not child_docs:
            return {"error": _("Attribute not found for the specified parent.")}

        child_doc_name = child_docs[0].name
        child_doc = frappe.get_doc(child_doctype, child_doc_name)
        
        child_doc.attribute_value = new_value
        child_doc.save() 

        return {"message": _("Updated successfully")}
    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        return {"error": _("Failed to update: {}".format(str(e)))}

@frappe.whitelist()
def create_item_from_design(design_name):

    design_doc = frappe.get_doc("Design", design_name)

    if not design_doc.design_template:
        frappe.throw("Design Template is not specified in the design document.")

    template_item = frappe.get_doc("Item", design_doc.design_template)

    template_attributes = {
        attr.attribute: attr.numeric_values for attr in template_item.attributes
    }

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