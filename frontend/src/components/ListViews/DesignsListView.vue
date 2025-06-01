<template>
    <ListView
      :class="$attrs.class"
      :columns="columns"
      :rows="rows"
      :options="{
        getRowRoute: (row) => ({
          name: 'Design',
          params: { designId: row.name },
          query: { view: route.query.view, viewType: route.params.viewType },
        }),
        selectable: options.selectable,
        showTooltip: options.showTooltip,
        resizeColumn: options.resizeColumn,
      }"
      row-key="name"
      @update:selections="(selections) => emit('selectionsChanged', selections)"
    >
      <ListHeader
        class="sm:mx-5 mx-3"
        @columnWidthUpdated="emit('columnWidthUpdated')"
      >
        <ListHeaderItem
          v-for="column in columns"
          :key="column.key"
          :item="column"
          @columnWidthUpdated="emit('columnWidthUpdated', column)"
        >
          <Button
            v-if="column.key == '_liked_by'"
            variant="ghosted"
            class="!h-4"
            :class="isLikeFilterApplied ? 'fill-red-500' : 'fill-white'"
            @click="() => emit('applyLikeFilter')"
          >
            <HeartIcon class="h-4 w-4" />
          </Button>
        </ListHeaderItem>
      </ListHeader>
      <ListRows
        :rows="rows"
        v-slot="{ idx, column, item, row }"
        doctype="Design"
      >
        <div v-if="column.key === '_assign'" class="flex items-center">
          <MultipleAvatar
            :avatars="item"
            size="sm"
            @click="
              (event) =>
                emit('applyFilter', {
                  event,
                  idx,
                  column,
                  item,
                  firstColumn: columns[0],
                })
            "
          />
        </div>
        <ListRowItem v-else :item="item" :align="column.align">
          <template #prefix>
            <div v-if="column.key === 'status'">
              <IndicatorIcon :class="item.color" />
            </div>

          </template>
          <template #default="{ label }">
            <div
              v-if="
                [
                  'modified',
                  'creation',
                  'first_response_time',
                  'first_responded_on',
                  'response_by',
                ].includes(column.key)
              "
              class="truncate text-base"
              @click="
                (event) =>
                  emit('applyFilter', {
                    event,
                    idx,
                    column,
                    item,
                    firstColumn: columns[0],
                  })
              "
            >
              <Tooltip :text="item.label">
                <div>{{ item.timeAgo }}</div>
              </Tooltip>
            </div>
            <div v-else-if="column.key === '_liked_by'">
              <Button
                v-if="column.key == '_liked_by'"
                variant="ghosted"
                :class="isLiked(item) ? 'fill-red-500' : 'fill-white'"
                @click.stop.prevent="
                  () =>
                    emit('likeDoc', {
                      name: row.name,
                      liked: isLiked(item),
                    })
                "
              >
                <HeartIcon class="h-4 w-4" />
              </Button>
            </div>
            
            <div v-else-if="column.type === 'Check'">
              <FormControl
                type="checkbox"
                :modelValue="item"
                :disabled="true"
                class="text-ink-gray-9"
              />
            </div>
            <div
              v-else
              class="truncate text-base"
              @click="
                (event) =>
                  emit('applyFilter', {
                    event,
                    idx,
                    column,
                    item,
                    firstColumn: columns[0],
                  })
              "
            >
              {{ label }}
            </div>
          </template>
        </ListRowItem>
      </ListRows>
      <ListSelectBanner>
        <template #actions="{ selections, unselectAll }">
          <Dropdown
            :options="filteredActions(selections, unselectAll)"
          >
            <Button icon="more-horizontal" variant="ghost" />
          </Dropdown>
        </template>
      </ListSelectBanner>
    </ListView>
    <ListFooter
      v-if="pageLengthCount"
      class="border-t sm:px-5 px-3 py-2"
      v-model="pageLengthCount"
      :options="{
        rowCount: options.rowCount,
        totalCount: options.totalCount,
      }"
      @loadMore="emit('loadMore')"
    />
    <ListBulkActions ref="listBulkActionsRef" v-model="list" doctype="Design" />
  </template>
  
  <script setup>
  import HeartIcon from '@/components/Icons/HeartIcon.vue'
  import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
  import MultipleAvatar from '@/components/MultipleAvatar.vue'
  import ListBulkActions from '@/components/ListBulkActions.vue'
  import ListRows from '@/components/ListViews/ListRows.vue'
  import {
    ListView,
    ListHeader,
    ListHeaderItem,
    ListSelectBanner,
    ListRowItem,
    ListFooter,
    Dropdown,
    Tooltip,
    createResource,
    toast
  } from 'frappe-ui'
  import { sessionStore } from '@/stores/session'
  import { ref, computed, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import { capture } from '@/telemetry'
  
  const props = defineProps({
    rows: {
      type: Array,
      required: true,
    },
    columns: {
      type: Array,
      required: true,
    },
    options: {
      type: Object,
      default: () => ({
        selectable: true,
        showTooltip: true,
        resizeColumn: false,
        totalCount: 0,
        rowCount: 0,
      }),
    },
  })
  
  const emit = defineEmits([
    'loadMore',
    'updatePageCount',
    'columnWidthUpdated',
    'applyFilter',
    'applyLikeFilter',
    'likeDoc',
    'selectionsChanged',
  ])
  
  const route = useRoute()
  
  const pageLengthCount = defineModel()
  const list = defineModel('list')
  
  const isLikeFilterApplied = computed(() => {
    return list.value.params?.filters?._liked_by ? true : false
  })
  
  const { user } = sessionStore()
  
  function isLiked(item) {
    if (item) {
      let likedByMe = JSON.parse(item)
      return likedByMe.includes(user)
    }
  }
  
  watch(pageLengthCount, (val, old_value) => {
    if (val === old_value) return
    emit('updatePageCount', val)
  })
  
  const listBulkActionsRef = ref(null)
  
  defineExpose({
    customListActions: computed(
      () => listBulkActionsRef.value?.customListActions,
    ),
  })

  //custom script

  const hideDelete = ref(true)
const handleDelete = (selections, unselectAll) => {
  createResource({
    url: 'crm.apiCpq.design.delete_items',
    params:{
      items: JSON.stringify(Array.from(selections)),
      doctype: 'Design',
    },
    onSuccess(data){
      if(data.status == 'success'){
        capture('bulk_delete')
        toast.success(__('Deleted successfully'))
        unselectAll()
        list.value.reload()
      }
      else if(data.status == 'error'){
        toast.error(__('Unable to Deleted'))
        list.value.reload()
      }
    },
    onError(data){
      toast.error(__('Unable to Delete'))
    }
  }).submit();
}
// Filtered actions with an additional custom "Delete" action
const filteredActions = (selections, unselectAll) => {
  const actions = listBulkActionsRef.value?.bulkActions(selections, unselectAll) || []
  // Filter out the original "Delete" action based on hideDelete
  const filtered = actions.filter(action => !(action.label === 'Delete' && hideDelete.value))
  // Add a new "Delete" action with a custom onClick handler
  filtered.push({
    label: __('Delete'),
    onClick: () => handleDelete(selections, unselectAll),
  })
  return filtered
}
  </script>
  