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
          <CpqFields v-if="LD_SECTIONS.data" :sections="LD_SECTIONS.data" :data="LD_ITEM" />
          <hr class="my-4" />

          <!-- Start of the variant section -->
          <div class="flex items-center justify-between">
            <div class="p-2 w-2/3">
              <FormControl type="autocomplete" :options="LA_OPTIONS" size="sm" variant="subtle"
                placeholder="Select the variant" label="Select the variant and Add to include in the Design Template."
                v-model="L_SELECTED_ATTRIBUTE" />
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
                  <div class="flex items-center gap-4 ml-3">
                    <Button variant="solid" label="Delete" @click="fnHandleDelete(selections)" />
                    <template v-if="selections.size === 1">
                      <FormControl :type="'text'" size="sm" variant="subtle" v-model="L_DEFAULT_VALUE"
                        placeholder="Enter value" />

                      <Button variant="ghost" label="Set Default" :disabled="!L_DEFAULT_VALUE"
                        @click="fnMarkAsDefault(selections)" />

                      <Button variant="solid" label="Clear Default" @click="fnClearDefault(selections)"
                        :disabled="!fnHasDefaultValue(selections)" />
                    </template>
                  </div>
                </template>
              </ListSelectBanner>
            </ListView>

          </div>
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button variant="solid" :label="__('Create')" :loading="LB_IS_ITEM_CREATING" @click="createNewItem" />
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
const LB_IS_ITEM_CREATING = ref(false)
const L_SELECTED_ATTRIBUTE = ref('')
const LA_SELECTED_ATTRIBUTES = ref([])
const LD_COLLAPSE_STATE = reactive({});

const L_DEFAULT_VALUE = ref('')

//this varible was build in of Listview
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
    {
      label: 'Default',
      key: 'default_value',
    },
  ];
});


const LD_SECTIONS = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['quickEntryFields', 'Item'],
  params: { doctype: 'Item', type: 'Quick Entry' },
  auto: true,
});

//get all the item attribute records
const LD_ATTRIBUTE_NAME_LIST = createResource({
  url: 'crm.api.docCpq.fn_get_item_attribute_record',
  auto: true
})

//convert the LD_ATTRIBUTE_NAME_LIST's response to options
//for the autocomplete(formcontrol)
const LA_OPTIONS = computed(() => {
  return LD_ATTRIBUTE_NAME_LIST.data?.map(ldAttribute => ({
    label: ldAttribute.name,
    value: ldAttribute.name,
  })) || []
})

const LD_ITEM = reactive({
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

  createItem.submit(LD_ITEM, {
    validate() {
      error.value = null
      if (!LD_ITEM.item_code) {
        error.value = __('Item Code is mandatory')
        return error.value
      }
      if (!LD_ITEM.item_group) {
        error.value = __('Item Group is mandatory')
      }
      LB_IS_ITEM_CREATING.value = true
    },
    onSuccess(data) {
      capture('item_created')
      LB_IS_ITEM_CREATING.value = false
      show.value = false
      router.push({ name: 'Item', params: { itemId: data.name } })
    },
    onError(err) {
      LB_IS_ITEM_CREATING.value = false
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
  return LA_SELECTED_ATTRIBUTES.value.reduce((acc, idAttribute) => {
    //group and acc are the reserved word 
    const group = idAttribute.custom_parent_of || 'Default Group';
    const row = {
      name: idAttribute.name,
      type: idAttribute.numeric_values === 1 ? 'Numeric' : 'Options',
      increment: idAttribute.numeric_values === 1 ? idAttribute.increment : null,
      from_range: idAttribute.numeric_values === 1 ? idAttribute.from_range : null,
      to_range: idAttribute.numeric_values === 1 ? idAttribute.to_range : null,
      item_attribute_values: idAttribute.numeric_values !== 1
        ? idAttribute.item_attribute_values.join(', ')
        : null,
      default_value: idAttribute.default_value || null,
      group,
    };

    // Initialize collapsedState if not already set
    if (!(group in LD_COLLAPSE_STATE)) {
      LD_COLLAPSE_STATE[group] = false;
    }

    const LA_EXISTING_GROUP = acc.find(ldGroup => ldGroup.group === group);
    if (LA_EXISTING_GROUP) {
      LA_EXISTING_GROUP.rows.push(row);
    } else {
      acc.push({
        group,
        collapsed: LD_COLLAPSE_STATE[group],
        rows: [row],
      });
    }
    return acc;
  }, []);
});


watch(
  L_SELECTED_ATTRIBUTE,
  (iNewValue) => {
    if (iNewValue) {
      // Make sure LD_ATTRIBUTE_NAME_LIST.data is available and contains data
      if (LD_ATTRIBUTE_NAME_LIST.data && Array.isArray(LD_ATTRIBUTE_NAME_LIST.data)) {
        const L_SELECTED_ATTRIBUTE_VALUE = L_SELECTED_ATTRIBUTE.value?.value || L_SELECTED_ATTRIBUTE.value;
        const LD_SELECTED_ATTRIBUTE_DATA = LD_ATTRIBUTE_NAME_LIST.data.find(attribute => attribute.name === L_SELECTED_ATTRIBUTE_VALUE);

        if (LD_SELECTED_ATTRIBUTE_DATA) {
          // Reset selected attribute after use
          L_SELECTED_ATTRIBUTE.value = '';
          LA_SELECTED_ATTRIBUTES.value.push(LD_SELECTED_ATTRIBUTE_DATA);
          LD_ITEM.attributes.push({
            attribute: LD_SELECTED_ATTRIBUTE_DATA.attribute_name,
            from_range: LD_SELECTED_ATTRIBUTE_DATA.from_range,
            to_range: LD_SELECTED_ATTRIBUTE_DATA.to_range,
            increment: LD_SELECTED_ATTRIBUTE_DATA.increment,
            numeric_values: LD_SELECTED_ATTRIBUTE_DATA.numeric_values
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

function fnHandleDelete(iaSelections) {
  if (iaSelections.size > 0) {
    const LA_SELECTIONS = [...iaSelections];

    LA_SELECTIONS.forEach(name => {
      const L_INDEX = LA_SELECTED_ATTRIBUTES.value.findIndex(ldAttribute => ldAttribute.name === name);

      if (L_INDEX !== -1) {
        LA_SELECTED_ATTRIBUTES.value.splice(L_INDEX, 1);

        const L_ITEM_INDEX = LD_ITEM.attributes.findIndex(ldAttribute => ldAttribute.attribute === name);
        if (L_ITEM_INDEX !== -1) {
          LD_ITEM.attributes.splice(L_ITEM_INDEX, 1);
        }
      }
    });

    iaSelections.clear();
  } else {
    console.log('No items selected for deletion');
  }
};

function fnToggleGroup(iGroupName) {
  if (iGroupName in LD_COLLAPSE_STATE) {
    LD_COLLAPSE_STATE[iGroupName] = !LD_COLLAPSE_STATE[iGroupName];
  }
}

function fnMarkAsDefault(iaSelections) {
  const LA_SELECTIONS = [...iaSelections];
  if (iaSelections.size == 1) {
    const L_ROW_INDEX = LA_SELECTED_ATTRIBUTES.value.findIndex(ldRow => ldRow.name === LA_SELECTIONS[0])
    if (L_ROW_INDEX !== -1) {
      LA_SELECTED_ATTRIBUTES.value[L_ROW_INDEX].default_value = L_DEFAULT_VALUE.value
      LD_ITEM.attributes[L_ROW_INDEX].attribute_value = L_DEFAULT_VALUE.value
      L_DEFAULT_VALUE.value = ''
    }
  } else {
    L_DEFAULT_VALUE.value = ''
  }
}

function fnHasDefaultValue(iaSelections) {
  const LA_SELECTIONS = [...iaSelections];
  if (iaSelections.size == 1) {
    const L_ROW_INDEX = LA_SELECTED_ATTRIBUTES.value.findIndex(ldRow => ldRow.name === LA_SELECTIONS[0]);
    return !(LA_SELECTED_ATTRIBUTES.value[L_ROW_INDEX].default_value === undefined || LA_SELECTED_ATTRIBUTES.value[L_ROW_INDEX].default_value === null);
  }
  return false

}

function fnClearDefault(iaSelections) {
  const LA_SELECTIONS = [...iaSelections];
  if (LA_SELECTIONS.length === 1) {
    const L_ROW_INDEX = LA_SELECTED_ATTRIBUTES.value.findIndex(ldRow => ldRow.name === LA_SELECTIONS[0]);
    if (L_ROW_INDEX !== -1) {
      LA_SELECTED_ATTRIBUTES.value[L_ROW_INDEX].default_value = null;
      LD_ITEM.attributes[L_ROW_INDEX].custom_default_value = null;
    }
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