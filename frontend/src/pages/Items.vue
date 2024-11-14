<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="itemsListView?.customListActions"
        :actions="itemsListView.customListActions"
      />
      
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="items"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Item"
  />
  <ItemsListView
    ref="itemsListView"
    v-if="items.data && rows.length"
    v-model="items.data.page_length_count"
    v-model:list="items"
    :rows="rows"
    :columns="items.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: items.data.row_count,
      totalCount: items.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
  />
  <div v-else-if="items.data" class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <span>{{ __('No Item Found') }}</span>
      
    </div>
  </div>
 
</template>

<script setup>

import CustomActions from '@/components/CustomActions.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import ItemsListView from '@/components/ListViews/ItemsListView.vue'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'


const breadcrumbs = [{ label: __('Items'), route: { name: 'Items' } }]
const itemsListView = ref(null)

// items data is loaded in the ViewControls component
const items = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Rows
const rows = computed(() => {
  if (!items.value?.data?.data) return []
  return items.value.data.data.map((item) => {
    let _rows = {}
    items.value.data.rows.forEach((row) => {
      _rows[row] = item[row]
    })
    return _rows
  })
})
</script>