import frappe
from frappe import _

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script

@frappe.whitelist()
def get_condition_value(name):
    ld_Condition_Value = frappe.qb.DocType("Condition Value")
    query = frappe.qb.from_(ld_Condition_Value).select("*").where(ld_Condition_Value.name == name).limit(1)
    ld_condition_value = query.run(as_dict=True)
    if not len(ld_condition_value):
        frappe.throw(_("Condition Value not found"), frappe.DoesNotExistError)
    ld_condition_value = ld_condition_value.pop()
    ld_condition_value["doctype"] = "Condition Type"
    ld_condition_value["fields_meta"] = get_fields_meta("Condition Type")
    ld_condition_value["_form_script"] = get_form_script('Condition Type')
    ld_condition_value["_assign"] = get_assigned_users("Condition Type", ld_condition_value.name, ld_condition_value.owner)
    return ld_condition_value