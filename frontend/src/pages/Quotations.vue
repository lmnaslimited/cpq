<template>
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Quotations" />
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
      @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
      @likeDoc="(data) => viewControls.likeDoc(data)"
      @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
    />
    <div v-else-if="quotations.data" class="flex h-full items-center justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
      >
        <LeadsIcon class="h-10 w-10" />
        <span>{{ __('No {0} Found', [__('Quotations')]) }}</span>
        <Button :label="__('Create')" @click="showQuotationModal = true">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </div>
    </div>
    <QuotationModal
      v-if="showQuotationModal"
      v-model="showQuotationModal"
      v-model:quickEntry="showQuickEntryModal"
      :defaults="defaults"
    />
    <QuickEntryModal v-if="showQuickEntryModal" v-model="showQuickEntryModal" doctype="Quotation" />
  </template>
  
  <script setup>
  import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
  import CustomActions from '@/components/CustomActions.vue'
  import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
  import LayoutHeader from '@/components/LayoutHeader.vue'
  import QuotationsListView from '@/components/ListViews/QuotationsListView.vue'
  import QuotationModal from '@/components/Modals/QuotationModal.vue'
  import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
  import ViewControls from '@/components/ViewControls.vue'
  import { getMeta } from '@/stores/meta'
  import { formatDate, timeAgo, formatTime } from '@/utils'
  import { ref, computed, reactive } from 'vue'
  
  const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
    getMeta('Quotation')
   
  const quotationsListView = ref(null)
  const showQuotationModal = ref(false)
  const showQuickEntryModal = ref(false)
  
  const defaults = reactive({})
  
  // leads data is loaded in the ViewControls component
  const quotations = ref({})
  const loadMore = ref(1)
  const triggerResize = ref(1)
  const updatedPageCount = ref(20)
  const viewControls = ref(null)
  
 
  // Rows
  const rows = computed(() => {
    if (!quotations.value?.data?.data) return []
    
      return parseRows(quotations.value?.data.data, quotations.value.data.columns)
    
  })
  
  function parseRows(rows, columns = []) {
    return rows.map((quotation) => {
      let _rows = {}
      quotations.value?.data.rows.forEach((row) => {
        _rows[row] = quotation[row]
  
        let fieldType = columns?.find(
          (col) => (col.key || col.value) == row,
        )?.type
  
        if (
          fieldType &&
          ['Date', 'Datetime'].includes(fieldType) &&
          !['modified', 'creation'].includes(row)
        ) {
          _rows[row] = formatDate(quotation[row], '', true, fieldType == 'Datetime')
        }
  
        if (fieldType && fieldType == 'Currency') {
          _rows[row] = getFormattedCurrency(row, quotation)
        }
  
        if (fieldType && fieldType == 'Float') {
          _rows[row] = getFormattedFloat(row, quotation)
        }
  
        if (fieldType && fieldType == 'Percent') {
          _rows[row] = getFormattedPercent(row, quotation)
        }
  
          else if (['modified', 'creation'].includes(row)) {
          _rows[row] = {
            label: formatDate(quotation[row]),
            timeAgo: __(timeAgo(quotation[row])),
          }
        } else if (
          ['first_response_time', 'first_responded_on', 'response_by'].includes(
            row,
          )
        ) {
          let field = row == 'response_by' ? 'response_by' : 'first_responded_on'
          _rows[row] = {
            label: quotation[field] ? formatDate(quotation[field]) : '',
            timeAgo: quotation[row]
              ? row == 'first_response_time'
                ? formatTime(quotation[row])
                : __(timeAgo(quotation[row]))
              : '',
          }
        }
      })
      _rows['_email_count'] = quotation._email_count
      _rows['_note_count'] = quotation._note_count
      _rows['_task_count'] = quotation._task_count
      _rows['_comment_count'] = quotation._comment_count
      return _rows
    })
  }
  </script>