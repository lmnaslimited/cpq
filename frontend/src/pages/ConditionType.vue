<template>
  <LayoutHeader v-if="condition.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
     
    </template>
  </LayoutHeader>
  <div v-if="condition?.data" class="flex h-full overflow-hidden">
    <div class="w-3/4 h-full flex flex-col space-y-4">
      <FadedScrollableDiv
        class="flex flex-col gap-1.5 overflow-y-auto max-h-full"
      >
    <Section is-opened="Opened" label="Input Sequence">
      <FadedScrollableDiv
        class="flex flex-col gap-1.5 overflow-y-auto max-h-[500px]"
      >
      <div class="w-[70%] p-4">
        <div class="overflow-x-auto rounded-md">
          <table class="table-fixed border-collapse w-full text-center" v-if="inputRows">
            <thead class="bg-gray-100 rounded-lg text-gray-600 border">
              <tr class="text-center text-sm bg-gray-200">
                <th class="px-6 py-1 w-6 text-center border-r border-gray-400">
                  <FormControl
                    type="checkbox"
                    v-model="SELECT_ALL"
                    class="form-control"
                    @change="fnToggleSelectAll('inputRow')"
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
                v-for="(row, index) in inputRows"
                :key="index"
                class="text-sm"
              >
                <td class="px-4 py-1 border border-gray-400">
                  <FormControl
                    type="checkbox"
                    v-model="row.selected"
                    class="form-control"
                    @click="fnToggleRowSelection('inputRow', row, row.selected)"
                  />
                </td>
                <td class="border border-gray-300 px-2 py-1">
                  <Autocomplete
                    :value="row.field_name"
                    :options="fields.data"
                    placeholder="Add field"
                    @change="(e) => fnUpdateRow(index, e, 'inputRow')"
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
                    @click="fnAddRow('inputRow')"
                    class="border border-gray-500 text-black px-2 py-1 text-sm rounded-md"
                  >
                    Add
                  </button>
                  <button
                  v-if="LA_SELECTED_ROWS_INPUT.length > 0"
                    @click="fnDeleteSelectedRows('inputRow')"
                    class="border border-red-500 text-red-500 px-2 py-1 text-sm rounded-md ml-4"
                  >
                    Delete
                  </button>
                  <button
                   @click="fnUpdateChildTable('input_sequence', inputRows)"
                    class="border border-green-500 text-green-500 px-2 py-1 text-sm rounded-md ml-4"
                  >
                    Update
                  </button>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
      </FadedScrollableDiv>
    </Section>
    <Section is-opened="Opened" label="Output Sequence">
      <FadedScrollableDiv
        class="flex flex-col gap-1.5 overflow-y-auto max-h-[500px]"
      >
      <div class="w-[70%] p-4">
        <div class="overflow-x-auto rounded-md">
          <table class="table-fixed border-collapse w-full text-center" v-if="outputRows">
            <thead class="bg-gray-100 rounded-lg text-gray-600 border">
              <tr class="text-center text-sm bg-gray-200">
                <th class="px-6 py-1 w-6 text-center border-r border-gray-400">
                  <FormControl
                    type="checkbox"
                    v-model="SELECT_OUTPUT_ALL"
                    class="form-control"
                    @change="fnToggleSelectAll('outputRow')"
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
                v-for="(row, index) in outputRows"
                :key="index"
                class="text-sm"
              >
                <td class="px-4 py-1 border border-gray-400">
                  <FormControl
                    type="checkbox"
                    v-model="row.selected"
                    class="form-control"
                    @click="fnToggleRowSelection('outputRow', row, row.selected)"
                  />
                </td>
                <td class="border border-gray-300 px-2 py-1">
                  <Autocomplete
                    :value="row.field_name"
                    :options="fields.data"
                    placeholder="Add field"
                    @change="(e) => fnUpdateRow(index, e, 'outputRow')"
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
                  @click="fnAddRow('outputRow')"
                    class="border border-gray-500 text-black px-2 py-1 text-sm rounded-md"
                  >
                    Add
                  </button>
                  <button
                  v-if="LA_SELECTED_ROWS_OUTPUT.length > 0"
                   @click="fnDeleteSelectedRows('outputRow')"
                    class="border border-red-500 text-red-500 px-2 py-1 text-sm rounded-md ml-4"
                  >
                    Delete
                  </button>
                  <button
                   @click="fnUpdateChildTable('output_sequence', outputRows)"
                    class="border border-green-500 text-green-500 px-2 py-1 text-sm rounded-md ml-4"
                  >
                    Update
                  </button>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </FadedScrollableDiv>
    </Section>
  </FadedScrollableDiv>
  </div>
    <Resizer class="flex flex-col justify-between border-l" side="right">
      <div
        class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium"
        @click="copyToClipboard(condition.data.name)"
      >
        {{ __(condition.data.name) }}
      </div>
      <div
        v-if="fieldsLayout.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <div class="flex flex-col overflow-y-auto">
          <div
            v-for="(section, i) in fieldsLayout.data"
            :key="section.label"
            class="flex flex-col p-3"
            :class="{ 'border-b': i !== fieldsLayout.data.length - 1 }"
          >
            <Section :is-opened="section.opened" :label="section.label">
              <SectionFields
                :fields="section.fields"
                :isLastSection="i == fieldsLayout.data.length - 1"
                v-model="condition.data"
                @update="updateField"
              />
            </Section>
          </div>
        </div>
      </div>
    </Resizer>
  </div>
  <AssignmentModal
    v-if="showAssignmentModal"
    v-model="showAssignmentModal"
    v-model:assignees="condition.data._assignedTo"
    :doc="condition.data"
    doctype="Condition Type"
  />
  
  <SidePanelModal
    v-if="showSidePanelModal"
    v-model="showSidePanelModal"
    @reload="() => fieldsLayout.reload()"
  />
</template>
<script setup>
import Icon from '@/components/Icon.vue'
import Resizer from '@/components/Resizer.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import AssignmentModal from '@/components/Modals/AssignmentModal.vue'
import SidePanelModal from '@/components/Settings/SidePanelModal.vue'
import Section from '@/components/Section.vue'
import SectionFields from '@/components/SectionFields.vue'
import Autocomplete from '@/components/frappe-ui/Autocomplete.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import FadedScrollableDiv from '@/components/FadedScrollableDiv.vue'
import {
  createToast,
  setupAssignees,
  setupCustomizations,
  copyToClipboard,
} from '@/utils'
import { getView } from '@/utils/view'
import { globalStore } from '@/stores/global'
import {
  createResource,
  Breadcrumbs,
  call,
  usePageMeta,
} from 'frappe-ui'
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const { $dialog, $socket } = globalStore()
const route = useRoute()
const router = useRouter()

const props = defineProps({
  conditionId: {
    type: String,
    required: true,
  },
})

const customActions = ref([])
const customStatuses = ref([])
const SELECT_ALL = ref(false)
const SELECT_OUTPUT_ALL = ref(false)
const DOCTYPE = ref('')

const condition = createResource({
  url: 'crm.cpq.doctype.condition_type.api.get_condition_type',
  params: { name: props.conditionId },
  onSuccess: async (data) => {
    DOCTYPE.value = data.document_reference
    let obj = {
      doc: data,
      $dialog,
      $socket,
      router,
      updateField,
      createToast,
      deleteDoc: deleteCondition,
      resource: {
        condition,
        fieldsLayout,
      },
      call,
    }
    setupAssignees(data)
    let customization = await setupCustomizations(data, obj)
    customActions.value = customization.actions || []
    customStatuses.value = customization.statuses || []
  },
})

onMounted(() => {
  if (condition.data) return
  condition.fetch().then(() =>{
    fields.fetch(params.value)
  })
})

const reload = ref(false)
const showAssignmentModal = ref(false)
const showSidePanelModal = ref(false)

function updateCondition(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  if (!Array.isArray(fieldname) && validateRequired(fieldname, value)) return

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'Condition Type',
      name: props.conditionId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      condition.reload()
      reload.value = true
      if(fieldname == 'document_reference'){
        DOCTYPE.value = value
        fields.fetch(params.value)
      }
      createToast({
        title: __('condition updated'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      callback?.()
    },
    onError: (err) => {
      createToast({
        title: __('Error updating condition'),
        text: __(err.messages?.[0]),
        icon: 'x',
        iconClasses: 'text-red-600',
      })
    },
  })
}

function validateRequired(fieldname, value) {
  let meta = condition.data.fields_meta || {}
  if (meta[fieldname]?.reqd && !value) {
    createToast({
      title: __('Error Updating condition'),
      text: __('{0} is a required field', [meta[fieldname].label]),
      icon: 'x',
      iconClasses: 'text-red-600',
    })
    return true
  }
  return false
}

const breadcrumbs = computed(() => {
  let items = [{ label: __('Condition Types'), route: { name: 'Condition Types' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'Condition Type')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Condition Types',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: condition.data.name || __('Untitled'),
    route: { name: 'Condition Type', params: { conditionId: condition.data.name } },
  })
  return items
})

usePageMeta(() => {
  return {
    title: condition.data?.name || condition.data?.name,
  }
})

const fieldsLayout = createResource({
  url: 'crm.api.doc.get_sidebar_fields',
  cache: ['fieldsLayout', props.conditionId],
  params: { doctype: 'Condition Type', name: props.conditionId },
  auto: true,
})

function updateField(name, value, callback) {
  updateCondition(name, value, () => {
    condition.data[name] = value
    callback?.()
  })
}

async function deleteCondition(name) {
  await call('frappe.client.delete', {
    doctype: 'Condition Type',
    name,
  })
  router.push({ name: 'Condition Types' })
}

const inputRows = computed(()=> {
  return condition.data.input_sequence
})

const outputRows = computed(()=> {
  return condition.data.output_sequence
})

const LA_SELECTED_ROWS_INPUT = ref([]);
const LA_SELECTED_ROWS_OUTPUT = ref([])

/**
 * Toggles the selection of all rows in the specified table.
 * 
 * @param {string} iRowName - The name of the row group ('inputRow' or 'outputRow').
*/
function fnToggleSelectAll(iRowName) {
  if (iRowName === 'inputRow') {
    SELECT_ALL.value = !SELECT_ALL.value;
    inputRows.value.forEach((idRow) => {
      idRow.selected = SELECT_ALL.value;
    });
    LA_SELECTED_ROWS_INPUT.value = [...inputRows.value];
  } else {
    SELECT_OUTPUT_ALL.value = !SELECT_OUTPUT_ALL.value;
    outputRows.value.forEach((idRow) => {
      idRow.selected = SELECT_OUTPUT_ALL.value;
    });
    LA_SELECTED_ROWS_OUTPUT.value = [...outputRows.value];
  }
}

/**
 * Toggles the selection of a single row.
 * 
 * @param {string} iRowName - The name of the row group ('inputRow' or 'outputRow').
 * @param {object} idRow - The row object being toggled.
 * @param {boolean} iIsSelected - Whether the row is currently selected.
 */
function fnToggleRowSelection(iRowName, idRow, iIsSelected) {
  if (iRowName === 'inputRow') {
    if (!iIsSelected) {
      // If the row is selected, add it to the LA_SELECTED_ROWS_INPUT array
      if (!LA_SELECTED_ROWS_INPUT.value.includes(idRow)) {
        LA_SELECTED_ROWS_INPUT.value.push(idRow);
      }
    } else {
      // If the row is unselected, remove it from the LA_SELECTED_ROWS_INPUT array
      LA_SELECTED_ROWS_INPUT.value = LA_SELECTED_ROWS_INPUT.value.filter((r) => r !== idRow);
    }
  } else {
    if (!iIsSelected) {
      // If the row is selected, add it to the LA_SELECTED_ROWS_OUTPUT array
      if (!LA_SELECTED_ROWS_OUTPUT.value.includes(idRow)) {
        LA_SELECTED_ROWS_OUTPUT.value.push(idRow);
      }
    } else {
      // If the row is unselected, remove it from the LA_SELECTED_ROWS_OUTPUT array
      LA_SELECTED_ROWS_OUTPUT.value = LA_SELECTED_ROWS_OUTPUT.value.filter((idRow) => idRow !== idRow);
    }
  }
}

 /**
 * Adds a new empty row to the specified row group.
 * 
 * @param {string} iRowName - The name of the row group ('inputRow' or 'outputRow').
 */
function fnAddRow(iRowName) {
  const NEW_ROW = {
    field_name: '',
    length: '',
    field_type: '',
    selected: false,
  };
  if (iRowName === 'inputRow') {
    condition.data.input_sequence.push(NEW_ROW);
  } else {
    condition.data.output_sequence.push(NEW_ROW);
  }
}

 /**
 * Deletes all selected rows from the specified row group.
 * 
 * @param {string} iRowName - The name of the row group ('inputRow' or 'outputRow').
 */
function fnDeleteSelectedRows(iRowName) {
  if (iRowName === 'inputRow') {
    condition.data.input_sequence = condition.data.input_sequence.filter(
      (idRow) => !LA_SELECTED_ROWS_INPUT.value.includes(idRow)
    );
    LA_SELECTED_ROWS_INPUT.value = [];
    SELECT_ALL.value = false;
  } else {
    condition.data.output_sequence = condition.data.output_sequence.filter(
      (idRow) => !LA_SELECTED_ROWS_OUTPUT.value.includes(idRow)
    );
    LA_SELECTED_ROWS_OUTPUT.value = [];
    SELECT_OUTPUT_ALL.value = false;
  }
}

/**
 * Updates a specific row with new field values.
 * 
 * @param {number} index - The index of the row to update.
 * @param {object} idField - The new field data.
 * @param {string} iRowName - The name of the row group ('inputRow' or 'outputRow').
 */
function fnUpdateRow(index, idField, iRowName) {
  if (iRowName == 'inputRow'){
    inputRows.value[index].field_name = idField.label
    inputRows.value[index].field_type = idField.fieldtype
  } else {
    outputRows.value[index].field_name = idField.label
    outputRows.value[index].field_type = idField.fieldtype
  }
}

function fnUpdateChildTable(iTableName, idRows) {
  createResource({
    url: "crm.api.docCpq.fn_update_child_table_row",
    params: { "doctype": "Condition Type","docname": props.conditionId, "child_field": iTableName, "values": idRows },
    auto: true,
    onSuccess: (response) => {
      condition.reload()
      reload.value = true
      createToast({
        title: __(`${iTableName.toUpperCase()} updated`),
        icon: "check",
        iconClasses: "text-green-600",
      });
    },
    onError: (err) => {
      createToast({
        title: __("Error updating child table"),
        text: __(err.messages?.[0] || "An unexpected error occurred."),
        icon: "x",
        iconClasses: "text-red-600",
      });
    },
  });
}

const RESTRICTED_FIELD_TYPES = [
  'Table','Geolocation','Attach','Attach Image','HTML','Signature',
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
  auto: false,
})

</script>
