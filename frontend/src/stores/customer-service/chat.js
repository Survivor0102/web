import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const currentSession = ref(null)
  const sessions = ref([])
  const messages = ref([])
  const onlineAgents = ref([])
  const connectionStatus = ref('disconnected') // disconnected, connecting, connected

  // 获取用户会话列表
  const getUserSessions = async (params = {}) => {
    try {
      const response = await api.get('/customer-service/sessions', { params })
      sessions.value = response.data.sessions || []
      return response.data
    } catch (error) {
      console.error('获取会话列表失败:', error)
      throw error
    }
  }

  // 获取会话详情
  const getSession = async (sessionId) => {
    try {
      const response = await api.get(`/customer-service/session/${sessionId}`)
      currentSession.value = response.data.session
      return response.data
    } catch (error) {
      console.error('获取会话详情失败:', error)
      throw error
    }
  }

  // 获取会话消息
  const getSessionMessages = async (sessionId, params = {}) => {
    try {
      const response = await api.get(`/customer-service/session/${sessionId}/messages`, { params })
      messages.value = response.data.messages || []
      return response.data
    } catch (error) {
      console.error('获取消息失败:', error)
      throw error
    }
  }

  // 开始新会话
  const startSession = async (data) => {
    try {
      console.log('startSession API call with data:', data)
      const response = await api.post('/customer-service/session/start', data)
      console.log('startSession response:', response.data)
      const newSession = response.data.session

      // 添加到会话列表
      sessions.value.unshift(newSession)
      currentSession.value = newSession

      return response.data
    } catch (error) {
      console.error('创建会话失败:', error)
      console.error('Error response:', error.response?.data)
      throw error
    }
  }

  // 发送消息
  const sendMessage = async (sessionId, content, attachments = []) => {
    try {
      const response = await api.post(`/customer-service/session/${sessionId}/send`, {
        content,
        attachments
      })

      // 添加消息到列表
      if (response.data.message) {
        messages.value.push(response.data.message)
      }

      return response.data
    } catch (error) {
      console.error('发送消息失败:', error)
      throw error
    }
  }

  // 关闭会话
  const closeSession = async (sessionId, feedback = null, rating = null) => {
    try {
      // 注意：这个API端点可能需要根据后端实现调整
      const response = await api.post(`/customer-service/session/${sessionId}/close`, {
        feedback,
        rating
      })

      // 更新会话状态
      const sessionIndex = sessions.value.findIndex(s => s.id === sessionId)
      if (sessionIndex !== -1) {
        sessions.value[sessionIndex].status = 'closed'
      }

      if (currentSession.value && currentSession.value.id === sessionId) {
        currentSession.value.status = 'closed'
      }

      return response.data
    } catch (error) {
      console.error('关闭会话失败:', error)
      throw error
    }
  }

  // 获取在线客服列表
  const getOnlineAgents = async () => {
    try {
      const response = await api.get('/customer-service/agents/online')
      onlineAgents.value = response.data.agents || []
      return response.data
    } catch (error) {
      console.error('获取在线客服失败:', error)
      throw error
    }
  }

  // 搜索FAQ
  const searchFAQ = async (query, categoryId = null) => {
    try {
      const params = { q: query }
      if (categoryId) params.category_id = categoryId

      const response = await api.get('/customer-service/faq/search', { params })
      return response.data
    } catch (error) {
      console.error('搜索FAQ失败:', error)
      throw error
    }
  }

  // 获取FAQ分类
  const getFAQCategories = async () => {
    try {
      const response = await api.get('/customer-service/faq/categories')
      return response.data
    } catch (error) {
      console.error('获取FAQ分类失败:', error)
      throw error
    }
  }

  // 更新客服状态（仅客服角色可用）
  const updateAgentStatus = async (status) => {
    try {
      const response = await api.put('/customer-service/agent/status', { status })
      return response.data
    } catch (error) {
      console.error('更新客服状态失败:', error)
      throw error
    }
  }

  // 获取客服会话列表（仅客服角色可用）
  const getAgentSessions = async (params = {}) => {
    try {
      const response = await api.get('/customer-service/agent/sessions', { params })
      return response.data
    } catch (error) {
      console.error('获取客服会话列表失败:', error)
      throw error
    }
  }

  // 客服接单（仅客服角色可用）
  const acceptSession = async (sessionId) => {
    try {
      const response = await api.post(`/customer-service/session/${sessionId}/accept`)
      return response.data
    } catch (error) {
      console.error('接单失败:', error)
      throw error
    }
  }

  // 转接会话给其他客服（仅客服角色可用）
  const transferSession = async (sessionId, toAgentId, note = '') => {
    try {
      const response = await api.post(`/customer-service/session/${sessionId}/transfer`, {
        to_agent_id: toAgentId,
        note: note
      })
      return response.data
    } catch (error) {
      console.error('转接会话失败:', error)
      throw error
    }
  }

  // 清空当前会话
  const clearCurrentSession = () => {
    currentSession.value = null
    messages.value = []
  }

  // 添加消息（用于WebSocket接收）
  const addMessage = (message) => {
    // 确保消息属于当前会话
    if (currentSession.value && currentSession.value.id === message.session_id) {
      messages.value.push(message)
    }
  }

  // 更新消息状态（用于WebSocket）
  const updateMessageStatus = (messageId, updates) => {
    const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      messages.value[messageIndex] = {
        ...messages.value[messageIndex],
        ...updates
      }
    }
  }

  // 更新会话信息
  const updateSession = (sessionId, updates) => {
    const sessionIndex = sessions.value.findIndex(s => s.id === sessionId)
    if (sessionIndex !== -1) {
      sessions.value[sessionIndex] = {
        ...sessions.value[sessionIndex],
        ...updates
      }
    }

    if (currentSession.value && currentSession.value.id === sessionId) {
      currentSession.value = {
        ...currentSession.value,
        ...updates
      }
    }
  }

  return {
    // 状态
    currentSession,
    sessions,
    messages,
    onlineAgents,
    connectionStatus,

    // 动作
    getUserSessions,
    getSession,
    getSessionMessages,
    startSession,
    sendMessage,
    closeSession,
    acceptSession,
    transferSession,
    getOnlineAgents,
    searchFAQ,
    getFAQCategories,
    updateAgentStatus,
    getAgentSessions,
    clearCurrentSession,
    addMessage,
    updateMessageStatus,
    updateSession
  }
})