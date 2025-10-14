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

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409EFF;">
              <el-icon size="24"><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.total_alerts }}</div>
              <div class="stat-label">总告警数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #E6A23C;">
              <el-icon size="24"><WarningFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.open_alerts }}</div>
              <div class="stat-label">待处理</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #F56C6C;">
              <el-icon size="24"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.critical_alerts }}</div>
              <div class="stat-label">严重告警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67C23A;">
              <el-icon size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.resolved_alerts }}</div>
              <div class="stat-label">已解决</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 告警趋势图 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="card-header">
          <span>告警趋势（最近7天）</span>
        </div>
      </template>
      <div ref="chartRef" style="width: 100%; height: 300px"></div>
    </el-card>
    
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
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Bell, WarningFilled, CircleClose, CircleCheck } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/api'

const alerts = ref([])
const loading = ref(false)
const statusFilter = ref('open')
const chartRef = ref()
let chartInstance = null

const statistics = ref({
  total_alerts: 0,
  open_alerts: 0,
  acknowledged_alerts: 0,
  resolved_alerts: 0,
  critical_alerts: 0,
  error_alerts: 0,
  warning_alerts: 0,
  info_alerts: 0,
  alerts_by_type: {},
  alerts_by_server: {}
})

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

const fetchStatistics = async () => {
  try {
    const response = await api.get('/alert-rules/statistics/overview')
    statistics.value = response.data
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  }
}

const fetchTrends = async () => {
  try {
    const response = await api.get('/alert-rules/statistics/trends')
    const trends = response.data
    
    await nextTick()
    initChart(trends)
  } catch (error) {
    console.error('Failed to fetch trends:', error)
  }
}

const initChart = (trends) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const dates = trends.map(t => t.date)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['严重', '错误', '警告', '信息']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '严重',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: { width: 2 },
        areaStyle: { opacity: 0.5 },
        emphasis: { focus: 'series' },
        data: trends.map(t => t.critical),
        itemStyle: { color: '#F56C6C' }
      },
      {
        name: '错误',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: { width: 2 },
        areaStyle: { opacity: 0.5 },
        emphasis: { focus: 'series' },
        data: trends.map(t => t.error),
        itemStyle: { color: '#E6A23C' }
      },
      {
        name: '警告',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: { width: 2 },
        areaStyle: { opacity: 0.5 },
        emphasis: { focus: 'series' },
        data: trends.map(t => t.warning),
        itemStyle: { color: '#F39C12' }
      },
      {
        name: '信息',
        type: 'line',
        stack: 'Total',
        smooth: true,
        lineStyle: { width: 2 },
        areaStyle: { opacity: 0.5 },
        emphasis: { focus: 'series' },
        data: trends.map(t => t.info),
        itemStyle: { color: '#909399' }
      }
    ]
  }
  
  chartInstance.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

const acknowledgeAlert = async (alert) => {
  try {
    await api.post(`/alerts/${alert.id}/acknowledge`)
    ElMessage.success('已确认告警')
    fetchAlerts()
    fetchStatistics()
  } catch (error) {
    console.error('Failed to acknowledge alert:', error)
  }
}

const resolveAlert = async (alert) => {
  try {
    await api.post(`/alerts/${alert.id}/resolve`)
    ElMessage.success('已解决告警')
    fetchAlerts()
    fetchStatistics()
  } catch (error) {
    console.error('Failed to resolve alert:', error)
  }
}

onMounted(() => {
  fetchAlerts()
  fetchStatistics()
  fetchTrends()
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

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

