<template>
  <Fields :sections="sections" :data="data">
    <template #custom-fields="{ field, data }">
      <!-- Custom fields for Design CPQ -->
      <div v-if="field.type === 'Range'">
         <p class="mb-2 text-sm text-gray-600">{{ __(field.label) }}</p>
        <input
          type="range"
          :class="field.name"
          :min="field.min"
          :max="field.max"
          :step="field.step"
          v-model="data[field.name]"
          @input="fnUpdateRangeDisplay(field.name, $event.target.value)"
          @change="fnHandleRangeChange(field.name, $event.target.value, field.min, field.max, field.step)"
          @blur="fnHandleRangeChange(field.name, data[field.name], field.min, field.max, field.step)"
          style="width:250px; accent-color: black;"
        />
        <p
          :id="field.name"
          class="text-gray-600 rounded px-2"
          contenteditable="true"
          @input="fnUpdateRangeValue(field.name, $event.target.innerText, field.min, field.max, field.step)"
          style="background-color: #f5f5f5;"
        >
          {{ data[field.name] }}
        </p>
        <span v-if="rangeErrors[field.name]" class="text-red-500">{{ rangeErrors[field.name] }}</span>
      </div>
      <div v-else-if="field.type == 'Text Editor'">
        <p class="mb-2 text-sm text-gray-600">{{ __(field.label) }}</p>
        <TextEditor
            variant="outline"
            ref="content"
            editor-class="!prose-sm overflow-auto min-h-[180px] max-h-80 py-1.5 px-2 rounded border border-gray-300 bg-white hover:border-gray-400 hover:shadow-sm focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors"
            :bubbleMenu="true"
            :content="data[field.name]"
            @change="(val) => (data[field.name] = val)"
            :placeholder="
              __('Took a call with John Doe and discussed the new project.')
            "
          />
      </div>
      <div v-else-if="field.type == 'Table'"></div>
      <div v-else-if="field.type === 'textbox'">
        <FormControl
          type="textarea"
          size="sm"
          variant="subtle"
          :placeholder="__(field.placeholder)"
          :disabled="false"
          v-model="data[field.name]"
        />
      </div>
    </template>
  </Fields>
</template>

<script setup>
import Fields from '@/components/Fields.vue'
import { usersStore } from '@/stores/users'
import { reactive, watch, onMounted } from 'vue'
import { validateRangeIncrement } from '@/cpqUtils.js'
import { TextEditor } from 'frappe-ui'

const { getUser } = usersStore()

const props = defineProps({
  sections: Array,
  data: Object,
})

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
    for (const LD_FIELD of LD_SECTION.fields) {
      if (LD_FIELD.type === 'Range') {
        const L_NAME = LD_FIELD.name
        const L_DEFAULT = LD_FIELD.default ? LD_FIELD.default : LD_FIELD.min
        // Set initial value to min if not defined
        if (props.data[L_NAME] === undefined || props.data[L_NAME] === null || props.data[L_NAME] === '' || props.data[L_NAME]) {
          props.data[L_NAME] = L_DEFAULT
          fnUpdateRangeValue(L_NAME, L_DEFAULT, L_DEFAULT, LD_FIELD.max, LD_FIELD.step)
          fnUpdateRangeDisplay(L_NAME, L_DEFAULT)
        }
      }else if (LD_FIELD.type === 'Select') {
        const L_NAME = LD_FIELD.name
        // Set default value for select field
        if (props.data[L_NAME] === undefined || props.data[L_NAME] === null || props.data[L_NAME]) {
          props.data[L_NAME] = LD_FIELD.default ? LD_FIELD.default : undefined
        }
      }
    }
  }
}

onMounted(() => {
  watch(
    () => props.sections,
    () => {
      fnSetInitialValues()
  
    }
  )
})
</script>

<style scoped>
:deep(.form-control.prefix select) {
  padding-left: 2rem;
}
</style>