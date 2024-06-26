<template>
  <div class="flex flex-col gap-4">
    <div
      v-for="section in sections"
      :key="section.section"
      class="first:border-t-0 first:pt-0"
      :class="section.hideBorder ? '' : 'border-t pt-4'"
    >
      <div
        class="grid gap-4"
        :class="
          section.columns ? 'grid-cols-' + section.columns : 'grid-cols-3'
        "
      >
        <div v-for="field in section.fields" :key="field.name">
          <div class="mb-2 text-sm text-gray-600">
            {{ __(field.label) }}
            <span class="text-red-500" v-if="field.mandatory">*</span>
          </div>
          <FormControl
            v-if="field.type === 'select'"
            type="select"
            class="form-control"
            :class="field.prefix ? 'prefix' : ''"
            :options="field.options"
            v-model="data[field.name]"
            :placeholder="__(field.placeholder)"
          >
            <template v-if="field.prefix" #prefix>
              <IndicatorIcon :class="field.prefix" />
            </template>
          </FormControl>
          <Link
            v-else-if="field.type === 'link'"
            class="form-control"
            :value="data[field.name]"
            :doctype="field.doctype"
            @change="(v) => (data[field.name] = v)"
            :placeholder="__(field.placeholder)"
            :onCreate="field.create"
          />
          <Link
            v-else-if="field.type === 'user'"
            class="form-control"
            :value="getUser(data[field.name]).full_name"
            :doctype="field.doctype"
            @change="(v) => (data[field.name] = v)"
            :placeholder="__(field.placeholder)"
            :hideMe="true"
          >
            <template #prefix>
              <UserAvatar class="mr-2" :user="data[field.name]" size="sm" />
            </template>
            <template #item-prefix="{ option }">
              <UserAvatar class="mr-2" :user="option.value" size="sm" />
            </template>
            <template #item-label="{ option }">
              <Tooltip :text="option.value">
                <div class="cursor-pointer">
                  {{ getUser(option.value).full_name }}
                </div>
              </Tooltip>
            </template>
          </Link>
          <div v-else-if="field.type === 'range'">
            <input
                type="range"
                :class="field.name"
                :min="field.min"
                :max="field.max"
                :step="field.step"
                style="width:250px;  accent-color: black;"
                variant="ghost"
                value="0"
                @input="handleChangeRange(field.id,$event.target.value)"
              />
              <p :id=field.id class="text-gray-600" contenteditable="true" @input="updateRangeValue(field.name, $event.target.innerText)">0</p>
          
          </div>
          <div v-else-if="field.type === 'dropdown'">
            <NestedPopover>
              <template #target="{ open }">
                <Button
                  :label="data[field.name]"
                  class="dropdown-button flex w-full items-center justify-between rounded border border-gray-100 bg-gray-100 px-2 py-1.5 text-base text-gray-800 placeholder-gray-500 transition-colors hover:border-gray-200 hover:bg-gray-200 focus:border-gray-500 focus:bg-white focus:shadow-sm focus:outline-none focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400"
                >
                  <div class="truncate">{{ data[field.name] }}</div>
                  <template #suffix>
                    <FeatherIcon
                      :name="open ? 'chevron-up' : 'chevron-down'"
                      class="h-4 text-gray-600"
                    />
                  </template>
                </Button>
              </template>
              <template #body>
                <div
                  class="my-2 space-y-1.5 divide-y rounded-lg border border-gray-100 bg-white p-1.5 shadow-xl"
                >
                  <div>
                    <DropdownItem
                      v-if="field.options?.length"
                      v-for="option in field.options"
                      :key="option.name"
                      :option="option"
                    />
                    <div v-else>
                      <div class="p-1.5 px-7 text-base text-gray-500">
                        {{ __('No {0} Available', [field.label]) }}
                      </div>
                    </div>
                  </div>
                  <div class="pt-1.5">
                    <Button
                      variant="ghost"
                      class="w-full !justify-start"
                      :label="__('Create New')"
                      @click="field.create()"
                    >
                      <template #prefix>
                        <FeatherIcon name="plus" class="h-4" />
                      </template>
                    </Button>
                  </div>
                </div>
              </template>
            </NestedPopover>
          </div>
          <FormControl
            v-else
            type="text"
            :placeholder="__(field.placeholder)"
            v-model="data[field.name]"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import NestedPopover from '@/components/NestedPopover.vue'
import DropdownItem from '@/components/DropdownItem.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import { usersStore } from '@/stores/users'
import { Tooltip } from 'frappe-ui'

const { getUser } = usersStore()

const props = defineProps({
  sections: Array,
  data: Object,
})

const handleChangeRange = (id,value) => {
   // Update the value displayed in the div with ID 'size'
  const sizeElement = document.getElementById(id);
  if (sizeElement) {
    sizeElement.innerHTML = value;
  }
};
const updateRangeValue=(id, value) => {
  const rangeElement = document.getElementsByClassName(id)
  if (rangeElement.length > 0) {
    // Assuming there's only one range input with this class
    rangeElement[0].value = value;
  }
}

</script>

<style scoped>
:deep(.form-control.prefix select) {
  padding-left: 2rem;
}
p[contenteditable="true"]:focus {
    outline: none;
  }
 
</style>
