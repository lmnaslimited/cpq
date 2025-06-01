<template>
    <LayoutHeader v-if="quotation.data">
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs">
          <template #prefix="{ quotation }">
            <!-- <Icon v-if="quotation.icon" :icon="quotation.icon" class="mr-2 h-4" /> -->
          </template>
        </Breadcrumbs>
      </template>
      <template #right-header>
        <CustomActions
          v-if="quotation.data._customActions?.length"
          :actions="quotation.data._customActions"
        />
        <AssignTo
          v-model="quotation.data._assignedTo"
          :data="quotation.data"
          doctype="Quotation"
        />
      </template>
    </LayoutHeader>
    <div v-if="quotation?.data" class="flex h-full overflow-hidden">
      <Tabs as="div" v-model="tabIndex" :tabs="tabs">
        <template #tab-panel>
          <Activities
            ref="activities"
            doctype="Quotation"
            :tabs="tabs"
            v-model:reload="reload"
            v-model:tabIndex="tabIndex"
            v-model="quotation"
          />
        </template>
      </Tabs>
      <Resizer class="flex flex-col justify-between border-l" side="right">
        <div
          class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
          @click="copyToClipboard(quotation.data.name)"
        >
          {{ __(quotation.data.name) }}
        </div>
        <div
          v-if="sections.data"
          class="flex flex-1 flex-col justify-between overflow-hidden"
        >
        <SidePanelLayout
          :sections="sections.data"
          doctype="Quotation"
          :docname="quotation.data.name"
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
    doctype="Quotation"
    :onlyRequired="true"
  />
  <FilesUploader
    v-if="quotation.data?.name"
    v-model="showFilesUploader"
    doctype="Quotation"
    :docname="quotation.data.name"
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
  import { globalStore } from '@/stores/global'
  import { getMeta } from '@/stores/meta'
  import {
    whatsappEnabled,
    callEnabled,
  } from '@/composables/settings'
  import {
    createResource,
    Tabs,
    Breadcrumbs,
    call,
    usePageMeta,
    toast
  } from 'frappe-ui'
  import { ref, reactive, computed, onMounted, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useActiveTabManager } from '@/composables/useActiveTabManager'
  
  const { brand } = getSettings()
  const { $dialog, $socket } = globalStore()
  const { doctypeMeta } = getMeta('Quotation')
  
  const route = useRoute()
  const router = useRouter()
  
  const props = defineProps({
    quotationId: {
      type: String,
      required: true,
    },
  })
  
  const errorTitle = ref('')
const errorMessage = ref('')

  const quotation = createResource({
    url: 'crm.apiCpq.design.get_doc_details',
    params: {doctype: "Quotation", name: props.quotationId },
    cache: ['quotation', props.quotationId],
    onSuccess: (data) => {
       errorTitle.value = ''
    errorMessage.value = ''
      setupAssignees(quotation)
      setupCustomizations(quotation, {
        doc: data,
        $dialog,
        $socket,
        router,
        toast,
        updateField,
        createToast: toast.create,
        deleteDoc: deleteQuotation,
        resource: { quotation, sections },
        call,
      })
    },
    onError: (err) => {
    if (err.messages?.[0]) {
      errorTitle.value = __('Not permitted')
      errorMessage.value = __(err.messages?.[0])
    } else {
      router.push({ name: 'Quotations' })
    }
  },
  })
  
  onMounted(() => {
    if (quotation.data) return
    quotation.fetch()
  })
  
  const reload = ref(false)
  const showFilesUploader = ref(false)
  
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
        toast.success(__('Quotation updated'))
        callback?.()
      },
      onError: (err) => {
        toast.error(__('Error updating Quotation'))
      },
    })
  }
  
  function validateRequired(fieldname, value) {
    let meta = quotation.data.fields_meta || {}
    if (meta[fieldname]?.reqd && !value) {
      toast.error(__('{0} is a required field', [meta[fieldname].label]))
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
        label: title.value,
        route: { name: 'Quotation', params: { quotationId: quotation.data.name } },
    })
    return items
  })
  
  const title = computed(() => {
    let t = doctypeMeta['Quotation']?.title_field || 'name'
    return quotation.data?.[t] || props.quotationId
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
  
  const { tabIndex, changeTabTo } = useActiveTabManager(tabs, 'lastQuotationTab')
  
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
    cache: ['sidePanelSections', 'Quotation'],
    params: { doctype: 'Quotation' },
    auto: true,
  })
  
  function updateField(name, value, callback) {
    updateQuotation(name, value, () => {
        Quotation.data[name] = value
      callback?.()
    })
  }
  
  async function deleteQuotation(name) {
    await call('frappe.client.delete', {
      doctype: 'Quotation',
      name,
    })
    router.push({ name: 'Quotations' })
  }

  const activities = ref(null) 
  const showQuickEntryModal = ref(false)

  </script>
  