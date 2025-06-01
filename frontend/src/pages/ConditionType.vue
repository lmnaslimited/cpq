<template>
    <LayoutHeader v-if="condType.data">
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs">
          <template #prefix="{ condType }">
            <!-- <Icon v-if="quotation.icon" :icon="quotation.icon" class="mr-2 h-4" /> -->
          </template>
        </Breadcrumbs>
      </template>
      <template #right-header>
        <CustomActions
          v-if="condType.data._customActions?.length"
          :actions="condType.data._customActions"
        />
        <AssignTo
          v-model="condType.data._assignedTo"
          :data="condType.data"
          doctype="Condition Type"
        />
      </template>
    </LayoutHeader>
    <div v-if="condType?.data" class="flex h-full overflow-hidden">
      <Tabs as="div" v-model="tabIndex" :tabs="tabs">
        <template #tab-panel>
          <Activities
            ref="activities"
            doctype="Condition Type"
            :tabs="tabs"
            v-model:reload="reload"
            v-model:tabIndex="tabIndex"
            v-model="condType"
          />
        </template>
      </Tabs>
      <Resizer class="flex flex-col justify-between border-l" side="right">
        <div
          class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
          @click="copyToClipboard(condType.data.name)"
        >
          {{ __(condType.data.name) }}
        </div>
        <div
          v-if="sections.data"
          class="flex flex-1 flex-col justify-between overflow-hidden"
        >
          <SidePanelLayout
            v-model="condType.data"
            :sections="sections.data"
            doctype="Condition Type"
            @update="updateField"
            @reload="sections.reload"
          />
        </div>
      </Resizer>
    </div>
    <QuickEntryModal
      v-if="showQuickEntryModal"
      v-model="showQuickEntryModal"
      doctype="Condition Type"
      :onlyRequired="true"
    />
    <FilesUploader
      v-if="condType.data?.name"
      v-model="showFilesUploader"
      doctype="Condition Type"
      :docname="condType.data.name"
      @after="
        () => {
          activities?.all_activities?.reload()
          changeTabTo('attachments')
        }
      "
    />
  </template>
  <script setup>
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
  const { doctypeMeta } = getMeta('Condition Type')
  
  const route = useRoute()
  const router = useRouter()
  
  const props = defineProps({
    condTypeId: {
      type: String,
      required: true,
    },
  })
  
  const condType = createResource({
    url: 'crm.apiCpq.design.get_doc_details',
    params: {doctype: "Condition Type", name: props.condTypeId },
    cache: ['condType', props.condTypeId],
    onSuccess: (data) => {
      setupAssignees(condType)
      setupCustomizations(condType, {
        doc: data,
        $dialog,
        $socket,
        router,
        toast,
        updateField,
        createToast: toast.create,
        deleteDoc: deleteCondType,
        resource: { condType, sections },
        call,
      })
    },
  })
  
  onMounted(() => {
    if (condType.data) return
    condType.fetch()
  })
  
  const reload = ref(false)
  const showFilesUploader = ref(false)
  
  function updateCondType(fieldname, value, callback) {
    value = Array.isArray(fieldname) ? '' : value
  
    if (!Array.isArray(fieldname) && validateRequired(fieldname, value)) return
  
    createResource({
      url: 'frappe.client.set_value',
      params: {
        doctype: 'Condition Type',
        name: props.condTypeId,
        fieldname,
        value,
      },
      auto: true,
      onSuccess: () => {
        condType.reload()
        reload.value = true
        toast.success(__('Condition Type updated'))
        callback?.()
      },
      onError: (err) => {
        toast.error(__('Error updating Condition Type'))
      },
    })
  }
  
  function validateRequired(fieldname, value) {
    let meta = condType.data.fields_meta || {}
    if (meta[fieldname]?.reqd && !value) {
      toast.success(__('Error Updating Condition Type'))
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
        label: title.value,
        route: { name: 'Condition Type', params: { condTypeId: condType.data.name } },
    })
    return items
  })
  
  const title = computed(() => {
    let t = doctypeMeta['Condition Type']?.title_field || 'name'
    return condType.data?.[t] || props.condTypeId
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
  
  const { tabIndex, changeTabTo } = useActiveTabManager(tabs, 'lastCondTypeTab')
  
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
    cache: ['sidePanelSections', 'ConditionType'],
    params: { doctype: 'Condition Type' },
    auto: true,
  })
  
  function updateField(name, value, callback) {
    updateCondType(name, value, () => {
      condType.data[name] = value
      callback?.()
    })
  }
  
  async function deleteCondType(name) {
    await call('frappe.client.delete', {
      doctype: 'Condition Type',
      name,
    })
    router.push({ name: 'Condition Types' })
  }

  const activities = ref(null) 
  const showQuickEntryModal = ref(false)

  </script>
  