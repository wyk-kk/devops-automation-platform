<template>
  <div class="dashboard">
    <h1 class="page-title">运维自动化平台</h1>
    
    <!-- 第一行：基础统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card server-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32"><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.serverCount }}</div>
              <div class="stat-label">服务器</div>
              <div class="stat-trend">
                <el-icon color="#67c23a"><TrendCharts /></el-icon>
                <span>在线 {{ stats.onlineServers }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card k8s-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32"><Grid /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ k8sStats.total_clusters }}</div>
              <div class="stat-label">K8s集群</div>
              <div class="stat-trend">
                <el-icon color="#409eff"><Connection /></el-icon>
                <span>活跃 {{ k8sStats.active_clusters }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card node-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32"><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ k8sStats.total_nodes }}</div>
              <div class="stat-label">总节点数</div>
              <div class="stat-trend">
                <el-icon color="#e6a23c"><Cpu /></el-icon>
                <span>{{ k8sStats.total_pods }} Pods</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card alert-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32"><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.alertCount }}</div>
              <div class="stat-label">待处理告警</div>
              <div class="stat-trend">
                <el-icon color="#f56c6c"><WarningFilled /></el-icon>
                <span>严重 {{ stats.criticalAlerts }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：K8s环境分布 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>资源使用趋势</span>
              <el-radio-group v-model="chartType" size="small">
                <el-radio-button label="server">服务器</el-radio-button>
                <el-radio-button label="k8s">K8s集群</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" style="width: 100%; height: 300px"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card style="height: 100%">
          <template #header>
            <div class="card-header">
              <span>K8s环境分布</span>
            </div>
          </template>
          <div ref="envChartRef" style="width: 100%; height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行：健康度评分和快速操作 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8">
        <el-card class="health-card">
          <template #header>
            <div class="card-header">
              <span>集群健康度</span>
            </div>
          </template>
          <div class="health-score">
            <el-progress 
              type="dashboard" 
              :percentage="healthScore" 
              :color="getHealthColor(healthScore)"
              :width="180"
            >
              <template #default="{ percentage }">
                <div class="health-text">
                  <div class="score">{{ percentage }}</div>
                  <div class="label">健康度</div>
                </div>
              </template>
            </el-progress>
            <div class="health-details">
              <div class="health-item">
                <el-tag :type="healthScore > 90 ? 'success' : 'warning'" effect="plain">
                  {{ healthScore > 90 ? '优秀' : healthScore > 70 ? '良好' : '需改进' }}
                </el-tag>
              </div>
              <div class="health-metrics">
                <div class="metric">
                  <span>节点就绪率:</span>
                  <strong>{{ nodeReadyRate }}%</strong>
                </div>
                <div class="metric">
                  <span>Pod运行率:</span>
                  <strong>{{ podRunningRate }}%</strong>
                </div>
                <div class="metric">
                  <span>告警数量:</span>
                  <strong>{{ stats.alertCount }}</strong>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <el-row :gutter="15">
            <el-col :span="6">
              <el-button 
                class="quick-btn" 
                @click="$router.push('/resources')"
                :icon="Monitor"
              >
                添加服务器
              </el-button>
            </el-col>
            <el-col :span="6">
              <el-button 
                class="quick-btn success" 
                @click="$router.push('/resources?tab=k8s')"
                :icon="Grid"
              >
                添加K8s集群
              </el-button>
            </el-col>
            <el-col :span="6">
              <el-button 
                class="quick-btn warning" 
                @click="$router.push('/scripts')"
                :icon="Document"
              >
                创建脚本
              </el-button>
            </el-col>
            <el-col :span="6">
              <el-button 
                class="quick-btn danger" 
                @click="$router.push('/alert-rules')"
                :icon="Setting"
              >
                配置告警
              </el-button>
            </el-col>
          </el-row>

          <el-divider />

          <div class="recent-activities">
            <h4>最近活动</h4>
            <el-timeline>
              <el-timeline-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :timestamp="activity.time"
                :type="activity.type"
              >
                {{ activity.content }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- K8s资源详情 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Kubernetes 集群状态</span>
              <el-button size="small" @click="refreshK8sData" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <el-table :data="k8sClusters" v-loading="loading" style="width: 100%">
            <el-table-column prop="name" label="集群名称" width="150" />
            <el-table-column prop="environment" label="环境" width="100">
              <template #default="{ row }">
                <el-tag :type="getEnvType(row.environment)" size="small">
                  {{ getEnvText(row.environment) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'connected' ? 'success' : 'danger'" size="small">
                  <el-icon><CircleCheck v-if="row.status === 'connected'" /><CircleClose v-else /></el-icon>
                  {{ row.status === 'connected' ? '正常' : '异常' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="version" label="版本" width="120" />
            <el-table-column label="资源统计" width="300">
              <template #default="{ row }">
                <div class="resource-tags">
                  <el-tag size="small">节点: {{ row.node_count }}</el-tag>
                  <el-tag size="small" type="success">Pod: {{ row.pod_count }}</el-tag>
                  <el-tag size="small" type="info">NS: {{ row.namespace_count }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="健康度" width="150">
              <template #default="{ row }">
                <el-progress 
                  :percentage="calculateClusterHealth(row)" 
                  :color="getHealthColor(calculateClusterHealth(row))"
                  :show-text="false"
                  style="width: 100px"
                />
                <span style="margin-left: 10px">{{ calculateClusterHealth(row) }}%</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewClusterDetail(row)">
                  详情
                </el-button>
                <el-button link type="success" size="small" @click="syncCluster(row)">
                  同步
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Monitor, Grid, Box, Bell, Document, Clock, Setting,
  TrendCharts, Connection, Cpu, WarningFilled,
  CircleCheck, CircleClose, Refresh
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/api'

const loading = ref(false)
const chartType = ref('server')
const trendChartRef = ref()
const envChartRef = ref()
let trendChart = null
let envChart = null

const stats = ref({
  serverCount: 0,
  onlineServers: 0,
  scriptCount: 0,
  taskCount: 0,
  alertCount: 0,
  criticalAlerts: 0
})

const k8sStats = ref({
  total_clusters: 0,
  active_clusters: 0,
  total_nodes: 0,
  total_pods: 0,
  total_namespaces: 0,
  clusters_by_env: {}
})

const k8sClusters = ref([])
const recentActivities = ref([
  { id: 1, content: '添加了新的K8s集群 production-k8s', time: '5分钟前', type: 'success' },
  { id: 2, content: '服务器 web-server-01 CPU使用率告警', time: '15分钟前', type: 'warning' },
  { id: 3, content: '执行了批量脚本任务', time: '1小时前', type: 'primary' },
])

const healthScore = computed(() => {
  // 简化的健康度计算
  const connectedClusters = k8sClusters.value.filter(c => c.status === 'connected').length
  const totalClusters = k8sClusters.value.length || 1
  const clusterHealth = (connectedClusters / totalClusters) * 40

  const alertPenalty = Math.min(stats.value.alertCount * 2, 30)
  const criticalPenalty = stats.value.criticalAlerts * 5

  return Math.max(0, Math.min(100, Math.round(clusterHealth + 60 - alertPenalty - criticalPenalty)))
})

const nodeReadyRate = computed(() => {
  // 假设所有节点都是就绪的（简化）
  return 95
})

const podRunningRate = computed(() => {
  // 假设大部分Pod都在运行（简化）
  return 92
})

onMounted(async () => {
  await fetchDashboardData()
  await nextTick()
  initCharts()
})

const fetchDashboardData = async () => {
  loading.value = true
  try {
    // 获取基础统计
    const [serversRes, scriptsRes, tasksRes, alertsRes, k8sStatsRes, k8sClustersRes] = await Promise.all([
      api.get('/servers'),
      api.get('/scripts'),
      api.get('/tasks'),
      api.get('/alerts?status=open'),
      api.get('/k8s/statistics'),
      api.get('/k8s/clusters')
    ])

    stats.value.serverCount = serversRes.data.length
    stats.value.onlineServers = serversRes.data.filter(s => s.status === 'online').length
    stats.value.scriptCount = scriptsRes.data.length
    stats.value.taskCount = tasksRes.data.length
    stats.value.alertCount = alertsRes.data.length
    stats.value.criticalAlerts = alertsRes.data.filter(a => a.level === 'critical').length

    k8sStats.value = k8sStatsRes.data
    k8sClusters.value = k8sClustersRes.data
  } catch (error) {
    console.error('获取仪表盘数据失败', error)
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    updateTrendChart()
  }

  if (envChartRef.value) {
    envChart = echarts.init(envChartRef.value)
    updateEnvChart()
  }

  window.addEventListener('resize', () => {
    trendChart?.resize()
    envChart?.resize()
  })
}

const updateTrendChart = () => {
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: chartType.value === 'server' ? 'CPU使用率' : 'Pod数量',
        type: 'line',
        smooth: true,
        data: chartType.value === 'server' 
          ? [65, 70, 68, 72, 69, 67, 71]
          : [120, 132, 101, 134, 90, 230, 210],
        areaStyle: {
          opacity: 0.3
        },
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
  
  trendChart?.setOption(option)
}

const updateEnvChart = () => {
  const envData = Object.entries(k8sStats.value.clusters_by_env).map(([name, value]) => ({
    name: getEnvText(name),
    value
  }))

  const option = {
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        data: envData.length > 0 ? envData : [
          { value: 1, name: '暂无数据' }
        ]
      }
    ]
  }

  envChart?.setOption(option)
}

const calculateClusterHealth = (cluster) => {
  if (cluster.status !== 'connected') return 0
  const base = 70
  const nodeBonus = Math.min(cluster.node_count * 5, 20)
  const podBonus = Math.min(cluster.pod_count / 10, 10)
  return Math.min(100, Math.round(base + nodeBonus + podBonus))
}

const getHealthColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 70) return '#e6a23c'
  if (score >= 50) return '#f56c6c'
  return '#909399'
}

const getEnvType = (env) => {
  const types = {
    prod: 'danger',
    staging: 'warning',
    test: 'info',
    dev: 'success'
  }
  return types[env] || ''
}

const getEnvText = (env) => {
  const texts = {
    prod: '生产',
    staging: '预发',
    test: '测试',
    dev: '开发'
  }
  return texts[env] || env
}

const refreshK8sData = async () => {
  await fetchDashboardData()
  ElMessage.success('数据已刷新')
}

const viewClusterDetail = (cluster) => {
  ElMessage.info(`查看集群 ${cluster.name} 详情（开发中）`)
}

const syncCluster = async (cluster) => {
  try {
    await api.post(`/k8s/clusters/${cluster.id}/sync`)
    ElMessage.success('同步任务已启动')
    setTimeout(() => refreshK8sData(), 3000)
  } catch (error) {
    ElMessage.error('同步失败')
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #303133;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.server-card .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.k8s-card .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.node-card .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.alert-card .stat-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.health-card {
  height: 100%;
}

.health-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.health-text {
  text-align: center;
}

.health-text .score {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
}

.health-text .label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.health-details {
  margin-top: 20px;
  width: 100%;
}

.health-item {
  text-align: center;
  margin-bottom: 15px;
}

.health-metrics {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.quick-btn {
  width: 100%;
  height: 48px;
  font-size: 14px;
}

.recent-activities h4 {
  margin: 10px 0;
  font-size: 14px;
  color: #606266;
}

.resource-tags {
  display: flex;
  gap: 8px;
}
</style>

