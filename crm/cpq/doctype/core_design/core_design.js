// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Core Design", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Core Design', {
    refresh(frm) {
        if (frm.doc.design_template) {
            core_design.load_fields(frm);
        }
    },

    design_template(frm) {
        core_design.load_fields(frm);
    },
    validate(frm) {
        if (core_design.has_invalid_fields) {
            frappe.throw(__('Please correct all validation errors before saving.'));
        }
    },
});

const core_design = {
    has_invalid_fields: false,

    load_fields(frm) {
        frappe.call({
            method: "crm.cpq.doctype.core_design.api.get_formated_item_variants",
            args: { item_template: frm.doc.design_template },
            callback: (r) => {
                if (r.message) {
                    core_design.render_fields(r.message, frm);
                }
            }
        });
    },

    render_fields(fields, frm) {
        //iteration through the field and rendering the element snipet
        const html = fields.map(field => {
            const saved_value = core_design.get_saved_value(frm, field.fieldname)
                || field.default || field.min || "";

            const template = field.numeric_values
                ? core_design.range_template()
                : core_design.select_template();

            return frappe.render(template, {
                field,
                saved_value
            });
        }).join("");

        // Wrap the all the render fields in a grid container
            const gridWrapper = `
            <div class="design-grid-wrapper" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                ${html}
            </div>
        `;
        //set them as a option in the for dynamic_section (html field)
        frm.set_df_property("dynamic_section", "options", gridWrapper);
        core_design.attach_listeners(fields, frm);
    },

    range_template() {
        return `
            <div class="form-column">
                <div class="frappe-control input-max-width" data-fieldtype="Range" data-fieldname="{{ field.fieldname }}">
                    <div class="form-group">
                        <label class="control-label">{{ field.label }}</label>
                        <div class="control-input flex flex-column" style="gap:8px;">
                            <input 
                                type="range"
                                class="form-range attribute-input"
                                id="{{ field.fieldname }}_range"
                                min="{{ field.min }}"
                                max="{{ field.max }}"
                                step="{{ field.step }}"
                                value="{{ saved_value }}"
                                style="width: 100%; accent-color: black;"
                            />
                            <input 
                                type="number"
                                class="form-control"
                                id="{{ field.fieldname }}_input"
                                min="{{ field.min }}"
                                max="{{ field.max }}"
                                step="{{ field.step }}"
                                value="{{ saved_value }}"
                            />
                            <p id="{{ field.fieldname }}_error" class="text-danger medium" style="margin:0;"></p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    select_template() {
        return `
            <div class="form-column">
                <div class="frappe-control input-max-width" data-fieldtype="Select" data-fieldname="{{ field.fieldname }}">
                    <div class="form-group">
                        <label class="control-label">{{ field.label }}</label>
                        <select class="form-control attribute-input" id="{{ field.fieldname }}">
                            <option disabled {% if not saved_value %}selected{% endif %}>Select {{ field.label }}</option>
                            {% for opt in field.options %}
                                <option value="{{ opt.value }}" {% if opt.value == saved_value %}selected{% endif %}>
                                    {{ opt.label }}
                                </option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
            </div>
        `;
    },

    attach_listeners(fields, frm) {
        fields.forEach(field => {
            if (field.numeric_values) {
                const inputEl = document.getElementById(`${field.fieldname}_input`);
                const rangeEl = document.getElementById(`${field.fieldname}_range`);
                if (inputEl) {
                    inputEl.addEventListener("input", () => {
                        const isValid = core_design.validate_range_input(frm, field.fieldname, field.min, field.max, field.step, inputEl, rangeEl);
                        if (isValid) {
                            rangeEl.value = inputEl.value; 
                        }
                    });
                }
    
                if (rangeEl) {
                    rangeEl.addEventListener("input", () => {
                        const isValid = core_design.validate_range_input(frm, field.fieldname, field.min, field.max, field.step, rangeEl, inputEl);
                        if (isValid) {
                            inputEl.value = rangeEl.value;
                        }
                    });
                }
            } else {
                const selectEl = document.getElementById(field.fieldname);
                if (selectEl) {
                    selectEl.addEventListener("change", () => {
                        core_design.update_field(frm, field.fieldname, selectEl.value);
                    });
                }
            }
        });
    },

    validate_range_input(frm, fieldname, min, max, step, sourceEl, targetEl) {
        const errorEl = document.getElementById(`${fieldname}_error`);
        const value = parseFloat(sourceEl.value);
        let errorMessage = "";
    
        if (isNaN(value)) {
            errorMessage = `Value is required`;
        } else if (value < min || value > max) {
            errorMessage = `Value should be between ${min} and ${max}`;
        } else {
            const quotient = (value - min) / step;
            if (Math.abs(quotient - Math.round(quotient)) > 1e-6) {
                errorMessage = `Value should increment by ${step}`;
            }
        }
    
        if (errorMessage) {
            errorEl.textContent = errorMessage;
            core_design.has_invalid_fields = true;
            return false;
        } else {
            errorEl.textContent = "";
            targetEl.value = value;  
            core_design.update_field(frm, fieldname, value);
            core_design.has_invalid_fields = false;  
            return true;
        }
    },    

    update_field(frm, fieldname, value) {
  
        let row = (frm.doc.design_attributes || []).find(r => r.attribute.toLowerCase() === fieldname.toLowerCase());

        if (!row) {
            row = frm.add_child('design_attributes', { attribute: fieldname });
        }

        frappe.model.set_value(row.doctype, row.name, 'attribute_value', value);
    },

    get_saved_value(frm, fieldname) {
        const row = (frm.doc.design_attributes || []).find(r => r.attribute.toLowerCase() === fieldname.toLowerCase());
        return row ? row.attribute_value : null;
    }
};


