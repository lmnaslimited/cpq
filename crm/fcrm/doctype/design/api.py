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


@frappe.whitelist(allow_guest=True)
def save_design(data):
    try:
        data = frappe.parse_json(data)
        
        # Define the doctype where the dynamic fields will be added
        doctype = "Design"

        # Initialize dictionaries for main doc and child table data
        main_doc_data = {}
        child_table_data = []

        # Get the meta for the doctype
        meta = frappe.get_meta(doctype)

        for fieldname, field_info in data.items():
            value = field_info['value']

            # Check if the field is in the main doctype fields
            if meta.has_field(field_info['name']):
                main_doc_data[field_info['name']] = value
            else:
                # If the field is not in the main doctype, add it to the child table data
                # Use the field label as the key instead of the fieldname
                child_table_data.append({
                    'attribute': field_info['label'],  # Use label as the key
                    'attribute_value': value
                })

        # Create a new document for your target DocType
        doc = frappe.get_doc({
            "doctype": doctype,
            **main_doc_data
        })

        # Add attributes to the child table
        for child in child_table_data:
            doc.append('design_attributes', child)

        # Save the document to the database
        doc.insert()
        frappe.db.commit()

        return {
            "status": "success",
            "message": _("Document saved successfully"),
            "docname": doc.name
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Failed to save design"))
        return {
            "status": "error",
            "message": str(e)
        }