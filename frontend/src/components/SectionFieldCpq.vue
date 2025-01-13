<template>
    <SectionFields 
      :fields="fields" 
      :isLastSection="isLastSection" 
      >
      <template #children="{ fields, data }">
      <div v-for="ldField in fields"> 
      <div v-if="ldField.children && ldField.children.length > 0" class="flex flex-col mt-2">
        <div v-for="ldChild in ldField.children" :key="ldChild.name" class="flex items-center justify-between gap-2 px-3">
          <Tooltip :text="__(ldChild.label)" :hoverDelay="1">
            <div class="flex items-center">
              <span class="sm:w-[106px] w-36 shrink-0 truncate text-sm text-gray-600">
                {{ __(ldChild.label) }}
              </span>
            </div>
          </Tooltip>
          <div class="flex-1">
            <FormControl
                v-if="ldChild.type === 'select'"
                class="form-control"
                type="select" 
                :options="ldChild.options"
                v-model="ldChild.value"
                placeholder="Select value"
                :debounce="500"
                @change="fnUpdateResource(ldChild.doctype, ldChild.parent, ldChild.label, $event.target.value, data.doctype, ldChild.name)"
              />
              <FormControl
                v-else
                class="form-control"
                type="text" 
                v-model="ldChild.value"
                placeholder="Enter Value"
                :debounce="500"
                @change="fnHandleInputChange(ldChild.doctype, ldChild.parent, ldChild.label, $event.target.value, data.doctype, ldChild.name, ldChild)"
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
    editIcon: {
      type: Boolean,
      default: false
    }
  })

 let lTimeout = null

 function fnValidateValue (iValue, idChild) {
  const L_FROM_RANGE = parseFloat(idChild.from_range);
  const L_TO_RANGE = parseFloat(idChild.to_range);
  const L_INCREMENT = parseFloat(idChild.increment);

  // Check if from_range, to_range, and increment are valid
  if (L_FROM_RANGE !== 0 || L_TO_RANGE !== 0 || L_INCREMENT !== 0) {
    // Ensure value is within the range
    if (iValue < L_FROM_RANGE || iValue > L_TO_RANGE) {
      createToast({
        title: __("Value should be between ") + L_FROM_RANGE + " and " + L_TO_RANGE,
        icon: 'error',
        iconClasses: 'text-red-600',
      });
      return false;
    }

    // Ensure the value adheres to the increment
    if (L_INCREMENT > 0 && (iValue % L_INCREMENT !== 0)) {
      createToast({
        title: __(`Value must be a multiple of + ${L_INCREMENT}`),
        icon: 'x',
        iconClasses: 'text-red-600',
      });
      return false;
    }
  } else {
    // check if value is included in the options
    if (!idChild.options.includes(iValue)) {
      createToast({
        title: __("Value must be one of the following options"),
        text:__(idChild.options.join(', ')),
        icon: 'x',
        iconClasses: 'text-red-600',
      });
      return false;
    }
    return true;
  }

  // If all checks pass, return true
  return true;
};


// Handle input change and debounce the update call
// since we used onChnaged event
function fnHandleInputChange(iDoctype, iDocName, iFieldName, iNewValue, iSourceDoctype, iTargetFieldname, idChild) {
  clearTimeout(lTimeout)
  if (!fnValidateValue(iNewValue, idChild)) {
    return;
  }
  lTimeout = setTimeout(() => {
    fnUpdateResource(iDoctype, iDocName, iFieldName, iNewValue, iSourceDoctype, iTargetFieldname)
  }, 500)
}

  // Parameters:
  // - iDoctype: The name of the child doctype to update.
  // - iDocName: The name of the parent document to which the child belongs.
  // - iFieldName: The field in the child doctype to update.
  // - iNewValue: The new value to assign to the target field.
  // - iSourceDoctype: The source doctype from which data is being updated.
  // - iTargetFieldname: the child table field your are updating the value
  function fnUpdateResource(iDoctype, iDocName, iFieldName, iNewValue, iSourceDoctype, iTargetFieldname) {
    
    createResource({
      url: 'crm.api.docCpq.fn_update_child_table',
      params: {
        doctype : iDoctype,
        doc_name : iDocName,
        field_name : iFieldName,
        new_value : iNewValue,
        target_fieldname : iTargetFieldname
      },
      debounce: 500,
      onSuccess(data) {
        capture(`${iSourceDoctype}_updated`);
         createToast({
            title: __(`${iSourceDoctype} Updated`),
            icon: 'check',
            iconClasses: 'text-green-600',
          })
        
      },
      onError(error) {
        createToast({
          title: __('Error'),
          text: __(err.messages?.[0] || 'Error'),
          icon: 'x',
          iconClasses: 'text-red-600',
          })
      },
    }).submit();
  };
  </script> 
  <style scoped>
 .form-control {
  margin: 2px;
}
  </style>
  