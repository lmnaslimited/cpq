// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Core Design", {
// 	refresh(frm) {

// 	},
// });

let has_invalid_value = new Set(); 
frappe.ui.form.on('Core Design', {
    refresh(frm) {
        if (frm.doc.design_template) {
            frm.events.load_and_render_fields(frm);
        }
    },

    design_template(frm) {
        frm.events.load_and_render_fields(frm);
    },

    validate(frm) {
        if (has_invalid_value && has_invalid_value.size > 0) {
            frappe.throw(__('Please correct all validation errors before saving.'));
        }
    },

    // MAIN LOAD FUNCTION
    load_and_render_fields(frm) {
        frappe.call({
            method: "crm.cpq.doctype.core_design.api.get_formated_item_variants",
            args: { item_template: frm.doc.design_template },
            callback: function (r) {
                if (!r.message) return;

                const fields = frm.events.prepare_field_data(frm, r.message);
                const html = frappe.render(frm.events.generate_template_html(), { fields });
                frm.events.render_dynamic_section(frm, html, fields);
            }
        });
    },

    prepare_field_data(frm, fields) {
        return fields.map(field => ({
            ...field,
            saved_value: frm.events.get_saved_value(frm, field.fieldname)
                || field.default || field.min || ""
        }));
    },

    generate_template_html() {
        return `
            <div class="design-grid-wrapper" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                {% for (var i = 0; i < fields.length; i++) {
                    var field = fields[i];
                %}
                <div class="form-column">
                    <div class="frappe-control input-max-width" data-fieldname="{%= field.fieldname %}">
                        <div class="form-group">
                            <label class="control-label">{%= field.label %}</label>
                            <div class="control-input flex flex-column" style="gap:8px;">
                                {% if (field.numeric_values) { %}
                                    <input type="range"
                                           class="range-field"
                                           data-fieldname="{%= field.fieldname %}"
                                           min="{%= field.min %}"
                                           max="{%= field.max %}"
                                           step="{%= field.step %}"
                                           value="{%= field.saved_value %}" 
                                           style="width: 100%; accent-color: black;"
                                           />
                                    <input type="number"
                                           class="number-field"
                                           data-fieldname="{%= field.fieldname %}"
                                           min="{%= field.min %}"
                                           max="{%= field.max %}"
                                           step="{%= field.step %}"
                                           value="{%= field.saved_value %}" />
                                   
                                    <small id="error_{%= field.fieldname %}" class="text-danger"></small>
                                    <small class="text-muted">
        From Range: {%= field.min %}, To Range: {%= field.max %}, Increment: {%= field.step %}
    </small>
                                {% } else { %}
                                    <select class="form-control select-field"
                                            data-fieldname="{%= field.fieldname %}">
                                        <option disabled {%= !field.saved_value ? 'selected' : '' %}>Select {%= field.label %}</option>
                                        {% for (var j = 0; j < field.options.length; j++) {
                                            var opt = field.options[j];
                                        %}
                                            <option value="{%= opt.value %}" {%= opt.value == field.saved_value ? 'selected' : '' %}>
                                                {%= opt.label %}
                                            </option>
                                        {% } %}
                                    </select>
                                {% } %}
                            </div>
                        </div>
                    </div>
                </div>
                {% } %}
            </div>
        `;
    },

    // render_dynamic_section(frm, html, fields) {
    //     frm.set_df_property("dynamic_section", "options", html);

    //     frappe.after_ajax(() => {
    //         const wrapper = frm.fields_dict["dynamic_section"].$wrapper.get(0);

    //         fields.forEach(field => {
    //             if (field.numeric_values) {
    //                 const rangeEl = wrapper.querySelector(`.range-field[data-fieldname="${field.fieldname}"]`);
    //                 const numberEl = wrapper.querySelector(`.number-field[data-fieldname="${field.fieldname}"]`);
    //                 const errorEl = numberEl?.nextElementSibling;


    //                 if(numberEl){
    //                     numberEl.addEventListener("input", () => {
    //                         const isValid = frm.events.validate_and_update_numeric_input(frm, field.fieldname, parseFloat(numberEl.value), numberEl, rangeEl, errorEl);
    //                         if (isValid) {
    //                             rangeEl.value = numberEl.value; 
    //                         }
    //                     });
    //             }
    //                 if (rangeEl) {
    //                     rangeEl.addEventListener("input", () => {
    //                         const isValid = frm.events.validate_and_update_numeric_input(frm, field.fieldname, parseFloat(rangeEl.value), rangeEl, numberEl, errorEl);
    //                         if (isValid) {
    //                             numberEl.value = rangeEl.value;
    //                         }
    //                     });
    //                 }
    //             } else {
    //                 const selectEl = wrapper.querySelector(`.select-field[data-fieldname="${field.fieldname}"]`);
    //                 selectEl?.addEventListener("change", () => {
    //                     frm.events.update_design_attribute(frm, field.fieldname, selectEl.value);
    //                 });
    //             }
    //         });
    //     });
    // },

    //followed jquery which frappe uses for there html event bind
    render_dynamic_section(frm, html, fields) {
        console.log("core design hello event bind")
        frm.set_df_property("dynamic_section", "options", html);
    
        frappe.after_ajax(() => {
            const $wrapper = $(frm.fields_dict["dynamic_section"].$wrapper.get(0));
    
            fields.forEach(field => {
                if (field.numeric_values) {
                    const $rangeEl = $wrapper.find(`.range-field[data-fieldname="${field.fieldname}"]`);
                    const $numberEl = $wrapper.find(`.number-field[data-fieldname="${field.fieldname}"]`);
                    const $errorEl = $numberEl.next('.text-danger');
    
                    $numberEl.on("input", function () {
                        const value = parseFloat(this.value);
                        const isValid = frm.events.validate_and_update_numeric_input(
                            frm,
                            field.fieldname,
                            value,
                            this,
                            $rangeEl.get(0),
                            $errorEl.get(0)
                        );
                        if (isValid) {
                            $rangeEl.val(this.value);
                        }
                    });
    
                    $rangeEl.on("input", function () {
                        const value = parseFloat(this.value);
                        const isValid = frm.events.validate_and_update_numeric_input(
                            frm,
                            field.fieldname,
                            value,
                            this,
                            $numberEl.get(0),
                            $errorEl.get(0)
                        );
                        if (isValid) {
                            $numberEl.val(this.value);
                        }
                    });
                } else {
                    const $selectEl = $wrapper.find(`.select-field[data-fieldname="${field.fieldname}"]`);
                    $selectEl.on("change", function () {
                        frm.events.update_design_attribute(frm, field.fieldname, this.value);
                    });
                }
            });
        });
    },
    

    get_saved_value(frm, fieldname) {
        const row = (frm.doc.design_attributes || []).find(
            r => r.attribute.toLowerCase() === fieldname.toLowerCase()
        );
        return row ? row.attribute_value : null;
    },

    update_design_attribute(frm, fieldname, value) {
        let row = (frm.doc.design_attributes || []).find(
            r => r.attribute.toLowerCase() === fieldname.toLowerCase()
        );

        if (!row) {
            row = frm.add_child('design_attributes', { attribute: fieldname });
        }

        frappe.model.set_value(row.doctype, row.name, 'attribute_value', value);
    },

    

    validate_and_update_numeric_input(frm, fieldname, value, sourceElement, targetElement, errorEl) {
        const min = parseFloat(sourceElement.getAttribute("min"));
        const max = parseFloat(sourceElement.getAttribute("max"));
        const step = parseFloat(sourceElement.getAttribute("step"));
        let errorMessage = "";

        if (isNaN(value)) {
            errorMessage = __("Value is required");
        } else if (value < min || value > max) {
            errorMessage = __(`Value must be between ${min} and ${max}`);
        } else {
            const quotient = (value - min) / step;
            const isStepValid = Math.abs(quotient - Math.round(quotient)) < 1e-6;
            if (!isStepValid) {
                errorMessage = __(`Value should increment by ${step}`);
            }
        }

        if (errorMessage) {
            errorEl.innerText = errorMessage;
            has_invalid_value.add(fieldname);
            return false
        } else {
            errorEl.innerText = "";
            targetElement.value = value;
            has_invalid_value.delete(fieldname);
            frm.events.update_design_attribute(frm, fieldname, value);
            return true
        }
    }
});