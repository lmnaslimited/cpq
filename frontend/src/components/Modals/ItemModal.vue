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
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  defaults: Object,
})

const { isManager } = usersStore()

const show = defineModel()
const router = useRouter()
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
})

const createItem = createResource({
  url: 'frappe.client.insert',
  makeParams(values) {
    return {
      doc: {
        doctype: 'Item',
        ...values,
      },
    }
  },
})


function createNewItem() {
  
  createItem.submit(item, {
    validate() {
      error.value = null
      if (!LD_ITEM.item_code) {
        error.value = __('Item Code is mandatory')

        return error.value
      }
      if (!LD_ITEM.item_group) {
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


</script>
