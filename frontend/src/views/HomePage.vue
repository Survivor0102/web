<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <h2>智慧矿山实验室</h2>
        </div>
        <div class="nav">
          <router-link to="/home" class="nav-item">首页</router-link>
          <router-link to="/customer-service" class="nav-item">客服中心</router-link>
          <span v-if="userStore.isAgent" class="nav-item">
            <router-link to="/customer-service/admin">客服工作台</router-link>
          </span>
        </div>
        <div class="user-info">
          <el-dropdown v-if="userStore.isAuthenticated" @command="handleCommand">
            <span class="el-dropdown-link">
              <el-avatar :size="32" :src="userAvatar">
                {{ userInitial }}
              </el-avatar>
              <span class="username">{{ userStore.currentUser?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <router-link v-else to="/login" class="login-link">登录</router-link>
        </div>
      </div>
    </el-header>

    <!-- 主要内容 -->
    <el-main class="main-content">
      <div class="welcome-section">
        <h1>欢迎使用智慧矿山实验室平台</h1>
        <p class="subtitle">成果转化 · 创新服务 · 专家咨询 · 项目申报</p>

        <div class="feature-cards">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <el-icon size="24"><Trophy /></el-icon>
                <span>成果中心</span>
              </div>
            </template>
            <p>展示最新的研究成果和技术成果</p>
            <div class="card-footer">
              <el-button type="primary" @click="goToAchievementCenter">
                查看成果
              </el-button>
              <el-button @click="openCustomerService('achievement')">
                需要对接
              </el-button>
            </div>
          </el-card>

          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <el-icon size="24"><Lightning /></el-icon>
                <span>创新中心</span>
              </div>
            </template>
            <p>分享和发现创新想法与技术方案</p>
            <div class="card-footer">
              <el-button type="primary" @click="goToInnovationCenter">
                查看创新
              </el-button>
              <el-button @click="openCustomerService('innovation')">
                需要对接
              </el-button>
            </div>
          </el-card>

          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <el-icon size="24"><User /></el-icon>
                <span>专家中心</span>
              </div>
            </template>
            <p>联系领域专家获取专业指导</p>
            <div class="card-footer">
              <el-button type="primary" @click="goToExpertCenter">
                查看专家
              </el-button>
              <el-button @click="openCustomerService('expert')">
                需要对接
              </el-button>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 客服入口悬浮按钮 -->
      <div class="floating-chat-btn" @click="openCustomerService('general')">
        <el-icon size="24"><ChatDotRound /></el-icon>
        <span>在线客服</span>
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  Trophy,
  Lightning,
  User,
  ChatDotRound
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const userAvatar = computed(() => {
  // 实际项目中可以从用户信息中获取头像
  return ''
})

const userInitial = computed(() => {
  const username = userStore.currentUser?.username
  return username ? username.charAt(0).toUpperCase() : ''
})

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch {
      // 用户取消
    }
  } else if (command === 'profile') {
    // 跳转到个人中心
    ElMessage.info('个人中心功能开发中')
  }
}

const goToAchievementCenter = () => {
  ElMessage.info('成果中心页面开发中')
}

const goToInnovationCenter = () => {
  ElMessage.info('创新中心页面开发中')
}

const goToExpertCenter = () => {
  ElMessage.info('专家中心页面开发中')
}

const openCustomerService = (context) => {
  // 如果未登录，跳转到登录页
  if (!userStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  // 跳转到客服页面，传递上下文
  router.push({
    path: '/customer-service',
    query: { context }
  })
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.logo h2 {
  color: #409eff;
  margin: 0;
  font-size: 20px;
}

.nav {
  display: flex;
  gap: 30px;
}

.nav-item {
  color: #333;
  text-decoration: none;
  font-size: 16px;
  padding: 5px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: #409eff;
  border-bottom-color: #409eff;
}

.user-info {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #333;
}

.login-link {
  color: #409eff;
  text-decoration: none;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 60px;
}

.welcome-section h1 {
  font-size: 36px;
  color: #333;
  margin-bottom: 15px;
}

.subtitle {
  font-size: 18px;
  color: #666;
  margin-bottom: 50px;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

.feature-card {
  height: 100%;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 500;
}

.card-header .el-icon {
  color: #409eff;
}

.feature-card p {
  color: #666;
  margin-bottom: 20px;
  min-height: 60px;
}

.card-footer {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.floating-chat-btn {
  position: fixed;
  bottom: 40px;
  right: 40px;
  background: #409eff;
  color: white;
  border-radius: 50px;
  padding: 15px 25px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;
  z-index: 1000;
}

.floating-chat-btn:hover {
  background: #337ecc;
  box-shadow: 0 6px 25px rgba(64, 158, 255, 0.4);
  transform: translateY(-2px);
}
</style>