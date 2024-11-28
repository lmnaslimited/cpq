<template>
    <SectionFields 
      :fields="fields" 
      :isLastSection="isLastSection" 
      >
      <template #children="{ fields, data, emit }">
      <div v-for="field in fields"> 
      <div v-if="field.children && field.children.length > 0" class="flex flex-col mt-2">
        <div v-for="child in field.children" :key="child.name" class="flex items-center justify-between gap-2 px-3">
          <Tooltip :text="__(child.label)" :hoverDelay="1">
            <div class="flex items-center">
              <span class="sm:w-[106px] w-36 shrink-0 truncate text-sm text-gray-600">
                {{ __(child.label) }}
              </span>
            </div>
          </Tooltip>
          <div class="flex-1">
            <FormControl
                v-if="child.type === 'select'"
                class="form-control"
                type="select" 
                :options="child.options"
                v-model="child.value"
                :placeholder="child.placeholder"
                :debounce="500"
                @change="updateResource(child.doctype, child.parent, child.label, $event.target.value, data.doctype)"
              />
              <FormControl
                v-else
                class="form-control"
                type="text" 
                v-model="child.value"
                :placeholder="child.placeholder"
                :debounce="500"
                @change="handleInputChange(child.doctype, child.parent, child.label, $event.target.value, data.doctype)"
              />
            </div>
        </div>
      </div>
      </div>
    </template>
    </SectionFields>
  </template>
  
  <script setup>
  import SectionFields from '@/components/SectionFields.vue'
  import { Tooltip, createResource} from 'frappe-ui'
  import { capture } from '@/telemetry'
  import { createToast } from '@/utils'
  const props = defineProps({
  fields: {
      type: Object,
      },
      isLastSection: {
          type: Boolean,
          default: false,
      },
      })

 let timeout = null

// Handle input change and debounce the update call
const handleInputChange = (childDoctype, parentDocName, targetField, newValue, sourceDoctype) => {
  clearTimeout(timeout)
  timeout = setTimeout(() => {
    updateResource(childDoctype, parentDocName, targetField, newValue, sourceDoctype)
  }, 500)
}

  // Parameters:
  // - childDoctype: The name of the child doctype to update.
  // - parentDocName: The name of the parent document to which the child belongs.
  // - targetField: The field in the child doctype to update.
  // - newValue: The new value to assign to the target field.
  // - sourceDoctype: The source doctype from which data is being updated.
  const updateResource = (childDoctype, parentDocName, targetField, newValue, sourceDoctype) => {
    
    createResource({
      url: 'crm.api.docCpq.update_item_attribute',
      method: 'PUT',
      params: {
        child_doctype : childDoctype,
        parent_docName : parentDocName,
        target_field : targetField,
        new_value : newValue,
      },
      debounce: 500,
      onSuccess(data) {
        capture(`${sourceDoctype}_updated`);
         createToast({
            title: __(`${sourceDoctype} Updated`),
            icon: 'check',
            iconClasses: 'text-green-600',
          })
        
      },
      onError(error) {
        console.error("Error updating resource:", error);
      },
    }).submit();
  };

  
  </script>
  
  <style scoped>
 .form-control {
  margin: 2px;
}
  </style>
  