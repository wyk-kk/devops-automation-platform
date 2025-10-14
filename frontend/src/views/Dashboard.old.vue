<template>
  <div class="dashboard">
    <h1 class="page-title">仪表盘</h1>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon server">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.serverCount }}</div>
              <div class="stat-label">服务器总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon script">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.scriptCount }}</div>
              <div class="stat-label">脚本总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon task">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.taskCount }}</div>
              <div class="stat-label">任务总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon alert">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.alertCount }}</div>
              <div class="stat-label">待处理告警</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速操作 -->
    <el-card class="section-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>快速操作</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-button type="primary" @click="$router.push('/servers')" style="width: 100%">
            <el-icon><Plus /></el-icon>
            添加服务器
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="success" @click="$router.push('/scripts')" style="width: 100%">
            <el-icon><Plus /></el-icon>
            创建脚本
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="warning" @click="$router.push('/tasks')" style="width: 100%">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="info" @click="$router.push('/alerts')" style="width: 100%">
            <el-icon><View /></el-icon>
            查看告警
          </el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 最近执行记录 -->
    <el-card class="section-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>最近执行记录</span>
        </div>
      </template>
      <el-table :data="recentExecutions" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="script_id" label="脚本ID" width="100" />
        <el-table-column prop="server_id" label="服务器ID" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" />
        <el-table-column prop="end_time" label="结束时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Monitor, Document, Clock, Bell, Plus, View } from '@element-plus/icons-vue'
import api from '@/api'

const stats = ref({
  serverCount: 0,
  scriptCount: 0,
  taskCount: 0,
  alertCount: 0
})

const recentExecutions = ref([])

const getStatusType = (status) => {
  const types = {
    'success': 'success',
    'failed': 'danger',
    'running': 'warning',
    'pending': 'info'
  }
  return types[status] || 'info'
}

const fetchStats = async () => {
  try {
    const [servers, scripts, tasks, alerts] = await Promise.all([
      api.get('/servers'),
      api.get('/scripts'),
      api.get('/tasks'),
      api.get('/alerts?status=open')
    ])
    
    stats.value = {
      serverCount: servers.data.length,
      scriptCount: scripts.data.length,
      taskCount: tasks.data.length,
      alertCount: alerts.data.length
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const fetchRecentExecutions = async () => {
  try {
    const response = await api.get('/scripts/executions/list?limit=10')
    recentExecutions.value = response.data
  } catch (error) {
    console.error('Failed to fetch executions:', error)
  }
}

onMounted(() => {
  fetchStats()
  fetchRecentExecutions()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.page-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  color: #fff;
}

.stat-icon.server {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.script {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.task {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.alert {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #999;
}

.section-card {
  margin-top: 20px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}
</style>

