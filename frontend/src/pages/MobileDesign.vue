<template>
  <LayoutHeader v-if="design.data">
    <header
      class="relative flex h-12 items-center justify-between gap-2 py-2.5 pl-5"
    >
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
      <div class="absolute right-0">
        <Dropdown :options="statusOptions('design', updateField, customStatuses)">
          <template #default="{ open }">
            <Button
              :label="design.data.status"
              :class="getLeadStatus(design.data.status).colorClass"
            >
              <template #prefix>
                <IndicatorIcon />
              </template>
              <template #suffix>
                <FeatherIcon
                  :name="open ? 'chevron-up' : 'chevron-down'"
                  class="h-4"
                />
              </template>
            </Button>
          </template>
        </Dropdown>
      </div>
    </header>
  </LayoutHeader>
  <div
    v-if="design.data"
    class="flex h-12 items-center justify-between gap-2 border-b px-3 py-2.5"
  >
    <component :is="design.data._assignedTo?.length == 1 ? 'Button' : 'div'">
      <MultipleAvatar
        :avatars="design.data._assignedTo"
        @click="showAssignmentModal = true"
      />
    </component>
    <div class="flex items-center gap-2">
      <CustomActions v-if="customActions" :actions="customActions" />
      <Button
        :label="__('Convert')"
        variant="solid"
        @click="showConvertToDealModal = true"
      />
    </div>
  </div>
  <div v-if="design?.data" class="flex h-full overflow-hidden">
    <Tabs
      v-model="tabIndex"
      v-slot="{ tab }"
      :tabs="tabs"
      tablistClass="!px-3"
      class="overflow-auto"
    >
      <div v-if="tab.name == 'Details'">
        <SLASection
          v-if="design.data.sla_status"
          v-model="design.data"
          @updateField="updateField"
        />
        <div
          v-if="fieldsLayout.data"
          class="flex flex-1 flex-col justify-between overflow-hidden"
        >
          <div class="flex flex-col overflow-y-auto">
            <div
              v-for="(section, i) in fieldsLayout.data"
              :key="section.label"
              class="flex flex-col px-2 py-3 sm:p-3"
              :class="{ 'border-b': i !== fieldsLayout.data.length - 1 }"
            >
              <Section :is-opened="section.opened" :label="section.label">
                <SectionFields
                  :fields="section.fields"
                  :isLastSection="i == fieldsLayout.data.length - 1"
                  v-model="design.data"
                  @update="updateField"
                />
              </Section>
            </div>
          </div>
        </div>
      </div>
      <Activities
        v-else
        doctype="Design"
        :tabs="tabs"
        v-model:reload="reload"
        v-model:tabIndex="tabIndex"
        v-model="design"
      />
    </Tabs>
  </div>
  <AssignmentModal
    v-if="showAssignmentModal"
    v-model="showAssignmentModal"
    v-model:assignees="design.data._assignedTo"
    :doc="design.data"
    doctype="Design"
  />
  <Dialog
    v-model="showConvertToDealModal"
    :options="{
      title: __('Convert to Deal'),
      size: 'xl',
      actions: [
        {
          label: __('Convert'),
          variant: 'solid',
          onClick: convertToDeal,
        },
      ],
    }"
  >
    <template #body-content>
      <div class="mb-4 flex items-center gap-2 text-gray-600">
        <OrganizationsIcon class="h-4 w-4" />
        <label class="block text-base">{{ __('Organization') }}</label>
      </div>
      <div class="ml-6">
        <div class="flex items-center justify-between text-base">
          <div>{{ __('Choose Existing') }}</div>
          <Switch v-model="existingOrganizationChecked" />
        </div>
        <Link
          v-if="existingOrganizationChecked"
          class="form-control mt-2.5"
          variant="outline"
          size="md"
          :value="existingOrganization"
          doctype="CRM Organization"
          @change="(data) => (existingOrganization = data)"
        />
        <div v-else class="mt-2.5 text-base">
          {{
            __(
              'New organization will be created based on the data in details section',
            )
          }}
        </div>
      </div>

      <div class="mb-4 mt-6 flex items-center gap-2 text-gray-600">
        <ContactsIcon class="h-4 w-4" />
        <label class="block text-base">{{ __('Contact') }}</label>
      </div>
      <div class="ml-6">
        <div class="flex items-center justify-between text-base">
          <div>{{ __('Choose Existing') }}</div>
          <Switch v-model="existingContactChecked" />
        </div>
        <Link
          v-if="existingContactChecked"
          class="form-control mt-2.5"
          variant="outline"
          size="md"
          :value="existingContact"
          doctype="Contact"
          @change="(data) => (existingContact = data)"
        />
        <div v-else class="mt-2.5 text-base">
          {{ __("New contact will be created based on the person's details") }}
        </div>
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import Icon from '@/components/Icon.vue'
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Activities from '@/components/Activities/Activities.vue'
import AssignmentModal from '@/components/Modals/AssignmentModal.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import Section from '@/components/Section.vue'
import SectionFields from '@/components/SectionFields.vue'
import SLASection from '@/components/SLASection.vue'
import CustomActions from '@/components/CustomActions.vue'
import { createToast, setupAssignees, setupCustomizations } from '@/utils'
import { getView } from '@/utils/view'
import { globalStore } from '@/stores/global'
import { contactsStore } from '@/stores/contacts'
import { statusesStore } from '@/stores/statuses'
import {
  whatsappEnabled,
  callEnabled,
  isMobileView,
} from '@/composables/settings'
import { useActiveTabManager } from '@/composables/useActiveTabManager'
import {
  createResource,
  Dropdown,
  Tabs,
  Switch,
  Breadcrumbs,
  call,
} from 'frappe-ui'
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const { $dialog, $socket } = globalStore()
const { getContactByName, contacts } = contactsStore()
const { statusOptions, getLeadStatus } = statusesStore()
const route = useRoute()
const router = useRouter()

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
  design.fetch()
})

const reload = ref(false)
const showAssignmentModal = ref(false)

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

const tabs = computed(() => {
  let tabOptions = [
    {
      name: 'Details',
      label: __('Details'),
      icon: DetailsIcon,
      condition: () => isMobileView.value,
    },
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

const fieldsLayout = createResource({
  url: 'crm.api.doc.get_sidebar_fields',
  cache: ['fieldsLayout', props.designId],
  params: { doctype: 'Design', name: props.designId },
  auto: true,
})

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