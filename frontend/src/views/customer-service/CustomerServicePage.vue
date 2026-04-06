<template>
  <div class="customer-service-page">
    <!-- 顶部导航栏 -->
    <div class="service-header">
      <div class="header-content">
        <div class="back-btn" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回</span>
        </div>
        <div class="service-title">
          <h2>在线客服</h2>
          <div class="service-status">
            <el-tag :type="connectionStatus === 'connected' ? 'success' : 'danger'" size="small">
              {{ connectionStatus === 'connected' ? '在线' : '离线' }}
            </el-tag>
            <span class="agent-info" v-if="currentSession?.agent">
              客服：{{ currentSession.agent.username }}
            </span>
          </div>
        </div>
        <div class="header-actions">
          <el-button v-if="currentSession" @click="endSession" type="danger" size="small">
            结束会话
          </el-button>
        </div>
      </div>
    </div>

    <div class="service-content">
      <!-- 左侧：会话列表（仅显示当前用户的会话） -->
      <div class="session-sidebar" v-if="sessions.length > 0">
        <div class="sidebar-header">
          <h3>我的会话</h3>
          <el-button @click="createNewSession" type="primary" size="small" plain>
            新会话
          </el-button>
        </div>
        <div class="session-list">
          <div v-for="session in sessions"
               :key="session.id"
               :class="['session-item', { active: currentSession?.id === session.id }]"
               @click="switchSession(session)">
            <div class="session-header">
              <div class="session-title">
                <span class="session-id">#{{ session.id.substring(0, 8) }}</span>
                <el-tag :type="getStatusTagType(session.status)" size="small">
                  {{ getStatusText(session.status) }}
                </el-tag>
              </div>
              <span class="session-time">{{ formatTime(session.last_message_at) }}</span>
            </div>
            <div class="session-preview">
              {{ getLastMessagePreview(session.id) }}
            </div>
            <div class="session-info">
              <span v-if="session.agent">客服: {{ session.agent.username }}</span>
              <span v-else>等待分配客服...</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：聊天区域 -->
      <div class="chat-area">
        <div v-if="!currentSession" class="empty-chat">
          <el-icon size="80"><ChatDotRound /></el-icon>
          <h3>欢迎使用在线客服</h3>
          <p>请选择左侧会话或创建新会话开始咨询</p>
          <el-button @click="createNewSession" type="primary" size="large">
            开始新会话
          </el-button>
          <div class="quick-actions" v-if="routeContext">
            <p>当前上下文: {{ getContextText(routeContext) }}</p>
            <el-button @click="createContextSession" type="success">
              基于当前上下文咨询
            </el-button>
          </div>
        </div>

        <div v-else class="chat-container">
          <!-- 消息区域 -->
          <div ref="messagesContainer" class="messages-container">
            <div v-for="message in messages" :key="message.id" class="message-wrapper">
              <div :class="['message-bubble', `message-${message.sender_type}`]">
                <!-- 消息头 -->
                <div class="message-header">
                  <template v-if="message.sender_type === 'system'">
                    <el-tag size="small" type="info">系统</el-tag>
                  </template>
                  <template v-else-if="message.sender_type === 'agent'">
                    <el-avatar :size="24" :src="getAgentAvatar(message.sender_id)">
                      {{ getAgentInitial(message.sender_id) }}
                    </el-avatar>
                    <span class="sender-name">{{ getAgentName(message.sender_id) }}</span>
                  </template>
                  <template v-else>
                    <el-avatar :size="24" :src="userStore.currentUser?.avatar">
                      {{ userStore.currentUser?.username?.charAt(0).toUpperCase() }}
                    </el-avatar>
                    <span class="sender-name">我</span>
                  </template>
                  <span class="message-time">{{ formatMessageTime(message.created_at) }}</span>
                </div>

                <!-- 消息内容 -->
                <div class="message-content">
                  {{ message.content }}
                  <div v-if="message.is_faq_answer" class="faq-tag">
                    <el-tag size="small" type="success">来自知识库</el-tag>
                  </div>
                </div>

                <!-- 消息状态 -->
                <div v-if="message.sender_type === 'user'" class="message-status">
                  <el-icon v-if="message.read_by_recipient" color="#67C23A"><Check /></el-icon>
                  <el-icon v-else-if="message.delivered" color="#909399"><Check /></el-icon>
                  <el-icon v-else color="#E6A23C"><Loading /></el-icon>
                </div>
              </div>
            </div>

            <!-- 输入中提示 -->
            <div v-if="isAgentTyping" class="typing-indicator">
              <div class="typing-dots">
                <span></span><span></span><span></span>
              </div>
              <span>{{ typingAgentName }} 正在输入...</span>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <div class="input-container">
              <el-input
                ref="messageInput"
                v-model="newMessage"
                type="textarea"
                :rows="3"
                placeholder="输入消息..."
                :disabled="!currentSession"
                @keydown.enter.exact.prevent="sendMessage"
                @input="handleTyping"
              />
              <div class="input-actions">
                <div class="action-left">
                  <el-tooltip content="发送" placement="top">
                    <el-button
                      @click="sendMessage"
                      type="primary"
                      :disabled="!newMessage.trim() || !currentSession"
                      :loading="sending"
                    >
                      <el-icon><Promotion /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
                <div class="action-right">
                  <span class="connection-status">
                    {{ connectionStatus === 'connected' ? '已连接' : '连接中...' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新会话对话框 -->
    <el-dialog
      v-model="showNewSessionDialog"
      title="创建新会话"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="newSessionForm" label-width="80px">
        <el-form-item label="咨询类型">
          <el-select v-model="newSessionForm.context" placeholder="请选择咨询类型">
            <el-option label="成果中心咨询" value="achievement" />
            <el-option label="创新中心咨询" value="innovation" />
            <el-option label="专家中心咨询" value="expert" />
            <el-option label="项目申报咨询" value="project" />
            <el-option label="一般咨询" value="general" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input
            v-model="newSessionForm.description"
            type="textarea"
            :rows="3"
            placeholder="简要描述您的问题..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showNewSessionDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmNewSession" :loading="creatingSession">
            开始会话
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useChatStore } from '@/stores/customer-service/chat'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  ChatDotRound,
  Check,
  Loading,
  Promotion
} from '@element-plus/icons-vue'
import io from 'socket.io-client'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const chatStore = useChatStore()

// 路由上下文（从首页传递过来的）
const routeContext = computed(() => route.query.context)

// 响应式数据
const currentSession = ref(null)
const sessions = ref([])
const messages = ref([])
const newMessage = ref('')
const sending = ref(false)
const showNewSessionDialog = ref(false)
const creatingSession = ref(false)
const connectionStatus = ref('disconnected')
const isAgentTyping = ref(false)
const typingAgentName = ref('')
const typingTimer = ref(null)

// 引用
const messagesContainer = ref(null)
const messageInput = ref(null)

// 初始化
onMounted(() => {
  if (!userStore.isAuthenticated) {
    router.push('/login')
    return
  }

  initializeChat()
  loadSessions()

  // 如果有上下文，提示创建会话
  if (routeContext.value) {
    setTimeout(() => {
      ElMessageBox.confirm(
        `您正在从${getContextText(routeContext.value)}页面咨询，是否创建新会话？`,
        '创建客服会话',
        {
          confirmButtonText: '创建会话',
          cancelButtonText: '稍后再说',
          type: 'info'
        }
      ).then(() => {
        createContextSession()
      }).catch(() => {
        // 用户取消
      })
    }, 1000)
  }
})

onUnmounted(() => {
  disconnectSocket()
  if (typingTimer.value) {
    clearTimeout(typingTimer.value)
  }
})

// 初始化聊天
const initializeChat = () => {
  connectSocket()
}

// WebSocket连接
let socket = null
const connectSocket = () => {
  const token = userStore.token
  if (!token) return

  socket = io('http://localhost:5000', {
    query: { token },
    transports: ['websocket', 'polling']
  })

  socket.on('connect', () => {
    console.log('WebSocket连接成功')
    connectionStatus.value = 'connected'

    // 加入当前会话（如果有）
    if (currentSession.value) {
      socket.emit('join_session', { session_id: currentSession.value.id })
    }
  })

  socket.on('disconnect', () => {
    console.log('WebSocket断开连接')
    connectionStatus.value = 'disconnected'
  })

  // 监听新消息
  socket.on('new_message', (data) => {
    console.log('用户端收到新消息:', data)
    if (data.session_id === currentSession.value?.id) {
      console.log('消息属于当前会话，处理消息')

      // 如果消息是用户自己发送的（服务器回传），查找并替换临时消息
      if (data.message.sender_type === 'user') {
        const tempMessageIndex = messages.value.findIndex(msg =>
          msg.is_temp &&
          msg.session_id === data.session_id &&
          msg.sender_id === data.message.sender_id &&
          msg.content === data.message.content
        )

        if (tempMessageIndex !== -1) {
          // 替换临时消息为服务器返回的真实消息
          console.log('找到临时消息，替换为真实消息')
          messages.value[tempMessageIndex] = data.message
        } else {
          // 如果没有临时消息，则添加新消息（可能是从其他设备发送的）
          console.log('未找到临时消息，添加新消息')
          messages.value.push(data.message)
        }
      } else {
        // 客服或系统消息，直接添加
        console.log('客服或系统消息，添加到消息列表')
        messages.value.push(data.message)

        // 停止输入提示
        isAgentTyping.value = false
      }

      scrollToBottom()
    } else {
      console.log('消息不属于当前会话或当前会话为空')
    }
  })

  // 监听用户输入状态
  socket.on('user_typing', (data) => {
    if (data.session_id === currentSession.value?.id && data.user_id !== userStore.currentUser.id) {
      isAgentTyping.value = data.is_typing
      typingAgentName.value = data.username
    }
  })

  // 监听会话分配
  socket.on('session_assigned', (data) => {
    ElMessage.success('客服已接入会话')
    // 更新当前会话信息
    if (currentSession.value && currentSession.value.id === data.session_id) {
      loadCurrentSession()
    }
  })

  // 监听会话被接单
  socket.on('session_accepted', (data) => {
    ElMessage.success(`客服 ${data.agent_name} 已接单`)
    // 更新当前会话信息
    if (currentSession.value && currentSession.value.id === data.session_id) {
      loadCurrentSession()
    }
  })

  // 监听会话关闭
  socket.on('session_closed', (data) => {
    if (currentSession.value && currentSession.value.id === data.session_id) {
      ElMessage.info('会话已结束')
      currentSession.value.status = 'closed'
    }
  })
}

const disconnectSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

// 加载会话列表
const loadSessions = async () => {
  try {
    // 这里应该调用API获取用户会话列表
    // 暂时使用模拟数据
    const response = await chatStore.getUserSessions()
    sessions.value = response.sessions || []

    // 如果没有当前会话但有会话列表，选择第一个
    if (!currentSession.value && sessions.value.length > 0) {
      await switchSession(sessions.value[0])
    }
  } catch (error) {
    console.error('加载会话列表失败:', error)
  }
}

// 加载当前会话消息
const loadSessionMessages = async (sessionId) => {
  try {
    const response = await chatStore.getSessionMessages(sessionId)
    messages.value = response.messages || []
    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败:', error)
    messages.value = []
  }
}

// 加载当前会话详情
const loadCurrentSession = async () => {
  if (!currentSession.value) return

  try {
    const response = await chatStore.getSession(currentSession.value.id)
    currentSession.value = response.session
  } catch (error) {
    console.error('加载会话详情失败:', error)
  }
}

// 切换会话
const switchSession = async (session) => {
  currentSession.value = session
  await loadSessionMessages(session.id)

  // 加入会话房间
  if (socket && socket.connected) {
    socket.emit('join_session', { session_id: session.id })
  }

  // 滚动到底部并聚焦输入框
  nextTick(() => {
    scrollToBottom()
    if (messageInput.value) {
      messageInput.value.focus()
    }
  })
}

// 发送消息
const sendMessage = async () => {
  if (!newMessage.value.trim() || !currentSession.value) return

  const message = newMessage.value.trim()
  sending.value = true

  try {
    // 通过WebSocket发送消息
    if (socket && socket.connected) {
      socket.emit('send_message', {
        session_id: currentSession.value.id,
        content: message
      })

      // 本地添加消息（乐观更新）
      const tempMessage = {
        id: Date.now(),
        session_id: currentSession.value.id,
        sender_type: 'user',
        sender_id: userStore.currentUser.id,
        content: message,
        created_at: new Date().toISOString(),
        delivered: false,
        read_by_recipient: false,
        is_temp: true  // 标记为临时消息，用于防止重复显示
      }

      messages.value.push(tempMessage)
      newMessage.value = ''
      scrollToBottom()

      // 停止输入状态
      if (socket && socket.connected) {
        socket.emit('typing', {
          session_id: currentSession.value.id,
          is_typing: false
        })
      }
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败')
  } finally {
    sending.value = false
  }
}

// 处理输入状态
const handleTyping = () => {
  if (!socket || !socket.connected || !currentSession.value) return

  // 发送输入状态
  socket.emit('typing', {
    session_id: currentSession.value.id,
    is_typing: true
  })

  // 清除之前的定时器
  if (typingTimer.value) {
    clearTimeout(typingTimer.value)
  }

  // 3秒后停止输入状态
  typingTimer.value = setTimeout(() => {
    if (socket && socket.connected) {
      socket.emit('typing', {
        session_id: currentSession.value.id,
        is_typing: false
      })
    }
  }, 3000)
}

// 创建新会话
const createNewSession = () => {
  showNewSessionDialog.value = true
}

// 基于上下文创建会话
const createContextSession = async () => {
  const contextValue = routeContext.value || 'general'

  creatingSession.value = true
  try {
    // 将字符串context转换为对象格式
    const contextData = {
      page: contextValue
    }

    const response = await chatStore.startSession({ context: contextData })
    const newSession = response.session

    // 重新加载会话列表以确保数据同步
    await loadSessions()

    // 切换到新会话（从重新加载的列表中查找）
    const sessionToSwitch = sessions.value.find(s => s.id === newSession.id)
    if (sessionToSwitch) {
      await switchSession(sessionToSwitch)
    } else {
      // 如果找不到，使用返回的新会话
      await switchSession(newSession)
    }

    ElMessage.success('会话创建成功，正在为您分配客服...')
    showNewSessionDialog.value = false
  } catch (error) {
    console.error('创建会话失败:', error)
    ElMessage.error('创建会话失败: ' + (error.response?.data?.error || error.message))
  } finally {
    creatingSession.value = false
  }
}

// 确认创建新会话
const confirmNewSession = async () => {
  console.log('confirmNewSession called, newSessionForm:', newSessionForm)
  if (!newSessionForm.context) {
    ElMessage.warning('请选择咨询类型')
    return
  }

  creatingSession.value = true
  try {
    // 将字符串context转换为对象格式，后端期望{page: 'type'}
    const contextData = {
      page: newSessionForm.context
    }

    console.log('Sending session data:', {
      context: contextData,
      description: newSessionForm.description
    })

    const response = await chatStore.startSession({
      context: contextData,
      description: newSessionForm.description
    })
    const newSession = response.session

    console.log('Session created:', newSession)

    // 重新加载会话列表以确保数据同步
    await loadSessions()

    // 切换到新会话（从重新加载的列表中查找）
    const sessionToSwitch = sessions.value.find(s => s.id === newSession.id)
    if (sessionToSwitch) {
      await switchSession(sessionToSwitch)
    } else {
      // 如果找不到，使用返回的新会话
      await switchSession(newSession)
    }

    ElMessage.success('会话创建成功，正在为您分配客服...')
    showNewSessionDialog.value = false
    resetNewSessionForm()
  } catch (error) {
    console.error('创建会话失败:', error)
    console.error('Error details:', error.response?.data || error.message)
    ElMessage.error('创建会话失败: ' + (error.response?.data?.error || error.message))
  } finally {
    creatingSession.value = false
  }
}

// 结束会话
const endSession = async () => {
  try {
    await ElMessageBox.confirm('确定要结束当前会话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await chatStore.closeSession(currentSession.value.id)
    ElMessage.success('会话已结束')

    // 更新会话状态
    currentSession.value.status = 'closed'
  } catch (error) {
    if (error !== 'cancel') {
      console.error('结束会话失败:', error)
      ElMessage.error('结束会话失败')
    }
  }
}

// 新会话表单
const newSessionForm = reactive({
  context: '',
  description: ''
})

const resetNewSessionForm = () => {
  newSessionForm.context = ''
  newSessionForm.description = ''
}

// 工具函数
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const getStatusTagType = (status) => {
  const types = {
    waiting: 'warning',
    active: 'success',
    closed: 'info',
    transferred: 'primary'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    waiting: '等待中',
    active: '进行中',
    closed: '已结束',
    transferred: '已转接'
  }
  return texts[status] || status
}

const formatTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  const now = new Date()
  const diff = now - date

  // 如果是今天，显示时间
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  // 如果是昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  }

  // 一周内显示星期几
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = ['日', '一', '二', '三', '四', '五', '六']
    return `周${days[date.getDay()]}`
  }

  // 否则显示日期
  return date.toLocaleDateString('zh-CN')
}

const formatMessageTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const getLastMessagePreview = (sessionId) => {
  // 这里应该根据sessionId获取最后一条消息的预览
  // 暂时返回固定文本
  return '点击查看对话...'
}

const getContextText = (context) => {
  const texts = {
    achievement: '成果中心',
    innovation: '创新中心',
    expert: '专家中心',
    project: '项目申报',
    general: '一般咨询'
  }

  // 如果context是对象，提取page属性
  if (context && typeof context === 'object' && context.page) {
    return texts[context.page] || context.page
  }

  // 否则当作字符串处理
  return texts[context] || context
}

const getAgentAvatar = (agentId) => {
  // 这里应该根据agentId获取客服头像
  return ''
}

const getAgentInitial = (agentId) => {
  // 这里应该根据agentId获取客服姓名首字母
  const session = sessions.value.find(s => s.agent_id === agentId)
  return session?.agent?.username?.charAt(0).toUpperCase() || 'A'
}

const getAgentName = (agentId) => {
  const session = sessions.value.find(s => s.agent_id === agentId)
  return session?.agent?.username || '客服'
}

const goBack = () => {
  router.back()
}

// 监听当前会话变化
watch(() => currentSession.value, (newSession) => {
  if (newSession && socket && socket.connected) {
    socket.emit('join_session', { session_id: newSession.id })
  }
})
</script>

<style scoped>
.customer-service-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.service-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  max-width: 1400px;
  margin: 0 auto;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
}

.back-btn:hover {
  color: #409eff;
}

.service-title {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.service-title h2 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.service-status {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}

.agent-info {
  font-size: 12px;
  color: #909399;
}

.service-content {
  flex: 1;
  display: flex;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
  gap: 20px;
  overflow: hidden;
}

.session-sidebar {
  width: 300px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.session-item {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.session-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.session-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.session-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.session-id {
  font-size: 12px;
  color: #909399;
}

.session-time {
  font-size: 11px;
  color: #c0c4cc;
}

.session-preview {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-info {
  font-size: 11px;
  color: #909399;
}

.chat-area {
  flex: 1;
  background: white;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #909399;
  text-align: center;
}

.empty-chat h3 {
  margin: 20px 0 10px;
  color: #303133;
}

.empty-chat p {
  margin-bottom: 30px;
}

.quick-actions {
  margin-top: 30px;
  padding: 20px;
  border: 1px dashed #409eff;
  border-radius: 6px;
  background: #f0f9ff;
}

.quick-actions p {
  margin-bottom: 15px;
  color: #606266;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #fafafa;
}

.message-wrapper {
  margin-bottom: 16px;
}

.message-bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 8px;
  position: relative;
}

.message-user {
  margin-left: auto;
  background: #95d475;
  color: white;
  border-bottom-right-radius: 2px;
}

.message-agent, .message-system {
  margin-right: auto;
  background: white;
  color: #303133;
  border: 1px solid #e4e7ed;
  border-bottom-left-radius: 2px;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.sender-name {
  font-size: 12px;
  color: #606266;
}

.message-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-left: auto;
}

.message-content {
  line-height: 1.5;
  word-wrap: break-word;
}

.faq-tag {
  margin-top: 4px;
}

.message-status {
  position: absolute;
  right: -20px;
  bottom: 5px;
  font-size: 12px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  color: #909399;
  font-size: 12px;
}

.typing-dots {
  display: flex;
  gap: 2px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c0c4cc;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
  }
}

.input-area {
  border-top: 1px solid #e4e7ed;
  padding: 20px;
  background: white;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-left {
  display: flex;
  gap: 10px;
}

.action-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.connection-status {
  font-size: 12px;
  color: #909399;
}
</style>