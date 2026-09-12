import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import { getToken } from '@/api/http'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { title: '登录', public: true },
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: '首页' },
    },
    {
      path: '/detection',
      name: 'detection',
      component: () => import('@/views/DetectionView.vue'),
      meta: { title: '检测分析' },
    },
    {
      path: '/defects',
      name: 'defects',
      component: () => import('@/views/DefectsView.vue'),
      meta: { title: '缺陷管理' },
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('@/views/ReportsView.vue'),
      meta: { title: '报告管理' },
    },
    {
      path: '/reports/:id',
      name: 'report-detail',
      component: () => import('@/views/ReportDetailView.vue'),
      meta: { title: '报告详情' },
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: () => import('@/views/StatisticsView.vue'),
      meta: { title: '统计报表' },
    },
    {
      path: '/datasets',
      name: 'datasets',
      component: () => import('@/views/DatasetsView.vue'),
      meta: { title: '数据集管理' },
    },
    {
      path: '/system',
      name: 'system',
      component: () => import('@/views/SystemView.vue'),
      meta: { title: '系统管理' },
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

// 路由守卫：未登录跳转登录页
router.beforeEach((to) => {
  if (!to.meta.public && !getToken()) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.path === '/login' && getToken()) {
    return { path: '/' }
  }
  return true
})

router.afterEach((to) => {
  const base = '桥路缺陷检测系统'
  document.title = to.meta.title ? `${to.meta.title as string} | ${base}` : base
})

export default router
