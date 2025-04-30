<template>
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Designs" />
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
      @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
      @likeDoc="(data) => viewControls.likeDoc(data)"
    />
    <div v-else-if="designs.data" class="flex h-full items-center justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
      >
        <span>{{ __('No {0} Found', [__('Design')]) }}</span>
        <Button :label="__('Create')" @click="showDesignModal = true">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </div>
    </div>
    <DesignModal
      v-if="showDesignModal"
      v-model="showDesignModal"
      v-model:quickEntry="showQuickEntryModal"
      :defaults="defaults"
    />
   
    <QuickEntryModal v-if="showQuickEntryModal" v-model="showQuickEntryModal" />
  </template>
  
  <script setup>
  import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
  import CustomActions from '@/components/CustomActions.vue'
  import LayoutHeader from '@/components/LayoutHeader.vue'
  import DesignsListView from '@/components/ListViews/DesignsListView.vue'
  import DesignModal from '@/components/Modals/DesignModal.vue'
  import NoteModal from '@/components/Modals/NoteModal.vue'
  import TaskModal from '@/components/Modals/TaskModal.vue'
  import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
  import ViewControls from '@/components/ViewControls.vue'
  import { getMeta } from '@/stores/meta'
  import { usersStore } from '@/stores/users'
  import { formatDate, timeAgo, formatTime } from '@/utils'
  import { ref, computed, reactive} from 'vue'
  
  const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
    getMeta('Design')
  const { getUser } = usersStore()
  
  const designsListView = ref(null)
  const showDesignModal = ref(false)
  const showQuickEntryModal = ref(false)
  
  const defaults = reactive({})
  
  // designs data is loaded in the ViewControls component
  const designs = ref({})
  const loadMore = ref(1)
  const triggerResize = ref(1)
  const updatedPageCount = ref(20)
  const viewControls = ref(null)
    
  // Rows
  const rows = computed(() => {
    if (!designs.value?.data?.data) return []
    
      return parseRows(designs.value?.data.data, designs.value.data.columns)
 
  })
    
  function parseRows(rows, columns = []) {
    let view_type = designs.value.data.view_type
    let key = view_type === 'kanban' ? 'fieldname' : 'key'
    let type = view_type === 'kanban' ? 'fieldtype' : 'type'
  
    return rows.map((design) => {
      let _rows = {}
      designs.value?.data.rows.forEach((row) => {
        _rows[row] = design[row]
  
        let fieldType = columns?.find((col) => (col[key] || col.value) == row)?.[
          type
        ]
  
        if (
          fieldType &&
          ['Date', 'Datetime'].includes(fieldType) &&
          !['modified', 'creation'].includes(row)
        ) {
          _rows[row] = formatDate(design[row], '', true, fieldType == 'Datetime')
        }
  
        if (fieldType && fieldType == 'Currency') {
          _rows[row] = getFormattedCurrency(row, design)
        }
  
        if (fieldType && fieldType == 'Float') {
          _rows[row] = getFormattedFloat(row, design)
        }
  
        if (fieldType && fieldType == 'Percent') {
          _rows[row] = getFormattedPercent(row, design)
        }
  
      if (['modified', 'creation'].includes(row)) {
          _rows[row] = {
            label: formatDate(design[row]),
            timeAgo: __(timeAgo(design[row])),
          }
        } else if (
          ['first_response_time', 'first_responded_on', 'response_by'].includes(
            row,
          )
        ) {
          let field = row == 'response_by' ? 'response_by' : 'first_responded_on'
          _rows[row] = {
            label: design[field] ? formatDate(design[field]) : '',
            timeAgo: design[row]
              ? row == 'first_response_time'
                ? formatTime(design[row])
                : __(timeAgo(design[row]))
              : '',
          }
        }
      })
      _rows['_email_count'] = design._email_count
      _rows['_note_count'] = design._note_count
      _rows['_task_count'] = design._task_count
      _rows['_comment_count'] = design._comment_count
      return _rows
    })
  }
  </script>
  