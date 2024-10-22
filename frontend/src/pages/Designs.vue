<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="designsListView?.customListActions"
        :actions="designsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        @click="showDesignModal = true"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="designs"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Design"
  />
  <DesignsListView
    ref="designsListView"
    v-if="designs.data && rows.length"
    v-model="designs.data.page_length_count"
    v-model:list="designs"
    :rows="rows"
    :columns="designs.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: designs.data.row_count,
      totalCount: designs.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
  />
  <div v-else-if="designs.data" class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <DealsIcon class="h-10 w-10" />
      <span>{{ __('No Designs Found') }}</span>
      <Button :label="__('Create')" @click="showDesignModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
  <DesignModal v-model="showDesignModal" />
</template>

<script setup>

import CustomActions from '@/components/CustomActions.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import DesignsListView from '@/components/ListViews/DesignsListView.vue'
import DesignModal from '@/components/Modals/DesignModal.vue'
import { usersStore } from '@/stores/users'
import { organizationsStore } from '@/stores/organizations'

import { statusesStore } from '@/stores/statuses'

import {
  dateFormat,
  dateTooltipFormat,
  timeAgo,
  formatNumberIntoCurrency,
  formatTime,
} from '@/utils'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'


const breadcrumbs = [{ label: __('Designs'), route: { name: 'Designs' } }]
const { getUser } = usersStore()
const { getOrganization } = organizationsStore()
const { getDealStatus } = statusesStore()

const designsListView = ref(null)
const showDesignModal = ref(false)

// desigs data is loaded in the ViewControls component
const designs = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Rows
const rows = computed(() => {
  if (!designs.value?.data?.data) return []
  return designs.value.data.data.map((design) => {
    let _rows = {}
    designs.value.data.rows.forEach((row) => {
      _rows[row] = design[row]
    })
    return _rows
  })
})
</script>