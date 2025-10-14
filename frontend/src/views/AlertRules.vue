<template>
  <div class="alert-rules-container">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>告警规则管理</h2>
          <p class="subtitle">配置自定义告警规则和通知方式</p>
        </div>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          创建规则
        </el-button>
      </div>
    </el-card>

    <!-- 筛选器 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="服务器">
          <el-select v-model="filters.server_id" placeholder="全部服务器" clearable style="width: 200px">
            <el-option label="全局规则" :value="null" />
            <el-option
              v-for="server in servers"
              :key="server.id"
              :label="server.name"
              :value="server.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.is_active" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchRules">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 规则列表 -->
    <el-card class="table-card">
      <el-table :data="rules" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="规则名称" min-width="150" />
        <el-table-column label="应用范围" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.server_id === null" type="info">全局规则</el-tag>
            <el-tag v-else type="success">特定服务器</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="监控指标" width="100">
          <template #default="{ row }">
            <el-tag :type="getMetricTypeColor(row.metric_type)">
              {{ getMetricTypeName(row.metric_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="阈值条件" width="150">
          <template #default="{ row }">
            {{ getOperatorSymbol(row.threshold_operator) }} {{ row.threshold_value }}%
          </template>
        </el-table-column>
        <el-table-column label="告警级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelColor(row.alert_level)">
              {{ getLevelName(row.alert_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="通知方式" width="150">
          <template #default="{ row }">
            <div class="notification-methods">
              <el-icon v-if="row.enable_email" color="#409EFF"><Message /></el-icon>
              <el-icon v-if="row.enable_webhook" color="#67C23A"><Link /></el-icon>
              <span v-if="!row.enable_email && !row.enable_webhook" style="color: #909399">未配置</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="toggleRule(row)"
              :loading="row.toggling"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editRule(row)">
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="deleteRule(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑规则对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑规则' : '创建规则'"
      width="700px"
      @close="resetForm"
    >
      <el-form :model="ruleForm" :rules="rules" ref="formRef" label-width="120px">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基础配置" name="basic">
            <el-form-item label="规则名称" prop="name">
              <el-input v-model="ruleForm.name" placeholder="输入规则名称" />
            </el-form-item>
            
            <el-form-item label="规则描述" prop="description">
              <el-input v-model="ruleForm.description" type="textarea" :rows="2" placeholder="规则描述（可选）" />
            </el-form-item>

            <el-form-item label="应用范围" prop="server_id">
              <el-select v-model="ruleForm.server_id" placeholder="选择服务器" clearable style="width: 100%">
                <el-option label="全局规则（应用于所有服务器）" :value="null" />
                <el-option
                  v-for="server in servers"
                  :key="server.id"
                  :label="server.name"
                  :value="server.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="监控指标" prop="metric_type">
              <el-select v-model="ruleForm.metric_type" placeholder="选择监控指标" style="width: 100%">
                <el-option label="CPU使用率" value="cpu" />
                <el-option label="内存使用率" value="memory" />
                <el-option label="磁盘使用率" value="disk" />
                <el-option label="网络流量" value="network" />
              </el-select>
            </el-form-item>

            <el-form-item label="阈值条件" required>
              <el-row :gutter="10">
                <el-col :span="8">
                  <el-form-item prop="threshold_operator">
                    <el-select v-model="ruleForm.threshold_operator" placeholder="操作符">
                      <el-option label="大于 (>)" value="gt" />
                      <el-option label="大于等于 (≥)" value="gte" />
                      <el-option label="小于 (<)" value="lt" />
                      <el-option label="小于等于 (≤)" value="lte" />
                      <el-option label="等于 (=)" value="eq" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="16">
                  <el-form-item prop="threshold_value">
                    <el-input-number
                      v-model="ruleForm.threshold_value"
                      :min="0"
                      :max="100"
                      :precision="2"
                      style="width: 100%"
                    >
                      <template #suffix>%</template>
                    </el-input-number>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form-item>

            <el-form-item label="告警级别" prop="alert_level">
              <el-select v-model="ruleForm.alert_level" placeholder="选择告警级别" style="width: 100%">
                <el-option label="信息" value="info" />
                <el-option label="警告" value="warning" />
                <el-option label="错误" value="error" />
                <el-option label="严重" value="critical" />
              </el-select>
            </el-form-item>

            <el-form-item label="持续时间" prop="duration">
              <el-input-number
                v-model="ruleForm.duration"
                :min="0"
                :step="60"
                style="width: 100%"
              />
              <div class="form-tip">连续超过阈值多少秒后触发告警</div>
            </el-form-item>

            <el-form-item label="静默期" prop="silence_duration">
              <el-input-number
                v-model="ruleForm.silence_duration"
                :min="0"
                :step="60"
                style="width: 100%"
              />
              <div class="form-tip">触发告警后，多少秒内不再重复告警</div>
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="通知配置" name="notification">
            <el-form-item label="邮件通知">
              <el-switch v-model="ruleForm.enable_email" />
            </el-form-item>

            <el-form-item v-if="ruleForm.enable_email" label="收件人" prop="email_recipients">
              <el-select
                v-model="ruleForm.email_recipients"
                multiple
                filterable
                allow-create
                placeholder="输入邮箱地址，按回车添加"
                style="width: 100%"
              >
              </el-select>
              <div class="form-tip">可添加多个邮箱地址</div>
            </el-form-item>

            <el-divider />

            <el-form-item label="Webhook通知">
              <el-switch v-model="ruleForm.enable_webhook" />
            </el-form-item>

            <el-form-item v-if="ruleForm.enable_webhook" label="Webhook URL" prop="webhook_url">
              <el-input v-model="ruleForm.webhook_url" placeholder="https://your-webhook-url.com/notify" />
            </el-form-item>

            <el-form-item v-if="ruleForm.enable_webhook" label="测试Webhook">
              <el-button @click="testWebhook" :loading="testingWebhook">发送测试消息</el-button>
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRule" :loading="saving">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Message, Link } from '@element-plus/icons-vue'
import api from '@/api'

const loading = ref(false)
const rules = ref([])
const servers = ref([])

const filters = reactive({
  server_id: null,
  is_active: null
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const activeTab = ref('basic')
const formRef = ref()
const saving = ref(false)
const testingWebhook = ref(false)

const ruleForm = reactive({
  name: '',
  description: '',
  server_id: null,
  metric_type: '',
  threshold_value: 80,
  threshold_operator: 'gt',
  duration: 60,
  alert_level: 'warning',
  enable_email: false,
  email_recipients: [],
  enable_webhook: false,
  webhook_url: '',
  silence_duration: 300,
  is_active: true
})

const formRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  metric_type: [{ required: true, message: '请选择监控指标', trigger: 'change' }],
  threshold_value: [{ required: true, message: '请输入阈值', trigger: 'blur' }],
  threshold_operator: [{ required: true, message: '请选择操作符', trigger: 'change' }],
  alert_level: [{ required: true, message: '请选择告警级别', trigger: 'change' }]
}

onMounted(() => {
  fetchRules()
  fetchServers()
})

const fetchRules = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.server_id !== null) params.server_id = filters.server_id
    if (filters.is_active !== null) params.is_active = filters.is_active
    
    const response = await api.get('/alert-rules', { params })
    rules.value = response.data
  } catch (error) {
    ElMessage.error('获取告警规则失败')
  } finally {
    loading.value = false
  }
}

const fetchServers = async () => {
  try {
    const response = await api.get('/servers')
    servers.value = response.data
  } catch (error) {
    console.error('获取服务器列表失败', error)
  }
}

const resetFilters = () => {
  filters.server_id = null
  filters.is_active = null
  fetchRules()
}

const showCreateDialog = () => {
  isEdit.value = false
  dialogVisible.value = true
  activeTab.value = 'basic'
}

const editRule = (row) => {
  isEdit.value = true
  Object.assign(ruleForm, row)
  dialogVisible.value = true
  activeTab.value = 'basic'
}

const resetForm = () => {
  Object.assign(ruleForm, {
    name: '',
    description: '',
    server_id: null,
    metric_type: '',
    threshold_value: 80,
    threshold_operator: 'gt',
    duration: 60,
    alert_level: 'warning',
    enable_email: false,
    email_recipients: [],
    enable_webhook: false,
    webhook_url: '',
    silence_duration: 300,
    is_active: true
  })
  formRef.value?.clearValidate()
}

const saveRule = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    
    if (isEdit.value) {
      await api.put(`/alert-rules/${ruleForm.id}`, ruleForm)
      ElMessage.success('规则更新成功')
    } else {
      await api.post('/alert-rules', ruleForm)
      ElMessage.success('规则创建成功')
    }
    
    dialogVisible.value = false
    fetchRules()
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data.detail || '操作失败')
    }
  } finally {
    saving.value = false
  }
}

const toggleRule = async (row) => {
  row.toggling = true
  try {
    await api.post(`/alert-rules/${row.id}/toggle`)
    ElMessage.success(row.is_active ? '规则已启用' : '规则已禁用')
  } catch (error) {
    row.is_active = !row.is_active
    ElMessage.error('操作失败')
  } finally {
    row.toggling = false
  }
}

const deleteRule = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则 "${row.name}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.delete(`/alert-rules/${row.id}`)
    ElMessage.success('删除成功')
    fetchRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const testWebhook = async () => {
  if (!ruleForm.webhook_url) {
    ElMessage.warning('请先输入Webhook URL')
    return
  }
  
  testingWebhook.value = true
  try {
    const response = await api.post('/alert-rules/test-webhook', null, {
      params: { webhook_url: ruleForm.webhook_url }
    })
    
    if (response.data.success) {
      ElMessage.success('Webhook测试成功')
    } else {
      ElMessage.error(`Webhook测试失败: ${response.data.error || '未知错误'}`)
    }
  } catch (error) {
    ElMessage.error('Webhook测试失败')
  } finally {
    testingWebhook.value = false
  }
}

const getMetricTypeName = (type) => {
  const names = {
    cpu: 'CPU',
    memory: '内存',
    disk: '磁盘',
    network: '网络'
  }
  return names[type] || type
}

const getMetricTypeColor = (type) => {
  const colors = {
    cpu: '',
    memory: 'success',
    disk: 'warning',
    network: 'info'
  }
  return colors[type] || ''
}

const getOperatorSymbol = (op) => {
  const symbols = {
    gt: '>',
    gte: '≥',
    lt: '<',
    lte: '≤',
    eq: '='
  }
  return symbols[op] || op
}

const getLevelName = (level) => {
  const names = {
    info: '信息',
    warning: '警告',
    error: '错误',
    critical: '严重'
  }
  return names[level] || level
}

const getLevelColor = (level) => {
  const colors = {
    info: 'info',
    warning: 'warning',
    error: 'danger',
    critical: 'danger'
  }
  return colors[level] || ''
}
</script>

<style scoped>
.alert-rules-container {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.notification-methods {
  display: flex;
  gap: 8px;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

:deep(.el-input-number .el-input__inner) {
  text-align: left;
}
</style>

