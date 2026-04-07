<template>
  <div class="home-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <template #header>
            <div class="card-header">
              <span>欢迎来到智慧矿山联合实验室平台</span>
            </div>
          </template>
          <p>这里是平台的主页，展示平台的核心功能和最新动态。</p>
          <p>请点击上方导航栏的"成果大厅"进入成果展示页面。</p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>平台简介</span>
            </div>
          </template>
          <p>本平台致力于连接矿山技术创新成果与产业需求，推动科技成果转化。</p>
          <p>提供成果展示、需求发布、专家咨询等服务。</p>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>核心功能</span>
            </div>
          </template>
          <ul>
            <li>成果展示与对接</li>
            <li>技术需求发布</li>
            <li>专家咨询服务</li>
            <li>合作伙伴对接</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
// 主页组件
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-card {
  text-align: center;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.el-row {
  margin-bottom: 20px;
}
</style>