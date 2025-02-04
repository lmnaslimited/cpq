<template>
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
      <template #right-header>
        <CustomActions
          v-if="conditionListView?.customListActions"
          :actions="conditionListView.customListActions"
        />
        <Button
          variant="solid"
          :label="__('Create')"
          @click="navigateToCreate"
        >
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </template>
    </LayoutHeader>
    <ViewControls
      ref="viewControls"
      v-model="conditions"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      doctype="Condition Type"
    />
    <ConditionsListView
      ref="conditionListView"
      v-if="conditions.data && rows.length"
      v-model="conditions.data.page_length_count"
      v-model:list="conditions"
      :rows="rows"
      :columns="conditions.data.columns"
      :options="{
        showTooltip: false,
        resizeColumn: true,
        rowCount: conditions.data.row_count,
        totalCount: conditions.data.total_count,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
    />
    <div v-else-if="conditions.data" class="flex h-full items-center justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <span>{{ __('No Condition Type Found') }}</span>
        <Button :label="__('Create')" @click="navigateToCreate">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </div>
    </div>
    <ItemModal v-model="showItemModal" />
  </template>
  
  <script setup>
  
  import CustomActions from '@/components/CustomActions.vue'
  import LayoutHeader from '@/components/LayoutHeader.vue'
  import ViewControls from '@/components/ViewControls.vue'
  import ConditionsListView from '@/components/ListViews/ConditionsListView.vue'
  import ItemModal from '@/components/Modals/ItemModal.vue'
  import { Breadcrumbs } from 'frappe-ui'
  import { ref, computed } from 'vue'
  import { useRouter } from 'vue-router'

  
  const router = useRouter()
  const breadcrumbs = [{ label: __('Condition Types'), route: { name: 'Condition Types' } }]
  const conditionListView = ref(null)
  const showItemModal = ref(false)
  
  const conditions = ref({})
  const loadMore = ref(1)
  const triggerResize = ref(1)
  const updatedPageCount = ref(20)
  const viewControls = ref(null)
  
  const rows = computed(() => {
    if (!conditions.value?.data?.data) return []
    return conditions.value.data.data.map((condition) => {
      let _rows = {}
      conditions.value.data.rows.forEach((row) => {
        _rows[row] = condition[row]
      })
      return _rows
    })
  })

  const navigateToCreate = () => {
  router.push({ name: 'Create' });
};

  </script>