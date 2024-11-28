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
import { validateRangeIncrement } from '@/cpqUtils.js'

const { getUser } = usersStore()

const props = defineProps({
  sections: Array,
  data: Object,
})

// Reactive object to hold validation errors for range fields
const rangeErrors = reactive({})


// Update display of range value in the text below the input
const updateRangeDisplay = (name, value) => {
  props.data[name] = value
  const sizeElement = document.getElementById(name)
  if (sizeElement) {
    sizeElement.innerHTML = value
  }
}

// Handle range value change and validation
const handleRangeChange = (name, value, min, max, step) => {
  const errorMsg = validateRangeIncrement(name, value, min, max, step)
  rangeErrors[name] = errorMsg
  props.data[name] = value
}

// Update range input from the text below and revalidate
const updateRangeValue = (name, value, min, max, step) => {
  const errorMsg = validateRangeIncrement(name, value, min, max, step)
  rangeErrors[name] = errorMsg
  props.data[name] = value
  const rangeElement = document.getElementsByClassName(name)
  if (rangeElement.length > 0) {
    rangeElement[0].value = value
  }
}

// Set initial values for range fields when sections change
const setInitialValues = () => {
  for (const section of props.sections) {
    for (const field of section.fields) {
      if (field.type === 'Range') {
        const name = field.name
        const min = field.min
        // Set initial value to min if not defined
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