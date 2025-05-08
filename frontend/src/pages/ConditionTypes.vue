<template>
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Condition Types" />
      </template>
      <template #right-header>
        <CustomActions
          v-if="condTypesListView?.customListActions"
          :actions="condTypesListView.customListActions"
        />
        <Button
          variant="solid"
          :label="__('Create')"
          @click="showCondTypeModal = true"
        >
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </template>
    </LayoutHeader>
    <ViewControls
      ref="viewControls"
      v-model="condTypes"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      doctype="Condition Type"
    />

    <CondTypesListView
      ref="condTypesListView"
      v-if="condTypes.data && rows.length"
      v-model="condTypes.data.page_length_count"
      v-model:list="condTypes"
      :rows="rows"
      :columns="condTypes.data.columns"
      :options="{
        showTooltip: false,
        resizeColumn: true,
        rowCount: condTypes.data.row_count,
        totalCount: condTypes.data.total_count,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
      @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
      @likeDoc="(data) => viewControls.likeDoc(data)"
    />
    <div v-else-if="condTypes.data" class="flex h-full items-center justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
      >
        <LeadsIcon class="h-10 w-10" />
        <span>{{ __('No {0} Found', [__('Condition Types')]) }}</span>
        <Button :label="__('Create')" @click="showCondTypeModal = true">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </div>
    </div>
    <CondTypeModal
      v-if="showCondTypeModal"
      v-model="showCondTypeModal"
      v-model:quickEntry="showQuickEntryModal"
      :defaults="defaults"
    />
    <QuickEntryModal v-if="showQuickEntryModal" v-model="showQuickEntryModal" doctype="Condition Type" />
  </template>
  
  <script setup>
  import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
  import CustomActions from '@/components/CustomActions.vue'
  import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
  import LayoutHeader from '@/components/LayoutHeader.vue'
  import CondTypesListView from '@/components/ListViews/CondTypesListView.vue'
  import CondTypeModal from '@/components/Modals/CondTypeModal.vue'
  import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
  import ViewControls from '@/components/ViewControls.vue'
  import { getMeta } from '@/stores/meta'
  import { formatDate, timeAgo, formatTime } from '@/utils'
  import { ref, computed, reactive } from 'vue'
  
  const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
    getMeta('Condition Type')
   
  const condTypesListView = ref(null)
  const showCondTypeModal = ref(false)
  const showQuickEntryModal = ref(false)
  
  const defaults = reactive({})
  
  // leads data is loaded in the ViewControls component
  const condTypes = ref({})
  const loadMore = ref(1)
  const triggerResize = ref(1)
  const updatedPageCount = ref(20)
  const viewControls = ref(null)
  
 
  // Rows
  const rows = computed(() => {
    if (!condTypes.value?.data?.data) return []
    
      return parseRows(condTypes.value?.data.data, condTypes.value.data.columns)
    
  })
  
  function parseRows(rows, columns = []) {
    return rows.map((condType) => {
      let _rows = {}
      condTypes.value?.data.rows.forEach((row) => {
        _rows[row] = condType[row]
  
        let fieldType = columns?.find(
          (col) => (col.key || col.value) == row,
        )?.type
  
        if (
          fieldType &&
          ['Date', 'Datetime'].includes(fieldType) &&
          !['modified', 'creation'].includes(row)
        ) {
          _rows[row] = formatDate(condType[row], '', true, fieldType == 'Datetime')
        }
  
        if (fieldType && fieldType == 'Currency') {
          _rows[row] = getFormattedCurrency(row, condType)
        }
  
        if (fieldType && fieldType == 'Float') {
          _rows[row] = getFormattedFloat(row, condType)
        }
  
        if (fieldType && fieldType == 'Percent') {
          _rows[row] = getFormattedPercent(row, condType)
        }
  
          else if (['modified', 'creation'].includes(row)) {
          _rows[row] = {
            label: formatDate(condType[row]),
            timeAgo: __(timeAgo(condType[row])),
          }
        } else if (
          ['first_response_time', 'first_responded_on', 'response_by'].includes(
            row,
          )
        ) {
          let field = row == 'response_by' ? 'response_by' : 'first_responded_on'
          _rows[row] = {
            label: condType[field] ? formatDate(condType[field]) : '',
            timeAgo: condType[row]
              ? row == 'first_response_time'
                ? formatTime(condType[row])
                : __(timeAgo(condType[row]))
              : '',
          }
        }
      })
      _rows['_email_count'] = condType._email_count
      _rows['_note_count'] = condType._note_count
      _rows['_task_count'] = condType._task_count
      _rows['_comment_count'] = condType._comment_count
      return _rows
    })
  }
  </script>