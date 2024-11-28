<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-gray-900">
              {{ __('Create Quotation') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager()"
              variant="ghost"
              class="w-7"
              @click="openQuickEntryModal"
            >
              <EditIcon class="h-4 w-4" />
            </Button>
            <Button variant="ghost" class="w-7" @click="show = false">
              <FeatherIcon name="x" class="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div>
          <CpqFields v-if="sections.data" :sections="sections.data" :data="quotation" />

          <!-- Items Table -->
          <div class="mt-6 border-t">
            <h4 class="text-lg font-semibold my-4">{{ __('Items') }}</h4>
            <div class="overflow-x-auto">
              <table class="min-w-full table-fixed"  style="border-spacing: 10px; border-collapse: collapse;">
                <thead class="bg-gray-100 rounded-lg text-gray-600">
                  <tr>
                    <th class="px-6 py-1 w-10 text-center">
                    
                      <input
                        type="checkbox"
                       class="rounded-sm border-gray-500 text-gray-900 hover:border-gray-600 focus:ring-offset-0 focus:border-gray-900 active:border-gray-700 transition w-3.5 h-3.5 hover:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 active:bg-gray-100"
                       :checked="areAllRowsSelected"
                       @click="selectAllRows($event.target.checked)"
                      /> 
                     
                    </th>
                    <th class="py-1 w-1/3 text-sm">{{ __('Item Code') }}</th>
                    <th class="py-1 w-1/6 text-sm">{{ __('Quantity') }}</th>
                    <th class="py-1 w-1/6 text-sm">{{ __('Rate') }}</th>
                    <th class="py-1 w-1/6 text-sm">{{ __('Total') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(item, index) in quotation.items"
                    :key="index"
                    class="border-t py-2"
                     :draggable="true"
                      @dragstart="onDragStart($event, index)"
                      @dragover="onDragOver($event)"
                      @drop="onDrop($event, index)"
                  >
                    <td class="text-center">
                      
                      <input
                        type="checkbox"
                        class="rounded-sm border-gray-500 text-gray-900 hover:border-gray-600 focus:ring-offset-0 focus:border-gray-900 active:border-gray-700 transition w-3.5 h-3.5 hover:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 active:bg-gray-100"
                        v-model="selectedRows"
                        :value="index"
                      /> 
                     
                    </td>
                    <td>
                      <Link
                        class="form-control"
                        variant="outline"
                        :value="item.item_code"
                        doctype="Item"
                        :filters="{ has_variants: 0 }"
                        @change="(value) => onItemCodeChange(value, item)"
                        placeholder="Select an item"
                      />
                    </td>
                    <td>
                      <FormControl
                        class="form-control"
                        variant="outline"
                        type="number"
                        v-model="item.qty"
                        placeholder="Quantity"
                      />
                    </td>
                    <td>
                      <FormControl
                        class="form-control"
                        variant="outline"
                        type="number"
                        v-model="item.rate"
                        placeholder="Rate"
                      />
                    </td>
                    <td>
                      {{ (item.qty * item.rate).toFixed(2) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          

            <!-- Add/Delete Rows -->
            <div class="flex justify-between items-center mt-4">
              <Button variant="outline" @click="addItem">
                {{ __('Add') }}
              </Button>
              <Button
                variant="outline"
                class="text-red-500 border border-red-500 bg-white"
                @click="deleteSelectedRows"
                :disabled="selectedRows.length === 0"
              >
                {{ __('Delete') }}
              </Button>
            </div>
          </div>
          
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isQuotationCreating"
            @click="createNewQuotation"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import CpqFields from '@/components/CpqFields.vue'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { capture } from '@/telemetry'
import { createResource,} from 'frappe-ui'
import { computed, onMounted, ref, reactive, nextTick , watch} from 'vue'
import { useRouter } from 'vue-router'
import Link from '@/components/Controls/Link.vue'

const props = defineProps({
  defaults: Object,
})

const { getUser, isManager } = usersStore()
const { getQuotationStatus, statusOptions } = statusesStore()

const show = defineModel()
const router = useRouter()
const error = ref(null)
const isQuotationCreating = ref(false)

//for item's table
const selectedRows = ref([])

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['quickEntryFields', 'Quotation'],
  params: { doctype: 'Quotation', type: 'Quick Entry' },
  auto: true,
  transform: (data) => {
   
    if (data && Array.isArray(data)) {
      data.forEach((section) => {
      
        if (section.fields && Array.isArray(section.fields)) {
          section.fields.forEach((field) => {
          
            if (field.name === 'party_name') {
              field.label = 'Customer';
              field.type = 'Link';
              field.options = 'Customer';
              field.mandatory = 1;
            }
          });
        }
      });
    }
    return data; 
  },
});

const quotation = reactive({
  quotation_to: 'Customer',
  party_name: '',
  transaction_date: '',
  valid_till: '',
  status: 'Draft',
  currency: '',
  selling_price_list: 'Standard Selling',
  items: [
    {
      item_code: '',
      qty: 1,
      rate: 0,
    },
  ],
})

const createQuotation = createResource({
  url: 'frappe.client.insert',
  makeParams(values) {
    return {
      doc: {
        doctype: 'Quotation',
        ...values,
      },
    }
  },
})

function createNewQuotation() {
 
  createQuotation.submit(quotation, {
    validate() {
      error.value = null
      if (!quotation.party_name) {
        error.value = __('Customer Name is mandatory')
        return error.value
      }
      isQuotationCreating.value = true
    },
    onSuccess(data) {
      capture('quotation_created')
      isQuotationCreating.value = false
      show.value = false
      router.push({ name: 'Quotation', params: { quotationId: data.name } })
    },
    onError(err) {
      isQuotationCreating.value = false
      if (!err.messages) {
        error.value = err.message
        return
      }
      error.value = err.messages.join('\n')
    },
  })
}

const showQuickEntryModal = defineModel('quickEntry')

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  nextTick(() => {
    show.value = false
  })
}

function addItem() {
  quotation.items.push({
    item_code: '',
    qty: 1,
    rate: 0,
  })
}

function deleteSelectedRows() {
  // Keep only rows that are not selected
  quotation.items = quotation.items.filter((_, index) => !selectedRows.value.includes(index))
  // Clear selected rows
  selectedRows.value = []
}

function selectAllRows(selectAll) {
  if (selectAll) {
    selectedRows.value = quotation.items.map((_, index) => index)
  } else {
    selectedRows.value = []
  }
}

const areAllRowsSelected = computed(() => selectedRows.value.length === quotation.items.length)

//get rate for the select item

function fetchItemRate(item) {
  const getItemRate = createResource({
    url: 'frappe.client.get_value',
    makeParams() {
      return {
        doctype: 'Item Price',
        fieldname: 'price_list_rate',
        filters: {
          price_list: quotation.selling_price_list,
          item_code: item.item_code,
        },
      };
    },
    auto: true,
    onSuccess(data) {
      item.rate = data.price_list_rate || 0; 
    },
    onError(error) {
      console.error('Error fetching rate:', error.message);
    },
  });
}

function onItemCodeChange(value, item) {
  item.item_code = value;
  if (item.item_code) {
    fetchItemRate(item);
  }
}

// Watch for changes in selling_price_list and update all items
watch(
  () => quotation.selling_price_list,
  async () => {
    for (const item of quotation.items) {
      fetchItemRate(item);
    }
  }
);


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

    const draggedRow = quotation.items[draggedIndex];
    quotation.items.splice(draggedIndex, 1); // Remove the dragged row
    quotation.items.splice(droppedRowIndex, 0, draggedRow); // Insert the dragged row at the new position
};
</script>
<style scoped>
.form-control.link {
    border-color: transparent;
    background: white !important;
}
.form-control.int {
    border-color: transparent;
    background: white !important;
}
</style>