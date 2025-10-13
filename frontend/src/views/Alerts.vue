<template>
  <div class="alerts-page">
    <div class="page-header">
      <h1 class="page-title">告警管理</h1>
      <el-radio-group v-model="statusFilter" @change="fetchAlerts">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="open">待处理</el-radio-button>
        <el-radio-button label="acknowledged">已确认</el-radio-button>
        <el-radio-button label="resolved">已解决</el-radio-button>
      </el-radio-group>
    </div>
    
    <el-card>
      <el-table :data="alerts" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="alert_type" label="类型" width="100">
          <template #default="scope">
            <el-tag>{{ scope.row.alert_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="scope">
            <el-tag :type="getLevelType(scope.row.level)">
              {{ scope.row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="message" label="消息" show-overflow-tooltip />
        <el-table-column prop="current_value" label="当前值" width="100">
          <template #default="scope">
            {{ scope.row.current_value ? scope.row.current_value.toFixed(2) + '%' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="triggered_at" label="触发时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'open'" 
              size="small" 
              type="primary" 
              @click="acknowledgeAlert(scope.row)"
            >
              确认
            </el-button>
            <el-button 
              v-if="scope.row.status !== 'resolved'" 
              size="small" 
              type="success" 
              @click="resolveAlert(scope.row)"
            >
              解决
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const alerts = ref([])
const loading = ref(false)
const statusFilter = ref('open')

const getLevelType = (level) => {
  const types = {
    'info': 'info',
    'warning': 'warning',
    'error': 'danger',
    'critical': 'danger'
  }
  return types[level] || 'info'
}

const getStatusType = (status) => {
  const types = {
    'open': 'danger',
    'acknowledged': 'warning',
    'resolved': 'success'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'open': '待处理',
    'acknowledged': '已确认',
    'resolved': '已解决'
  }
  return texts[status] || status
}

const fetchAlerts = async () => {
  loading.value = true
  try {
    const params = statusFilter.value ? `?status=${statusFilter.value}` : ''
    const response = await api.get(`/alerts${params}`)
    alerts.value = response.data
  } catch (error) {
    console.error('Failed to fetch alerts:', error)
  } finally {
    loading.value = false
  }
}

const acknowledgeAlert = async (alert) => {
  try {
    await api.post(`/alerts/${alert.id}/acknowledge`)
    ElMessage.success('已确认告警')
    fetchAlerts()
  } catch (error) {
    console.error('Failed to acknowledge alert:', error)
  }
}

const resolveAlert = async (alert) => {
  try {
    await api.post(`/alerts/${alert.id}/resolve`)
    ElMessage.success('已解决告警')
    fetchAlerts()
  } catch (error) {
    console.error('Failed to resolve alert:', error)
  }
}

onMounted(() => {
  fetchAlerts()
})
</script>

<style scoped>
.alerts-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  margin: 0;
  color: #333;
}
</style>

