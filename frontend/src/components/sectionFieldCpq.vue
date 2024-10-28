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
                @input="updateResource(child.doctype, child.parent, child.name, $event.target.value)"
              />
              <FormControl
                v-else
                class="form-control"
                type="text" 
                v-model="child.value"
                :placeholder="child.placeholder"
                :debounce="500"
                @input="updateResource(child.doctype, child.parent, child.name, $event.target.value)"
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
  const props = defineProps({
  fields: {
      type: Object,
      },
      isLastSection: {
          type: Boolean,
          default: false,
      },
      })
 
  const updateResource = (doctype, parent, fieldName, value) => {
    createResource({
      url: 'crm.api.customDoc.update_child_table',
      params: {
        doctype, 
        parent, 
        fieldName, 
        value
      },
      onSuccess(data) {
        console.log("response", data);
      },
    });
  };

  
  </script>
  
  <style scoped>
 .form-control {
  margin: 2px;
}
  </style>
  