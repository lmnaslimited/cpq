<template>
  <Fields :sections="sections" :data="data">
    <template #custom-fields="{ field, data }">
      <!-- Custom fields for Design CPQ -->
      <div v-if="field.type === 'Range'">
        <input
          type="range"
          :class="field.name"
          :min="field.min"
          :max="field.max"
          :step="field.step"
          v-model="data[field.name]"
          @input="updateRangeDisplay(field.name, $event.target.value)"
          @change="handleRangeChange(field.name, $event.target.value, field.min, field.max, field.step)"
          @blur="handleRangeChange(field.name, data[field.name], field.min, field.max, field.step)"
          style="width:250px; accent-color: black;"
        />
        <p
          :id="field.name"
          class="text-gray-600 rounded px-2"
          contenteditable="true"
          @input="updateRangeValue(field.name, $event.target.innerText, field.min, field.max, field.step)"
          style="background-color: #f5f5f5;"
        >
          {{ data[field.name] }}
        </p>
        <span v-if="rangeErrors[field.name]" class="text-red-500">{{ rangeErrors[field.name] }}</span>
      </div>
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

const { getUser } = usersStore()

const props = defineProps({
  sections: Array,
  data: Object,
})

// Added for Design CPQ

const rangeErrors = reactive({})

//Validation Part for Range input
//check for onlu nemeric, within min and max
// and increment step
const validateRangeIncrement = (name, value, min, max, step) => {
  const numericValue = parseFloat(value)
  const numericMin = parseFloat(min)
  const numericMax = parseFloat(max)
  const numericStep = parseFloat(step)

  if (!/^\d*\.?\d*$/.test(value)) {
    return 'Invalid Input.'
  }

  if (numericValue < numericMin || numericValue > numericMax) {
    return `Value should be between ${min} and ${max}`
  }

  const stepDecimalPlaces = step.toString().split('.')[1]?.length || 0
  const valueDecimalPlaces = (value.toString().includes('.') ? value.split('.')[1].length : 0) || 0

  if (stepDecimalPlaces > 0) {
    if (numericValue === numericMin || numericValue === numericMax) {
      return null
    }
    if (valueDecimalPlaces !== stepDecimalPlaces) {
      return `Value should increment by ${step}`
    }
  } else {
    if (value.toString().includes('.') && value.toString().split('.')[1].length === 0) {
      return 'Invalid Input.'
    }
    if ((numericValue - numericMin) % numericStep !== 0) {
      return `Value should increment by ${step}`
    }
  }

  return null
}

const updateRangeDisplay = (name, value) => {
  props.data[name] = value
  const sizeElement = document.getElementById(name)
  if (sizeElement) {
    sizeElement.innerHTML = value
  }
}

const handleRangeChange = (name, value, min, max, step) => {
  const errorMsg = validateRangeIncrement(name, value, min, max, step)
  rangeErrors[name] = errorMsg
  props.data[name] = value
}

const updateRangeValue = (name, value, min, max, step) => {
  const errorMsg = validateRangeIncrement(name, value, min, max, step)
  rangeErrors[name] = errorMsg
  props.data[name] = value
  const rangeElement = document.getElementsByClassName(name)
  if (rangeElement.length > 0) {
    rangeElement[0].value = value
  }
}

const setInitialValues = () => {
  for (const section of props.sections) {
    for (const field of section.fields) {
      if (field.type === 'Range') {
        const name = field.name
        const min = field.min
        if (props.data[name] === undefined || props.data[name] === null || props.data[name] === '') {
          props.data[name] = min
          updateRangeValue(name, min, min, field.max, field.step)
          updateRangeDisplay(name, min)
        }
      }
    }
  }
}

onMounted(() => {
  watch(
    () => props.sections,
    (newValue, oldValue) => {
      if (newValue !== oldValue && newValue.length > 0) {
        setInitialValues()
      }
    }
  )
})
</script>

<style scoped>
:deep(.form-control.prefix select) {
  padding-left: 2rem;
}
</style>