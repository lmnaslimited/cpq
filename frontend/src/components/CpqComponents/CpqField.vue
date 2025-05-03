<template>
    <Field
    v-for="field in sections"
    :key="field.fieldname"
    :field="field"
    :data-name="field.fieldname"
  >
      <template #custom-fields="{ field }">
        <!-- Custom fields for Design CPQ -->
        <div v-if="field.fieldtype === 'Range'">
           <p class="mb-2 text-sm text-gray-600">{{ __(field.label) }}</p>
          <input
            type="range"
            :class="field.fieldname"
            :min="field.min"
            :max="field.max"
            :step="field.step"
            v-model="data[field.fieldname]"
            @input="fnUpdateRangeDisplay(field.fieldname, $event.target.value)"
            @change="fnHandleRangeChange(field.fieldname, $event.target.value, field.min, field.max, field.step)"
            @blur="fnHandleRangeChange(field.fieldname, data[field.fieldname], field.min, field.max, field.step)"
            style="width:250px; accent-color: black;"
          />
          <p
            :id="field.fieldname"
            class="text-gray-600 rounded px-2"
            contenteditable="true"
            @input="fnUpdateRangeValue(field.fieldname, $event.target.innerText, field.min, field.max, field.step)"
            style="background-color: #f5f5f5;"
          >
            {{ data[field.fieldname] }}
          </p>
          <span v-if="rangeErrors[field.fieldname]" class="text-red-500">{{ rangeErrors[field.fieldname] }}</span>
        </div>
      </template>
    </Field>
  </template>
  
  <script setup>
  import Field from '@/components/FieldLayout/Field.vue'
  import { reactive, watch, provide, computed } from 'vue'
  import { validateRangeIncrement } from '@/cpqUtils.js'
  
  const props = defineProps({
    sections: Array,
    data: Object,
    doctype: String,
    preview: {
      type: Boolean,
      default: false,
  },
  })
  
  provide('doctype', props.doctype)
  provide('preview', props.preview)
  provide(
  'data',
  computed(() => props.data),
)

  // Reactive object to hold validation errors for range fields
  const rangeErrors = reactive({})
  
  
  // Update display of range value in the text below the input
  function fnUpdateRangeDisplay(iName, iValue){
    props.data[iName] = iValue
    const L_ELEMENT = document.getElementById(iName)
    if (L_ELEMENT) {
      L_ELEMENT.innerHTML = iValue
    }
  }
  
  // Handle range value change and validation
  function fnHandleRangeChange(iName, iValue, iMin, iMax, iStep) {
    const L_ERROR = validateRangeIncrement(iName, iValue, iMin, iMax, iStep)
    rangeErrors[iName] = L_ERROR
    props.data[iName] = iValue
  }
  
  // Update range input from the text below and revalidate
  function fnUpdateRangeValue (iName, iValue, iMin, iMax, iStep) {
    const L_ERROR = validateRangeIncrement(iName, iValue, iMin, iMax, iStep)
    rangeErrors[iName] = L_ERROR
    props.data[iName] = iValue
    const LA_RANGE_ELEMENT = document.getElementsByClassName(iName)
    if (LA_RANGE_ELEMENT.length > 0) {
      LA_RANGE_ELEMENT[0].value = iValue
    }
  }
  
  // Set initial values for range fields when sections change
  function fnSetInitialValues() {
    for (const LD_SECTION of props.sections) {
        if (LD_SECTION.fieldtype === 'Range') {
          const L_NAME = LD_SECTION.fieldname
          const L_DEFAULT = LD_SECTION.default ? LD_SECTION.default : LD_SECTION.min
          // Set initial value to min if not defined
          if (props.data[L_NAME] === undefined || props.data[L_NAME] === null || props.data[L_NAME] === '' || props.data[L_NAME]) {
            props.data[L_NAME] = L_DEFAULT
            fnUpdateRangeValue(L_NAME, L_DEFAULT, L_DEFAULT, LD_SECTION.max, LD_SECTION.step)
            fnUpdateRangeDisplay(L_NAME, L_DEFAULT)
          }
        }else if (LD_SECTION.fieldtype === 'Select') {
          const L_NAME = LD_SECTION.fieldname
          // Set default value for select field
          if (props.data[L_NAME] === undefined || props.data[L_NAME] === null || props.data[L_NAME]) {
            props.data[L_NAME] = LD_SECTION.default ? LD_SECTION.default : undefined
          }
        }
      
    }
  }
  
  watch(
  () => props.sections,
  () => {
    fnSetInitialValues()
  },
  { immediate: true }
)

  </script>
  
  <style scoped>
  :deep(.form-control.prefix select) {
    padding-left: 2rem;
  }
  </style>