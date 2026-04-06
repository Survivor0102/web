import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(sessionStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)
  const currentUser = computed(() => user.value)

  const hasRole = (role) => {
    return user.value?.role === role
  }

  const isAgent = computed(() => hasRole('agent'))
  const isAdmin = computed(() => hasRole('admin'))

  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials)
      const { user: userData, token: authToken } = response.data

      // 保存token和用户信息
      token.value = authToken
      user.value = userData
      sessionStorage.setItem('token', authToken)

      return { success: true, user: userData }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: error.response?.data?.error || '登录失败' }
    }
  }

  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register', userData)
      const { user: newUser, token: authToken } = response.data

      token.value = authToken
      user.value = newUser
      sessionStorage.setItem('token', authToken)

      return { success: true, user: newUser }
    } catch (error) {
      console.error('注册失败:', error)
      return { success: false, error: error.response?.data?.error || '注册失败' }
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    sessionStorage.removeItem('token')
  }

  const fetchUser = async () => {
    if (!token.value) return

    try {
      const response = await api.get('/auth/me')
      user.value = response.data.user
    } catch (error) {
      console.error('获取用户信息失败:', error)
      logout()
      // token无效，跳转到登录页
      if (error.response?.status === 401) {
        window.location.href = '/login'
      }
    }
  }

  // 初始化时获取用户信息
  if (token.value) {
    fetchUser()
  }

  return {
    user,
    token,
    isAuthenticated,
    currentUser,
    hasRole,
    isAgent,
    isAdmin,
    login,
    register,
    logout,
    fetchUser
  }
})