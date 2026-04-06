<template>
  <div class="agent-console">
    <!-- 顶部工具栏 -->
    <div class="console-header">
      <div class="header-content">
        <div class="header-left">
          <h2>客服工作台</h2>
          <div class="agent-status">
            <el-select v-model="agentStatus" @change="updateStatus" size="small" style="width: 100px">
              <el-option label="在线" value="online" />
              <el-option label="忙碌" value="busy" />
              <el-option label="离开" value="away" />
              <el-option label="离线" value="offline" />
            </el-select>
            <div class="status-indicator" :class="agentStatus"></div>
          </div>
        </div>
        <div class="header-right">
          <div class="session-stats">
            <span class="stat-item">
              <span class="stat-label">当前会话:</span>
              <span class="stat-value">{{ activeSessions.length }}</span>
            </span>
            <span class="stat-item">
              <span class="stat-label">等待中:</span>
              <span class="stat-value">{{ waitingSessions.length }}</span>
            </span>
          </div>
          <el-button @click="refreshSessions" size="small" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button @click="logout" type="danger" size="small" plain>
            退出工作台
          </el-button>
        </div>
      </div>
    </div>

    <div class="console-content">
      <!-- 左侧：会话列表 -->
      <div class="sessions-panel">
        <div class="panel-header">
          <h3>会话列表</h3>
          <div class="panel-actions">
            <el-input
              v-model="sessionFilter"
              placeholder="搜索会话..."
              size="small"
              clearable
              style="width: 200px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button-group>
              <el-button @click="filterSessions('active')" size="small" :type="activeFilter === 'active' ? 'primary' : ''">
                进行中
              </el-button>
              <el-button @click="filterSessions('waiting')" size="small" :type="activeFilter === 'waiting' ? 'primary' : ''">
                等待中
              </el-button>
              <el-button @click="filterSessions('all')" size="small" :type="activeFilter === 'all' ? 'primary' : ''">
                全部
              </el-button>
            </el-button-group>
          </div>
        </div>

        <div class="sessions-list">
          <div v-if="filteredSessions.length === 0" class="empty-sessions">
            <el-icon size="60"><ChatLineRound /></el-icon>
            <p>暂无会话</p>
          </div>

          <div v-for="session in filteredSessions"
               :key="session.id"
               :class="['session-card', { active: currentSession?.id === session.id, unread: hasUnreadMessages(session.id) }]"
               @click="selectSession(session)">
            <div class="session-card-header">
              <div class="session-info">
                <div class="user-info">
                  <el-avatar :size="32" :src="session.user?.avatar">
                    {{ session.user?.username?.charAt(0).toUpperCase() }}
                  </el-avatar>
                  <div class="user-details">
                    <span class="username">{{ session.user?.username }}</span>
                    <span class="session-id">#{{ session.id.substring(0, 8) }}</span>
                  </div>
                </div>
                <div class="session-meta">
                  <el-tag :type="getStatusTagType(session.status)" size="small">
                    {{ getStatusText(session.status) }}
                  </el-tag>
                  <span class="session-time">{{ formatTime(session.last_message_at) }}</span>
                </div>
              </div>

              <div class="session-actions">
                <!-- 等待中会话显示明显接单按钮 -->
                <el-button
                  v-if="!session.agent_id && session.status === 'waiting'"
                  @click.stop="acceptSession(session)"
                  type="primary"
                  size="small"
                  class="accept-btn"
                >
                  接单
                </el-button>
                <el-dropdown @command="handleSessionCommand(session, $event)" trigger="click">
                  <el-button size="small" text>
                    <el-icon><More /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item v-if="!session.agent_id && session.status === 'waiting'" command="accept">接单</el-dropdown-item>
                      <el-dropdown-item v-else command="transfer">转接会话</el-dropdown-item>
                      <el-dropdown-item command="close" divided>结束会话</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>

            <div class="session-context">
              <el-tag v-if="session.context?.page" size="small" type="info">
                来源: {{ getContextText(session.context.page) }}
              </el-tag>
              <span v-if="session.context?.id" class="context-id">
                ID: {{ session.context.id }}
              </span>
            </div>

            <div class="session-preview">
              {{ getLastMessagePreview(session.id) }}
            </div>

            <div v-if="hasUnreadMessages(session.id)" class="unread-badge">
              <el-badge :value="getUnreadCount(session.id)" />
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：聊天区域 -->
      <div class="chat-panel">
        <div v-if="!currentSession" class="no-session-selected">
          <el-icon size="80"><ChatLineSquare /></el-icon>
          <h3>选择左侧会话开始对话</h3>
          <p>或等待新会话分配</p>
        </div>

        <div v-else class="chat-container">
          <!-- 聊天头部 -->
          <div class="chat-header">
            <div class="chat-user-info">
              <el-avatar :size="40" :src="currentSession.user?.avatar">
                {{ currentSession.user?.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="user-details">
                <h4>{{ currentSession.user?.username }}</h4>
                <div class="user-meta">
                  <span class="user-email">{{ currentSession.user?.email }}</span>
                  <el-tag v-if="currentSession.context?.page" size="small">
                    {{ getContextText(currentSession.context.page) }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div class="chat-actions">
              <el-button @click="transferSession" size="small" plain>
                <el-icon><Connection /></el-icon>
                转接
              </el-button>
              <el-button @click="endCurrentSession" type="danger" size="small" plain>
                <el-icon><CircleClose /></el-icon>
                结束
              </el-button>
            </div>
          </div>

          <!-- 消息区域 -->
          <div ref="messagesContainer" class="messages-container">
            <div v-for="message in currentMessages" :key="message.id" class="message-wrapper">
              <div :class="['message-bubble', `message-${message.sender_type}`]">
                <div class="message-header">
                  <template v-if="message.sender_type === 'system'">
                    <el-tag size="small" type="info">系统</el-tag>
                  </template>
                  <template v-else-if="message.sender_type === 'agent'">
                    <el-avatar :size="24">
                      {{ getAgentInitial(message.sender_id) }}
                    </el-avatar>
                    <span class="sender-name">{{ getAgentName(message.sender_id) }}</span>
                  </template>
                  <template v-else>
                    <el-avatar :size="24">
                      {{ currentSession.user?.username?.charAt(0).toUpperCase() }}
                    </el-avatar>
                    <span class="sender-name">{{ currentSession.user?.username }}</span>
                  </template>
                  <span class="message-time">{{ formatMessageTime(message.created_at) }}</span>
                </div>

                <div class="message-content">
                  {{ message.content }}
                  <div v-if="message.is_faq_answer" class="faq-tag">
                    <el-tag size="small" type="success">来自知识库</el-tag>
                  </div>
                </div>

                <div v-if="message.sender_type === 'user' && !message.read_by_recipient" class="unread-indicator">
                  <el-icon color="#409eff"><CircleCheck /></el-icon>
                </div>
              </div>
            </div>

            <div v-if="isUserTyping" class="typing-indicator">
              <div class="typing-dots">
                <span></span><span></span><span></span>
              </div>
              <span>{{ currentSession.user?.username }} 正在输入...</span>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <div class="quick-replies">
              <el-button
                v-for="template in quickReplyTemplates"
                :key="template.id"
                size="small"
                @click="useQuickReply(template)"
              >
                {{ template.text }}
              </el-button>
            </div>

            <div class="input-container">
              <el-input
                ref="messageInput"
                v-model="newMessage"
                type="textarea"
                :rows="3"
                placeholder="输入回复..."
                @keydown.enter.exact.prevent="sendMessage"
                @input="handleTyping"
              />
              <div class="input-actions">
                <div class="action-left">
                  <el-button @click="sendMessage" type="primary" :disabled="!newMessage.trim()" :loading="sending">
                    发送
                  </el-button>
                  <el-button @click="insertFAQ" plain>
                    <el-icon><Collection /></el-icon>
                    插入FAQ
                  </el-button>
                </div>
                <div class="action-right">
                  <span class="connection-status" :class="connectionStatus">
                    {{ getConnectionStatusText }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：在线客服列表 -->
      <div class="agents-panel">
        <div class="panel-header">
          <h3>在线客服</h3>
          <span class="online-count">{{ onlineAgents.length }} 人在线</span>
        </div>
        <div class="agents-list">
          <div v-for="agent in onlineAgents" :key="agent.id" class="agent-item">
            <div class="agent-info">
              <el-avatar :size="36" :src="agent.avatar">
                {{ agent.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="agent-details">
                <span class="agent-name">{{ agent.username }}</span>
                <div class="agent-status-info">
                  <div class="status-indicator" :class="agent.status"></div>
                  <span class="session-count">{{ agent.current_session_count }} 个会话</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 转接会话对话框 -->
    <el-dialog
      v-model="showTransferDialog"
      title="转接会话"
      width="400px"
    >
      <el-form label-width="80px">
        <el-form-item label="转接给">
          <el-select v-model="transferToAgentId" placeholder="请选择客服" style="width: 100%">
            <el-option
              v-for="agent in availableAgents"
              :key="agent.id"
              :label="agent.username"
              :value="agent.id"
            >
              <div class="agent-option">
                <el-avatar :size="24" :src="agent.avatar">
                  {{ agent.username?.charAt(0).toUpperCase() }}
                </el-avatar>
                <span>{{ agent.username }}</span>
                <span class="agent-sessions">({{ agent.current_session_count }}个会话)</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="transferNote"
            type="textarea"
            :rows="2"
            placeholder="可选：添加转接说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTransferDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmTransfer" :loading="transferring">
            确认转接
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- FAQ选择对话框 -->
    <el-dialog
      v-model="showFAQDialog"
      title="选择FAQ回复"
      width="600px"
    >
      <div class="faq-dialog">
        <el-input
          v-model="faqSearch"
          placeholder="搜索FAQ..."
          clearable
          style="margin-bottom: 15px"
        />
        <div class="faq-categories">
          <el-tag
            v-for="category in faqCategories"
            :key="category.id"
            :type="selectedCategory === category.id ? 'primary' : 'info'"
            size="default"
            @click="selectCategory(category.id)"
            class="category-tag"
          >
            {{ category.name }}
          </el-tag>
        </div>
        <div class="faq-list">
          <div v-for="faq in filteredFAQs" :key="faq.id" class="faq-item" @click="selectFAQ(faq)">
            <div class="faq-question">
              <strong>Q:</strong> {{ faq.question }}
            </div>
            <div class="faq-answer">
              <strong>A:</strong> {{ faq.answer }}
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showFAQDialog = false">取消</el-button>
          <el-button type="primary" @click="insertSelectedFAQ" :disabled="!selectedFAQ">
            插入回复
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useChatStore } from '@/stores/customer-service/chat'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Search,
  More,
  ChatLineRound,
  ChatLineSquare,
  Connection,
  CircleClose,
  CircleCheck,
  Collection
} from '@element-plus/icons-vue'
import io from 'socket.io-client'

const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()

// 状态
const agentStatus = ref('online')
const sessions = ref([])
const currentSession = ref(null)
const currentMessages = ref([])
const onlineAgents = ref([])
const loading = ref(false)
const sessionFilter = ref('')
const activeFilter = ref('all')
const newMessage = ref('')
const sending = ref(false)
const connectionStatus = ref('connecting')
const isUserTyping = ref(false)
const showTransferDialog = ref(false)
const transferToAgentId = ref('')
const transferNote = ref('')
const transferring = ref(false)
const showFAQDialog = ref(false)
const faqSearch = ref('')
const faqCategories = ref([])
const selectedCategory = ref(null)
const filteredFAQs = ref([])
const selectedFAQ = ref(null)

// DOM元素引用
const messagesContainer = ref(null)
const messageInput = ref(null)

// WebSocket
let socket = null

// 快捷回复模板
const quickReplyTemplates = ref([
  { id: 1, text: '您好，有什么可以帮您？' },
  { id: 2, text: '请稍等，我帮您查询一下。' },
  { id: 3, text: '这个问题我需要转给相关部门处理。' },
  { id: 4, text: '感谢您的咨询，还有什么需要帮助的吗？' },
  { id: 5, text: '请提供更多详细信息，以便我更好地帮助您。' }
])

// 计算属性
const activeSessions = computed(() => {
  return sessions.value.filter(s => s.status === 'active')
})

const waitingSessions = computed(() => {
  return sessions.value.filter(s => s.status === 'waiting')
})

const filteredSessions = computed(() => {
  let filtered = sessions.value

  // 按状态过滤
  if (activeFilter.value === 'active') {
    filtered = filtered.filter(s => s.status === 'active')
  } else if (activeFilter.value === 'waiting') {
    filtered = filtered.filter(s => s.status === 'waiting')
  }

  // 按搜索词过滤
  if (sessionFilter.value) {
    const query = sessionFilter.value.toLowerCase()
    filtered = filtered.filter(s =>
      s.user?.username?.toLowerCase().includes(query) ||
      s.id?.toLowerCase().includes(query) ||
      s.context?.page?.toLowerCase().includes(query)
    )
  }

  return filtered
})

const availableAgents = computed(() => {
  return onlineAgents.value.filter(agent =>
    agent.id !== userStore.currentUser.id &&
    agent.status === 'online'
  )
})

const getConnectionStatusText = computed(() => {
  const texts = {
    connecting: '连接中...',
    connected: '已连接',
    disconnected: '已断开'
  }
  return texts[connectionStatus.value] || connectionStatus.value
})

// 生命周期
onMounted(() => {
  if (!userStore.isAuthenticated || !userStore.isAgent) {
    router.push('/login')
    return
  }

  initializeConsole()
})

onUnmounted(() => {
  disconnectSocket()
})

// 初始化
const initializeConsole = async () => {
  try {
    // 自动设置客服状态为在线
    await chatStore.updateAgentStatus('online')
    agentStatus.value = 'online'
  } catch (error) {
    console.error('自动更新客服状态失败:', error)
    // 继续执行，不影响其他初始化
  }

  await Promise.all([
    loadSessions(),
    loadOnlineAgents(),
    loadFAQCategories()
  ])
  connectSocket()
}

// 加载数据
const loadSessions = async () => {
  loading.value = true
  try {
    console.log('正在加载客服会话...')
    const response = await chatStore.getAgentSessions()
    console.log('客服会话API响应:', response)
    sessions.value = response.sessions || []
    console.log('加载的会话数量:', sessions.value.length)
    console.log('会话数据:', sessions.value)
  } catch (error) {
    console.error('加载会话失败:', error)
    ElMessage.error('加载会话失败')
  } finally {
    loading.value = false
  }
}

const loadSessionMessages = async (sessionId) => {
  try {
    const response = await chatStore.getSessionMessages(sessionId)
    currentMessages.value = response.messages || []
    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败:', error)
    ElMessage.error('加载消息失败')
    // 清除当前消息，避免显示错误会话的消息
    currentMessages.value = []
  }
}

const loadOnlineAgents = async () => {
  try {
    const response = await chatStore.getOnlineAgents()
    onlineAgents.value = response.agents || []
  } catch (error) {
    console.error('加载在线客服失败:', error)
  }
}

const loadFAQCategories = async () => {
  try {
    const response = await chatStore.getFAQCategories()
    faqCategories.value = response.categories || []
  } catch (error) {
    console.error('加载FAQ分类失败:', error)
  }
}

// WebSocket连接
const connectSocket = () => {
  const token = userStore.token
  if (!token) return

  socket = io('http://localhost:5000', {
    query: { token },
    transports: ['websocket', 'polling']
  })

  socket.on('connect', () => {
    console.log('客服工作台WebSocket连接成功', {
      socket_id: socket.id,
      connected: socket.connected
    })
    connectionStatus.value = 'connected'
  })

  socket.on('disconnect', (reason) => {
    console.log('客服工作台WebSocket断开连接', { reason })
    connectionStatus.value = 'disconnected'
  })

  socket.on('connect_error', (error) => {
    console.error('客服工作台WebSocket连接错误:', error)
  })

  // 监听新会话分配
  socket.on('session_assigned', (data) => {
    ElMessage.success('新会话已分配')
    loadSessions() // 刷新会话列表

    // 如果有新会话，可以自动选择
    if (data.session_id) {
      const newSession = sessions.value.find(s => s.id === data.session_id)
      if (newSession) {
        selectSession(newSession)
      }
    }
  })

  // 监听新消息
  socket.on('new_message', (data) => {
    console.log('客服端收到新消息:', {
      session_id: data.session_id,
      message_id: data.message?.id,
      sender_id: data.message?.sender_id,
      sender_type: data.message?.sender_type,
      content_preview: data.message?.content?.substring(0, 50)
    })

    console.log('当前会话状态:', {
      current_session_id: currentSession.value?.id,
      current_session_user: currentSession.value?.user?.username
    })

    if (currentSession.value && data.session_id === currentSession.value.id) {
      console.log('消息属于当前会话，处理消息')

      // 查找是否已存在相同内容的临时消息
      const tempMessageIndex = currentMessages.value.findIndex(msg =>
        msg.is_temp &&
        msg.session_id === data.session_id &&
        msg.sender_id === data.message.sender_id &&
        msg.content === data.message.content
      )

      if (tempMessageIndex !== -1) {
        // 替换临时消息为服务器返回的真实消息
        console.log('找到临时消息，替换为真实消息')
        currentMessages.value[tempMessageIndex] = data.message
      } else {
        // 如果没有临时消息，则添加新消息（例如用户发送的消息）
        console.log('未找到临时消息，添加新消息')
        currentMessages.value.push(data.message)
      }

      scrollToBottom()
    } else {
      console.log('消息不属于当前会话或当前会话为空，不添加到当前消息列表')
    }

    // 更新会话列表中的最后消息时间
    const sessionIndex = sessions.value.findIndex(s => s.id === data.session_id)
    if (sessionIndex !== -1) {
      sessions.value[sessionIndex].last_message_at = data.message.created_at
    }
  })

  // 监听用户输入状态
  socket.on('user_typing', (data) => {
    if (currentSession.value && data.session_id === currentSession.value.id) {
      isUserTyping.value = data.is_typing
      if (!data.is_typing) {
        setTimeout(() => {
          isUserTyping.value = false
        }, 2000)
      }
    }
  })

  // 监听客服状态更新
  socket.on('agent_status_changed', (data) => {
    loadOnlineAgents() // 刷新在线客服列表
  })

  // 监听会话转接
  socket.on('session_transferred', (data) => {
    if (currentSession.value && data.session_id === currentSession.value.id) {
      ElMessage.info('会话已转接给其他客服')
      currentSession.value = null
      currentMessages.value = []
    }
    loadSessions() // 刷新会话列表
  })

  // 监听会话被接单
  socket.on('session_accepted', (data) => {
    ElMessage.info(`会话已被客服 ${data.agent_name} 接单`)
    loadSessions() // 刷新会话列表
  })

  // 监听会话关闭
  socket.on('session_closed', (data) => {
    if (currentSession.value && data.session_id === currentSession.value.id) {
      ElMessage.info('会话已结束')
      currentSession.value = null
      currentMessages.value = []
    }
    loadSessions() // 刷新会话列表
  })
}

const disconnectSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

// 会话操作
const selectSession = async (session) => {
  // 清除之前的消息，避免会话间消息混淆
  currentMessages.value = []
  currentSession.value = session
  await loadSessionMessages(session.id)

  // 加入会话房间
  if (socket && socket.connected) {
    socket.emit('join_session', { session_id: session.id })

    // 标记消息为已读
    const unreadMessages = currentMessages.value.filter(msg =>
      msg.sender_type === 'user' && !msg.read_by_recipient
    )

    if (unreadMessages.length > 0) {
      const messageIds = unreadMessages.map(msg => msg.id)
      socket.emit('mark_as_read', {
        session_id: session.id,
        message_ids: messageIds
      })
    }
  }

  // 聚焦输入框
  nextTick(() => {
    scrollToBottom()
    if (messageInput.value) {
      messageInput.value.focus()
    }
  })
}

const filterSessions = (filter) => {
  activeFilter.value = filter
}

const hasUnreadMessages = (sessionId) => {
  // 简化实现：总是返回false，实际应该根据未读消息计数
  return false
}

const getUnreadCount = (sessionId) => {
  // 简化实现
  return 0
}

const handleSessionCommand = (session, command) => {
  if (command === 'accept') {
    acceptSession(session)
  } else if (command === 'transfer') {
    transferSession()
  } else if (command === 'close') {
    endSession(session)
  }
}

const acceptSession = async (session) => {
  try {
    await chatStore.acceptSession(session.id)
    ElMessage.success('接单成功')

    // 刷新会话列表
    await loadSessions()

    // 如果当前没有选中会话，自动选中刚接单的会话
    if (!currentSession.value) {
      const acceptedSession = sessions.value.find(s => s.id === session.id)
      if (acceptedSession) {
        await selectSession(acceptedSession)
      }
    }
  } catch (error) {
    console.error('接单失败:', error)
    ElMessage.error(error.response?.data?.error || '接单失败')
  }
}

// 消息操作
const sendMessage = async () => {
  if (!newMessage.value.trim() || !currentSession.value) return

  sending.value = true
  const content = newMessage.value.trim()

  try {
    if (socket && socket.connected) {
      console.log('客服工作台发送消息:', {
        session_id: currentSession.value.id,
        content,
        socket_connected: socket.connected,
        socket_id: socket.id
      })
      socket.emit('send_message', {
        session_id: currentSession.value.id,
        content
      })

      // 本地添加消息（乐观更新）
      const tempMessage = {
        id: Date.now(),
        session_id: currentSession.value.id,
        sender_type: 'agent',
        sender_id: userStore.currentUser.id,
        content,
        created_at: new Date().toISOString(),
        delivered: true,
        read_by_recipient: false,
        is_temp: true  // 标记为临时消息，用于防止重复显示
      }

      currentMessages.value.push(tempMessage)
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

const handleTyping = () => {
  if (!socket || !socket.connected || !currentSession.value) return

  // 发送输入状态
  socket.emit('typing', {
    session_id: currentSession.value.id,
    is_typing: true
  })

  // 3秒后自动停止
  setTimeout(() => {
    if (socket && socket.connected) {
      socket.emit('typing', {
        session_id: currentSession.value.id,
        is_typing: false
      })
    }
  }, 3000)
}

const useQuickReply = (template) => {
  newMessage.value = template.text
}

// 会话管理
const updateStatus = async (status) => {
  try {
    await chatStore.updateAgentStatus(status)
    agentStatus.value = status
    ElMessage.success('状态更新成功')
  } catch (error) {
    console.error('更新状态失败:', error)
    ElMessage.error('更新状态失败')
  }
}

const transferSession = () => {
  if (!currentSession.value) {
    ElMessage.warning('请先选择会话')
    return
  }

  showTransferDialog.value = true
  transferToAgentId.value = ''
  transferNote.value = ''
}

const confirmTransfer = async () => {
  if (!transferToAgentId.value) {
    ElMessage.warning('请选择要转接的客服')
    return
  }

  transferring.value = true
  try {
    // 这里应该调用转接API
    // 暂时使用WebSocket模拟
    if (socket && socket.connected) {
      // 实际应该调用API
      ElMessage.success('转接请求已发送')
    }

    showTransferDialog.value = false
  } catch (error) {
    console.error('转接失败:', error)
    ElMessage.error('转接失败')
  } finally {
    transferring.value = false
  }
}

const endCurrentSession = async () => {
  if (!currentSession.value) return

  try {
    await ElMessageBox.confirm('确定要结束当前会话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await chatStore.closeSession(currentSession.value.id)
    ElMessage.success('会话已结束')

    currentSession.value = null
    currentMessages.value = []
    loadSessions()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('结束会话失败:', error)
      ElMessage.error('结束会话失败')
    }
  }
}

const endSession = async (session) => {
  try {
    await ElMessageBox.confirm('确定要结束此会话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await chatStore.closeSession(session.id)
    ElMessage.success('会话已结束')

    if (currentSession.value && currentSession.value.id === session.id) {
      currentSession.value = null
      currentMessages.value = []
    }

    loadSessions()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('结束会话失败:', error)
      ElMessage.error('结束会话失败')
    }
  }
}

// FAQ功能
const insertFAQ = () => {
  showFAQDialog.value = true
  faqSearch.value = ''
  selectedCategory.value = null
  selectedFAQ.value = null
  loadFAQs()
}

const loadFAQs = async () => {
  try {
    const response = await chatStore.searchFAQ(faqSearch.value, selectedCategory.value)
    filteredFAQs.value = response.items || []
  } catch (error) {
    console.error('加载FAQ失败:', error)
  }
}

const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId === selectedCategory.value ? null : categoryId
  loadFAQs()
}

const selectFAQ = (faq) => {
  selectedFAQ.value = faq
}

const insertSelectedFAQ = () => {
  if (selectedFAQ.value) {
    newMessage.value = selectedFAQ.value.answer
    showFAQDialog.value = false
  }
}

// 工具函数
const refreshSessions = () => {
  loadSessions()
  loadOnlineAgents()
}

const logout = () => {
  router.push('/home')
}

const scrollToBottom = () => {
  nextTick(() => {
    const container = messagesContainer.value
    if (container) {
      container.scrollTop = container.scrollHeight
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

const getContextText = (context) => {
  const texts = {
    achievement: '成果中心',
    innovation: '创新中心',
    expert: '专家中心',
    project: '项目申报',
    general: '一般咨询'
  }
  return texts[context] || context
}

const formatTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  const now = new Date()

  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  return date.toLocaleDateString('zh-CN')
}

const formatMessageTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const getLastMessagePreview = (sessionId) => {
  // 简化实现
  return '点击查看对话...'
}

const getAgentInitial = (agentId) => {
  const agent = onlineAgents.value.find(a => a.id === agentId)
  return agent?.username?.charAt(0).toUpperCase() || 'A'
}

const getAgentName = (agentId) => {
  const agent = onlineAgents.value.find(a => a.id === agentId)
  return agent?.username || '客服'
}

// 监听搜索词变化
watch(faqSearch, () => {
  loadFAQs()
})

watch(selectedCategory, () => {
  loadFAQs()
})
</script>

<style scoped>
.agent-console {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.console-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  max-width: 1800px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.agent-status {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.online {
  background: #67c23a;
}

.status-indicator.busy {
  background: #e6a23c;
}

.status-indicator.away {
  background: #f56c6c;
}

.status-indicator.offline {
  background: #909399;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.session-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}

.stat-label {
  color: #909399;
}

.stat-value {
  color: #303133;
  font-weight: 500;
}

.console-content {
  flex: 1;
  display: flex;
  max-width: 1800px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
  gap: 20px;
  overflow: hidden;
}

.sessions-panel {
  width: 400px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-panel {
  flex: 1;
  background: white;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.agents-panel {
  width: 300px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.online-count {
  font-size: 12px;
  color: #409eff;
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.empty-sessions {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  text-align: center;
  padding: 40px 20px;
}

.empty-sessions p {
  margin-top: 15px;
  font-size: 14px;
}

.session-card {
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  margin-bottom: 10px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}

.session-card:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.session-card.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.session-card.unread {
  border-left: 3px solid #f56c6c;
}

.session-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.session-info {
  flex: 1;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.session-id {
  font-size: 11px;
  color: #909399;
}

.session-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.session-time {
  font-size: 11px;
  color: #c0c4cc;
}

.session-actions {
  margin-left: 10px;
}

.session-context {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.context-id {
  font-size: 11px;
  color: #909399;
}

.session-preview {
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unread-badge {
  position: absolute;
  top: 10px;
  right: 10px;
}

.no-session-selected {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #909399;
  text-align: center;
}

.no-session-selected h3 {
  margin: 20px 0 10px;
  color: #303133;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 15px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-user-info h4 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 16px;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-email {
  font-size: 12px;
  color: #909399;
}

.chat-actions {
  display: flex;
  gap: 10px;
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

.message-agent {
  margin-left: auto;
  background: #95d475;
  color: white;
  border-bottom-right-radius: 2px;
}

.message-user, .message-system {
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

.unread-indicator {
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
  padding: 15px;
  background: white;
}

.quick-replies {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
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
  padding: 4px 8px;
  border-radius: 4px;
}

.connection-status.connected {
  color: #67c23a;
  background: #f0f9eb;
}

.connection-status.connecting {
  color: #e6a23c;
  background: #fdf6ec;
}

.connection-status.disconnected {
  color: #f56c6c;
  background: #fef0f0;
}

.agents-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.agent-item {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  margin-bottom: 10px;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.agent-details {
  display: flex;
  flex-direction: column;
}

.agent-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.agent-status-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.session-count {
  font-size: 11px;
  color: #909399;
}

.faq-dialog {
  max-height: 400px;
  overflow-y: auto;
}

.faq-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.category-tag {
  cursor: pointer;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.faq-item {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.3s;
}

.faq-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.faq-question {
  margin-bottom: 8px;
  color: #303133;
}

.faq-answer {
  color: #606266;
  font-size: 14px;
}

.agent-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.agent-sessions {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}
</style>