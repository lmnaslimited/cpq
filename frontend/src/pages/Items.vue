<template>
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Items" />
      </template>
      <template #right-header>
        <CustomActions
          v-if="itemsListView?.customListActions"
          :actions="itemsListView.customListActions"
        />
        <Button
          variant="solid"
          :label="__('Create')"
          @click="showItemModal = true"
        >
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
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
      @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
      @likeDoc="(data) => viewControls.likeDoc(data)"
      @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
    />
    <div v-else-if="items.data" class="flex h-full items-center justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
      >
        <LeadsIcon class="h-10 w-10" />
        <span>{{ __('No {0} Found', [__('Items')]) }}</span>
        <Button :label="__('Create')" @click="showItemModal = true">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </div>
    </div>
    <ItemModal
      v-if="showItemModal"
      v-model="showItemModal"
      v-model:quickEntry="showQuickEntryModal"
      :defaults="defaults"
    />
    <QuickEntryModal v-if="showQuickEntryModal" v-model="showQuickEntryModal" doctype="Item" />
  </template>
  
  <script setup>
  import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
  import CustomActions from '@/components/CustomActions.vue'
  import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
  import LayoutHeader from '@/components/LayoutHeader.vue'
  import ItemsListView from '@/components/ListViews/ItemsListView.vue'
  import ItemModal from '@/components/Modals/ItemModal.vue'
  import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
  import ViewControls from '@/components/ViewControls.vue'
  import { getMeta } from '@/stores/meta'
  import { globalStore } from '@/stores/global'
  import { statusesStore } from '@/stores/statuses'
  import { formatDate, timeAgo, formatTime } from '@/utils'
  import { useRoute } from 'vue-router'
  import { ref, computed, reactive } from 'vue'
  
  const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
    getMeta('Item')
   
  const itemsListView = ref(null)
  const showItemModal = ref(false)
  const showQuickEntryModal = ref(false)
  
  const defaults = reactive({})
  
  // leads data is loaded in the ViewControls component
  const items = ref({})
  const loadMore = ref(1)
  const triggerResize = ref(1)
  const updatedPageCount = ref(20)
  const viewControls = ref(null)
  
 
  // Rows
  const rows = computed(() => {
    if (!items.value?.data?.data) return []
    
      return parseRows(items.value?.data.data, items.value.data.columns)
    
  })
  
  function parseRows(rows, columns = []) {
    return rows.map((item) => {
      let _rows = {}
      items.value?.data.rows.forEach((row) => {
        _rows[row] = item[row]
  
        let fieldType = columns?.find(
          (col) => (col.key || col.value) == row,
        )?.type
  
        if (
          fieldType &&
          ['Date', 'Datetime'].includes(fieldType) &&
          !['modified', 'creation'].includes(row)
        ) {
          _rows[row] = formatDate(item[row], '', true, fieldType == 'Datetime')
        }
  
        if (fieldType && fieldType == 'Currency') {
          _rows[row] = getFormattedCurrency(row, item)
        }
  
        if (fieldType && fieldType == 'Float') {
          _rows[row] = getFormattedFloat(row, item)
        }
  
        if (fieldType && fieldType == 'Percent') {
          _rows[row] = getFormattedPercent(row, item)
        }
  
          else if (['modified', 'creation'].includes(row)) {
          _rows[row] = {
            label: formatDate(item[row]),
            timeAgo: __(timeAgo(item[row])),
          }
        } else if (
          ['first_response_time', 'first_responded_on', 'response_by'].includes(
            row,
          )
        ) {
          let field = row == 'response_by' ? 'response_by' : 'first_responded_on'
          _rows[row] = {
            label: item[field] ? formatDate(item[field]) : '',
            timeAgo: item[row]
              ? row == 'first_response_time'
                ? formatTime(item[row])
                : __(timeAgo(item[row]))
              : '',
          }
        }
      })
      _rows['_email_count'] = item._email_count
      _rows['_note_count'] = item._note_count
      _rows['_task_count'] = item._task_count
      _rows['_comment_count'] = item._comment_count
      return _rows
    })
  }
  </script>