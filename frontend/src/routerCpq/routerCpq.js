export function getCustomRoutes(){

  const handleMobileView = (componentName) => {
    return window.innerWidth < 768 ? `Mobile${componentName}` : componentName;
  };

    return [
        {
          alias: '/designs',
          path: '/designs/view/:viewType?',
          name: 'Designs',
          component: () => import('@/pages/Designs.vue'),
          meta: { scrollPos: { top: 0, left: 0 } },
      },
      {
        path: '/designs/:designId',
        name: 'Design',
        component: () => import(`@/pages/${handleMobileView('Design')}.vue`),
        props: true,
      }
    ]
  }