<template>
    <Dialog v-model="show" :options="{ size: '3xl' }">
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
              <FormControl
                type="autocomplete"
                :options="attributeOptions"
                size="sm"
                variant="subtle"
                placeholder="Select the variant"
                label="Select the variant and Add to include in the Design Template."
                v-model="selectedAttribute"
              />
            </div>
              <!-- <Button
                variant="solid"
                :label="__('Add')"
                @click="selectAttribute"
              ></Button> -->
            </div>
            <div class="mt-5">
            <!-- Start of the Variant card Dispay -->
            <!-- <div class="grid grid-cols-2 gap-4">
              <div
                v-for="(attribute, index) in selectedAttributes"
                :key="index"
                class="mb-4 p-4 border rounded-md shadow-sm"
              >
                <div class="flex justify-between items-center">
                  <h1 class="text-lg">{{ attribute.name }}</h1>
                 
                  <button
                    class="text-red-500 hover:text-red-700"
                    @click="deleteAttribute(index)"
                  >
                    <FeatherIcon name="trash" class="h-5 w-5" />
                  </button>
                </div>
               
                <div v-if="attribute.numeric_values === 1" class="mt-4">
                  <div class="flex gap-4">
                    <div class="flex-1">
                     
                      <p class="text-sm text-red-500 rounded-md bg-gray-100 w-fit px-2 py-1">
                        {{ __('Numeric') }}
                      </p>
                    </div>
                    <div class="flex-1">
                      <p class="text-sm text-gray-700">
                        {{ __('Increment:') }} {{ attribute.increment }}
                      </p>
                    </div>
                  </div>
                  <div class="flex gap-4 mt-2">
                    <div class="flex-1">
                      <p class="text-sm text-gray-700">
                        {{ __('From Range :') }} {{ attribute.from_range }}
                      </p>
                    </div>
                    <div class="flex-1">
                      <p class="text-sm text-gray-700">
                        {{ __('To Range:') }} {{ attribute.to_range }}
                      </p>
                    </div>
                  </div>
                </div>
                <div v-else class="mt-4">
                  <p class="text-sm text-green-800 bg-gray-50 w-fit px-2 py-1 rounded-md">
                    {{ __('Options') }}
                  </p>
                  <p>
                    <span v-for="(value, index) in attribute.item_attribute_values" :key="index" class="text-sm text-gray-700">
                      {{ value }}<span v-if="index < attribute.item_attribute_values.length - 1">, </span>
                    </span>
                  </p>
                </div>
              </div>
            </div> -->

            <ListView
              v-if="rows.length"
              class="h-[300px]"
              :columns="columns"
              :rows="rows"
              :options="{
                selectable: true,
                showTooltip: true,
                resizeColumn: true,
              }"
              row-key="name"
            >
            <!-- Loop over groups within rows -->
              <ListHeader>
                <ListHeaderItem 
                v-for="column in columns"
                  :key="column.key"
                  :item="column"
                >
              </ListHeaderItem>
              </ListHeader>
              <ListGroups>
                  <template #group-header="{ group }">
                    <span class="text-base font-medium leading-6 text-ink-gray-9">
                      {{ group.group }} ({{ group.rows.length }})
                    </span>
                  </template>
              </ListGroups>

              <!-- Select Banner for actions -->
              <ListSelectBanner>
                <template #actions="{ selections, unselectAll }">
                  <Button
                    variant="ghost"
                    label="Delete"
                    @click="handleDelete(selections)"
                  />
                </template>
              </ListSelectBanner>

            </ListView>

          </div>
            <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
            
          </div>
          </div>
        <div class="px-4 pb-7 pt-4 sm:px-6">
          <div class="flex flex-row-reverse gap-2">
            <Button
              variant="solid"
              :label="__('Create')"
              :loading="isItemCreating"
              @click="createNewItem"
            />
          </div>
        </div>
      </template>
    </Dialog>
  </template>
  
  <script setup>
  import CpqFields from '@/components/CpqFields.vue'
  import { capture } from '@/telemetry'
  import { createResource, ListView, ListSelectBanner, ListGroups, ListHeaderItem, ListHeader} from 'frappe-ui'
  import { ref, reactive, computed, watch} from 'vue'
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

 

// Define columns dynamically based on `selectedAttributes`
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

  //getting the item attribute list
  const attributeList = createResource({
    url: 'crm.api.docCpq.get_item_attribute_record',
    auto: true
  })

// Generate options from attributeList
const attributeOptions = computed(() => {
  return attributeList.data?.map(attribute => ({
    label: attribute.name,
    value: attribute.name,
  })) || []
})

// function selectAttribute() {
//   // Make sure attributeList.data is available and contains data
//   if (attributeList.data && Array.isArray(attributeList.data)) {
//     const selectedAttributeValue = selectedAttribute.value?.value || selectedAttribute.value;
//     const selectedAttributeData = attributeList.data.find(attribute => attribute.name === selectedAttributeValue);

//     if (selectedAttributeData) {
//       // Reset selected attribute after use
//       selectedAttribute.value = '';
//       console.log(selectedAttributeData)
//       selectedAttributes.value.push(selectedAttributeData);
//       item.attributes.push({
//         attribute: selectedAttributeData.name,
//       });
//     } else {
//       console.log('Attribute not found');
//     }
//   } else {
//     console.log('No attributes available');
//   }
// }

function deleteAttribute(index) {
  selectedAttributes.value.splice(index, 1)
  item.attributes.splice(index, 1);
}

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
        if (!item.item_group){
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
  
//   watch(selectedAttribute, (newValue) => {
//   if (newValue) {
//     // Make sure attributeList.data is available and contains data
//   if (attributeList.data && Array.isArray(attributeList.data)) {
//     const selectedAttributeValue = selectedAttribute.value?.value || selectedAttribute.value;
//     const selectedAttributeData = attributeList.data.find(attribute => attribute.name === selectedAttributeValue);

//     if (selectedAttributeData) {
//       // Reset selected attribute after use
//       selectedAttribute.value = '';
//       console.log(selectedAttributeData)
//       selectedAttributes.value.push(selectedAttributeData);
//       item.attributes.push({
//         attribute: selectedAttributeData.name,
//       });
//     } else {
//       console.log('Attribute not found');
//     }
//   } else {
//     console.log('No attributes available');
//   }
//   }
// })

// Define computed `rows` based on `selectedAttributes`
const rows = computed(() => {
  return selectedAttributes.value.reduce((acc, attribute) => {
    // Create row for the attribute
    const row = {
      name: attribute.name,
      type: attribute.numeric_values === 1 ? 'Numeric' : 'Options',
      increment: attribute.numeric_values === 1 ? attribute.increment : null,
      from_range: attribute.numeric_values === 1 ? attribute.from_range : null,
      to_range: attribute.numeric_values === 1 ? attribute.to_range : null,
      item_attribute_values: attribute.numeric_values !== 1
        ? attribute.item_attribute_values.join(', ')
        : null,
      group: attribute.custom_parent_of || 'Default Group',
    };

    // Find the existing group or create a new one
    const existingGroup = acc.find(group => group.group === row.group);

    if (existingGroup) {
      existingGroup.rows.push(row);
    } else {
      acc.push({
        group: row.group,
        collapsed: false, 
        rows: [row],
      });
    }

    return acc;
  }, []);
});

// Handle attribute selection
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