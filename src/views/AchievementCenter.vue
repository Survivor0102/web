<template>
  <div class="achievement-center">

    <!-- 搜索区域（带背景图片） -->
    <div class="search-hero">
      <div class="search-hero-content">
        <div class="search-container-hero">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索成果名称、关键词..."
            class="search-input-hero"
            @keyup.enter="handleSearch"
            size="large"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>
          <div class="search-actions-hero">
            <el-button type="primary" @click="handleSearch" size="large">搜索</el-button>
            <el-button @click="resetFilters" size="large">重置</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选区域 -->
    <el-card class="filter-card-new">
      <div class="filter-section-new">
        <div class="filter-left-column">
          <div class="filter-category">
            <h3 class="filter-category-title">应用方向</h3>
            <div class="filter-options">
              <el-button
                :type="selectedTechField === '' ? 'primary' : ''"
                @click="toggleTechField('')"
                size="small"
              >
                全部
              </el-button>
              <el-button
                v-for="field in techFields"
                :key="field.value"
                :type="selectedTechField === field.value ? 'primary' : ''"
                @click="toggleTechField(field.value)"
                size="small"
              >
                {{ field.label }}
              </el-button>
            </div>
          </div>

          <div class="filter-category">
            <h3 class="filter-category-title">成熟度</h3>
            <div class="filter-options">
              <el-button
                :type="selectedMaturity === '' ? 'primary' : ''"
                @click="toggleMaturity('')"
                size="small"
              >
                全部
              </el-button>
              <el-button
                v-for="maturity in maturities"
                :key="maturity.value"
                :type="selectedMaturity === maturity.value ? 'primary' : ''"
                @click="toggleMaturity(maturity.value)"
                size="small"
              >
                {{ maturity.label }}
              </el-button>
            </div>
          </div>

          <div class="filter-category">
            <h3 class="filter-category-title">拟转化方式</h3>
            <div class="filter-options">
              <el-button
                :type="selectedTransformation === '' ? 'primary' : ''"
                @click="toggleTransformation('')"
                size="small"
              >
                全部
              </el-button>
              <el-button
                v-for="method in transformationMethods"
                :key="method.value"
                :type="selectedTransformation === method.value ? 'primary' : ''"
                @click="toggleTransformation(method.value)"
                size="small"
              >
                {{ method.label }}
              </el-button>
            </div>
          </div>

          <div class="filter-category">
            <h3 class="filter-category-title">所在地区</h3>
            <div class="filter-options">
              <el-button
                v-for="region in regions"
                :key="region.value"
                :type="selectedRegion === region.value ? 'primary' : ''"
                @click="toggleRegion(region.value)"
                size="small"
              >
                {{ region.label }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 成果列表 -->
    <div class="achievement-list">
      <div class="list-header">
        <span class="total-count">共 {{ filteredAchievements.length }} 个成果</span>
      </div>

      <el-row >
        <el-col
          v-for="achievement in paginatedAchievements"
          :key="achievement.id"
          :xs="24"
          :sm="24"
          :md="24"
          :lg="24"
        >
          <el-card class="achievement-card" shadow="hover">

            <div class="achievement-content-new">
              <!-- 标题区 -->
              <div class="achievement-header">
                <h3 class="achievement-title-new">{{ achievement.title }}</h3>
                <div class="view-count-header">
                  <span class="view-number">{{ achievement.viewCount }}</span>
                  <span class="view-icon">人感兴趣</span>
                </div>
              </div>
              <div class="title-divider"></div>

              <!-- 详情信息区：三列布局 -->
              <div class="detail-info-section">
                <!-- 第一列 -->
                <div class="info-column">
                  <div class="info-row">
                    <span class="info-label">成果编号：{{ achievement.code }}</span>
                    
                  </div>
                  <div class="info-row">
                    <span class="info-label">应用方向：{{ getTechFieldLabel(achievement.techField) }}</span>
                  </div>
                </div>

                <!-- 第二列 -->
                <div class="info-column">
                  <div class="info-row">
                    <span class="info-label">拟转化方式：{{ achievement.transformationText }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">成熟度：{{ getMaturityLabel(achievement.maturity) }}</span>
                  </div>
                </div>

                <!-- 第三列 -->
                <div class="info-column">
                  <div class="info-row">
                    <span class="info-label">所在地区：{{ achievement.region }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">成果持有人：{{ achievement.holder }}</span>

                  </div>
                </div>
              </div>

              <!-- 交互区：右侧按钮 -->
              <div class="interaction-section">
                <el-button
                  type="primary"
                  @click="handleContact(achievement.id)"
                  size="small"
                  class="contact-button-1"
                >
                  我要对接
                </el-button>
              <el-button
                  type="primary"
                  @click="goDetail(achievement.id)"
                  size="small"
                  class="contact-button-2"
                >
                  查看详情
                </el-button>  
                
              </div>
              
            </div>

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
const selectedMaturity = ref('')
const selectedTransformation = ref('')
const selectedRegion = ref('all')

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
  { value: 'green-energy', label: '绿色能源' },
  { value: 'digital', label: '数字化技术' }
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

// 所在地区筛选
const regions = ref([
  { value: 'all', label: '全部' },
  { value: 'north', label: '华北地区' },
  { value: 'east', label: '华东地区' },
  { value: 'south', label: '华南地区' },
  { value: 'central', label: '华中地区' },
  { value: 'northeast', label: '东北地区' },
  { value: 'northwest', label: '西北地区' },
  { value: 'southwest', label: '西南地区' }
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
    title: 'PEM 电解制氢关键部件及系统产业化',
    code: 'CG260100131',
    techField: 'green-energy',
    transformation: 'license',
    transformationText: '技术许可、自行投资转化（创业转化）',
    maturity: 'demonstration',
    region: '山东省・青岛市',
    holder: '中科院青岛能源所',
    viewCount: 5,
    publishDate: '2024-03-15'
  },
  {
    id: 2,
    title: '生物天然气产业化',
    code: 'CG260100132',
    techField: 'green-energy',
    transformation: 'license',
    transformationText: '技术许可、合作开发',
    maturity: 'pilot',
    region: '北京市',
    holder: '中国石油大学',
    viewCount: 8,
    publishDate: '2024-03-10'
  },
  {
    id: 3,
    title: '矿山废水处理新工艺',
    code: 'CG260100133',
    techField: 'environment',
    transformation: 'license',
    transformationText: '技术许可、技术服务',
    maturity: 'pilot',
    region: '江苏省・南京市',
    holder: '南京工业大学',
    viewCount: 12,
    publishDate: '2024-03-10'
  },
  {
    id: 4,
    title: '矿山数字化管理平台',
    code: 'CG260100134',
    techField: 'digital',
    transformation: 'service',
    transformationText: '技术服务、合作开发',
    maturity: 'industrialization',
    region: '北京市',
    holder: '清华大学',
    viewCount: 25,
    publishDate: '2024-01-20'
  },
  {
    id: 5,
    title: '智能通风控制系统',
    code: 'CG260100135',
    techField: 'automation',
    transformation: 'investment',
    transformationText: '技术入股、技术服务',
    maturity: 'demonstration',
    region: '山西省・太原市',
    holder: '太原理工大学',
    viewCount: 18,
    publishDate: '2024-03-05'
  },
  {
    id: 6,
    title: '矿山地质灾害预警技术',
    code: 'CG260100136',
    techField: 'safety',
    transformation: 'transfer',
    transformationText: '技术转让、技术许可',
    maturity: 'laboratory',
    region: '四川省・成都市',
    holder: '四川大学',
    viewCount: 9,
    publishDate: '2024-02-15'
  },
  {
    id: 7,
    title: '清洁能源采矿技术',
    code: 'CG260100137',
    techField: 'green-energy',
    transformation: 'cooperation',
    transformationText: '合作开发、技术许可',
    maturity: 'pilot',
    region: '内蒙古・呼和浩特市',
    holder: '内蒙古工业大学',
    viewCount: 15,
    publishDate: '2024-03-01'
  },
  {
    id: 8,
    title: '矿山机器人巡检系统',
    code: 'CG260100138',
    techField: 'automation',
    transformation: 'license',
    transformationText: '技术许可、技术服务',
    maturity: 'demonstration',
    region: '辽宁省・沈阳市',
    holder: '东北大学',
    viewCount: 22,
    publishDate: '2024-02-10'
  },
  {
    id: 9,
    title: '尾矿资源化利用技术',
    code: 'CG260100139',
    techField: 'environment',
    transformation: 'transfer',
    transformationText: '技术转让、技术许可',
    maturity: 'industrialization',
    region: '河北省・唐山市',
    holder: '华北理工大学',
    viewCount: 31,
    publishDate: '2024-01-30'
  },
  {
    id: 10,
    title: '智能选矿控制系统',
    code: 'CG260100140',
    techField: 'automation',
    transformation: 'service',
    transformationText: '技术服务、合作开发',
    maturity: 'pilot',
    region: '湖南省・长沙市',
    holder: '中南大学',
    viewCount: 19,
    publishDate: '2024-03-12'
  },
  {
    id: 11,
    title: '矿山应急救援装备',
    code: 'CG260100141',
    techField: 'safety',
    transformation: 'cooperation',
    transformationText: '合作开发、技术许可',
    maturity: 'demonstration',
    region: '陕西省・西安市',
    holder: '西安科技大学',
    viewCount: 27,
    publishDate: '2024-02-25'
  },
  {
    id: 12,
    title: '数字化矿山建模软件',
    code: 'CG260100142',
    techField: 'digital',
    transformation: 'license',
    transformationText: '技术许可、技术服务',
    maturity: 'industrialization',
    region: '上海市',
    holder: '同济大学',
    viewCount: 34,
    publishDate: '2024-03-08'
  }
])

// 计算属性 - 过滤后的成果
const filteredAchievements = computed(() => {
  return achievements.value.filter(item => {
    // 关键词搜索
    const keywordMatch = !searchKeyword.value ||
      item.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) 


    // 技术领域筛选
    const techFieldMatch = !selectedTechField.value ||
      item.techField === selectedTechField.value
    

    // 成熟度筛选
    const maturityMatch = !selectedMaturity.value ||
      item.maturity === selectedMaturity.value

    // 转化方式筛选
    const transformationMatch = !selectedTransformation.value ||
      item.transformation === selectedTransformation.value

    // 所在地区筛选
    const regionMatch = selectedRegion.value === 'all' || !selectedRegion.value ||
  (() => {
    // 简单地区匹配逻辑
    const regionMap = {
      'north': ['北京', '天津', '河北', '山西', '内蒙古'],
      'east': ['上海', '江苏', '浙江', '安徽', '福建', '江西', '山东'],
      'south': ['广东', '广西', '海南'],
      'central': ['河南', '湖北', '湖南'],
      'northeast': ['辽宁', '吉林', '黑龙江'],
      'northwest': ['陕西', '甘肃', '青海', '宁夏', '新疆'],
      'southwest': ['四川', '贵州', '云南', '重庆', '西藏']
    }
    
    const selected = regionMap[selectedRegion.value]
    if (!selected) return true
    
    return selected.some(area => item.region.includes(area))
  })()

    return keywordMatch && techFieldMatch &&
           maturityMatch && transformationMatch && regionMatch
  })
})

// 计算属性 - 分页数据
const paginatedAchievements = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAchievements.value.slice(start, end)
})

// 辅助函数 - 获取标签文本
const getTechFieldLabel = (value) => {
  const field = techFields.value.find(item => item.value === value)
  return field ? field.label : value
}

const getMaturityLabel = (value) => {
  const maturity = maturities.value.find(item => item.value === value)
  return maturity ? maturity.label : value
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
  selectedMaturity.value = ''
  selectedTransformation.value = ''
  selectedRegion.value = 'all'
  currentPage.value = 1
}

// 筛选按钮切换方法
const toggleTechField = (value) => {
  selectedTechField.value = selectedTechField.value === value ? '' : value
  currentPage.value = 1
}

const toggleMaturity = (value) => {
  selectedMaturity.value = selectedMaturity.value === value ? '' : value
  currentPage.value = 1
}

const toggleTransformation = (value) => {
  selectedTransformation.value = selectedTransformation.value === value ? '' : value
  currentPage.value = 1
}

const toggleRegion = (value) => {
  selectedRegion.value = selectedRegion.value === value ? '' : value
  currentPage.value = 1
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// const handleContact = (id) => {
//   selectedQuestion.value = ''
//   humanServiceRequested.value = false
//   contactDialogVisible.value = true
// }

const handleContact = () => {
  contactDialogVisible.value = true
}

// 跳转到详情页
const goDetail = (id) => {
  router.push({
    name: 'AchievementDetail', // 用你路由里的 name
    params: { id }
  })
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
  width: 100%;
  padding: 0;
  margin: 0;
}

.achievement-list {
  margin-top: 5px;
  padding: 0 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  margin-left:100px;
}

.total-count {
  color: #909399;
  font-size: 20px;
}

/* 成果卡片改进 - 横向布局 */
.achievement-card {
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
  margin-bottom: 12px;
  background-color: #fff;
  transition: all 0.3s ease;
  /* 从第647行添加的宽度控制 */
  max-width: 1600px;
  margin-left: auto;
  margin-right: auto;
  max-height: 160px;
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


/* 搜索英雄区域 */
.search-hero {
  background-image: url('@/assets/搜索框背景.png');
  background-size: cover;
  background-position: center;
  height: 20vh;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  overflow: hidden;
  position: relative;
}

.search-hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.search-hero-content {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 800px;
  padding: 20px;
}

.search-container-hero {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.search-input-hero {
  flex: 1;
}

.search-actions-hero {
  display: flex;
  gap: 10px;
}

/* 新筛选区域 */
.filter-card-new {
  margin-bottom: 5px;
  border: none;
  box-shadow: none;
  padding: 0 20px;
}

.filter-section-new {
  padding: 15px 0;
}

.filter-left-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-category {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.filter-category-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  min-width: 80px;
  line-height: 32px;
  white-space: nowrap;
}

.filter-options {
  display: flex;
  flex-wrap: nowrap;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 5px;
  flex: 1;
}

.achievement-card:hover {
  background-color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.08);
  border-color: #409eff;
}

/* 新成果卡片布局 */
.achievement-content-new {
  display: flex;
  position: relative;
  right:20px;
  min-height: 120px;
}

.achievement-header {
  position: absolute;
  top: 0px;
  left: 0px;
  right: 160px;
  display: flex;
  align-items: center;

}

.achievement-title-new {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  flex: 1;
}

.view-count-header {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 14px;
}

.view-icon {
  font-size: 16px;
}

.title-divider {
  position: absolute;
  top: 30px;
  left: 20px;
  right: 160px;
  height: 1px;
  background-color: #ebeef5;
  margin: 8px 0;
}



.detail-info-section {
  position: absolute;
  top: 70px;
  left: 20px;
  right: 160px;
  display: flex;
  gap: 30px;
}

.info-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  align-items: flex-start;
  font-size: 14px;
  line-height: 1.4;
}

.info-label {
  color: #606266;
  font-weight: 500;
  max-width: 0px;
  white-space: nowrap;
}

.info-content {
  color: #303133;
  flex: 1;
}

.interaction-section {
  position: absolute;
  top: 50%;
  left: auto;     /* 关键：不让左边影响它 */
  right: 20px;
  transform: translateY(-15%);
  width: 120px;
  display: flex; /* 新增：弹性布局 */
  flex-direction: column; /* 新增：垂直排列 */
  gap: 12px; /* 新增：按钮之间的间距，可自行调整 */
  align-items: flex-end;
}


.contact-button-1 {
  width: 100%;
  height: 36px;
  font-weight: 600;
  border-radius: 18px;
  text-align: center;

}

.contact-button-2{
  width: 100%;
  height: 36px;
  font-weight: 600;
  border-radius: 18px;
  text-align: center;
}

</style>