<template>
    <LayoutHeader v-if="item.data">
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs">
          <template #prefix="{ item }">
            <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
          </template>
        </Breadcrumbs>
      </template>
      <template #right-header>
        <CustomActions
          v-if="item.data._customActions?.length"
          :actions="item.data._customActions"
        />
        <AssignTo
          v-model="item.data._assignedTo"
          :data="item.data"
          doctype="Item"
        />
      </template>
    </LayoutHeader>
    <div v-if="item?.data" class="flex h-full overflow-hidden">
      <Tabs as="div" v-model="tabIndex" :tabs="tabs">
        <template #tab-panel>
          <Activities
            ref="activities"
            doctype="Item"
            :tabs="tabs"
            v-model:reload="reload"
            v-model:tabIndex="tabIndex"
            v-model="item"
          />
        </template>
      </Tabs>
      <Resizer class="flex flex-col justify-between border-l" side="right">
        <div
          class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
          @click="copyToClipboard(item.data.name)"
        >
          {{ __(item.data.name) }}
        </div>
        <div
          v-if="sections.data"
          class="flex flex-1 flex-col justify-between overflow-hidden"
        >
        <SidePanelLayout
          :sections="sections.data"
          doctype="Item"
          :docname="item.data.name"
          @reload="sections.reload"
        />
        </div>
      </Resizer>
    </div>
    <ErrorPage
    v-else-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />
    <QuickEntryModal
    v-if="showQuickEntryModal"
    v-model="showQuickEntryModal"
    doctype="Item"
    :onlyRequired="true"
  />
  <FilesUploader
    v-if="item.data?.name"
    v-model="showFilesUploader"
    doctype="Item"
    :docname="item.data.name"
    @after="
      () => {
        activities?.all_activities?.reload()
        changeTabTo('attachments')
      }
    "
  />
  </template>
  <script setup>
  import ErrorPage from '@/components/ErrorPage.vue'
  import Icon from '@/components/Icon.vue'
  import Resizer from '@/components/Resizer.vue'
  import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
  import EmailIcon from '@/components/Icons/EmailIcon.vue'
  import CommentIcon from '@/components/Icons/CommentIcon.vue'
  import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
  import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
  import TaskIcon from '@/components/Icons/TaskIcon.vue'
  import NoteIcon from '@/components/Icons/NoteIcon.vue'
  import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
  import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
  import LayoutHeader from '@/components/LayoutHeader.vue'
  import Activities from '@/components/Activities/Activities.vue'
  import AssignTo from '@/components/AssignTo.vue'
  import FilesUploader from '@/components/FilesUploader/FilesUploader.vue'
  import SidePanelLayout from '@/components/SidePanelLayout.vue'
  import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
  import CustomActions from '@/components/CustomActions.vue'
  import {
    setupAssignees,
    setupCustomizations,
    copyToClipboard,
  } from '@/utils'
  import { getView } from '@/utils/view'
  import { getSettings } from '@/stores/settings'
  import { usersStore } from '@/stores/users'
  import { globalStore } from '@/stores/global'
  import { statusesStore } from '@/stores/statuses'
  import { getMeta } from '@/stores/meta'
  import {
    whatsappEnabled,
    callEnabled,
  } from '@/composables/settings'
  import { capture } from '@/telemetry'
  import {
    createResource,
    Tabs,
    Breadcrumbs,
    call,
    usePageMeta,
    toast
  } from 'frappe-ui'
  import { useOnboarding } from 'frappe-ui/frappe'
  import { ref, reactive, computed, onMounted, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useActiveTabManager } from '@/composables/useActiveTabManager'
  
  const { brand } = getSettings()
  const { $dialog, $socket } = globalStore()
  const { doctypeMeta } = getMeta('Item')
  
  const { updateOnboardingStep } = useOnboarding('frappecrm')
  
  const route = useRoute()
  const router = useRouter()
  
  const props = defineProps({
    itemId: {
      type: String,
      required: true,
    },
  })

  const errorTitle = ref('')
const errorMessage = ref('')
  
  const item = createResource({
    url: 'crm.apiCpq.design.get_doc_details',
    params: {doctype: "Item", name: props.itemId },
    cache: ['item', props.itemId],
    onSuccess: (data) => {
      errorTitle.value = ''
    errorMessage.value = ''
      setupAssignees(item)
      setupCustomizations(item, {
        doc: data,
        $dialog,
        $socket,
        router,
        toast,
        updateField,
        createToast: toast.create,
        deleteDoc: deleteItem,
        resource: { item, sections },
        call,
      })
    },
    onError: (err) => {
    if (err.messages?.[0]) {
      errorTitle.value = __('Not permitted')
      errorMessage.value = __(err.messages?.[0])
    } else {
      router.push({ name: 'Items' })
    }
  },
  })
  
  onMounted(() => {
    if (item.data) return
    item.fetch()
  })
  
  const reload = ref(false)
  const showFilesUploader = ref(false)
  
  function updateItem(fieldname, value, callback) {
    value = Array.isArray(fieldname) ? '' : value
  
    if (!Array.isArray(fieldname) && validateRequired(fieldname, value)) return
  
    createResource({
      url: 'frappe.client.set_value',
      params: {
        doctype: 'Item',
        name: props.itemId,
        fieldname,
        value,
      },
      auto: true,
      onSuccess: () => {
        item.reload()
        sections.reload()
        reload.value = true
        toast.success(__('Item updated'))
        callback?.()
      },
      onError: (err) => {
        toast.error(__('Error updating item'))
      },
    })
  }
  
  function validateRequired(fieldname, value) {
    let meta = item.data.fields_meta || {}
    if (meta[fieldname]?.reqd && !value) {
      toast.error(__('{0} is a required field', [meta[fieldname].label]))
      return true
    }
    return false
  }
  
  const breadcrumbs = computed(() => {
    let items = [{ label: __('Items'), route: { name: 'Items' } }]
  
    if (route.query.view || route.query.viewType) {
      let view = getView(route.query.view, route.query.viewType, 'Item')
      if (view) {
        items.push({
          label: __(view.label),
          icon: view.icon,
          route: {
            name: 'Items',
            params: { viewType: route.query.viewType },
            query: { view: route.query.view },
          },
        })
      }
    }
  
    items.push({
      label: title.value,
      route: { name: 'Item', params: { itemId: item.data.name } },
    })
    return items
  })
  
  const title = computed(() => {
    let t = doctypeMeta['Item']?.title_field || 'name'
    return item.data?.[t] || props.itemId
  })
  
  usePageMeta(() => {
    return {
      title: title.value,
      icon: brand.favicon,
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
        name: 'Data',
        label: __('Data'),
        icon: DetailsIcon,
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
        name: 'Attachments',
        label: __('Attachments'),
        icon: AttachmentIcon,
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
  
  const { tabIndex, changeTabTo } = useActiveTabManager(tabs, 'lastItemTab')
  
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
  
  const sections = createResource({
    url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
    cache: ['sidePanelSections', 'Item'],
    params: { doctype: 'Item' },
    auto: true,
  })
  
  function updateField(name, value, callback) {
    updateItem(name, value, () => {
      item.data[name] = value
      callback?.()
    })
  }
  
  async function deleteItem(name) {
    await call('frappe.client.delete', {
      doctype: 'Item',
      name,
    })
    router.push({ name: 'Items' })
  }

  const activities = ref(null) 
  const showQuickEntryModal = ref(false)

//   watch(
//   () => sections.data,
//   (val) => {
//     if (val && item.data?.variant_of) {
//       val.forEach(section => {
//         section.columns?.forEach(column => {
//           column.fields?.forEach(field => {
//             field.read_only = 1;
//           });
//         });
//       });
//     }
//   },
//   { immediate: true }
// );
  
function makeFieldsReadOnly(val) {
  if (val && item.data?.variant_of) {
    val.forEach(section => {
      section.columns?.forEach(column => {
        column.fields?.forEach(field => {
          field.read_only = 1
        })
      })
    })
  }
}

onMounted(() => {
  if (sections.data) {
    makeFieldsReadOnly(sections.data)
  }
})

watch(() => sections.data, (val) => {
  makeFieldsReadOnly(val)
})
  </script>
  