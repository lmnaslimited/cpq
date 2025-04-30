<template>
    <LayoutHeader v-if="design.data">
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs">
          <template #prefix="{ item }">
            <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
          </template>
        </Breadcrumbs>
      </template>
      <template #right-header>
        <CustomActions
          v-if="design.data._customActions?.length"
          :actions="design.data._customActions"
        />
        <AssignTo
          v-model="design.data._assignedTo"
          :data="design.data"
          doctype="Design"
        />
        <Button
            v-if="!design.data.item"
            :label="__('Create Item')"
            variant="solid"
            :loading="isItemCreating"
            @click="createItem" 
        />
        <Button
            v-if="design.data.item"
            :label="__('View Item')"
            variant="solid"
            @click="viewItem"
        />
      </template>
    </LayoutHeader>
    <div v-if="design?.data" class="flex h-full overflow-hidden">
      <Tabs as="div" v-model="tabIndex" :tabs="tabs">
        <template #tab-panel>
          <Activities
            ref="activities"
            doctype="Design"
            :tabs="tabs"
            v-model:reload="reload"
            v-model:tabIndex="tabIndex"
            v-model="design"
          />
        </template>
      </Tabs>
      <Resizer class="flex flex-col justify-between border-l" side="right">
        <div
          class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
          @click="copyToClipboard(design.data.name)"
        >
          {{ __(design.data.name) }}
        </div>
        <div
          v-if="sections.data"
          class="flex flex-1 flex-col justify-between overflow-hidden"
        >
          <SidePanelLayout
            v-model="design.data"
            :sections="sections.data"
            doctype="Design"
            @update="updateField"
            @reload="sections.reload"
          />
        </div>
      </Resizer>
    </div>

    <QuickEntryModal
      v-if="showQuickEntryModal"
      v-model="showQuickEntryModal"
      doctype="Design"
      :onlyRequired="true"
    />
    <FilesUploader
    v-if="design.data?.name"
    v-model="showFilesUploader"
    doctype="Design"
    :docname="design.data.name"
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
  import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
  import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
  import FilesUploader from '@/components/FilesUploader/FilesUploader.vue'
  import LayoutHeader from '@/components/LayoutHeader.vue'
  import Activities from '@/components/Activities/Activities.vue'
  import AssignTo from '@/components/AssignTo.vue'
  import SidePanelLayout from '@/components/SidePanelLayout.vue'
  import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
  import CustomActions from '@/components/CustomActions.vue'
  import {
    createToast,
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
    Dropdown,
    Tabs,
    Breadcrumbs,
    call,
    usePageMeta,
  } from 'frappe-ui'
  import { useOnboarding } from 'frappe-ui/frappe'
  import { ref, reactive, computed, onMounted, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useActiveTabManager } from '@/composables/useActiveTabManager'
  
  const { brand } = getSettings()
  const { isManager } = usersStore()
  const { $dialog, $socket, makeCall } = globalStore()
  const { statusOptions, getDesignStatus, getDealStatus } = statusesStore()
  const { doctypeMeta } = getMeta('Design')
  
  const { updateOnboardingStep } = useOnboarding('frappecrm')
  
  const route = useRoute()
  const router = useRouter()
  
  const props = defineProps({
    designId: {
      type: String,
      required: true,
    },
  })
  
  const design = createResource({
    url: 'crm.apiCpq.design.get_design',
    params: { name: props.designId },
    cache: ['design', props.designId],
    onSuccess: (data) => {
      setupAssignees(design)
      setupCustomizations(design, {
        doc: data,
        $dialog,
        $socket,
        router,
        updateField,
        createToast,
        deleteDoc: deleteDesign,
        resource: { design, sections },
        call,
      })
    },
  })
  
  onMounted(() => {
    if (design.data) return
    design.fetch()
  })
  
  const reload = ref(false)
  const showFilesUploader = ref(false)
  
  function updateDesign(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  if (!Array.isArray(fieldname) && validateRequired(fieldname, value)) return

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'Design',
      name: props.designId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      design.reload()
      sections.reload()
      reload.value = true
      createToast({
        title: __('Design updated'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      callback?.()
    },
    onError: (err) => {
      createToast({
        title: __('Error updating design'),
        text: __(err.messages?.[0]),
        icon: 'x',
        iconClasses: 'text-red-600',
      })
    },
  })
}
  
  function validateRequired(fieldname, value) {
    let meta = design.data.fields_meta || {}
    if (meta[fieldname]?.reqd && !value) {
      createToast({
        title: __('Error Updating design'),
        text: __('{0} is a required field', [meta[fieldname].label]),
        icon: 'x',
        iconClasses: 'text-ink-red-4',
      })
      return true
    }
    return false
  }
  
  const breadcrumbs = computed(() => {
    let items = [{ label: __('Designs'), route: { name: 'Designs' } }]
  
    if (route.query.view || route.query.viewType) {
      let view = getView(route.query.view, route.query.viewType, 'Design')
      if (view) {
        items.push({
          label: __(view.label),
          icon: view.icon,
          route: {
            name: 'Design',
            params: { viewType: route.query.viewType },
            query: { view: route.query.view },
          },
        })
      }
    }
  
    items.push({
      label: title.value,
      route: { name: 'Design', params: { designId: design.data.name } },
    })
    return items
  })
  
  const title = computed(() => {
    let t = doctypeMeta['Design']?.title_field || 'name'
    return design.data?.[t] || props.designId
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
  
  const { tabIndex, changeTabTo } = useActiveTabManager(tabs, 'lastDesignTab')
  
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
    cache: ['sidePanelSections', 'Design'],
    params: { doctype: 'Design' },
    auto: true,
    onSuccess: (data) => {
        // Check if 'design.data.item' is present before proceeding
        if (design.data?.item) {
        // Loop through each section
        data.forEach(section => {
            // Loop through each column in the section
            section.columns?.forEach(column => {
            // Loop through each field in the column
            column.fields?.forEach(field => {
                field.read_only = 1;
            });
            });
        });
        }
    }
  })

  console.log("sections data", sections)
  
  function updateField(name, value, callback) {
    updateDesign(name, value, () => {
      design.data[name] = value
      callback?.()
    })
  }
  
  async function deleteDesign(name) {
  await call('frappe.client.delete', {
    doctype: 'Design',
    name,
  })
  router.push({ name: 'Designs' })
}
  const activities = ref(null)
  
  const showQuickEntryModal = ref(false)

  const isItemCreating = ref(false)

  //custom button
  const createItem = () => {
  isItemCreating.value = true;
  createResource({
    url: 'crm.apiCpq.design.fn_create_item_from_design',
    params: { design_name: props.designId },
    onSuccess: (data) => {
      isItemCreating.value = false;
      updateField("item", data)
      createToast({
        title: __('Item created successfully'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    },
    onError: (err) => {
      isItemCreating.value = false;
      createToast({
        title: __('Error creating item'),
        text: __(err.messages?.[0] || 'Failed to create item'),
        icon: 'x',
        iconClasses: 'text-red-600',
      })
    },
  }).fetch()
}

const viewItem = async () => {
  if (design.data.item) {
   router.push({ name: 'Item', params: { itemId: design.data.item } });
  }
};

//direct material cost
watch(
  () => design.data?.direct_material_cost,
  (newValue, oldValue) => {
    const newCost = Number(newValue);
    const oldCost = Number(oldValue);

    if (!Number.isNaN(newCost) && !Number.isNaN(oldCost)) {
      if (newCost !== oldCost) {
        if (newCost > 0){
          getTotalCost()
        } else {
          updateField("total_cost", 0);
        }
      } else {

      }
    } else {

    }
  },
  { immediate: false }
);

const getTotalCost = () => {
  createResource({
    url: 'crm.apiCpq.pricing.get_total_cost_from_direct_material_cost',
    params: {  i_direct_material_cost: design.data.direct_material_cost },
    onSuccess: (data) => {
      updateField("total_cost", data.total_cost);
    }
  }).fetch()
}
  </script>
  