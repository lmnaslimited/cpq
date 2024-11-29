<template>
  <LayoutHeader v-if="quotation.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <CustomActions v-if="customActions" :actions="customActions" />
      <component :is="quotation.data._assignedTo?.length == 1 ? 'Button' : 'div'">
        <MultipleAvatar
          :avatars="quotation.data._assignedTo"
          @click="showAssignmentModal = true"
        />
      </component>
    </template>
  </LayoutHeader>
  <div v-if="quotation?.data" class="flex h-full w-full overflow-hidden">
    <div class="flex flex-col h-full w-[80%] overflow-y-auto">
    <div class="h-[50%]">
      <Tabs v-model="tabIndex" v-slot="{ tab }" :tabs="tabs">
      <FadedScrollableDiv
          class="flex flex-col gap-1.5 overflow-y-auto"
          :class="[isLastSection ? '' : 'max-h-[350px]']"
          >
      <Activities
        ref="activities"
        doctype="Quotation"
        :tabs="tabs"
        v-model:reload="reload"
        v-model:tabIndex="tabIndex"
        v-model="quotation"
      />
      </FadedScrollableDiv>
    </Tabs>
    </div>
    <div class="border-t pt-4 mt-4">
    <div class="w-[70%] p-4">
    <Table
      :rows="rows"
      :columns="columns"
      :filteredColumns="filteredColumns"
      label="Quotation Items"
      @item-changed="handleItemCodeChange"
      @update-rows="updateQuotationItem"
      :isTabRequired="true"
      @open-tab="openVariantTab"
    />
    </div>
    </div>
    </div>
    <div class="flex flex-col border border-l h-full w-[20%] overflow-y-auto">
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
            v-model="quotation.data"
            @update="updateField"
          />
        </Section>
      </div>
    </div>
  </div>
  <AssignmentModal
    v-if="showAssignmentModal"
    v-model="showAssignmentModal"
    v-model:assignees="quotation.data._assignedTo"
    :doc="quotation.data"
    doctype="Quotation"
  />
  
</template>
<script setup>
import FadedScrollableDiv from '@/components/FadedScrollableDiv.vue'
import Icon from '@/components/Icon.vue'
import Resizer from '@/components/Resizer.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import LinkIcon from '@/components/Icons/LinkIcon.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Activities from '@/components/Activities/Activities.vue'
import AssignmentModal from '@/components/Modals/AssignmentModal.vue'
import SidePanelModal from '@/components/Settings/SidePanelModal.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import Section from '@/components/Section.vue'
import SectionFields from '@/components/SectionFields.vue'
import SLASection from '@/components/SLASection.vue'
import CustomActions from '@/components/CustomActions.vue'
import Table from '@/components/CustomComponent/Table.vue'
import {
  openWebsite,
  createToast,
  setupAssignees,
  setupCustomizations,
  errorMessage,
  copyToClipboard,
} from '@/utils'
import { getView } from '@/utils/view'
import { globalStore } from '@/stores/global'
import { contactsStore } from '@/stores/contacts'
import { statusesStore } from '@/stores/statuses'
import { usersStore } from '@/stores/users'
import { whatsappEnabled, callEnabled } from '@/composables/settings'
import { capture } from '@/telemetry'
import {
  createResource,
  FileUploader,
  Dropdown,
  Tooltip,
  Avatar,
  Tabs,
  Switch,
  Breadcrumbs,
  call,
  usePageMeta,
} from 'frappe-ui'
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useActiveTabManager } from '@/composables/useActiveTabManager'

const { $dialog, $socket, makeCall } = globalStore()
const { getContactByName, contacts } = contactsStore()
const { statusOptions, getQuotationStatus } = statusesStore()
const { isManager } = usersStore()
const route = useRoute()
const router = useRouter()

const props = defineProps({
  quotationId: {
    type: String,
    required: true,
  },
})

const customActions = ref([])
const customStatuses = ref([])

const quotation = createResource({
  url: 'crm.api.docCpq.get_quotation',
  params: { name: props.quotationId },
  cache: ['quotation', props.quotationId],
  onSuccess: async (data) => {
    let obj = {
      doc: data,
      $dialog,
      $socket,
      router,
      updateField,
      createToast,
      deleteDoc: deleteQuotation,
      resource: {
        quotation,
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
  if (quotation.data) return
  quotation.fetch()
})

const reload = ref(false)
const showAssignmentModal = ref(false)
const showSidePanelModal = ref(false)

function updateQuotation(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  if (!Array.isArray(fieldname) && validateRequired(fieldname, value)) return

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'Quotation',
      name: props.quotationId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      quotation.reload()
      reload.value = true
      createToast({
        title: __('Quotation updated'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      callback?.()
    },
    onError: (err) => {
      createToast({
        title: __('Error updating quotation'),
        text: __(err.messages?.[0]),
        icon: 'x',
        iconClasses: 'text-red-600',
      })
    },
  })
}

function updateQuotationItem(rows) {

  createResource({
    url: "crm.api.docCpq.update_child_table_row",
    params: { "quotation_name": props.quotationId, "child_field": "items", "values": rows },
    auto: true,
    onSuccess: (response) => {
      quotation.reload()
      reload.value = true
      createToast({
        title: __("Quotation updated"),
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

function validateRequired(fieldname, value) {
  let meta = quotation.data.fields_meta || {}
  if (meta[fieldname]?.reqd && !value) {
    createToast({
      title: __('Error Updating Quotation'),
      text: __('{0} is a required field', [meta[fieldname].label]),
      icon: 'x',
      iconClasses: 'text-red-600',
    })
    return true
  }
  return false
}

const breadcrumbs = computed(() => {
  let items = [{ label: __('Quotations'), route: { name: 'Quotations' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'Quotation')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Quotations',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: quotation.data.name || __('Untitled'),
    route: { name: 'Quotation', params: { quotationId: quotation.data.name } },
  })
  return items
})

usePageMeta(() => {
  return {
    title: quotation.data?.name || quotation.data?.name,
  }
})

const tabs = computed(() => {
  let tabOptions = [
    {
      name: 'Activity',
      label: __('Activity'),
      icon: ActivityIcon,
    },
    {
      name: 'Emails',
      label: __('Emails'),
      icon: EmailIcon,
    },
    {
      name: 'Comments',
      label: __('Comments'),
      icon: CommentIcon,
    },
    {
      name: 'Calls',
      label: __('Calls'),
      icon: PhoneIcon,
      condition: () => callEnabled.value,
    },
    {
      name: 'Tasks',
      label: __('Tasks'),
      icon: TaskIcon,
    },
    {
      name: 'Notes',
      label: __('Notes'),
      icon: NoteIcon,
    },
    {
      name: 'WhatsApp',
      label: __('WhatsApp'),
      icon: WhatsAppIcon,
      condition: () => whatsappEnabled.value,
    },
  ]
  return tabOptions.filter((tab) => (tab.condition ? tab.condition() : true))
})

const { tabIndex } = useActiveTabManager(tabs, 'lastQuotationTab')

watch(tabs, (value) => {
  if (value && route.params.tabName) {
    let index = value.findIndex(
      (tab) => tab.name.toLowerCase() === route.params.tabName.toLowerCase(),
    )
    if (index !== -1) {
      tabIndex.value = index
    }
  }
})

function validateFile(file) {
  let extn = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg', 'jpeg'].includes(extn)) {
    return __('Only PNG and JPG images are allowed')
  }
}

const fieldsLayout = createResource({
  url: 'crm.api.doc.get_sidebar_fields',
  cache: ['fieldsLayout', props.quotationId],
  params: { doctype: 'Quotation', name: props.quotationId },
  auto: true,
})

//function to get table fields rows and columns
const tableData = createResource({
  url: 'crm.api.docCpq.get_table_rows_columns',
  cache: ['tableData', props.quotationId],
  params: { doctype: 'Quotation', docname: props.quotationId },
  auto: true,
})

const filteredColumns = computed(() => {
  const itemsColumn = tableData.data.columns.find(col => col.fieldname === 'items');
  
  if (!itemsColumn) return [];
  
  return itemsColumn.fields
    .filter(field => ['item_code', 'qty', 'rate', 'amount'].includes(field.fieldname))
    .map(field => {
      if (field.fieldname === 'item_code') {
      
        return { ...field, link_filters: { "has_variants": 0 } };
      } else if (field.fieldname === 'qty') {
      
        return { ...field, default: 1 };
      } else {
        // For other fields, return them unchanged
        return field;
      }
    });
});


const columns = computed(() => {
  
  return tableData.data.columns.find(col => col.fieldname === 'items');
})

const rows = computed(() => {
  return (tableData.data.rows.items || []).sort((a, b) => a.idx - b.idx);
});

function updateField(name, value, callback) {
  updateQuotation(name, value, () => {
    quotation.data[name] = value
    callback?.()
  })
}

const fetchItemRate = (item, price_list, row) => {
    const data =  createResource({
      url: 'frappe.client.get_value',
      makeParams() {
        return {
          doctype: 'Item Price',
          fieldname: 'price_list_rate',
          filters: {
            price_list: price_list,
            item_code: item,
          },
        };
      },
      auto: true,
      onSuccess(data) {
       
        row.rate =  data.price_list_rate || 0;
        row.amount = row.qty * data.price_list_rate
      },
     onError(error) {
      console.error('Error fetching rate:', error.message);
    },
    });
};

const handleItemCodeChange = ({ value, fieldname, row }) => {
  if (fieldname === 'item_code') {
    const priceList = quotation.data.selling_price_list;
   
    const priceListRate = fetchItemRate(value, priceList, row);
    
  }
  else if(fieldname === 'qty'){
    
    const quantity = parseFloat(value);
    row.amount = row.rate * quantity;
  }
  else if(fieldname === 'rate'){
    const rate = parseFloat(value);
    row.amount = rate * row.qty;
  }
};

function openVariantTab(itemCode) {
    console.log(itemCode)
}

async function deleteQuotation(name) {
  await call('frappe.client.delete', {
    doctype: 'Quotation',
    name,
  })
  router.push({ name: 'Quotations' })
}

const activities = ref(null)

function openEmailBox() {
  activities.value.emailBox.show = true
}
</script>
