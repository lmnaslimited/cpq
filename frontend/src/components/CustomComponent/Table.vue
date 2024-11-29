<template>
  <div class="table-component">
    <h3 class="text-lg font-semibold mb-2">{{ label }}</h3>
    <table class="min-w-full table-fixed" style="border-spacing: 10px; border-collapse: collapse;">
      <thead class="bg-gray-100 rounded-lg text-gray-600 border">
        <tr>
          <th class="px-6 py-1 w-10 text-center">
            <input
              type="checkbox"
              class="rounded-sm border-gray-500 text-gray-900 hover:border-gray-600 focus:ring-offset-0 focus:border-gray-900 active:border-gray-700 transition w-3.5 h-3.5 hover:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 active:bg-gray-100"
              :checked="areAllRowsSelected"
              @click="selectAllRows($event.target.checked)"
            /> 
          </th>
          <th class="py-1 px-6 w-10 text-sm text-center">No</th>

          <th
            v-for="column in filteredColumns"
            :key="column.fieldname"
            class="py-1 w-1/4 text-sm"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, rowIndex) in localRows" 
          :key="row.idx" 
          class="border-t py-2"
          :draggable="true"
          @dragstart="onDragStart($event, rowIndex)"
          @dragover="onDragOver($event)"
          @drop="onDrop($event, rowIndex)"
        >
          <td class="text-center border border-gray-300 px-1 py-1">
            <input
              type="checkbox"
              class="rounded-sm border-gray-500 text-gray-900 hover:border-gray-600 focus:ring-offset-0 focus:border-gray-900 active:border-gray-700 transition w-3.5 h-3.5 hover:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 active:bg-gray-100"
              v-model="selectedRows"
              :value="row.idx"
            /> 
          </td>
          <td class="text-center border border-gray-300 text-sm text-gray-600 px-1 py-1">
            {{ row.idx }}
          </td>
          <td
            v-for="column in filteredColumns"
            :key="column.fieldname"
            class="border border-gray-300 px-2 py-1"
          >
            <Link
              v-if="column.fieldtype === 'Link' && column.read_only === 0 && column.hidden === 0"
              class="form-control"
              variant="outline"
              :value="row[column.fieldname]"
              :doctype="column.options"
              :filters="column.link_filters ? column.link_filters : {}"
              @change="(value) => onLinkFieldChange(value, row, column.fieldname)"
              @click="isVariantTabNeeded(row[column.fieldname])"
              :placeholder="column.fieldname"
            />
            <FormControl
              v-else-if="(column.fieldtype === 'Currency' || column.fieldtype === 'Float' || column.fieldtype === 'Int') && column.read_only === 0 && column.hidden === 0"
              class="form-control"
              variant="outline"
              type="number"
              v-model="row[column.fieldname]"
              @change="(event) => onFormFieldChange(event.target.value, row, column.fieldname)"
              :placeholder="column.fieldname"
            />
            <FormControl
              v-else-if="column.read_only === 0 && column.hidden === 0"
              class="form-control"
              variant="outline"
              type="text"
              v-model="row[column.fieldname]"
              :placeholder="column.fieldname"
            />
            <div v-if="column.read_only === 1">{{ row[column.fieldname] }}</div>
          </td>
        </tr>
      </tbody>

      <tfoot>
        <tr>
          <td colspan="100%" class="py-2">
            <button
              @click="addNewRow"
              class="border border-gray-500 text-black px-2 py-1 text-sm rounded-md"
            >
              Add Row
            </button>
             <button
              v-if="selectedRows.length > 0"
              @click="deleteSelectedRows"
              class="border border-red-500 text-red-500 px-2 py-1 text-sm rounded-md ml-4"
            >
              Delete
            </button>
            <button
              @click="updateRows"
              class="border border-blue-500 text-blue-500 px-2 py-1 text-sm rounded-md ml-4"
            >
              Update
            </button>
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<script setup>
import Link from '@/components/Controls/Link.vue'
import { computed, ref, reactive, watch } from 'vue'

const emit = defineEmits();

const props = defineProps({
  rows: {
    type: Array,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  label: {
    type: String,
    default: "Table",
  },
  filteredColumns: {
    type: Array,
    required: true,
  },
  isTabRequired: {
    type: Boolean,
    default: false
  }
});

// Create a local state for rows
const localRows = ref([...props.rows]);

// Watch for changes in props.rows and update localRows
watch(
  () => props.rows,
  (newRows) => {
    localRows.value = [...newRows];
  },
  { immediate: true }
);

// Track selected rows (Indexes of selected rows)
const selectedRows = ref([]);

// Compute whether all rows are selected
const areAllRowsSelected = computed(() => {
  return selectedRows.value.length === localRows.value.length;
});

// Method to add a new row
const addNewRow = () => {
  const newRow = reactive({});
  const newIndex = localRows.value.length + 1;
  props.filteredColumns.forEach((column) => {
    newRow[column.fieldname] = column.default || "";
  });

  newRow.idx = newIndex;
  localRows.value.push(newRow);
};

// Method to delete selected rows
const deleteSelectedRows = () => {
  // Filter out rows based on selected row indexes
  localRows.value = localRows.value.filter((row) => !selectedRows.value.includes(row.idx));
  selectedRows.value = [];
};

// Select or deselect all rows
const selectAllRows = (checked) => {
  if (checked) {
    // Select all row indexes
    selectedRows.value = localRows.value.map(row => row.idx);
  } else {
    // Deselect all rows
    selectedRows.value = [];
  }
};

const onLinkFieldChange = (value, row, fieldname) => {
  row[fieldname] = value;
  emit('item-changed', { value, fieldname, row });
};

const onFormFieldChange = (value, row, fieldname) => {
  emit('item-changed', { value, fieldname, row });
};

// Drag-and-drop methods
let draggedRowIndex = ref(null);

// Handle the start of a drag event
const onDragStart = (event, rowIndex) => {
  draggedRowIndex.value = rowIndex;
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", rowIndex);
};

// Handle the dragging over event (allow drop)
const onDragOver = (event) => {
  event.preventDefault(); // Allow drop
};

// Handle the drop event
const onDrop = (event, droppedRowIndex) => {
  event.preventDefault();
  const draggedIndex = draggedRowIndex.value;

  if (draggedIndex === droppedRowIndex) return; // No movement if the same row

  const draggedRow = localRows.value[draggedIndex];
  localRows.value.splice(draggedIndex, 1); // Remove the dragged row
  localRows.value.splice(droppedRowIndex, 0, draggedRow); // Insert the dragged row at the new position

  // Update idx values to reflect the new order
  updateIdxValues();
};

// Update idx values to reflect the current order
const updateIdxValues = () => {
  localRows.value.forEach((row, index) => {
    row.idx = index + 1; // Reassign idx starting from 1
  });
};

const updateRows = () => {
  const rawArray = JSON.parse(JSON.stringify(localRows.value));
  emit('update-rows', rawArray);
}

const isVariantTabNeeded = (itemCode) => {

  console.log("touched item", itemCode)
  console.log("Boolean", props.isTabRequired)
  if (props.isTabRequired) {
    emit('open-tab', itemCode);
  }
};

</script>

<style scoped>
.table-component {
  margin-bottom: 1.5rem;
}
</style>
