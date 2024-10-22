// importing the icon
import TaskIcon from '@/components/Icons/TaskIcon.vue'

//cpq Menu 
export const extraLinks = [
    {
        label: 'Designs',
        icon: TaskIcon,
        to: 'Designs',
    },
  
]

//custom function to add the icon
export function getCustomIcon(routeName) {
  switch (routeName) {
    case 'Designs':
      return TaskIcon
    default:
      return null
  }
}
