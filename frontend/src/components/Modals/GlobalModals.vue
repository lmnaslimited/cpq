<template>
   <!-- Show DesignModal ONLY when doctype is 'Design' customize for cpq demo -->
   <template v-if="createDocumentDoctype === 'Design'">
    <DesignModal
      v-model="showCreateDocumentModal"
      v-model:quickEntry="showQuickEntryModal"
      :defaults="defaults"
    />
  </template>
  <!-- commented for cpq demo <CreateDocumentModal
    v-if="showCreateDocumentModal"
    v-model="showCreateDocumentModal"
    :doctype="createDocumentDoctype"
    :data="createDocumentData"
    @showQuickEntryModal="(dt) => openQuickEntryModal(dt)"
    @callback="(data) => createDocumentCallback(data)"
  /> -->
   <!-- Otherwise show CreateDocumentModal customize for cpq demo-->
   <template v-else>
    <CreateDocumentModal
      v-model="showCreateDocumentModal"
      :doctype="createDocumentDoctype"
      :data="createDocumentData"
      @showQuickEntryModal="(dt) => openQuickEntryModal(dt)"
      @callback="(data) => createDocumentCallback(data)"
    />
  </template>
  <QuickEntryModal
    v-if="showQuickEntryModal"
    v-model="showQuickEntryModal"
    :doctype="quickEntryDoctype"
  />
  <AboutModal v-model="showAboutModal" />
</template>
<script setup>
import CreateDocumentModal from '@/components/Modals/CreateDocumentModal.vue'
import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
import AboutModal from '@/components/Modals/AboutModal.vue'
import {
  showCreateDocumentModal,
  createDocumentDoctype,
  createDocumentData,
  createDocumentCallback,
} from '@/composables/document'
import { showAboutModal } from '@/composables/settings'
import { ref, reactive } from 'vue'

//added for cpq demo
import DesignModal from '@/components/Modals/DesignModal.vue'
const defaults = reactive({})
//end

const showQuickEntryModal = ref(false)
const quickEntryDoctype = ref('')

function openQuickEntryModal(dt) {
  showQuickEntryModal.value = true
  quickEntryDoctype.value = dt
}
</script>
