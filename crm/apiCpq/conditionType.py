import frappe
from frappe import _

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