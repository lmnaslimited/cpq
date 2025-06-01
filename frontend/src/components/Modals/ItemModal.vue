<template>
    <Dialog v-model="show" :options="{ size: '3xl' }">
      <template #body>
        <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
          <div class="mb-5 flex items-center justify-between">
            <div>
              <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
                {{ __('Create Item Template') }}
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
            <FieldLayout v-if="tabs.data" :tabs="tabs.data" :data="item" />
            <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
          </div>
        </div>
        <div class="px-4 pb-7 pt-4 sm:px-6">
          <div class="flex flex-row-reverse gap-2">
            <Button
              variant="solid"
              :label="__('Create')"
              :loading="isItemCreating"
              @click="createNewItem"
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
  import { ref, reactive, nextTick, watch } from 'vue'
  import { useRouter } from 'vue-router'
  
  const props = defineProps({
    defaults: Object,
  })
  
  const { isManager } = usersStore()
  const { updateOnboardingStep } = useOnboarding('frappecrm')
  const router = useRouter()
  
  const show = defineModel()
  const error = ref(null)
  const isItemCreating = ref(false)
  
  const tabs = createResource({
    url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
    cache: ['QuickEntry', 'Item'],
    params: { doctype: 'Item', type: 'Quick Entry' },
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
                item[field.fieldname] = []
              }
            })
          })
        })
      })
    },
  })
  
  const item = reactive({
    item_code: '',
    item_name: '',
    item_group: '',
    stock_uom: '',
    attributes: [],
  })
  
  //custom function
  const getAttributes = createResource({
  url: 'frappe.client.get_list',
  makeParams(attributeNames) {
    return {
      doctype: 'Item Attribute',
      fields: ['*'],
      filters: [['name', 'in', attributeNames]],
      limit_page_length: attributeNames.length,
    }
  },
})

  const createItem = createResource({
    url: 'frappe.client.insert',
    makeParams(values) {
      return {
        doc: {
          doctype: 'Item',
          has_variants: 1,
          ...values,
        },
      }
    },
  })
  
  
  async function createNewItem() {
    const attributeNames = item.attributes.map(a => a.attribute)

    const attributeDetails = await getAttributes.fetch(attributeNames)

    // Create a lookup map for quick access
    const attributeMap = Object.fromEntries(
      attributeDetails.map(attr => [attr.name, attr])
    )

    // Merge additional fields into item.attributes
    item.attributes = item.attributes.map(attr => ({
      ...attr,
      numeric_values: attributeMap[attr.attribute]?.numeric_values || 0,
      from_range: attributeMap[attr.attribute]?.from_range || null,
      to_range: attributeMap[attr.attribute]?.to_range || null,
      increment: attributeMap[attr.attribute]?.increment || null,
    }))
    createItem.submit(item, {
      validate() {
        error.value = null
        if (!item.item_code) {
        error.value = __('Item Code is mandatory')
        return error.value
      }
      if (!item.item_group) {
        error.value = __('Item Group is mandatory')
        return error.value
      }
        isItemCreating.value = true
      },
      onSuccess(data) {
        capture('item_created')
        isItemCreating.value = false
        show.value = false
        router.push({ name: 'Item', params: { itemId: data.name } })
        updateOnboardingStep('create_first_item', true, false, () => {
          localStorage.setItem('firstItem', data.name)
        })
      },
      onError(err) {
        isItemCreating.value = false
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

  watch(
    () => item.item_code, 
    (newValue) => {
      console.log("item code change", newValue)
      item.item_name = newValue
    }
  )
  
  </script>
  