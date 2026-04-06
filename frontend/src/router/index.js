import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 页面组件（使用懒加载）
const LoginPage = () => import('@/views/LoginPage.vue')
const HomePage = () => import('@/views/HomePage.vue')
const CustomerServicePage = () => import('@/views/customer-service/CustomerServicePage.vue')
const AgentConsole = () => import('@/views/customer-service/admin/AgentConsole.vue')

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { guestOnly: true }
  },
  {
    path: '/home',
    name: 'home',
    component: HomePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/customer-service',
    name: 'customer-service',
    component: CustomerServicePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/customer-service/admin',
    name: 'agent-console',
    component: AgentConsole,
    meta: {
      requiresAuth: true,
      requiredRoles: ['agent'] // 只有客服角色可以访问
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/home'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 检查是否需要认证
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
    return
  }

  // 检查是否仅限游客（如登录页）
  if (to.meta.guestOnly && userStore.isAuthenticated) {
    next('/home')
    return
  }

  // 检查角色权限
  if (to.meta.requiredRoles) {
    const hasRequiredRole = to.meta.requiredRoles.some(role =>
      userStore.hasRole(role)
    )

    if (!hasRequiredRole) {
      // 无权限，跳转到首页或403页面
      next('/home')
      return
    }
  }

  next()
})

export default router