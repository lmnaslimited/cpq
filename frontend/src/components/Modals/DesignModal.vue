<template>
    <Dialog
      v-model="show"
      :options="{
        size: '4xl',
        title: __('Create Design'),
      }"
    >
      <template #body-content>
        <div class="mb-4 grid grid-cols-1">
          <div class="flex items-center gap-3 text-sm text-gray-600">
            <div>{{ __('Select Design Type') }}</div>
            <Select
              :options="designTemplateOptions"
              v-model="design.design_template"
              style="width: 200px;"
            />
          </div>
        </div>
        <FieldsCpq class="border-t pt-4" :sections="sections" :data="design" @updateField="handleFieldUpdate" />
        <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
      </template>
      <template #actions>
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isDesignCreating"
            @click="createDesign"
          />
        </div>
      </template>
    </Dialog>
  </template>
  
  <script setup>
  import FieldsCpq from '@/components/FieldsCpq.vue'
  import { usersStore } from '@/stores/users'
  import { statusesStore } from '@/stores/statuses'
  import { Select } from 'frappe-ui'
  import { computed, ref, reactive, onMounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { call } from 'frappe-ui'
  
  const { getUser } = usersStore()
  const { statusOptions } = statusesStore()
  
  const show = defineModel()
  const router = useRouter()
  const error = ref(null)
  
  const design = reactive({
    design_owner: '',
     design_template: '',
  })
  
  const isDesignCreating = ref(false)
  const designTemplateOptions = ref([])
  const fetchedFields = ref([])
  
  const sections = computed(() => {
    const fields = fetchedFields.value.length ? [{
      section: '',
      fields: fetchedFields.value
    }] : []
  
    return fields
  })

  const designStatuses = computed(() => {
    let statuses = statusOptions('design')
    if (!design.status) {
      design.status = statuses[0].value
    }
    return statuses
  })
  
  
  async function fetchDesignTemplates() {
    try {
      const message = await call('crm.fcrm.doctype.design.api.get_item_variant')
      designTemplateOptions.value = message
    } catch (error) {
      console.error('Error fetching transformer types:', error)
    }
  }
  
  async function fetchItemDetails(designType) {
    try {
      const itemDetail = await call('frappe.client.get', {
        doctype: 'Item',
        name: designType
      })
  
      if (itemDetail.attributes) {
        const itemAttribute = itemDetail.attributes
        const fields = await Promise.all(itemAttribute.map(async (attribute) => {
        const itemVariant = await call('frappe.client.get', {
            doctype: 'Item Attribute',
            name: attribute.attribute
          })
        
          let field
          if (itemVariant.numeric_values != 1) {
            // If numeric_value is 0, it should be a select type
            field = {
              label: itemVariant.attribute_name,
              name: itemVariant.attribute_name.replace(/\s+/g, '_').replace(/[()]/g, '').toLowerCase(),
              type: 'Select',
              numeric_values: 0,
              options: itemVariant.item_attribute_values.map(val => ({
                label: val.attribute_value,
                value: val.attribute_value
              }))
            }
          } else {
            // Otherwise, it's an range type
            field = {
              label: itemVariant.attribute_name,
              name: itemVariant.attribute_name.replace(/\s+/g, '_').replace(/[()]/g, '').toLowerCase(),
              type: 'Range',
              numeric_values: 1,
              min: itemVariant.from_range,
              max: itemVariant.to_range,
              step: itemVariant.increment,
              id: `${itemVariant.attribute_name.replace(/\s+/g, '_').replace(/[()]/g, '').toLowerCase()}_id`,
              placeholder: ''
            }
          }
          
          return field
        }))
        fetchedFields.value = fields
      }
    } catch (error) {
      console.error('Error fetching transformer details:', error)
    }
  }
  
  
  
  const validateRangeIncrement = (name, value, min, max, step) => {
  
    const numericValue = parseFloat(value);
    const numericMin = parseFloat(min);
    const numericMax = parseFloat(max);
    const numericStep = parseFloat(step);
  
   if (!/^\d*\.?\d*$/.test(value)) {
      return 'Invalid Input.';
    }
  
  
    // Check if the value is outside the range
    if (numericValue < numericMin || numericValue > numericMax) {
      return `Value should be between ${min} and ${max}`;
    }
  
    // Extract the number of decimal places in the step
    const stepDecimalPlaces = step.toString().split('.')[1]?.length || 0;
  
    // Extract the number of decimal places in the value
    const valueDecimalPlaces = (value.toString().includes('.') ? value.split('.')[1].length : 0) || 0;
  
    if(stepDecimalPlaces > 0){
    // Check if the value has the correct number of decimal places as the step
    if (numericValue === numericMin || numericValue === numericMax) {
      return null; // No need for further validation
    }
    if (valueDecimalPlaces !== stepDecimalPlaces) {
      return `Value should increment by ${step}`;
    }
    }else {
      if (value.toString().includes('.') && value.toString().split('.')[1].length === 0) {
        return 'Invalid Input.'; // Error if there's a dot without succeeding digits
      }
      // If the step is an integer
      if ((numericValue - numericMin) % numericStep !== 0) {
        return `Value should increment by ${step}`;
      }
    }
  
    return null;
  };
  
  
    const createDesign = async () => {
    isDesignCreating.value = true;
    error.value = null;
    try {
     const rangeFields = fetchedFields.value.filter(field => field.type === 'range');
      const rangeValidationResults = rangeFields.map(field => ({
        name: field.name,
        error: validateRangeIncrement(field.name, design[field.name], field.min, field.max, field.step)
      }));
  
      // Check if any errors exist
      const rangeErrors = rangeValidationResults.filter(result => result.error !== null);
  
      if (rangeErrors.length > 0) {
        // Handle range validation errors, e.g., display error message
        const errorFields = rangeErrors.map(result => result.name).join(', ');
        error.value = ``;
        return;
      }
  
      // Prepare the payload for design creation
      const payload = {};
  
      // Include fields from fetchedFields
      for (const [key, value] of Object.entries(design)) {
        const field = fetchedFields.value.find(field => field.name === key);
  
        if (field) {
          payload[field.label] = {
            label: field.label,
            name: field.name,
            value: value,
            numeric_values: field.numeric_values,
            type: 'data'
          }
        }
      }
  
      // Include other fields like design_owner and design_template
      payload['Design Owner'] = {
        label: 'Design Owner',
        name: 'design_owner',
        value: design.design_owner,
        type: 'data'
      };
  
      payload['Design Template'] = {
        label: 'Design Template',
        name: 'design_template',
        value: design.design_template,
        type: 'data'
      };
  
      // Proceed with design creation
      const response = await call('crm.fcrm.doctype.design.api.save_design', {
        data: payload
      });

      if (response.status === 'success') {
        isDesignCreating.value = false;
        show.value = false;
        router.push({ name: 'Design', params: { designId: response.docname } });
      } else {
        error.value = response.message;
        console.log("error on success")
      }
    } catch (err) {
      error.value = err.message;
      console.log("error on catch")
    } finally {
      isDesignCreating.value = false;
    }
  };
  
  function handleFieldUpdate({ name, value }) {
    design[name] = value
  }
  
  onMounted(() => {
    if (!design.design_owner) {
      design.design_owner = getUser().email
    }
    fetchDesignTemplates()
  })
  
  watch(() => design.design_template, (newValue, oldValue) => {
    if (newValue !== oldValue) {
      fetchItemDetails(newValue)
    }
  })
  </script>
  
  <style scoped>
  /* Remove outline for the specific formControl component */
  .form-control:focus,
  .form-control:focus-visible {
    outline: none !important;
  }
  </style>