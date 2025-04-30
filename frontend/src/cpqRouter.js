

const handleMobileView = (componentName) => {
    return window.innerWidth < 768 ? `Mobile${componentName}` : componentName
  }
  
  export const cpqRoutes = [
      {
          alias: '/designs',
          path: '/designs/view/:viewType?',
          name: 'Designs',
          component: () => import('@/pages/Designs.vue'),
      },
      {
        path: '/designs/:designId',
        name: 'Design',
        component: () => import(`@/pages/${handleMobileView('Design')}.vue`),
        props: true,
      },
    //   {
    //     alias: '/items',
    //     path: '/items/view/:viewType?',
    //     name: 'Items',
    //     component: () => import('@/pages/Items.vue'),
    //   },
    //   {
    //     path: '/items/:itemId',
    //     name: 'Item',
    //     component: () => import(`@/pages/${handleMobileView('Item')}.vue`),
    //     props: true,
    //   },
    //   {
    //     alias: '/quotations',
    //     path: '/quotations/view/:viewType?',
    //     name: 'Quotations',
    //     component: () => import('@/pages/Quotations.vue'),
    //   },
    //   {
    //     path: '/quotations/:quotationId',
    //     name: 'Quotation',
    //     component: () => import(`@/pages/${handleMobileView('Quotation')}.vue`),
    //     props: true,
    //   },
    //   {
    //     alias: '/condition-types',
    //     path: '/condition-types/view/:viewType?',
    //     name: 'Condition Types',
    //     component: () => import('@/pages/ConditionTypes.vue'),
    //   },
    //   {
    //     path: '/condition-types/:conditionId',
    //     name: 'Condition Type',
    //     component: () => import(`@/pages/${handleMobileView('ConditionType')}.vue`),
    //     props: true,
    //   },
    //   {
    //     path: '/condition-types/create',
    //     name: 'Create',
    //     component: () => import('@/pages/CreateConditionType.vue'),
    //   },
    //   {
    //     alias: '/condition-values',
    //     path: '/condition-values/view/:viewType?',
    //     name: 'Condition Values',
    //     component: () => import('@/pages/ConditionValues.vue'),
    //   },
    //   {
    //     path: '/condition-values/:conditionValueId',
    //     name: 'Condition Value',
    //     component: () => import(`@/pages/${handleMobileView('ConditionValue')}.vue`),
    //     props: true,
    //   },
  ]
  
  // importing the icon
  import TaskIcon from '@/components/Icons/TaskIcon.vue'
//   import NoteIcon from '@/components/Icons/NoteIcon.vue'
  
  //cpq Menu 
  export const cpqLinks = [
      {
          label: 'Designs',
          icon: TaskIcon,
          to: 'Designs',
      },
    //   {
    //     label: 'Items',
    //     icon: TaskIcon,
    //     to: 'Items',
    //   },
    //   {
    //     label: 'Quotations',
    //     icon: NoteIcon,
    //     to: 'Quotations',
    //   },
    //   {
    //     label: 'Condition Types',
    //     icon: NoteIcon,
    //     to: 'Condition Types',
    //   },
    //   {
    //     label: 'Condition Values',
    //     icon: TaskIcon,
    //     to: 'Condition Values',
    //   },
    
  ]
  
  //custom function to add the icon
  export function getCustomIcon(routeName) {
      switch (routeName) {
        case 'Designs':
          return TaskIcon
        // case 'Items':
        //   return TaskIcon
        // case 'Quotations':
        //   return NoteIcon
        // case 'Condition Types':
        //   return NoteIcon
        // case 'Condition Values':
        //   return TaskIcon
        default:
          return null
      }
    }
  