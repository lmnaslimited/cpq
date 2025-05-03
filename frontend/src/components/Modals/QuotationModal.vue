<template>
    <Dialog v-model="show" :options="{ size: '3xl' }">
      <template #body>
        <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
          <div class="mb-5 flex items-center justify-between">
            <div>
              <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
                {{ __('Create Quotation') }}
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
            <FieldLayout v-if="tabs.data" :tabs="tabs.data" :data="quotation" />
            <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
          </div>
        </div>
        <div class="px-4 pb-7 pt-4 sm:px-6">
          <div class="flex flex-row-reverse gap-2">
            <Button
              variant="solid"
              :label="__('Create')"
              :loading="isQuotationCreating"
              @click="createNewQuotation"
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
  import { ref, reactive, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  
  const props = defineProps({
    defaults: Object,
  })
  
  const { isManager } = usersStore()
  const { updateOnboardingStep } = useOnboarding('frappecrm')
  const router = useRouter()
  
  const show = defineModel()
  const error = ref(null)
  const isQuotationCreating = ref(false)
  
  const tabs = createResource({
    url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
    cache: ['QuickEntry', 'Quotation'],
    params: { doctype: 'Quotation', type: 'Quick Entry' },
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
                quotation[field.fieldname] = []
              }
              if (field.fieldname === 'party_name') {
                field.label = 'Customer';
                field.fieldtype = 'Link';
                field.options = 'Customer';
                field.mandatory = 1;
                }
            })
          })
        })
      })
    },
  })
  
  const quotation = reactive({
    quotation_to: 'Customer',
    party_name: '',
    transaction_date: '',
    valid_till: '',
    status: 'Draft',
    currency: '',
    selling_price_list: 'Standard Selling',
    items: []
  })
  
  const createQuotation = createResource({
    url: 'frappe.client.insert',
    makeParams(values) {
      return {
        doc: {
          doctype: 'Quotation',
          ...values,
        },
      }
    },
  })
  
  
  function createNewQuotation() {
  
    createQuotation.submit(quotation, {
      validate() {
        error.value = null
        isQuotationCreating.value = true
      },
      onSuccess(data) {
        capture('quotation_created')
        isQuotationCreating.value = false
        show.value = false
        router.push({ name: 'Quotation', params: { quotationId: data.name } })
        updateOnboardingStep('create_first_quotation', true, false, () => {
          localStorage.setItem('firstQuotation', data.name)
        })
      },
      onError(err) {
        isQuotationCreating.value = false
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
  
  </script>
  