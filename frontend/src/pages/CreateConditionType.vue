<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs
        :items="[
          {
            label: __('Condition Types'),
            route: { name: 'Condition Types' },
          }
        ]"
      >
        <template #prefix="{ item }"></template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <Button
        :label="__('Save')"
        variant="solid"
        :loading="isConditionCreating"
        @click="fnCreateNewCondition"
        size="md"
      />
    </template>
  </LayoutHeader>
  <div class="flex h-full overflow-hidden">
    <div class="w-3/4 h-full">
      <Section is-opened="Opened" label="Input Sequence">
        <div class="w-[70%] p-4 h-1/2">
        <div class="overflow-x-auto rounded-md">
          <table class="table-fixed border-collapse w-full text-center">
            <thead class="bg-gray-100 rounded-lg text-gray-600 border">
              <tr class="text-center text-sm bg-gray-200">
                <th class="px-6 py-1 w-6 text-center border-r border-gray-400">
                  <FormControl
                    type="checkbox"
                    v-model="SELECT_ALL"
                    @change="fnToggleSelectAll('input')"
                    class="form-control"
                  />
                </th>
                <th class="px-4 py-2 border-r border-gray-400 text-sm text-center w-40"> {{ __('Field Name') }}</th>
                <th class="px-4 py-2 border-r border-gray-400 text-sm text-center w-40"> {{ __('Length') }}</th>
                <th class="px-4 py-2 border-r border-gray-400 text-sm text-center w-40"> {{ __('Field Type') }}</th>
                <th class="px-4 py-2 text-sm text-center w-6"> {{ __('Edit') }}</th>
              </tr>
            </thead>
            <tbody class="rounded-t-md">
              <tr
                v-for="(row, index) in LA_ROWS"
                :key="index"
                class="text-sm"
              >
                <td class="px-4 py-1 border border-gray-400">
                  <FormControl
                    type="checkbox"
                    v-model="row.selected"
                    class="form-control"
                  />
                </td>
                <td class="border border-gray-300 px-2 py-1">
                  <Autocomplete
                    :value="row.field_name"
                    :options="fields.data"
                    placeholder="Add field"
                    @change="(e) => fnUpdateField(index, e, 'input')"
                  >
                    <template #item-label="{ option }">
                      <div class="flex flex-col gap-1">
                        <div>{{ option.label }}</div>
                        <div class="text-gray-500 text-sm">
                          {{ `${option.fieldname} - ${option.fieldtype}` }}
                        </div>
                      </div>
                    </template>
                  </Autocomplete>
                </td>
                <td class="border border-gray-300 px-2 py-1">
                  <FormControl
                    type="number"
                    placeholder="Enter Length"
                    v-model="row.length"
                  />
                </td>
                <td class="border border-gray-300 px-2 py-1">{{ row.field_type }}</td>
                <td class="px-4 py-1 border border-gray-400">
                  <Button
                    @click="showEditDialog.value=true"
                    variant="ghost"
                    class="w-7 mr-2"
                  >
                  <EditIcon class="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td class=" flex py-2">
                  <button
                    @click="fnAddRow('input')"
                    class="border border-gray-500 text-black px-2 py-1 text-sm rounded-md"
                  >
                    Add
                  </button>
                  <button
                    v-if="selectedRows.length > 0"
                    @click="fnDeleteRow('input')"
                    class="border border-red-500 text-red-500 px-2 py-1 text-sm rounded-md ml-4"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
      </Section>
      <Section is-opened="Opened" label="Output Sequence">
        <div class="w-[70%] p-4 h-1/2">
        <div class="overflow-x-auto rounded-md">
          <table class="table-fixed border-collapse w-full text-center">
            <thead class="bg-gray-100 rounded-lg text-gray-600 border">
              <tr class="text-center text-sm bg-gray-200">
                <th class="px-6 py-1 w-6 text-center border-r border-gray-400">
                  <FormControl
                    type="checkbox"
                    v-model="OUTPUT_SELECT_ALL"
                    @change="fnToggleSelectAll('output')"
                    class="form-control"
                  />
                </th>
                <th class="px-4 py-2 border-r border-gray-400 text-sm text-center w-40"> {{ __('Field Name') }}</th>
                <th class="px-4 py-2 border-r border-gray-400 text-sm text-center w-40"> {{ __('Length') }}</th>
                <th class="px-4 py-2 border-r border-gray-400 text-sm text-center w-40"> {{ __('Field Type') }}</th>
                <th class="px-4 py-2 text-sm text-center w-6"> {{ __('Edit') }}</th>
              </tr>
            </thead>
            <tbody class="rounded-t-md">
              <tr
                v-for="(row, index) in OUTPUT_ROWS"
                :key="index"
                class="text-sm"
              >
                <td class="px-4 py-1 border border-gray-400">
                  <FormControl
                    type="checkbox"
                    v-model="row.selected"
                    class="form-control"
                  />
                </td>
                <td class="border border-gray-300 px-2 py-1">
                  <Autocomplete
                    :value="row.field_name"
                    :options="fields.data"
                    placeholder="Add field"
                    @change="(e) => fnUpdateField(index, e, 'output')"
                  >
                    <template #item-label="{ option }">
                      <div class="flex flex-col gap-1">
                        <div>{{ option.label }}</div>
                        <div class="text-gray-500 text-sm">
                          {{ `${option.fieldname} - ${option.fieldtype}` }}
                        </div>
                      </div>
                    </template>
                  </Autocomplete>
                </td>
                <td class="border border-gray-300 px-2 py-1">
                  <FormControl
                    type="number"
                    placeholder="Enter Length"
                    v-model="row.length"
                  />
                </td>
                <td class="border border-gray-300 px-2 py-1">{{ row.field_type }}</td>
                <td class="px-4 py-1 border border-gray-400">
                  <Button
                    @click="showEditDialog.value=true"
                    variant="ghost"
                    class="w-7 mr-2"
                  >
                  <EditIcon class="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td class="flex py-2">
                  <button
                    @click="fnAddRow('output')"
                    class="border border-gray-500 text-black px-2 py-1 text-sm rounded-md"
                  >
                    Add
                  </button>
                  <button
                    v-if="outputSelectRow.length > 0"
                    @click="fnDeleteRow('output')"
                    class="border border-red-500 text-red-500 px-2 py-1 text-sm rounded-md ml-4"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
      </Section>
    </div>
    <div class="flex flex-col justify-between border-l">
      <div
        class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium"
      >
        {{ __('Detail') }}
      </div>
      <div class="flex flex-1 flex-col justify-between overflow-hidden">
        <div class="flex flex-col overflow-y-auto">
          <div class="flex flex-col gap-4 overflow-y-auto">
            <template v-for="(field, index) in SIDE_PANNEL_FIELD" :key="index">
              <div class="section-field flex items-center gap-2 px-3 leading-5 first:mt-3">
                <div class="sm:w-[106px] w-36 shrink-0 truncate text-sm text-gray-600 px-2 py-1">
                  <span>
                    {{ field.label }}
                  </span>
                  <span v-if="field.required" class="text-red-500"> *</span>
                </div>
                <div class="grid min-h-[28px] flex-1 items-center overflow-hidden text-base">
                  <!-- Conditional rendering -->
                  <template v-if="field.type === 'link'">
                    <Link
                      v-model="field.model"
                      :doctype="field.props.doctype"
                      :placeholder="field.props.placeholder"
                      :class="field.props.class"
                      :variant="field.props.variant"
                    />
                  </template>
                  <template v-else-if="field.type === 'checkbox'">
                    <FormControl
                      type="checkbox"
                      v-model="field.model"
                      :class="field.props.class"
                    />
                  </template>
                  <template v-else-if="field.type === 'text'">
                    <FormControl
                      type="text"
                      v-model="field.model"
                      :placeholder="field.props.placeholder"
                      :class="field.props.class"
                      :variant="field.props.variant"
                    />
                  </template>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import { ref, watch, computed } from 'vue'
import Section from '@/components/Section.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import Autocomplete from '@/components/frappe-ui/Autocomplete.vue'
import { useRouter } from 'vue-router'
import { capture } from '@/telemetry'
import {
  Breadcrumbs,
  createResource
} from 'frappe-ui'

const router = useRouter()
// Fields Data Configuration
const DOCTYPE = ref('')
const CONDITION_TYPE = ref('')
const IS_FORMULA = ref(false)
const IS_API = ref(false)
const IS_VALUE = ref(false)
const ENABLE = ref(false)
const isConditionCreating = ref(false)
const error = ref(null)
const showEditDialog = ref(false)
const SELECT_ALL = ref(false)
const OUTPUT_SELECT_ALL = ref(false)
const LA_ROWS = ref([
  { field_name: '', length: '', field_type: '', selected: false },
])

const OUTPUT_ROWS = ref([
  {field_name: '', length: '', field_type: '', selected: false},
])

const SIDE_PANNEL_FIELD = ref([
  {
    label: __('Document Reference'),
    required: true,
    type: 'link',
    model: DOCTYPE,
    props: {
      class: 'form-control',
      doctype: 'DocType',
      variant: 'outline',
      placeholder: 'Document Reference',
    },
  },
  {
    label: __('Condition Type'),
    required: true,
    type: 'text',
    model: CONDITION_TYPE,
    props: {
      placeholder: 'Condition Type',
      class: 'form-control',
      variant: 'outline',
    },
  },
  {
    label: __('Is Formula Based'),
    required: false,
    type: 'checkbox',
    model: IS_FORMULA,
    props: {
      class: 'form-control',
    },
  },
  {
    label: __('Is API Based'),
    required: false,
    type: 'checkbox',
    model: IS_API,
    props: {
      class: 'form-control',
    },
  },
  {
    label: __('Is Value Based'),
    required: false,
    type: 'checkbox',
    model: IS_VALUE,
    props: {
      class: 'form-control',
    },
  },
  {
    label: __('Enable'),
    required: false,
    type: 'checkbox',
    model: ENABLE,
    props: {
      class: 'form-control',
    },
  },
])

const RESTRICTED_FIELD_TYPES = [
  'Table', 'Geolocation', 'Attach', 'Attach Image', 'HTML', 'Signature',
]

const params = computed(() => {
  return {
    doctype: DOCTYPE.value,
    restricted_fieldtypes: RESTRICTED_FIELD_TYPES,
    as_array: true,
  }
})

const fields = createResource({
  url: 'crm.api.doc.get_fields_meta',
  params: params.value,
  auto: DOCTYPE.value == '' ? false : true,
})

const selectedRows = computed(() => LA_ROWS.value.filter((row) => row.selected))
const outputSelectRow = computed(() => OUTPUT_ROWS.value.filter((row) => row.selected))

/**
 * Adds a new row to either the input table (LA_ROWS) or output table (OUTPUT_ROWS).
 * The function accepts 'iRowName' to determine which table to update.
 * A new row is initialized with empty field values and 'selected' set to false.
 */
function fnAddRow(iRowName) {
  if(iRowName == 'input'){
    LA_ROWS.value.push({ field_name: '', length: '', field_type: '', selected: false })
  } else{
    OUTPUT_ROWS.value.push({ field_name: '', length: '', field_type: '', selected: false })
  }
}

/**
 * Deletes selected rows from either the input table (LA_ROWS) or output table (OUTPUT_ROWS).
 * The function filters out the rows where 'selected' is true.
 * It also resets the select-all checkbox for the respective table.
 */
function fnDeleteRow(iRowName) {
  if(iRowName == 'input'){
    LA_ROWS.value = LA_ROWS.value.filter((row) => !row.selected)
    SELECT_ALL.value = false
  }else{
    OUTPUT_ROWS.value = OUTPUT_ROWS.value.filter((row) => !row.selected)
    OUTPUT_SELECT_ALL.value = false
  }
}

/**
 * Toggles the selection of all rows in either the input table (LA_ROWS) or output table (OUTPUT_ROWS).
 * When the select-all checkbox is checked, all rows are marked as selected.
 * When unchecked, all rows are deselected.
 */
function fnToggleSelectAll(iRowName) {
  if(iRowName == 'input'){
    LA_ROWS.value.forEach((idRow) => {
      idRow.selected = SELECT_ALL.value
    })
  }else{
    OUTPUT_ROWS.value.forEach((idRow) => {
      idRow.selected = OUTPUT_SELECT_ALL.value
  })
  }
}

/**
 * Updates the field name and field type of a specific row in either 
 * the input table (LA_ROWS) or output table (OUTPUT_ROWS).
 * It modifies the row at the specified index based on the selected field.
 */
function fnUpdateField(index, field, iRowName) {
  if(iRowName == 'input'){
    LA_ROWS.value[index].field_name = field.label
    LA_ROWS.value[index].field_type = field.fieldtype
  }else{
    OUTPUT_ROWS.value[index].field_name = field.label
    OUTPUT_ROWS.value[index].field_type = field.fieldtype
  }
}

/**
 * Watches for changes in the DOCTYPE value.
 * When DOCTYPE changes, it triggers a fetch for field metadata.
 * It also resets the input (LA_ROWS) and output (OUTPUT_ROWS) tables to their default states.
 */
watch(DOCTYPE, (newVal) => {
  if (newVal) {
    fields.fetch(params.value)
    LA_ROWS.value = [
  { field_name: '', length: '', field_type: '', selected: false },
]
OUTPUT_ROWS.value = [
    { field_name: '', length: '', field_type: '', selected: false },
  ]
  }
})

/**
 * Creates a new condition entry in the database.
 * Constructs a document with input and output sequences based on the current selections.
 * Performs validation checks before submission.
 * On success, redirects to the created condition type.
 * On error, displays appropriate messages.
 */
const createCondition = createResource({
  url: 'frappe.client.insert',
  makeParams(values) {
    return {
      doc: {
        doctype: 'Condition Type',
        ...values
      },
    }
  },
})
function fnCreateNewCondition() {
  const VALUES = {
    document_reference: DOCTYPE.value,
    condition_type: CONDITION_TYPE.value,
    enable: ENABLE.value,
    is_formula_based: IS_FORMULA.value,
    is_api_based: IS_API.value,
    is_value_based: IS_VALUE.value,
    input_sequence: LA_ROWS.value,
    output_sequence: OUTPUT_ROWS.value
  }
  createCondition.submit(VALUES, {
   validate() {
     error.value = null
     if (!CONDITION_TYPE.value) {
       error.value = __('Condition Type is mandatory')
       return error.value
     }
     if(!DOCTYPE.value){
      error.value = __('Document Reference is mandatory')
       return error.value
     }
     isConditionCreating.value = true
   },
   onSuccess(data) {
     capture('condition_type_created')
     isConditionCreating.value = false
     router.push({ name: 'Condition Type', params: { conditionId: data.name } })
   },
   onError(err) {
    isConditionCreating.value = false
     if (!err.messages) {
       error.value = err.message
       return
     }
     error.value = err.messages.join('\n')
   },
 })
}
</script>