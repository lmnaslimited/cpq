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
        <CpqFields class="border-t" :sections="sections" :data="design" @updateField="handleFieldUpdate" />
        <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
      </template>
      <template #actions>
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isDesignCreating"
            @click="createNewDesign"
          />
        </div>
      </template>
    </Dialog>
  </template>
  
  <script setup>
  import CpqFields from '@/components/CpqFields.vue'
  import { usersStore } from '@/stores/users'
  import { statusesStore } from '@/stores/statuses'
  import { Select } from 'frappe-ui'
  import { computed, ref, reactive, onMounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { call,  createResource} from 'frappe-ui'
  import { validateRangeIncrement } from '@/cpqUtils.js'
  import { capture } from '@/telemetry'
  const { getUser } = usersStore()
  const { statusOptions } = statusesStore()
  
  const show = defineModel()
  const router = useRouter()
  const error = ref(null)
  
  const design = reactive({
    created_by: '',
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
      const message = await call('crm.cpq.doctype.design.api.get_item_variant')
      designTemplateOptions.value = message
    } catch (error) {
      console.error('Error fetching transformer types:', error)
    }
  }
  async function fnFetchItemDetails(itemName) {
    try {
      const fields = await call('crm.cpq.doctype.design.api.get_formatted_item_details', {
        item_name: itemName
      })
      fetchedFields.value = fields;
    } catch (error) {
      console.error('Error fetching item details:', error);
    }
  }


  const createDesign = createResource({
  url: 'frappe.client.insert',
  makeParams(design) {
    // Only constructing the parameters for the API request
    const visibleFields = {};  // Fields for the main doc
    const designAttributes = [];  // Child table fields

    // Loop through all fields and separate into main doc and child table fields
    Object.entries(design).forEach(([key, value]) => {
      const field = fetchedFields.value.find(f => f.name === key);
      if (['design_template', 'status', 'created_by', 'item'].includes(key)) {
          visibleFields[key] = value;  // Add to main doc fields
        }
      if (field) {
          designAttributes.push({
            attribute: field.label,
            attribute_value: value,
            numeric_values: field.numeric_values,
          });  // Add to child table
      }
    });
    
    // Return the payload for the API request
    return {
      doc: {
        doctype: 'Design',
        ...visibleFields,  // Spread visible fields for the main document
        design_attributes: designAttributes,  // Add child table data
      },
    };
  },
});

async function createNewDesign() {
  isDesignCreating.value = true;
  error.value = null;

  // Perform range validation before submission
  const rangeErrors = validateRangeFields(fetchedFields.value, design);
  if (rangeErrors.length > 0) {
    error.value = `Range validation failed for: ${rangeErrors.map(result => result.name).join(', ')}`;
    isDesignCreating.value = false;
    return;
  }

  // Now submit the design
  try {
    await createDesign.submit(design, {
      validate() {
        error.value = null;  // Reset error value before submission
        return true;  // Proceed with submission
      },
      onSuccess(response) {
        capture('design_created');
        isDesignCreating.value = false;
        show.value = false;
        router.push({ name: 'Design', params: { designId: response.name } });
      },
      onError(err) {
        isDesignCreating.value = false;
        error.value = err.messages ? err.messages.join('\n') : err.message;
      },
    });
  } catch (err) {
    isDesignCreating.value = false;
    error.value = err.message;
  }
}

// Function to validate range fields (validation logic outside of makeParams)
function validateRangeFields(fetchedFields, design) {
  return fetchedFields
    .filter(field => field.type === 'range')  // Get range fields
    .map(field => ({
      name: field.name,
      error: validateRangeIncrement(field.name, design[field.name], field.min, field.max, field.step),
    }))
    .filter(result => result.error !== null);  // Only keep fields with errors
}

  
  function handleFieldUpdate({ name, value }) {
    design[name] = value
  }
  
  onMounted(() => {
    if (!design.created_by) {
      design.created_by = getUser().email
    }
    fetchDesignTemplates()
  })
  
  watch(() => design.design_template, (newValue, oldValue) => {
    if (newValue !== oldValue) {
      fnFetchItemDetails(newValue)
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