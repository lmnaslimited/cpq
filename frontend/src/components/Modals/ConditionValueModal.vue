<template>
    <Dialog
      v-model="show"
      :options="{
        size: '4xl',
        title: __('Create Condition Value'),
      }"
    >
      <template #body-content>
        <div class="mb-4 grid grid-cols-1">
          <div class="flex items-center gap-3 text-sm text-gray-600">
            <div>{{ __('Select Condition Type') }}</div>
            <Link
                class="form-control"
                doctype="Condition Type"
                v-model="value.condition_type"
                placeholder="Condition Type"
              />
          </div>
        </div>
        <div class="flex flex-col gap-4">
          <div class="section first:border-t-0 first:pt-0 border-t pt-4">
            <div class="flex h-7 mb-3 max-w-fit cursor-pointer items-center gap-2 text-base font-semibold leading-5">
              {{ __('Input Value') }}
             </div>
             <div class="grid gap-4 grid-cols-2">
              <div v-for="field in LA_INPUT_FIELD" :key="field.field_name">
                <div class="settings-field">
                  <div class="mb-2 text-sm text-gray-600" >
                      {{ __(field.field_name) }}
                  </div>
                  <FormControl
                    type="text"
                    placeholder="Enter the Value"
                    v-model="LD_FORM_DATA[field.field_name]"
                  />
                </div>
              </div>
            </div>
          </div>
          <div class="section first:border-t-0 first:pt-0 border-t pt-4">
            <div class="flex h-7 mb-3 max-w-fit cursor-pointer items-center gap-2 text-base font-semibold leading-5">
              {{ __('Output Value') }}
             </div>
             <div class="grid gap-4 grid-cols-2">
              <div v-for="field in OUTPUT_FIELD" :key="field.field_name">
                <div class="settings-field">
                  <div class="mb-2 text-sm text-gray-600" >
                      {{ __(field.field_name) }}
                  </div>
                  <FormControl
                    type="text"
                    placeholder="Enter the Value"
                    v-model="LD_FORM_DATA[field.field_name]"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
      </template>
      <template #actions>
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isvalueCreating"
            @click="fnCreateNewValue"
          />
        </div>
      </template>
    </Dialog>
  </template>
  
  <script setup>
  import Link from '@/components/Controls/Link.vue'
  import { ref, reactive, watch} from 'vue'
  import { createResource} from 'frappe-ui'
  import { useRouter } from 'vue-router'
  import { capture } from '@/telemetry'
  
  const show = defineModel()
  const error = ref(null)
  const router = useRouter()
  
  const value = reactive({
    condition_type: '',
  })
  
  const isvalueCreating = ref(false)
  const LA_INPUT_FIELD = ref([])
  const OUTPUT_FIELD = ref([])
  const LD_FORM_DATA = reactive({})

  /**
 * Fetches details of a Condition Type from the Frappe backend.
 * This function makes an API call to retrieve the input and output sequences
 * of the specified Condition Type and updates the reactive variables `LA_INPUT_FIELD`
 * and `OUTPUT_FIELD` accordingly.
 */
  function fnFetchConditionType(iName){
    const data = createResource({
      url:'frappe.client.get',
      params: {'doctype': 'Condition Type', 'name': iName},
      auto: true,
      onSuccess(data){
        LA_INPUT_FIELD.value = data.input_sequence,
        OUTPUT_FIELD.value = data.output_sequence
      }
    })
  }

/**
 * Formats a given value based on the specified field's type and length.
 * If the value exceeds the maximum allowed length, it is truncated.
 * If the field type is numeric (`Int`, `Float`, `Currency`), the value is right-padded with spaces.
 * Otherwise, it is left-padded.
 */
  function fnFormatValue(iValue, idField) {
    const MAX_LENGTH = idField.length || 0 
    if (iValue.length > MAX_LENGTH) {
      return iValue.substring(0, MAX_LENGTH) 
    }

    if (['Int', 'Float', 'Currency'].includes(idField.field_type)) {
      return iValue.padStart(MAX_LENGTH, ' ') 
    } else {
      return iValue.padEnd(MAX_LENGTH, ' ') 
    }
}

/**
 * Creates a new Condition Value in Frappe.
 * This function is used to submit new condition values by sending an API request
 * to `frappe.client.insert`. The function `makeParams` dynamically constructs the 
 * request payload based on provided values.
 */
  const createConditionValue = createResource({
  url: 'frappe.client.insert',
  makeParams(values) {
    return {
      doc: {
        doctype: 'Condition Value',
        ...values,
      },
    }
  },
})

/**
 * Creates a new Condition Value record and submits it to Frappe.
 * 
 * This function:
 * 1. Constructs the `access_key` from the input sequence.
 * 2. Concatenates input and output field values based on user input.
 * 3. Submits the newly created Condition Value to the server.
 * 4. Handles success and error cases, updating the UI accordingly.
 */
function fnCreateNewValue() {
   
  const ACCESS_KEY = LA_INPUT_FIELD.value.map(f => f.field_name).join('/')
  let lInputConcatenatedValues = ''
  let lOutputConcatenatedValues = ''

  LA_INPUT_FIELD.value.forEach(field => {
    let lUserValue = LD_FORM_DATA[field.field_name] || ''
    lInputConcatenatedValues += fnFormatValue(lUserValue, field)
  })

  OUTPUT_FIELD.value.forEach(field => {
    let lUserValue = LD_FORM_DATA[field.field_name] || ''
    lOutputConcatenatedValues += fnFormatValue(lUserValue, field)
  })

  isvalueCreating.value = true

  createConditionValue.submit({
    condition_type: value.condition_type,
    access_key: ACCESS_KEY,
    input_value: lInputConcatenatedValues,
    output_value: lOutputConcatenatedValues,
  }, {
    onSuccess(data) {
      capture('condition_value_created')
      isvalueCreating.value = false
      show.value = false
      router.push({ name: 'Condition Value', params: { conditionValueId: data.name } })
    },
    onError(err) {
      isvalueCreating.value = false
      error.value = err.messages ? err.messages.join('\n') : err.message
    },
  })
}

/**
 * Watches for changes in `value.condition_type` and fetches the corresponding Condition Type.
 * 
 * If the condition type is updated, this function automatically fetches its
 * details and updates the necessary fields.
 */
  watch(() => value.condition_type, (newValue, oldValue) => {
    if (newValue !== oldValue) {
      fnFetchConditionType(newValue)
    }
  })

  </script>