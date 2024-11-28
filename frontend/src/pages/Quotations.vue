<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="quotationsListView?.customListActions"
        :actions="quotationsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        @click="showQuotationModal = true"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="quotations"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Quotation"
  />
  <QuotationsListView
    ref="quotationsListView"
    v-if="quotations.data && rows.length"
    v-model="quotations.data.page_length_count"
    v-model:list="quotations"
    :rows="rows"
    :columns="quotations.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: quotations.data.row_count,
      totalCount: quotations.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
  />
  <div v-else-if="quotations.data" class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <span>{{ __('No Quotations Found') }}</span>
      <Button :label="__('Create')" @click="showQuotationModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
  <QuotationModal v-model="showQuotationModal" />
</template>

<script setup>

import CustomActions from '@/components/CustomActions.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import QuotationsListView from '@/components/ListViews/QuotationsListView.vue'
import QuotationModal from '@/components/Modals/QuotationModal.vue'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'


const breadcrumbs = [{ label: __('Quotations'), route: { name: 'Quotations' } }]
const quotationsListView = ref(null)
const showQuotationModal = ref(false)

// quotations data is loaded in the ViewControls component
const quotations = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Rows
const rows = computed(() => {
  if (!quotations.value?.data?.data) return []
  return quotations.value.data.data.map((quotation) => {
    let _rows = {}
    quotations.value.data.rows.forEach((row) => {
      _rows[row] = quotation[row]
    })
    return _rows
  })
})
</script>