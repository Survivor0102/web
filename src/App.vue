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
      <!-- 顶部导航栏 -->
      <el-header style="padding: 0">
        <el-menu
          :default-active="activeIndex"
          class="el-menu-demo"
          mode="horizontal"
          @select="handleSelect"
        >
          <el-menu-item index="1">主页</el-menu-item>
          <el-menu-item index="2">成果大厅</el-menu-item>
          <el-menu-item index="3">需求中心</el-menu-item>
          <el-menu-item index="4">专家中心</el-menu-item>
          <el-menu-item index="5">合作伙伴</el-menu-item>
          <el-menu-item index="6">金融服务</el-menu-item>
          <el-menu-item index="7">关于我们</el-menu-item>
          <div style="flex-grow: 1"></div>
          <el-menu-item index="8">登录/注册</el-menu-item>
        </el-menu>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main>
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
}

.el-header {
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.el-menu-demo {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
