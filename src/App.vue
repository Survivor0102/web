<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeIndex = ref('1')

const handleSelect = (key, keyPath) => {
  console.log(key, keyPath)
  if (key === '1') {
    router.push('/')
  } else if (key === '2') {
    router.push('/achievement-center')
  }
}
</script>

<template>
  <div id="app">
    <el-container>
      <el-header class="header-container">
        <!-- 外层容器：控制整体宽度 + 左右布局 -->
        <div class="menu-wrapper">
          <!-- 左侧居中菜单组 -->
          <el-menu
            :default-active="activeIndex"
            mode="horizontal"
            @select="handleSelect"
            class="center-menu"
            :ellipsis="false" 
          >
            <el-menu-item index="1">主页</el-menu-item>
            <el-menu-item index="2">成果大厅</el-menu-item>
            <el-menu-item index="3">需求中心</el-menu-item>
            <el-menu-item index="4">专家中心</el-menu-item>
            <el-menu-item index="5">合作伙伴</el-menu-item>
            <el-menu-item index="6">金融服务</el-menu-item>
            <el-menu-item index="7">关于我们</el-menu-item>
          </el-menu>

          <!-- 右侧登录按钮（独立菜单） -->
          <el-menu
            mode="horizontal"
            class="right-menu"
            @select="handleSelect"
            :ellipsis="false"
          >
            <el-menu-item index="8">登录/注册</el-menu-item>
          </el-menu>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>


<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  width: 100%;
}

/* 头部容器 */
.el-header.header-container {
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 0 !important;
}

/* 菜单外层：宽度限制 + Flex 左右布局 */
.menu-wrapper {
  max-width: 1000px;
  width: 100%;
  margin: 0 auto; /* 整体在页面居中 */
  display: flex;
  justify-content: space-between; /* 左右分开 */
  align-items: center;
  height: 60px; /* 与 header 等高 */
}

/* 左侧核心菜单：居中 */
.center-menu {
  flex: none;
  display: flex;
  justify-content: center; /* 菜单项居中 */
  border-bottom: none !important;
}

/* 右侧登录菜单：右置 */
.right-menu {
  flex: none;
  border-bottom: none !important;
}

/* 清除默认样式并保证水平排列 */
::v-deep .el-menu--horizontal {
  display: flex;
  border-bottom: none;
}
::v-deep .el-menu-item {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.main-content {
  padding: 0 !important;
  margin: 0 !important;
}
</style>
