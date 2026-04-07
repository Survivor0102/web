<template>
  <div class="achievement-center">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>成果大厅</h1>
      <p class="subtitle">展示最新的矿山技术创新成果，促进科技成果转化</p>
    </div>

    <!-- 搜索和筛选区域 -->
    <el-card class="filter-card">
      <div class="filter-section">
        <!-- 搜索框 -->
        <div class="search-row">
          <div class="search-container">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索成果名称、关键词..."
              class="search-input"
              @keyup.enter="handleSearch"
              size="large"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch" />
              </template>
            </el-input>
            <div class="search-actions">
              <el-button type="primary" @click="handleSearch" size="large">搜索</el-button>
              <el-button @click="resetFilters" size="large">重置</el-button>
            </div>
          </div>
        </div>

        <!-- 分类筛选 -->
        <div class="filter-grid">
          <div class="filter-column">
            <div class="filter-group">
              <div class="filter-header">
                <span class="filter-icon">🔍</span>
                <h3>技术领域</h3>
              </div>
              <el-select
                v-model="selectedTechField"
                placeholder="全部技术领域"
                clearable
                class="filter-select"
                size="large"
              >
                <el-option
                  v-for="item in techFields"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </div>

            <div class="filter-group">
              <div class="filter-header">
                <span class="filter-icon">📊</span>
                <h3>成果类型</h3>
              </div>
              <el-select
                v-model="selectedAchievementType"
                placeholder="全部成果类型"
                clearable
                class="filter-select"
                size="large"
              >
                <el-option
                  v-for="item in achievementTypes"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </div>
          </div>

          <div class="filter-column">
            <div class="filter-group">
              <div class="filter-header">
                <span class="filter-icon">📈</span>
                <h3>成熟度</h3>
              </div>
              <el-select
                v-model="selectedMaturity"
                placeholder="全部成熟度"
                clearable
                class="filter-select"
                size="large"
              >
                <el-option
                  v-for="item in maturities"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </div>

            <div class="filter-group">
              <div class="filter-header">
                <span class="filter-icon">🔄</span>
                <h3>转化方式</h3>
              </div>
              <el-select
                v-model="selectedTransformation"
                placeholder="全部转化方式"
                clearable
                class="filter-select"
                size="large"
              >
                <el-option
                  v-for="item in transformationMethods"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 成果列表 -->
    <div class="achievement-list">
      <div class="list-header">
        <h2>成果展示</h2>
        <span class="total-count">共 {{ filteredAchievements.length }} 个成果</span>
      </div>

      <el-row :gutter="20">
        <el-col
          v-for="achievement in paginatedAchievements"
          :key="achievement.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card class="achievement-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-tag
                  :type="getTechFieldTagType(achievement.techField)"
                  size="small"
                >
                  {{ getTechFieldLabel(achievement.techField) }}
                </el-tag>
                <el-tag
                  :type="getTypeTagType(achievement.type)"
                  size="small"
                  style="margin-left: 5px"
                >
                  {{ getTypeLabel(achievement.type) }}
                </el-tag>
              </div>
            </template>

            <div class="achievement-content">
              <h3 class="achievement-title">{{ achievement.title }}</h3>
              <p class="achievement-desc">{{ achievement.description }}</p>

              <div class="achievement-meta">
                <div class="meta-item">
                  <span class="meta-label">成熟度：</span>
                  <span>{{ getMaturityLabel(achievement.maturity) }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">转化方式：</span>
                  <span>{{ getTransformationLabel(achievement.transformation) }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">发布时间：</span>
                  <span>{{ achievement.publishDate }}</span>
                </div>
              </div>
            </div>

            <template #footer>
              <div class="card-footer">
                <el-button type="primary" @click="viewDetail(achievement.id)">
                  查看详情
                </el-button>
                <el-button @click="handleContact(achievement.id)">
                  我要对接
                </el-button>
              </div>
            </template>
          </el-card>
        </el-col>
      </el-row>

      <!-- 分页 -->
      <div class="pagination" v-if="filteredAchievements.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredAchievements.length"
          :page-sizes="[12, 24, 36, 48]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 无数据提示 -->
      <div class="empty-state" v-if="filteredAchievements.length === 0">
        <el-empty description="暂无相关成果" />
      </div>
    </div>

    <!-- 客服对话框 -->
    <el-dialog
      v-model="contactDialogVisible"
      title="我要对接"
      width="500px"
    >
      <div class="contact-dialog">
        <p>您好！我是智能客服，将为您提供对接服务。</p>
        <p>请选择您想要咨询的问题：</p>
        <el-radio-group v-model="selectedQuestion">
          <el-radio
            v-for="question in commonQuestions"
            :key="question.id"
            :label="question.id"
          >
            {{ question.text }}
          </el-radio>
        </el-radio-group>

        <div v-if="selectedQuestion" class="answer-section">
          <h4>回答：</h4>
          <p>{{ getAnswer(selectedQuestion) }}</p>
        </div>

        <div class="human-service">
          <p>如需人工客服，请点击下方按钮：</p>
          <el-button type="warning" @click="requestHumanService">
            请求人工客服
          </el-button>
          <p v-if="humanServiceRequested" class="human-service-note">
            人工客服已收到您的请求，请稍等片刻...
          </p>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="contactDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="contactDialogVisible = false">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()

// 搜索和筛选数据
const searchKeyword = ref('')
const selectedTechField = ref('')
const selectedAchievementType = ref('')
const selectedMaturity = ref('')
const selectedTransformation = ref('')

// 分页数据
const currentPage = ref(1)
const pageSize = ref(12)

// 对话框控制
const contactDialogVisible = ref(false)
const selectedQuestion = ref('')
const humanServiceRequested = ref(false)

// 筛选选项数据
const techFields = ref([
  { value: 'mining', label: '采矿技术' },
  { value: 'safety', label: '安全技术' },
  { value: 'automation', label: '自动化技术' },
  { value: 'environment', label: '环保技术' },
  { value: 'energy', label: '能源技术' },
  { value: 'digital', label: '数字化技术' }
])

const achievementTypes = ref([
  { value: 'patent', label: '专利' },
  { value: 'software', label: '软件著作权' },
  { value: 'paper', label: '学术论文' },
  { value: 'equipment', label: '设备装置' },
  { value: 'process', label: '工艺方法' },
  { value: 'standard', label: '技术标准' }
])

const maturities = ref([
  { value: 'laboratory', label: '实验室阶段' },
  { value: 'pilot', label: '小试阶段' },
  { value: 'demonstration', label: '中试示范' },
  { value: 'industrialization', label: '产业化' }
])

const transformationMethods = ref([
  { value: 'transfer', label: '技术转让' },
  { value: 'license', label: '技术许可' },
  { value: 'cooperation', label: '合作开发' },
  { value: 'investment', label: '技术入股' },
  { value: 'service', label: '技术服务' }
])

// 常见问题
const commonQuestions = ref([
  { id: '1', text: '这项技术的具体参数是什么？', answer: '具体技术参数请联系技术负责人获取详细资料。' },
  { id: '2', text: '这项技术的转化条件是什么？', answer: '转化条件包括技术使用费、合作方式等，具体可面谈商议。' },
  { id: '3', text: '是否有成功应用案例？', answer: '目前已在XX矿山成功应用，效果显著。' },
  { id: '4', text: '技术支持和服务内容？', answer: '提供技术培训、现场指导、后期维护等全方位服务。' }
])

// 模拟数据 - 成果列表
const achievements = ref([
  {
    id: 1,
    title: '智能化矿山安全监测系统',
    description: '基于物联网的矿山安全实时监测系统，实现安全隐患预警。',
    techField: 'safety',
    type: 'software',
    maturity: 'industrialization',
    transformation: 'transfer',
    publishDate: '2024-03-15'
  },
  {
    id: 2,
    title: '高效节能采矿设备',
    description: '新型采矿设备，能耗降低30%，效率提升25%。',
    techField: 'mining',
    type: 'equipment',
    maturity: 'demonstration',
    transformation: 'cooperation',
    publishDate: '2024-02-28'
  },
  {
    id: 3,
    title: '矿山废水处理新工艺',
    description: '环保型废水处理技术，处理效率高，运行成本低。',
    techField: 'environment',
    type: 'process',
    maturity: 'pilot',
    transformation: 'license',
    publishDate: '2024-03-10'
  },
  {
    id: 4,
    title: '矿山数字化管理平台',
    description: '集成生产、安全、设备的全方位数字化管理平台。',
    techField: 'digital',
    type: 'software',
    maturity: 'industrialization',
    transformation: 'service',
    publishDate: '2024-01-20'
  },
  {
    id: 5,
    title: '智能通风控制系统',
    description: '基于AI的矿井通风智能调控系统，节能效果显著。',
    techField: 'automation',
    type: 'patent',
    maturity: 'demonstration',
    transformation: 'investment',
    publishDate: '2024-03-05'
  },
  {
    id: 6,
    title: '矿山地质灾害预警技术',
    description: '先进的地质灾害监测预警技术，准确率高达95%。',
    techField: 'safety',
    type: 'patent',
    maturity: 'laboratory',
    transformation: 'transfer',
    publishDate: '2024-02-15'
  },
  {
    id: 7,
    title: '清洁能源采矿技术',
    description: '利用清洁能源替代传统能源的绿色采矿技术。',
    techField: 'energy',
    type: 'process',
    maturity: 'pilot',
    transformation: 'cooperation',
    publishDate: '2024-03-01'
  },
  {
    id: 8,
    title: '矿山机器人巡检系统',
    description: '自主巡检机器人系统，替代人工完成危险区域巡检。',
    techField: 'automation',
    type: 'equipment',
    maturity: 'demonstration',
    transformation: 'license',
    publishDate: '2024-02-10'
  },
  {
    id: 9,
    title: '尾矿资源化利用技术',
    description: '将尾矿转化为建筑材料的技术，实现资源循环利用。',
    techField: 'environment',
    type: 'process',
    maturity: 'industrialization',
    transformation: 'transfer',
    publishDate: '2024-01-30'
  },
  {
    id: 10,
    title: '智能选矿控制系统',
    description: '基于机器学习的选矿过程优化控制系统。',
    techField: 'automation',
    type: 'software',
    maturity: 'pilot',
    transformation: 'service',
    publishDate: '2024-03-12'
  },
  {
    id: 11,
    title: '矿山应急救援装备',
    description: '新型应急救援装备，提高救援效率和安全保障。',
    techField: 'safety',
    type: 'equipment',
    maturity: 'demonstration',
    transformation: 'cooperation',
    publishDate: '2024-02-25'
  },
    {
    id: 12,
    title: '数字化矿山建模软件',
    description: '三维矿山建模与可视化软件，支持生产决策。',
    techField: 'digital',
    type: 'software',
    maturity: 'industrialization',
    transformation: 'license',
    publishDate: '2024-03-08'
  }
])

// 计算属性 - 过滤后的成果
const filteredAchievements = computed(() => {
  return achievements.value.filter(item => {
    // 关键词搜索
    const keywordMatch = !searchKeyword.value ||
      item.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      item.description.toLowerCase().includes(searchKeyword.value.toLowerCase())

    // 技术领域筛选
    const techFieldMatch = !selectedTechField.value ||
      item.techField === selectedTechField.value

    // 成果类型筛选
    const typeMatch = !selectedAchievementType.value ||
      item.type === selectedAchievementType.value

    // 成熟度筛选
    const maturityMatch = !selectedMaturity.value ||
      item.maturity === selectedMaturity.value

    // 转化方式筛选
    const transformationMatch = !selectedTransformation.value ||
      item.transformation === selectedTransformation.value

    return keywordMatch && techFieldMatch && typeMatch &&
           maturityMatch && transformationMatch
  })
})

// 计算属性 - 分页数据
const paginatedAchievements = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAchievements.value.slice(start, end)
})

// 辅助函数 - 获取标签类型
const getTechFieldTagType = (value) => {
  const types = {
    'mining': 'primary',
    'safety': 'danger',
    'automation': 'success',
    'environment': 'warning',
    'energy': 'info',
    'digital': ''
  }
  return types[value] || ''
}

const getTypeTagType = (value) => {
  const types = {
    'patent': 'success',
    'software': 'primary',
    'paper': 'warning',
    'equipment': 'danger',
    'process': 'info',
    'standard': ''
  }
  return types[value] || ''
}

// 辅助函数 - 获取标签文本
const getTechFieldLabel = (value) => {
  const field = techFields.value.find(item => item.value === value)
  return field ? field.label : value
}

const getTypeLabel = (value) => {
  const type = achievementTypes.value.find(item => item.value === value)
  return type ? type.label : value
}

const getMaturityLabel = (value) => {
  const maturity = maturities.value.find(item => item.value === value)
  return maturity ? maturity.label : value
}

const getTransformationLabel = (value) => {
  const method = transformationMethods.value.find(item => item.value === value)
  return method ? method.label : value
}

const getAnswer = (questionId) => {
  const question = commonQuestions.value.find(item => item.id === questionId)
  return question ? question.answer : ''
}

// 方法
const handleSearch = () => {
  currentPage.value = 1 // 搜索后回到第一页
  // 这里可以添加实际的搜索逻辑
}

const resetFilters = () => {
  searchKeyword.value = ''
  selectedTechField.value = ''
  selectedAchievementType.value = ''
  selectedMaturity.value = ''
  selectedTransformation.value = ''
  currentPage.value = 1
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const viewDetail = (id) => {
  router.push(`/achievement-detail/${id}`)
}

const handleContact = (id) => {
  selectedQuestion.value = ''
  humanServiceRequested.value = false
  contactDialogVisible.value = true
}

const requestHumanService = () => {
  humanServiceRequested.value = true
  // 这里可以添加请求人工客服的实际逻辑
}

onMounted(() => {
  // 可以在这里加载实际数据
})
</script>

<style scoped>
.achievement-center {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 32px;
  margin-bottom: 10px;
  color: #303133;
}

.subtitle {
  font-size: 16px;
  color: #909399;
}

.filter-card {
  margin-bottom: 30px;
}

.filter-section {
  padding: 10px 0;
}

.search-row {
  margin-bottom: 25px;
}

/* .search-input {
  flex: 1;
  max-width: 400px;
} */

/* .filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
} */

/* .filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
} */

/* .filter-label {
  font-weight: 500;
  white-space: nowrap;
} */

.achievement-list {
  margin-top: 30px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h2 {
  font-size: 24px;
  color: #303133;
}

.total-count {
  color: #909399;
  font-size: 14px;
}

.achievement-card {
  height: 100%;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.achievement-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
}

.achievement-content {
  min-height: 200px;
}

.achievement-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #303133;
  line-height: 1.4;
}

.achievement-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.achievement-meta {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 13px;
}

.meta-label {
  color: #909399;
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: space-between;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.empty-state {
  margin: 50px 0;
}

.contact-dialog {
  padding: 10px;
}

.answer-section {
  margin-top: 15px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.answer-section h4 {
  margin-bottom: 10px;
  color: #303133;
}

.human-service {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.human-service-note {
  margin-top: 10px;
  color: #e6a23c;
  font-size: 14px;
}

/* 更新搜索区域样式 */
.search-container {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.search-input {
  flex: 1;
}

.search-actions {
  display: flex;
  gap: 10px;
}

/* 更新筛选区域样式 */
.filter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  margin-top: 20px;
}

.filter-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-group {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.filter-group:hover {
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #409eff;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-icon {
  font-size: 20px;
}

.filter-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.filter-select {
  width: 100%;
}

/* 成果卡片改进 */
.achievement-card {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e9ecef;
}

.achievement-content {
  min-height: 180px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .filter-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .filter-column {
    gap: 15px;
  }

  .filter-group {
    padding: 15px;
  }

  .search-container {
    flex-direction: column;
    gap: 10px;
  }

  .search-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .search-input {
    width: 100%;
  }

  .achievement-content {
    min-height: auto;
  }
}
</style>