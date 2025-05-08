<template>
    <Dialog v-model="show" :options="{ size: '3xl' }">
      <template #body>
        <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
          <div class="mb-5 flex items-center justify-between">
            <div>
              <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
                {{ __('Create Condition Type') }}
              </h3>
            </div>
            <div class="flex items-center gap-1">
              <Button
                v-if="isManager() && !isMobileView"
                variant="ghost"
                class="w-7"
                @click="openQuickEntryModal"
              >
                <EditIcon class="h-4 w-4" />
              </Button>
              <Button variant="ghost" class="w-7" @click="show = false">
                <FeatherIcon name="x" class="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div>
            <FieldLayout v-if="tabs.data" :tabs="tabs.data" :data="condType" />
            <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
          </div>
        </div>
        <div class="px-4 pb-7 pt-4 sm:px-6">
          <div class="flex flex-row-reverse gap-2">
            <Button
              variant="solid"
              :label="__('Create')"
              :loading="isCondTypeCreating"
              @click="createNewCondType"
            />
          </div>
        </div>
      </template>
    </Dialog>
  </template>
  
  <script setup>
  import EditIcon from '@/components/Icons/EditIcon.vue'
  import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
  import { usersStore } from '@/stores/users'
  import { isMobileView } from '@/composables/settings'
  import { capture } from '@/telemetry'
  import { createResource } from 'frappe-ui'
  import { useOnboarding } from 'frappe-ui/frappe'
  import { ref, reactive, nextTick, watch, computed } from 'vue'
  import { useRouter } from 'vue-router'
  
  const props = defineProps({
    defaults: Object,
  })
  
  const { isManager } = usersStore()
  const { updateOnboardingStep } = useOnboarding('frappecrm')
  const router = useRouter()
  
  const show = defineModel()
  const error = ref(null)
  const isCondTypeCreating = ref(false)
  
  const tabs = createResource({
    url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
    cache: ['QuickEntry', 'ConditionType'],
    params: { doctype: 'Condition Type', type: 'Quick Entry' },
    auto: true,
    transform: (_tabs) => {
      return _tabs.forEach((tab) => {
        tab.sections.forEach((section) => {
          section.columns.forEach((column) => {
            column.fields.forEach((field) => {
              if (field.fieldtype === 'Table') {
                field.hidden = 0
                field.depends_on = null
                field.mandatory_depends_on = null
                condType[field.fieldname] = []
              }
            })
          })
        })
      })
    },
  })
  
  const condType = reactive({
    document_reference: '',
    condition_type: '',
    enable: 1,
    is_formula_based: 0,
    is_api_based: 0,
    is_value_based: 0,
    input_sequence: [],
    output_sequence: []
  })
  
  const createCondType = createResource({
    url: 'frappe.client.insert',
    makeParams(values) {
      return {
        doc: {
          doctype: 'Condition Type',
          ...values,
        },
      }
    },
  })
  
  
  function createNewCondType() {
  
    createCondType.submit(condType, {
      validate() {
        error.value = null
        isCondTypeCreating.value = true
      },
      onSuccess(data) {
        capture('condition_type_created')
        isCondTypeCreating.value = false
        show.value = false
        router.push({ name: 'Condition Type', params: { condTypeId: data.name } })
        updateOnboardingStep('create_first_condition_type', true, false, () => {
          localStorage.setItem('firstConditionType', data.name)
        })
      },
      onError(err) {
        isCondTypeCreating.value = false
        if (!err.messages) {
          error.value = err.message
          return
        }
        error.value = err.messages.join('\n')
      },
    })
  }
  
  const showQuickEntryModal = defineModel('quickEntry')
  
  function openQuickEntryModal() {
    showQuickEntryModal.value = true
    nextTick(() => {
      show.value = false
    })
  }

  //custom logic
  const LaRestrictedFieldType = [
  'Table', 'Geolocation', 'Attach', 'Attach Image', 'HTML', 'Signature',
]
  const params = computed(() => {
  return {
    doctype: condType.document_reference,
    restricted_fieldtypes: LaRestrictedFieldType,
    as_array: true,
  }
})

const fnFields = createResource({
  url: 'crm.api.doc.get_fields_meta',
  params: params.value,
  auto: condType.document_reference == '' ? false : true,
  transform:(data) => {
    return data.map(field => ({
      label: field.label,
      value: field.fieldname
    }));
  }
})
  
  watch(() => condType.document_reference, (newValue) => {
    if (newValue) {
      fnFields.fetch(params.value).then(() => {
      console.log("new value of modal", fnFields);
    });
    }
  })

  </script>
  