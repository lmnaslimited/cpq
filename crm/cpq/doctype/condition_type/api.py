import frappe
from frappe import _

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script

@frappe.whitelist()
def get_condition_type(name):
    ld_condition_type = frappe.get_doc("Condition Type", name)

    if not ld_condition_type:
        frappe.throw(_("Condition Type not found"), frappe.DoesNotExistError)

    # Convert the document to a dictionary for manipulation
    ld_condition_type_dict = ld_condition_type.as_dict()

    # Add additional fields to the dictionary
    ld_condition_type_dict["fields_meta"] = get_fields_meta("Condition Type")
    ld_condition_type_dict["_form_script"] = get_form_script("Condition Type")
    ld_condition_type_dict["_assign"] = get_assigned_users("Condition Type", ld_condition_type.name, ld_condition_type.owner)

    # Return the modified dictionary
    return ld_condition_type_dict
    
    