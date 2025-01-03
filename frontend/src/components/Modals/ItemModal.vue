<template>
  <Dialog v-model="show" :options="{ size: '4xl' }">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-gray-900">
              {{ __('Create Design Template') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button variant="ghost" class="w-7" @click="show = false">
              <FeatherIcon name="x" class="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div>
          <CpqFields v-if="sections.data" :sections="sections.data" :data="item" />
          <hr class="my-4" />

          <!-- Start of the variant section -->
          <div class="flex items-center justify-between">
            <div class="p-2 w-2/3">
              <FormControl type="autocomplete" :options="attributeOptions" size="sm" variant="subtle"
                placeholder="Select the variant" label="Select the variant and Add to include in the Design Template."
                v-model="selectedAttribute" />
            </div>
          </div>
          <div class="mt-5">
            <ListView v-if="rows.length" class="h-[300px]" :columns="columns" :rows="rows" :options="{
              selectable: true,
              showTooltip: true,
              resizeColumn: true,
            }" row-key="name">
              <ListHeader>
                <ListHeaderItem v-for="column in columns" :key="column.key" :item="column">
                </ListHeaderItem>
              </ListHeader>
              <ListGroups>
                <template #group-header="{ group }">
                  <button @click="fnToggleGroup(group.group)">
                    <span class="text-base font-medium leading-6 text-ink-gray-9">
                      {{ group.group }} ({{ group.rows.length }})
                    </span>
                  </button>
                </template>
              </ListGroups>
              <ListSelectBanner>
                <template #actions="{ selections, unselectAll }">
                  <Button variant="ghost" label="Delete" @click="handleDelete(selections)" />
                </template>
              </ListSelectBanner>
            </ListView>

          </div>
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button variant="solid" :label="__('Create')" :loading="isItemCreating" @click="createNewItem" />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import CpqFields from '@/components/CpqFields.vue'
import { capture } from '@/telemetry'
import { createResource, ListView, ListSelectBanner, ListGroups, ListHeaderItem, ListHeader } from 'frappe-ui'
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  defaults: Object,
})

const show = defineModel()
const router = useRouter()
const error = ref(null)
const isItemCreating = ref(false)
const selectedAttribute = ref('')
const selectedAttributes = ref([])
const collapsedState = reactive({});

const columns = computed(() => {
  return [
    {
      label: 'Name',
      key: 'name',
    },
    {
      label: 'Type',
      key: 'type',
      width: '100px'
    },
    {
      label: 'Increment',
      key: 'increment',
      width: '100px'
    },
    {
      label: 'From Range',
      key: 'from_range',
      width: '100px'
    },
    {
      label: 'To Range',
      key: 'to_range',
      width: '100px'
    },
    {
      label: 'options',
      key: 'item_attribute_values',
    },
  ];
});


const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['quickEntryFields', 'Item'],
  params: { doctype: 'Item', type: 'Quick Entry' },
  auto: true,
});

//get all the item attribute records
const attributeList = createResource({
  url: 'crm.api.docCpq.get_item_attribute_record',
  auto: true
})

//convert the attributeList's response to options
//for the autocomplete(formcontrol)
const attributeOptions = computed(() => {
  return attributeList.data?.map(attribute => ({
    label: attribute.name,
    value: attribute.name,
  })) || []
})

const item = reactive({
  item_code: '',
  item_name: '',
  item_group: '',
  stock_uom: '',
  attributes: [],
})

const createItem = createResource({
  url: 'frappe.client.insert',
  makeParams(values) {
    return {
      doc: {
        doctype: 'Item',
        has_variants: 1,
        ...values,
      },
    }
  },
})

function createNewItem() {

  createItem.submit(item, {
    validate() {
      error.value = null
      if (!item.item_code) {
        error.value = __('Item Code is mandatory')
        return error.value
      }
      if (!item.item_group) {
        error.value = __('Item Group is mandatory')
      }
      isItemCreating.value = true
    },
    onSuccess(data) {
      capture('item_created')
      isItemCreating.value = false
      show.value = false
      router.push({ name: 'Item', params: { itemId: data.name } })
    },
    onError(err) {
      isItemCreating.value = false
      if (!err.messages) {
        error.value = err.message
        return
      }
      error.value = err.messages.join('\n')
    },
  })
}

//rows where structured situable for grouped rows
//based on frappe-ui ListView docs
const rows = computed(() => {
  return selectedAttributes.value.reduce((acc, attribute) => {
    const group = attribute.custom_parent_of || 'Default Group';
    const row = {
      name: attribute.name,
      type: attribute.numeric_values === 1 ? 'Numeric' : 'Options',
      increment: attribute.numeric_values === 1 ? attribute.increment : null,
      from_range: attribute.numeric_values === 1 ? attribute.from_range : null,
      to_range: attribute.numeric_values === 1 ? attribute.to_range : null,
      item_attribute_values: attribute.numeric_values !== 1
        ? attribute.item_attribute_values.join(', ')
        : null,
      group,
    };

    // Initialize collapsedState if not already set
    if (!(group in collapsedState)) {
      collapsedState[group] = false;
    }

    const existingGroup = acc.find(g => g.group === group);
    if (existingGroup) {
      existingGroup.rows.push(row);
    } else {
      acc.push({
        group,
        collapsed: collapsedState[group],
        rows: [row],
      });
    }
    return acc;
  }, []);
});


watch(
  selectedAttribute,
  (newValue) => {
    if (newValue) {
      // Make sure attributeList.data is available and contains data
      if (attributeList.data && Array.isArray(attributeList.data)) {
        const selectedAttributeValue = selectedAttribute.value?.value || selectedAttribute.value;
        const selectedAttributeData = attributeList.data.find(attribute => attribute.name === selectedAttributeValue);

        if (selectedAttributeData) {
          // Reset selected attribute after use
          selectedAttribute.value = '';

          selectedAttributes.value.push(selectedAttributeData);
          item.attributes.push({
            attribute: selectedAttributeData.name,
          });
        } else {
          console.log('Attribute not found');
        }
      } else {
        console.log('No attributes available');
      }
    }
  }
);
const handleDelete = (selections) => {
  if (selections.size > 0) {
    const selectedNames = [...selections];

    selectedNames.forEach(name => {
      const index = selectedAttributes.value.findIndex(attribute => attribute.name === name);

      if (index !== -1) {
        selectedAttributes.value.splice(index, 1);

        const itemIndex = item.attributes.findIndex(attr => attr.attribute === name);
        if (itemIndex !== -1) {
          item.attributes.splice(itemIndex, 1);
        }
      }
    });

    selections.clear();
  } else {
    console.log('No items selected for deletion');
  }
};

function fnToggleGroup(groupName) {
  if (groupName in collapsedState) {
    collapsedState[groupName] = !collapsedState[groupName];
  }
}
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