<template>
  <div class="achievement-detail">
    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button type="primary" :icon="ArrowLeft" @click="goBack">
        返回成果列表
      </el-button>
    </div>

    <!-- 成果详情卡片 -->
    <el-card class="detail-card">
      <!-- 成果标题和标签 -->
      <div class="detail-header">
        <div class="title-section">
          <h1 class="detail-title">{{ achievement.title }}</h1>
          <div class="tag-section">
            <el-tag :type="getTechFieldTagType(achievement.techField)" size="large">
              {{ getTechFieldLabel(achievement.techField) }}
            </el-tag>
            <el-tag :type="getTypeTagType(achievement.type)" size="large" style="margin-left: 10px">
              {{ getTypeLabel(achievement.type) }}
            </el-tag>
            <el-tag type="info" size="large" style="margin-left: 10px">
              成熟度：{{ getMaturityLabel(achievement.maturity) }}
            </el-tag>
            <el-tag type="warning" size="large" style="margin-left: 10px">
              转化方式：{{ getTransformationLabel(achievement.transformation) }}
            </el-tag>
          </div>
        </div>

        <div class="action-section">
          <el-button type="primary" size="large" @click="handleContact">
            <el-icon style="vertical-align: middle; margin-right: 5px">
              <Message />
            </el-icon>
            我要对接
          </el-button>
          <el-button size="large" @click="handleCollect">
            <el-icon style="vertical-align: middle; margin-right: 5px">
              <Star />
            </el-icon>
            {{ isCollected ? '已收藏' : '收藏' }}
          </el-button>
        </div>
      </div>

      <!-- 成果基本信息 -->
      <div class="basic-info">
        <el-descriptions title="成果基本信息" :column="2" border>
          <el-descriptions-item label="成果编号">
            {{ achievement.id }}
          </el-descriptions-item>
          <el-descriptions-item label="发布单位">
            {{ achievement.publisher }}
          </el-descriptions-item>
          <el-descriptions-item label="联系人">
            {{ achievement.contactPerson }}
          </el-descriptions-item>
          <el-descriptions-item label="联系电话">
            {{ achievement.contactPhone }}
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">
            {{ achievement.contactEmail }}
          </el-descriptions-item>
          <el-descriptions-item label="发布时间">
            {{ achievement.publishDate }}
          </el-descriptions-item>
          <el-descriptions-item label="浏览量">
            {{ achievement.viewCount }}
          </el-descriptions-item>
          <el-descriptions-item label="对接次数">
            {{ achievement.contactCount }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 成果详细介绍 -->
      <div class="detail-content">
        <div class="content-section">
          <h2 class="section-title">成果简介</h2>
          <p class="section-content">{{ achievement.description }}</p>
        </div>

        <div class="content-section">
          <h2 class="section-title">技术特点</h2>
          <ul class="tech-features">
            <li v-for="(feature, index) in achievement.techFeatures" :key="index">
              {{ feature }}
            </li>
          </ul>
        </div>

        <div class="content-section">
          <h2 class="section-title">应用领域</h2>
          <div class="application-areas">
            <el-tag
              v-for="area in achievement.applicationAreas"
              :key="area"
              type="info"
              size="medium"
              style="margin-right: 10px; margin-bottom: 10px"
            >
              {{ area }}
            </el-tag>
          </div>
        </div>

        <div class="content-section">
          <h2 class="section-title">经济效益</h2>
          <el-table :data="achievement.economicBenefits" style="width: 100%">
            <el-table-column prop="item" label="项目" width="200" />
            <el-table-column prop="value" label="数值" width="150" />
            <el-table-column prop="description" label="说明" />
          </el-table>
        </div>

        <div class="content-section">
          <h2 class="section-title">技术参数</h2>
          <el-table :data="achievement.techParameters" style="width: 100%">
            <el-table-column prop="name" label="参数名称" width="200" />
            <el-table-column prop="value" label="参数值" width="150" />
            <el-table-column prop="unit" label="单位" width="100" />
            <el-table-column prop="remark" label="备注" />
          </el-table>
        </div>

        <div class="content-section">
          <h2 class="section-title">合作要求</h2>
          <ul class="cooperation-requirements">
            <li v-for="(requirement, index) in achievement.cooperationRequirements" :key="index">
              {{ requirement }}
            </li>
          </ul>
        </div>

        <div class="content-section">
          <h2 class="section-title">附件下载</h2>
          <div class="attachments">
            <div v-for="attachment in achievement.attachments" :key="attachment.id" class="attachment-item">
              <el-link :icon="Document" type="primary" :underline="false">
                {{ attachment.name }} ({{ attachment.size }})
              </el-link>
              <el-button type="text" size="small" @click="downloadAttachment(attachment.id)">
                下载
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 相关成果 -->
      <div class="related-achievements" v-if="relatedAchievements.length > 0">
        <h2 class="section-title">相关成果推荐</h2>
        <el-row :gutter="20">
          <el-col
            v-for="item in relatedAchievements"
            :key="item.id"
            :xs="24"
            :sm="12"
            :md="8"
          >
            <el-card class="related-card" shadow="hover" @click="viewRelatedDetail(item.id)">
              <template #header>
                <div class="related-card-header">
                  <el-tag size="small">{{ getTechFieldLabel(item.techField) }}</el-tag>
                  <el-tag size="small" style="margin-left: 5px" :type="getTypeTagType(item.type)">
                    {{ getTypeLabel(item.type) }}
                  </el-tag>
                </div>
              </template>
              <h3 class="related-title">{{ item.title }}</h3>
              <p class="related-desc">{{ item.shortDescription }}</p>
              <div class="related-footer">
                <span class="related-date">{{ item.publishDate }}</span>
                <el-button type="text" size="small">查看详情</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 客服对话框（与成果大厅相同） -->
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
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Message, Star, Document } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 对话框控制
const contactDialogVisible = ref(false)
const selectedQuestion = ref('')
const humanServiceRequested = ref(false)
const isCollected = ref(false)

// 常见问题（与成果大厅相同）
const commonQuestions = ref([
  { id: '1', text: '这项技术的具体参数是什么？', answer: '具体技术参数请联系技术负责人获取详细资料。' },
  { id: '2', text: '这项技术的转化条件是什么？', answer: '转化条件包括技术使用费、合作方式等，具体可面谈商议。' },
  { id: '3', text: '是否有成功应用案例？', answer: '目前已在XX矿山成功应用，效果显著。' },
  { id: '4', text: '技术支持和服务内容？', answer: '提供技术培训、现场指导、后期维护等全方位服务。' }
])

// 模拟数据 - 成果详情
const achievement = ref({
  id: 1,
  title: '智能化矿山安全监测系统',
  description: '基于物联网的矿山安全实时监测系统，通过部署传感器网络实时监测矿山环境参数、设备状态和人员位置，实现安全隐患的智能预警和应急响应。系统具有高可靠性、易扩展性和智能化分析能力，已在多个矿山成功应用。',
  techField: 'safety',
  type: 'software',
  maturity: 'industrialization',
  transformation: 'transfer',
  publisher: '大连海事大学智慧矿山实验室',
  contactPerson: '张教授',
  contactPhone: '138****1234',
  contactEmail: 'zhang@dlmu.edu.cn',
  publishDate: '2024-03-15',
  viewCount: 1256,
  contactCount: 48,
  techFeatures: [
    '实时监测：7x24小时不间断监测矿山安全状态',
    '智能预警：基于AI算法的安全隐患智能识别与预警',
    '多参数融合：集成环境、设备、人员等多维度数据',
    '可视化展示：3D可视化界面，直观展示安全状态',
    '应急响应：自动触发应急预案，提高响应效率'
  ],
  applicationAreas: [
    '煤矿安全监测',
    '金属矿山安全',
    '非金属矿山安全',
    '隧道工程安全',
    '地下工程安全'
  ],
  economicBenefits: [
    { item: '安全事故率降低', value: '60%', description: '相比传统监测方式' },
    { item: '监测成本降低', value: '40%', description: '自动化监测替代人工巡检' },
    { item: '应急响应时间缩短', value: '70%', description: '从小时级到分钟级' },
    { item: '设备维护周期延长', value: '50%', description: '预测性维护减少故障' }
  ],
  techParameters: [
    { name: '监测精度', value: '99.5', unit: '%', remark: '环境参数监测' },
    { name: '响应时间', value: '＜5', unit: '秒', remark: '从监测到预警' },
    { name: '数据更新频率', value: '1', unit: '秒', remark: '实时数据更新' },
    { name: '系统可用性', value: '99.9', unit: '%', remark: '年可用率' },
    { name: '传感器数量支持', value: '1000+', unit: '个', remark: '单系统最大支持' }
  ],
  cooperationRequirements: [
    '合作方需具备相应的矿山运营资质',
    '需提供必要的现场实施条件',
    '接受技术培训和技术支持',
    '按照合同约定支付技术使用费',
    '保护知识产权，不得擅自转让'
  ],
  attachments: [
    { id: 1, name: '技术方案文档.pdf', size: '2.5MB' },
    { id: 2, name: '用户手册.docx', size: '1.8MB' },
    { id: 3, name: '应用案例介绍.pptx', size: '5.2MB' }
  ]
})

// 相关成果数据
const relatedAchievements = ref([
  {
    id: 2,
    title: '矿山应急救援装备系统',
    shortDescription: '集成多种救援装备的智能系统，提高救援效率。',
    techField: 'safety',
    type: 'equipment',
    publishDate: '2024-02-25'
  },
  {
    id: 3,
    title: '矿山地质安全评估系统',
    shortDescription: '基于地质数据的矿山安全评估与预警系统。',
    techField: 'safety',
    type: 'software',
    publishDate: '2024-03-10'
  },
  {
    id: 4,
    title: '智能通风控制系统',
    shortDescription: 'AI驱动的矿井通风智能调控系统。',
    techField: 'automation',
    type: 'software',
    publishDate: '2024-03-05'
  }
])

// 辅助函数（与成果大厅相同）
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

const getTechFieldLabel = (value) => {
  const techFields = [
    { value: 'mining', label: '采矿技术' },
    { value: 'safety', label: '安全技术' },
    { value: 'automation', label: '自动化技术' },
    { value: 'environment', label: '环保技术' },
    { value: 'energy', label: '能源技术' },
    { value: 'digital', label: '数字化技术' }
  ]
  const field = techFields.find(item => item.value === value)
  return field ? field.label : value
}

const getTypeLabel = (value) => {
  const types = [
    { value: 'patent', label: '专利' },
    { value: 'software', label: '软件著作权' },
    { value: 'paper', label: '学术论文' },
    { value: 'equipment', label: '设备装置' },
    { value: 'process', label: '工艺方法' },
    { value: 'standard', label: '技术标准' }
  ]
  const type = types.find(item => item.value === value)
  return type ? type.label : value
}

const getMaturityLabel = (value) => {
  const maturities = [
    { value: 'laboratory', label: '实验室阶段' },
    { value: 'pilot', label: '小试阶段' },
    { value: 'demonstration', label: '中试示范' },
    { value: 'industrialization', label: '产业化' }
  ]
  const maturity = maturities.find(item => item.value === value)
  return maturity ? maturity.label : value
}

const getTransformationLabel = (value) => {
  const methods = [
    { value: 'transfer', label: '技术转让' },
    { value: 'license', label: '技术许可' },
    { value: 'cooperation', label: '合作开发' },
    { value: 'investment', label: '技术入股' },
    { value: 'service', label: '技术服务' }
  ]
  const method = methods.find(item => item.value === value)
  return method ? method.label : value
}

const getAnswer = (questionId) => {
  const question = commonQuestions.value.find(item => item.id === questionId)
  return question ? question.answer : ''
}

// 方法
const goBack = () => {
  router.push('/achievement-center')
}

const handleContact = () => {
  selectedQuestion.value = ''
  humanServiceRequested.value = false
  contactDialogVisible.value = true
}

const handleCollect = () => {
  isCollected.value = !isCollected.value
  const message = isCollected.value ? '收藏成功' : '取消收藏'
  ElMessage.success(message)
}

const downloadAttachment = (attachmentId) => {
  ElMessage.info('开始下载附件（模拟）')
  // 这里添加实际下载逻辑
}

const viewRelatedDetail = (id) => {
  router.push(`/achievement-detail/${id}`)
}

const requestHumanService = () => {
  humanServiceRequested.value = true
}

onMounted(() => {
  // 这里可以根据路由参数加载实际数据
  const achievementId = route.params.id
  console.log('加载成果详情，ID:', achievementId)
  // 实际项目中应该根据ID从API获取数据
})
</script>

<style scoped>
.achievement-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.back-button {
  margin-bottom: 20px;
}

.detail-card {
  padding: 30px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.title-section {
  flex: 1;
  margin-right: 20px;
}

.detail-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
  line-height: 1.3;
}

.tag-section {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.action-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 180px;
}

.basic-info {
  margin: 30px 0;
}

.detail-content {
  margin-top: 40px;
}

.content-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.content-section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.section-content {
  font-size: 16px;
  line-height: 1.8;
  color: #606266;
}

.tech-features {
  list-style-type: none;
  padding-left: 0;
}

.tech-features li {
  position: relative;
  padding-left: 20px;
  margin-bottom: 10px;
  font-size: 16px;
  line-height: 1.6;
  color: #606266;
}

.tech-features li:before {
  content: "•";
  color: #409eff;
  font-size: 20px;
  position: absolute;
  left: 0;
  top: -2px;
}

.application-areas {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.cooperation-requirements {
  list-style-type: none;
  padding-left: 0;
}

.cooperation-requirements li {
  position: relative;
  padding-left: 20px;
  margin-bottom: 10px;
  font-size: 16px;
  line-height: 1.6;
  color: #606266;
}

.cooperation-requirements li:before {
  content: "✓";
  color: #67c23a;
  font-size: 16px;
  position: absolute;
  left: 0;
  top: 2px;
}

.attachments {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.related-achievements {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #ebeef5;
}

.related-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.related-card:hover {
  transform: translateY(-5px);
}

.related-card-header {
  display: flex;
  align-items: center;
}

.related-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
  line-height: 1.4;
}

.related-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.related-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.related-date {
  font-size: 12px;
  color: #909399;
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

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
  }

  .title-section {
    margin-right: 0;
    margin-bottom: 20px;
  }

  .action-section {
    width: 100%;
    flex-direction: row;
    justify-content: flex-start;
  }

  .tag-section {
    flex-wrap: wrap;
  }
}
</style>