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
      <CustomActions v-if="customActions" :actions="customActions" />
          <Button
            :label="design.data.status"
          >
            <template #prefix>
              <IndicatorIcon />
            </template>
          </Button>
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
    <Tabs v-model="tabIndex" v-slot="{ tab }" :tabs="tabs">
      <Activities
        ref="activities"
        doctype="Design"
        :tabs="tabs"
        v-model:reload="reload"
        v-model:tabIndex="tabIndex"
        v-model="design"
      />
    </Tabs>
    <Resizer class="flex flex-col justify-between border-l" side="right">
      <div
        class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium"
        @click="copyToClipboard(design.data.name)"
      >
        {{ __(design.data.name) }}
      </div>
     
      <!-- <SLASection
        v-if="design.data.sla_status"
        v-model="design.data"
        @updateField="updateField"
      /> -->
      <div
        v-if="fieldsLayout.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <div class="flex flex-col overflow-y-auto">
          <div
            v-for="(section, i) in fieldsLayout.data"
            :key="section.label"
            class="flex flex-col p-3"
            :class="{ 'border-b': i !== fieldsLayout.data.length - 1 }"
          >
            <Section :is-opened="section.opened" :label="section.label">
              <SectionFieldCpq
                :fields="section.fields"
                :isLastSection="i == fieldsLayout.data.length - 1"
                v-model="design.data"
                @update="updateField"
              />
              <!-- <template v-if="i == 0 && isManager()" #actions>
                <Button
                  variant="ghost"
                  class="w-7 mr-2"
                  @click="showSidePanelModal = true"
                >
                  <EditIcon class="h-4 w-4" />
                </Button>
              </template> -->
            </Section>
          </div>
        </div>
      </div>
    </Resizer>
  </div>
  <AssignmentModal
    v-if="showAssignmentModal"
    v-model="showAssignmentModal"
    v-model:assignees="design.data._assignedTo"
    :doc="design.data"
    doctype="Design"
  />
  <SidePanelModal
    v-if="showSidePanelModal"
    v-model="showSidePanelModal"
    @reload="() => fieldsLayout.reload()"
  />
</template>
<script setup>
import Icon from '@/components/Icon.vue'
import Resizer from '@/components/Resizer.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Activities from '@/components/Activities/Activities.vue'
import AssignmentModal from '@/components/Modals/AssignmentModal.vue'
import SidePanelModal from '@/components/Settings/SidePanelModal.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import Section from '@/components/Section.vue'
import SectionFieldCpq from '@/components/SectionFieldCpq.vue'
import SLASection from '@/components/SLASection.vue'
import CustomActions from '@/components/CustomActions.vue'
import {
  createToast,
  setupAssignees,
  setupCustomizations,
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
const { statusOptions, getLeadStatus } = statusesStore()
const { isManager } = usersStore()
const route = useRoute()
const router = useRouter()
const isItemCreating = ref(false)

const props = defineProps({
  designId: {
    type: String,
    required: true,
  },
})

const customActions = ref([])
const customStatuses = ref([])

const design = createResource({
  url: 'crm.cpq.doctype.design.api.get_design',
  params: { name: props.designId },
  cache: ['design', props.designId],
  onSuccess: async (data) => {
    let obj = {
      doc: data,
      $dialog,
      $socket,
      router,
      updateField,
      createToast,
      deleteDoc: deleteDesign,
      resource: {
        design,
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
  if (design.data) return
  design.fetch().catch((err) => {
});
})

const reload = ref(false)
const showAssignmentModal = ref(false)
const showSidePanelModal = ref(false)

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
      title: __('Error Updating Design'),
      text: __('{0} is a required field', [meta[fieldname].label]),
      icon: 'x',
      iconClasses: 'text-red-600',
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
          name: 'Designs',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: design.data.name || __('Untitled'),
    route: { name: 'Design', params: { designId: design.data.name } },
  })
  return items
})

usePageMeta(() => {
  return {
    title: design.data?.name || design.data?.name,
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

const { tabIndex } = useActiveTabManager(tabs, 'lastDesignTab')

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

watch(
  () => design.data?.direct_material_cost,
  (newValue, oldValue) => {
    const newCost = Number(newValue);
    const oldCost = Number(oldValue);

    if (!Number.isNaN(newCost) && !Number.isNaN(oldCost)) {
      if (newCost !== oldCost) {
        // Only update total_cost if newCost is different from oldCost
        console.log("Value changed:", oldCost, newCost);
        updateField("total_cost", newCost);
      } else {
        console.log("No change in value:", oldCost, newCost);
      }
    } else {
      console.log("Skipping update due to NaN value:", "newCost:", newCost, "oldCost:", oldCost);
    }
  },
  { immediate: false }
)

const fieldsLayout = createResource({
  url: 'crm.api.docCpq.get_sidebar_fields_with_table',
  cache: ['fieldsLayout', props.designId],
  params: { doctype: 'Design', name: props.designId },
  auto: true,
})

const createItem = () => {
  isItemCreating.value = true;
  createResource({
    url: 'crm.api.docCpq.create_item_from_design',
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

</script>