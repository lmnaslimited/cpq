<template>
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
      <template #right-header>
        
        <Button
          variant="solid"
          :label="__('Create')"
          @click="showValueModal = true"
        >
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </template>
    </LayoutHeader>
    <ViewControls
      ref="viewControls"
      v-model="conditionaValues"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      doctype="Condition Value"
    />
    <ConditionValuesListView
      ref="conditionValueListView"
      v-if="conditionaValues.data && rows.length"
      v-model="conditionaValues.data.page_length_count"
      v-model:list="conditionaValues"
      :rows="rows"
      :columns="conditionaValues.data.columns"
      :options="{
        showTooltip: false,
        resizeColumn: true,
        rowCount: conditionaValues.data.row_count,
        totalCount: conditionaValues.data.total_count,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
    />
    <div v-else-if="conditionaValues.data" class="flex h-full items-center justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <span>{{ __('No Condition Value Found') }}</span>
        <Button :label="__('Create')" @click="showValueModal = true">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </div>
    </div>
    <ConditionValueModal v-model="showValueModal" />
  </template>
  
  <script setup>
  
  import LayoutHeader from '@/components/LayoutHeader.vue'
  import ViewControls from '@/components/ViewControls.vue'
  import ConditionValuesListView from '@/components/ListViews/ConditionValuesListView.vue'
  import ConditionValueModal from '@/components/Modals/ConditionValueModal.vue'
  import { Breadcrumbs } from 'frappe-ui'
  import { ref, computed } from 'vue'
  
  
  const breadcrumbs = [{ label: __('Condition Values'), route: { name: 'Condition Values' } }]
  const conditionValueListView = ref(null)
  const showValueModal = ref(false)
  
  const conditionaValues = ref({})
  const loadMore = ref(1)
  const triggerResize = ref(1)
  const updatedPageCount = ref(20)
  const viewControls = ref(null)
  
  const rows = computed(() => {
    if (!conditionaValues.value?.data?.data) return []
    return conditionaValues.value.data.data.map((conditionaValue) => {
      let _rows = {}
      conditionaValues.value.data.rows.forEach((row) => {
        _rows[row] = conditionaValue[row]
      })
      return _rows
    })
  })
  </script>