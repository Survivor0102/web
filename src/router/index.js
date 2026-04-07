import { createRouter, createWebHistory } from 'vue-router'

// 导入视图组件
const HomePage = () => import('@/views/HomePage.vue')
const AchievementCenter = () => import('@/views/AchievementCenter.vue')
const AchievementDetail = () => import('@/views/AchievementDetail.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/achievement-center',
    name: 'AchievementCenter',
    component: AchievementCenter
  },
  {
    path: '/achievement-detail/:id',
    name: 'AchievementDetail',
    component: AchievementDetail,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router