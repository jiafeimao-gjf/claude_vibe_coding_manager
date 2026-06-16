import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('../views/ProjectList.vue'),
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: () => import('../views/ProjectDetail.vue'),
  },
  {
    path: '/sessions/:id',
    name: 'SessionDetail',
    component: () => import('../views/SessionDetail.vue'),
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue'),
  },
  {
    path: '/import',
    name: 'Import',
    component: () => import('../views/ImportPage.vue'),
  },
  {
    path: '/file-history',
    name: 'FileHistory',
    component: () => import('../views/FileHistory.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
