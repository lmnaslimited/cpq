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
                field.label = quotation['quotation_to'];
                field.fieldtype = 'Link';
                field.options = quotation['quotation_to'];
                field.mandatory = 1;
                quotation[field.fieldname] = ''
                }
            })
          })
        })
      })
    },
  })
  
  const quotation = reactive({
    quotation_to: 'CRM Deal',
    party_name: '',
    transaction_date: '',
    status: 'Draft',
    currency: 'INR',
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
  
  //custom implementation begins

  //to refetch the tab if the quotation_to(which is Link to Doctype)
  //change, so the party_name whicg is Dynamic Link field depends on quotation_to
  watch(
    () => quotation.quotation_to,
  () => {
    tabs.fetch()
      },
  )
  
  //get the item price list for the
  //params passed
  const itemPriceList = createResource({
    url: 'frappe.client.get_list',
    auto: false
  });

  //this watch the items table and selling_price_list field changes
  watch(
  () => [quotation.items, quotation.selling_price_list],
  ([newItems, newPriceList], [oldItems, oldPriceList]) => {
    //loop through each rows in the items table
    newItems.forEach( (value, index) => {
      //flag to check if the rate should be fetched again
      //to avoid unwanted fetching of resource (performance)
      const shouldRefetch =
        !value.rate || newPriceList !== oldPriceList;
        console.log("should change", shouldRefetch)
      //if flag is true and item_code is present
      //fetch the itemPriceList 
      if (shouldRefetch && value.item_code){
        //construction of param required
        //to get the pricelist's rate for 
        //selected selling_price_list and item_code
        quotation.items[index].item_name = value.item_code
        const params = {
            doctype: "Item Price",
            fields: ['price_list_rate'],
            filters: {
              item_code: value.item_code,
              price_list: quotation.selling_price_list
            }
        }
        itemPriceList.fetch(params).then((res)=>{
          if (res && res.length > 0) {
            // Ensure we're getting the correct price
            //since it return as array
            const price = res[0].price_list_rate;
            // Update the rate in the quotation item
            quotation.items[index].rate = price;
          }
        }).catch(err => {
          console.log('Error fetching price:', err);
        });
      }
      if(value.rate && value.qty){
        quotation.items[index].amount = value.rate * value.qty
      }
    })
  },
  { deep: true }
);
  </script>
  