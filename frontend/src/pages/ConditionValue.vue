<template>
    <LayoutHeader v-if="value.data">
      <template #left-header>
        <Breadcrumbs :items="BREADCRUMBS">
          <template #prefix="{ item }">
            <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
          </template>
        </Breadcrumbs>
      </template>
    </LayoutHeader>
    <div v-if="value?.data" class="flex h-full overflow-hidden">
      <Tabs v-model="tabIndex" v-slot="{ tab }" :tabs="TABS">
        
      </Tabs>
      <Resizer class="flex flex-col justify-between border-l" side="right">
        <div
          class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium"
          @click="copyToClipboard(value.data.name)"
        >
          {{ __(value.data.name) }}
        </div>
        <div class="flex flex-1 flex-col justify-between overflow-hidden">
          <div class="flex flex-col overflow-y-auto">
            <div class="flex flex-col p-3">
              <Section is-opened="Opened" label="Input Value">
                <div class="flex flex-col gap-1.5 overflow-y-auto">
                <div v-for="(field, index) in LA_INPUT_VALUES" :key="Object.keys(field)[0]" class="section-field flex items-center gap-2 px-3 leading-5 first:mt-3">
                    <Tooltip :text="__(Object.keys(field)[0])" :hoverDelay="1">
                        <div class="sm:w-[106px] w-36 shrink-0 truncate text-sm text-gray-600">
                            <span>{{ __(Object.keys(field)[0]) }}</span>
                        </div>
                    </Tooltip>
                    <div class="grid min-h-[28px] flex-1 items-center overflow-hidden text-base">
                        <FormControl
                            type="text"
                            placeholder="Enter the Value"
                            v-model="LA_INPUT_VALUES[index][Object.keys(field)[0]]"
                            @change.stop="fnUpdateField(Object.keys(field)[0], $event.target.value, 'input_value')"
                        />
                    </div>
                </div>
            </div>
              </Section>
              <Section is-opened="Opened" label="Output Value">
                <div class="flex flex-col gap-1.5 overflow-y-auto">
                <div v-for="(field, index) in LA_OUTPUT_VALUES" :key="Object.keys(field)[0]" class="section-field flex items-center gap-2 px-3 leading-5 first:mt-3">
                    <Tooltip :text="__(Object.keys(field)[0])" :hoverDelay="1">
                        <div class="sm:w-[106px] w-36 shrink-0 truncate text-sm text-gray-600">
                            <span>{{ __(Object.keys(field)[0]) }}</span>
                        </div>
                    </Tooltip>
                    <div class="grid min-h-[28px] flex-1 items-center overflow-hidden text-base">
                        <FormControl
                            type="text"
                            placeholder="Enter the Value"
                            v-model="LA_OUTPUT_VALUES[index][Object.keys(field)[0]]"
                            @change.stop="fnUpdateField(Object.keys(field)[0], $event.target.value, 'output_value')"
                        />
                    </div>
                </div>
            </div>
              </Section>
            </div>
          </div>
        </div>
      </Resizer>
    </div>
    <AssignmentModal
      v-if="showAssignmentModal"
      v-model="showAssignmentModal"
      v-model:assignees="value.data._assignedTo"
      :doc="value.data"
      doctype="Condition Value"
    />
  </template>
  <script setup>
  import Icon from '@/components/Icon.vue'
  import Resizer from '@/components/Resizer.vue'
  import CommentIcon from '@/components/Icons/CommentIcon.vue'
  import NoteIcon from '@/components/Icons/NoteIcon.vue'
  import LayoutHeader from '@/components/LayoutHeader.vue'
  import AssignmentModal from '@/components/Modals/AssignmentModal.vue'
  import Section from '@/components/Section.vue'
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
    Tooltip,
    Tabs,
    Breadcrumbs,
    call,
    usePageMeta,
  } from 'frappe-ui'
  import { ref, computed, onMounted, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useActiveTabManager } from '@/composables/useActiveTabManager'
  
  const { $dialog, $socket } = globalStore()
  const route = useRoute()
  const router = useRouter()
  
  const props = defineProps({
    conditionValueId: {
      type: String,
      required: true,
    },
  })
  
  const customActions = ref([])
  const customStatuses = ref([])
  const CONDITION_TYPE_VALUE = ref('')
  const ACCESS_KEY = ref('')
  const LA_INPUT_VALUES = ref([])
  const LA_OUTPUT_VALUES = ref([])
  const LA_INPUT_SEQUENCE = ref([])
  const LA_OUTPUT_SEQUENCE = ref([])

  const value = createResource({
    url: 'crm.cpq.doctype.condition_value.api.get_condition_value',
    params: { name: props.conditionValueId },
    onSuccess: async (data) => {
      CONDITION_TYPE_VALUE.value = data.condition_type
      ACCESS_KEY.value = data.access_key
      let obj = {
        doc: data,
        $dialog,
        $socket,
        router,
        fnUpdateField,
        createToast,
        deleteDoc: deleteValue,
        resource: {value, conditionType},
        call,
      }
      setupAssignees(data)
      let customization = await setupCustomizations(data, obj)
      customActions.value = customization.actions || []
      customStatuses.value = customization.statuses || []
      await conditionType.fetch({'doctype': 'Condition Type','name': CONDITION_TYPE_VALUE.value}, {
        onSuccess(conditionData){
            const { input_sequence, output_sequence } = conditionData
        
            let lInputIndex = 0
            let lOutputIndex = 0
            
            LA_INPUT_VALUES.value = []
            LA_OUTPUT_VALUES.value = []

            LA_INPUT_SEQUENCE.value = input_sequence
            LA_OUTPUT_SEQUENCE.value = output_sequence

            input_sequence.forEach(ldField => {
            const { field_name, length } = ldField
            const lValue = data.input_value.substring(lInputIndex, lInputIndex + length).trim()
            LA_INPUT_VALUES.value.push({ [field_name]: lValue }) 
            lInputIndex += length
            })

            // Extract Output Values
            output_sequence.forEach(ldField => {
            const { field_name, length } = ldField
            const lValue = data.output_value.substring(lOutputIndex, lOutputIndex + length).trim()
            LA_OUTPUT_VALUES.value.push({ [field_name]: lValue }) 
            lOutputIndex += length
            })

            const CON_TYPE_ACCESS_KEY = LA_INPUT_SEQUENCE.value.map(seq => seq.field_name).join('/');
              if(CON_TYPE_ACCESS_KEY != ACCESS_KEY.value){
                fnUpdateValue('access_key', CON_TYPE_ACCESS_KEY)
                ACCESS_KEY.value = CON_TYPE_ACCESS_KEY;
              }
        }
      })
    },
  })
  
  onMounted(() => {
    if (value.data) return
    value.fetch()
  })

const showAssignmentModal = ref(false)

/**
 * Formats a field value based on its type and length.
 * Trims the value if it exceeds the specified length.
 * Pads it with spaces based on the field type.
 */
function fnFormatFieldValue(iFieldValue, iFieldLength, iFieldType) {
  if (!iFieldValue) iFieldValue = '';
    let lValue = iFieldValue.toString();
    if (lValue.length > iFieldLength) {
      lValue = lValue.substring(0, iFieldLength);
    }
    if (iFieldType === 'Int' || iFieldType === 'Float' || iFieldType === 'Currency') {
      return lValue.padStart(iFieldLength, ' ');
    } else {
      return lValue.padEnd(iFieldLength, ' ');
    }
  }

  /**
 * Processes a sequence of fields and formats
 *  them into a concatenated string.
 */
function fnProcessSequence(iaSequence, iaValues) {
  let lFormattedValue = '';

  iaSequence.forEach(idRow => {
    const FIELD_NAME = idRow.field_name;
    const LD_FIELD_VALUES = iaValues.find(seq => Object.keys(seq)[0] === FIELD_NAME) || {};
    const FIELD_VALUE = LD_FIELD_VALUES[FIELD_NAME] || '';

    lFormattedValue += fnFormatFieldValue(FIELD_VALUE, idRow.length, idRow.field_type);
  });

  return lFormattedValue;
}

/**
 * Updates a specific field's value in the input or output sequence.
 * If the target is 'input_value', it updates the formatted input value.
 * If the target is an output field, it processes and updates the output sequence.
 */
async function fnUpdateField(iFieldname, value, iTarget) {
  if (iTarget === 'input_value') {
    const LA_FIELD_ORDER = ACCESS_KEY.value.split('/');
    let lFormattedValue = '';
    
    LA_FIELD_ORDER.forEach(iFieldName => {
      const LA_INPUT_ROW = LA_INPUT_SEQUENCE.value.find(seq => seq.field_name === iFieldName);
      if (LA_INPUT_ROW) {
        const LA_FIELD_VALUES = LA_INPUT_VALUES.value.find(seq => Object.keys(seq)[0] === iFieldName) || {};
        const FIELD_VALUE = LA_FIELD_VALUES[iFieldName] || '';
        const FORMATED_VALUE = fnFormatFieldValue(FIELD_VALUE, LA_INPUT_ROW.length, LA_INPUT_ROW.field_type);
        lFormattedValue += FORMATED_VALUE;
        if(iFieldName == iFieldname){
          const LD_CURRENT_VALUE = LA_INPUT_VALUES.value.find(item => item.hasOwnProperty(iFieldName));
          if (LD_CURRENT_VALUE) {
            LD_CURRENT_VALUE[iFieldname] = FORMATED_VALUE;
          }
        }
      } else {
        console.log(`Field ${iFieldName} not found in inputSequence`);
      }
    });

    await fnUpdateValue(iTarget, lFormattedValue)
  } else {
    const FORMATED_VALUE = fnProcessSequence(LA_OUTPUT_SEQUENCE.value, LA_OUTPUT_VALUES.value);
    await fnUpdateValue(iTarget, FORMATED_VALUE);
  }
}

/**
 * Sends an API request to update a field value in the Frappe backend.
 * Displays a success or error toast based on the API response.
 */
function fnUpdateValue(fieldname, value) {
  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'Condition Value',
      name: props.conditionValueId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
        createToast({
          title: __('value updated'),
          icon: 'check',
          iconClasses: 'text-green-600',
        })
    },
    onError: (err) => {
        createToast({
          title: __('Error updating value'),
          text: __(err.messages?.[0]),
          icon: 'x',
          iconClasses: 'text-red-600',
        })
    },
  })
}

  const BREADCRUMBS = computed(() => {
    let laItems = [{ label: __('Condition Values'), route: { name: 'Condition Values' } }]
  
    if (route.query.view || route.query.viewType) {
      let ldView = getView(route.query.view, route.query.viewType, 'Condition Value')
      if (ldView) {
        laItems.push({
          label: __(ldView.label),
          icon: ldView.icon,
          route: {
            name: 'Condition Values',
            params: { viewType: route.query.viewType },
            query: { view: route.query.view },
          },
        })
      }
    }
  
    laItems.push({
      label: value.data.name || __('Untitled'),
      route: { name: 'Condition Value', params: { conditionValueId: value.data.name } },
    })
    return laItems
  })
  
  usePageMeta(() => {
    return {
      title: value.data?.name || value.data?.name,
    }
  })
  
  const TABS = computed(() => {
    let ldTabOptions = [
    
      {
        name: 'Comments',
        label: __('Comments'),
        icon: CommentIcon,
      },
      {
        name: 'Notes',
        label: __('Notes'),
        icon: NoteIcon,
      },
    ]
    return ldTabOptions.filter((ldTab) => (ldTab.condition ? ldTab.condition() : true))
  })
  
  const { tabIndex } = useActiveTabManager(TABS, 'lastValueTab')
  
  watch(TABS, (value) => {
    if (value && route.params.tabName) {
      let index = value.findIndex(
        (tab) => tab.name.toLowerCase() === route.params.tabName.toLowerCase(),
      )
      if (index !== -1) {
        tabIndex.value = index
      }
    }
  })
  
  async function deleteValue(name) {
    await call('frappe.client.delete', {
      doctype: 'Condition Value',
      name,
    })
    router.push({ name: 'Condition Values' })
  }
  
  const conditionType = createResource({
    url:'frappe.client.get',
    auto: false
  })
  </script>