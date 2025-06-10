import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import { capture } from '@/telemetry'
import { parseColor } from '@/utils'
import { defineStore } from 'pinia'
import { createListResource } from 'frappe-ui'
import { reactive, h } from 'vue'

export const cpqStatuses = defineStore('cpq-statuses', () => {

    let designStatusesByName = reactive({})

    const designStatuses = createListResource({
        doctype: 'CRM Design Status',
        fields: ['name', 'color', 'position'],
        orderBy: 'position asc',
        cache: 'design-statuses',
        initialData: [],
        auto: true,
        transform(statuses) {
          for (let status of statuses) {
            status.color = parseColor(status.color)
            designStatusesByName[status.name] = status
          }
          return statuses
        },
      })

    function getDesignStatus(name) {
        if (!name) {
            name = designStatuses.data[0].name
        }
        return designStatusesByName[name]
    }

    function cpqStatusOptions(doctype, action, statuses = []) {
        let statusesByName = designStatusesByName
        //   doctype == 'deal' ? dealStatusesByName : leadStatusesByName
    
        if (statuses.length) {
          statusesByName = statuses.reduce((acc, status) => {
            acc[status] = statusesByName[status]
            return acc
          }, {})
        }
    
        let options = []

        for (const status in statusesByName) {
          options.push({
            label: statusesByName[status]?.name,
            value: statusesByName[status]?.name,
            icon: () => h(IndicatorIcon, { class: statusesByName[status]?.color }),
            onClick: () => {
              capture('status_changed', { doctype, status })
              action && action('status', statusesByName[status]?.name)
            },
          })
        }

        return options
      }
    
    return {
        designStatuses,
        getDesignStatus,
        cpqStatusOptions,
      }
})