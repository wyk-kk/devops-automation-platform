<template>
  <div class="resources-page">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>资源管理</h2>
          <p class="subtitle">管理服务器和Kubernetes集群</p>
        </div>
        <el-button-group>
          <el-button 
            type="primary" 
            @click="showCreateDialog('server')"
            :icon="Monitor"
          >
            添加服务器
          </el-button>
          <el-button 
            type="success" 
            @click="showCreateDialog('k8s')"
            :icon="Grid"
          >
            添加K8s集群
          </el-button>
        </el-button-group>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409EFF;">
              <el-icon size="24"><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ servers.length }}</div>
              <div class="stat-label">服务器</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67C23A;">
              <el-icon size="24"><Grid /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ k8sClusters.length }}</div>
              <div class="stat-label">K8s集群</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #E6A23C;">
              <el-icon size="24"><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalNodes }}</div>
              <div class="stat-label">总节点数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Tab切换 -->
    <el-card class="content-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="服务器" name="servers">
          <el-table :data="servers" v-loading="loading" stripe>
            <el-table-column prop="name" label="名称" width="150" />
            <el-table-column prop="host" label="IP地址" width="150" />
            <el-table-column prop="port" label="端口" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'online' ? 'success' : 'danger'">
                  {{ row.status === 'online' ? '在线' : '离线' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="资源使用" min-width="200">
              <template #default="{ row }">
                <div class="resource-bars">
                  <div class="resource-item">
                    <span>CPU:</span>
                    <el-progress :percentage="row.cpu_percent || 0" :color="getProgressColor(row.cpu_percent)" />
                  </div>
                  <div class="resource-item">
                    <span>内存:</span>
                    <el-progress :percentage="row.memory_percent || 0" :color="getProgressColor(row.memory_percent)" />
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewServerDetail(row)">
                  详情
                </el-button>
                <el-button link type="success" size="small" @click="showWebTerminal(row)">
                  <el-icon><Monitor /></el-icon> 终端
                </el-button>
                <el-button link type="warning" size="small" @click="testServerConnection(row)">
                  测试
                </el-button>
                <el-button link type="danger" size="small" @click="deleteResource('server', row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="K8s集群" name="k8s">
          <el-table :data="k8sClusters" v-loading="loading" stripe>
            <el-table-column prop="name" label="集群名称" width="150" />
            <el-table-column prop="api_server" label="API Server" min-width="200" show-overflow-tooltip />
            <el-table-column prop="version" label="版本" width="120" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getK8sStatusType(row.status)">
                  {{ getK8sStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="资源统计" width="280">
              <template #default="{ row }">
                <div class="k8s-stats">
                  <el-tag size="small">节点: {{ row.node_count }}</el-tag>
                  <el-tag size="small" type="success">Pod: {{ row.pod_count }}</el-tag>
                  <el-tag size="small" type="info">NS: {{ row.namespace_count }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewK8sDetail(row)">
                  详情
                </el-button>
                <el-button link type="success" size="small" @click="syncK8sCluster(row)">
                  同步
                </el-button>
                <el-button link type="danger" size="small" @click="deleteResource('k8s', row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 创建服务器对话框 -->
    <el-dialog v-model="serverDialogVisible" title="添加服务器" width="600px">
      <el-form :model="serverForm" label-width="100px">
        <el-form-item label="服务器名称">
          <el-input v-model="serverForm.name" placeholder="输入服务器名称" />
        </el-form-item>
        <el-form-item label="IP地址">
          <el-input v-model="serverForm.host" placeholder="192.168.1.100" />
        </el-form-item>
        <el-form-item label="SSH端口">
          <el-input-number v-model="serverForm.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="serverForm.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="serverForm.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="serverDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createServer" :loading="saving">创建</el-button>
      </template>
    </el-dialog>

    <!-- 创建K8s集群对话框 -->
    <el-dialog v-model="k8sDialogVisible" title="添加K8s集群" width="700px">
      <el-form :model="k8sForm" label-width="120px">
        <el-form-item label="集群名称">
          <el-input v-model="k8sForm.name" placeholder="输入集群名称" />
        </el-form-item>
        <el-form-item label="API Server">
          <el-input v-model="k8sForm.api_server" placeholder="https://k8s.example.com:6443" />
        </el-form-item>
        <el-form-item label="认证方式">
          <el-select v-model="k8sForm.auth_type" style="width: 100%">
            <el-option label="Kubeconfig" value="kubeconfig" />
            <el-option label="Token" value="token" />
            <el-option label="证书" value="cert" />
          </el-select>
        </el-form-item>
        <el-form-item label="Kubeconfig" v-if="k8sForm.auth_type === 'kubeconfig'">
          <el-input 
            v-model="k8sForm.kubeconfig" 
            type="textarea" 
            :rows="8"
            placeholder="粘贴kubeconfig内容"
          />
        </el-form-item>
        <el-form-item label="Token" v-if="k8sForm.auth_type === 'token'">
          <el-input 
            v-model="k8sForm.token" 
            type="textarea" 
            :rows="3"
            placeholder="输入Token"
          />
        </el-form-item>
        <el-form-item label="环境">
          <el-select v-model="k8sForm.environment" style="width: 100%">
            <el-option label="开发环境" value="dev" />
            <el-option label="测试环境" value="test" />
            <el-option label="预发环境" value="staging" />
            <el-option label="生产环境" value="prod" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="k8sDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createK8sCluster" :loading="saving">创建</el-button>
      </template>
    </el-dialog>

    <!-- K8s集群详情对话框 -->
    <el-dialog 
      v-model="k8sDetailVisible" 
      :title="`集群详情 - ${currentCluster?.cluster_name || ''}`" 
      width="1200px"
      destroy-on-close
    >
      <div v-if="currentCluster" v-loading="detailLoading">
        <!-- 集群基本信息卡片 -->
        <el-card class="detail-info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-tag :type="getK8sStatusType(currentCluster.status)">
                {{ getK8sStatusText(currentCluster.status) }}
              </el-tag>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="info-item">
                <label>集群名称:</label>
                <span>{{ currentCluster.cluster_name }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>Kubernetes版本:</label>
                <span>{{ currentCluster.version || 'N/A' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>环境:</label>
                <el-tag size="small">{{ getEnvironmentText(currentCluster.environment) }}</el-tag>
              </div>
            </el-col>
            <el-col :span="24" style="margin-top: 15px;">
              <div class="info-item">
                <label>API Server:</label>
                <span>{{ currentCluster.api_server }}</span>
              </div>
            </el-col>
            <el-col :span="8" style="margin-top: 15px;">
              <div class="info-item">
                <label>节点数:</label>
                <span class="stat-number">{{ currentCluster.node_count || 0 }}</span>
              </div>
            </el-col>
            <el-col :span="8" style="margin-top: 15px;">
              <div class="info-item">
                <label>命名空间数:</label>
                <span class="stat-number">{{ currentCluster.namespace_count || 0 }}</span>
              </div>
            </el-col>
            <el-col :span="8" style="margin-top: 15px;">
              <div class="info-item">
                <label>Pod数:</label>
                <span class="stat-number">{{ currentCluster.pod_count || 0 }}</span>
              </div>
            </el-col>
            <el-col :span="12" style="margin-top: 15px;">
              <div class="info-item">
                <label>创建时间:</label>
                <span>{{ formatDateTime(currentCluster.created_at) }}</span>
              </div>
            </el-col>
            <el-col :span="12" style="margin-top: 15px;">
              <div class="info-item">
                <label>最后检查:</label>
                <span>{{ formatDateTime(currentCluster.last_check_time) }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- Tab切换查看详细资源 -->
        <el-tabs v-model="detailTab" style="margin-top: 20px;">
          <!-- 节点列表 -->
          <el-tab-pane label="节点列表" name="nodes">
            <el-table :data="clusterNodes" stripe max-height="400">
              <el-table-column prop="node_name" label="节点名称" width="180" />
              <el-table-column prop="node_ip" label="IP地址" width="150" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'Ready' ? 'success' : 'danger'" size="small">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="角色" width="120">
                <template #default="{ row }">
                  <el-tag v-for="role in row.roles" :key="role" size="small" type="info" style="margin-right: 5px;">
                    {{ role }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="资源容量" width="200">
                <template #default="{ row }">
                  <div style="font-size: 12px;">
                    <div>CPU: {{ row.cpu_capacity }}</div>
                    <div>内存: {{ row.memory_capacity }}</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="os_image" label="操作系统" min-width="200" show-overflow-tooltip />
              <el-table-column prop="kubelet_version" label="Kubelet版本" width="120" />
            </el-table>
          </el-tab-pane>

          <!-- 命名空间列表 -->
          <el-tab-pane label="命名空间" name="namespaces">
            <el-table :data="clusterNamespaces" stripe max-height="400">
              <el-table-column prop="namespace_name" label="命名空间" width="200" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="标签" min-width="300">
                <template #default="{ row }">
                  <el-tag 
                    v-for="(value, key) in row.labels" 
                    :key="key" 
                    size="small" 
                    style="margin: 2px;"
                  >
                    {{ key }}: {{ value }}
                  </el-tag>
                  <span v-if="!row.labels || Object.keys(row.labels).length === 0">-</span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- Pod列表 -->
          <el-tab-pane label="Pod列表" name="pods">
            <el-table :data="clusterPods" stripe max-height="400">
              <el-table-column prop="pod_name" label="Pod名称" width="250" show-overflow-tooltip />
              <el-table-column prop="namespace" label="命名空间" width="150" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag 
                    :type="getPodStatusType(row.status)" 
                    size="small"
                  >
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="node_name" label="所在节点" width="180" show-overflow-tooltip />
              <el-table-column prop="pod_ip" label="Pod IP" width="130" />
              <el-table-column label="容器" width="100">
                <template #default="{ row }">
                  {{ row.ready_containers }}/{{ row.total_containers }}
                </template>
              </el-table-column>
              <el-table-column prop="restart_count" label="重启次数" width="100" />
              <el-table-column label="运行时间" min-width="150">
                <template #default="{ row }">
                  {{ formatDateTime(row.start_time) }}
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <el-button @click="k8sDetailVisible = false">关闭</el-button>
        <el-button type="success" @click="loadClusterDetails(currentCluster.id)">
          刷新数据
        </el-button>
      </template>
    </el-dialog>

    <!-- 服务器详情对话框 -->
    <el-dialog 
      v-model="serverDetailVisible" 
      :title="`服务器详情 - ${currentDetailServer?.name || ''}`" 
      width="900px"
      destroy-on-close
    >
      <div v-if="currentDetailServer" v-loading="serverDetailLoading">
        <!-- 基本信息卡片 -->
        <el-card class="detail-info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-tag :type="currentDetailServer.status === 'online' ? 'success' : 'danger'">
                {{ currentDetailServer.status === 'online' ? '在线' : '离线' }}
              </el-tag>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="info-item">
                <label>服务器名称:</label>
                <span>{{ currentDetailServer.name }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>IP地址:</label>
                <span>{{ currentDetailServer.host }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>SSH端口:</label>
                <span>{{ currentDetailServer.port }}</span>
              </div>
            </el-col>
            <el-col :span="8" style="margin-top: 15px;">
              <div class="info-item">
                <label>用户名:</label>
                <span>{{ currentDetailServer.username }}</span>
              </div>
            </el-col>
            <el-col :span="8" style="margin-top: 15px;">
              <div class="info-item">
                <label>操作系统:</label>
                <span>{{ currentDetailServer.os_type || '-' }} {{ currentDetailServer.os_version || '' }}</span>
              </div>
            </el-col>
            <el-col :span="8" style="margin-top: 15px;">
              <div class="info-item">
                <label>CPU核心数:</label>
                <span>{{ currentDetailServer.cpu_cores || '-' }}</span>
              </div>
            </el-col>
            <el-col :span="12" style="margin-top: 15px;">
              <div class="info-item">
                <label>总内存:</label>
                <span>{{ currentDetailServer.memory_total || '-' }} MB</span>
              </div>
            </el-col>
            <el-col :span="12" style="margin-top: 15px;">
              <div class="info-item">
                <label>总磁盘:</label>
                <span>{{ currentDetailServer.disk_total || '-' }} GB</span>
              </div>
            </el-col>
            <el-col :span="12" style="margin-top: 15px;">
              <div class="info-item">
                <label>创建时间:</label>
                <span>{{ formatDateTime(currentDetailServer.created_at) }}</span>
              </div>
            </el-col>
            <el-col :span="12" style="margin-top: 15px;">
              <div class="info-item">
                <label>最后检查:</label>
                <span>{{ formatDateTime(currentDetailServer.last_check_time) }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 实时资源使用情况 -->
        <el-card v-if="serverDetailInfo" class="detail-info-card" shadow="never" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>实时资源使用</span>
              <el-tag type="info" size="small">{{ formatDateTime(serverDetailInfo.check_time) }}</el-tag>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="resource-chart">
                <div class="resource-label">CPU使用率</div>
                <el-progress 
                  :percentage="serverDetailInfo.cpu_percent || 0" 
                  :color="getProgressColor(serverDetailInfo.cpu_percent)"
                  :stroke-width="20"
                >
                  <span style="font-size: 14px;">{{ (serverDetailInfo.cpu_percent || 0).toFixed(2) }}%</span>
                </el-progress>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="resource-chart">
                <div class="resource-label">内存使用率</div>
                <el-progress 
                  :percentage="serverDetailInfo.memory_percent || 0" 
                  :color="getProgressColor(serverDetailInfo.memory_percent)"
                  :stroke-width="20"
                >
                  <span style="font-size: 14px;">{{ (serverDetailInfo.memory_percent || 0).toFixed(2) }}%</span>
                </el-progress>
                <div class="resource-detail">
                  {{ serverDetailInfo.memory_used || 0 }} MB / {{ serverDetailInfo.memory_total || 0 }} MB
                </div>
              </div>
            </el-col>
            <el-col :span="12" style="margin-top: 20px;">
              <div class="resource-chart">
                <div class="resource-label">磁盘使用率</div>
                <el-progress 
                  :percentage="serverDetailInfo.disk_percent || 0" 
                  :color="getProgressColor(serverDetailInfo.disk_percent)"
                  :stroke-width="20"
                >
                  <span style="font-size: 14px;">{{ (serverDetailInfo.disk_percent || 0).toFixed(2) }}%</span>
                </el-progress>
                <div class="resource-detail">
                  {{ serverDetailInfo.disk_used || 0 }} GB / {{ serverDetailInfo.disk_total || 0 }} GB
                </div>
              </div>
            </el-col>
            <el-col :span="12" style="margin-top: 20px;">
              <div class="resource-chart">
                <div class="resource-label">系统运行时间</div>
                <div style="padding: 10px; text-align: center; font-size: 16px; color: #409EFF;">
                  {{ serverDetailInfo.uptime || '-' }}
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 离线提示 -->
        <el-alert 
          v-if="currentDetailServer.status !== 'online'" 
          type="warning"
          :closable="false"
          show-icon
          style="margin-top: 20px;"
        >
          <template #title>
            服务器离线，无法获取实时资源使用情况
          </template>
        </el-alert>
      </div>

      <template #footer>
        <el-button @click="serverDetailVisible = false">关闭</el-button>
        <el-button type="primary" @click="refreshServerInfo" :loading="serverDetailLoading">
          刷新信息
        </el-button>
      </template>
    </el-dialog>

    <!-- Web Terminal对话框 -->
    <el-dialog 
      v-model="terminalDialogVisible" 
      :title="`Web Terminal - ${terminalServer?.name || ''}`" 
      width="1000px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div style="height: 500px;">
        <WebTerminal 
          v-if="terminalDialogVisible && terminalServer"
          :server-id="terminalServer.id"
          :title="`${terminalServer.host}:${terminalServer.port}`"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Monitor, Grid, Box, Loading } from '@element-plus/icons-vue'
import api from '@/api'
import WebTerminal from '@/components/WebTerminal.vue'

const loading = ref(false)
const saving = ref(false)
const activeTab = ref('servers')
const servers = ref([])
const k8sClusters = ref([])

const serverDialogVisible = ref(false)
const k8sDialogVisible = ref(false)

const serverForm = ref({
  name: '',
  host: '',  // 修复：改为host以匹配后端
  port: 22,
  username: 'root',
  password: ''
})

const k8sForm = ref({
  name: '',
  api_server: '',
  auth_type: 'kubeconfig',
  kubeconfig: '',
  token: '',
  environment: 'dev'
})

const totalNodes = computed(() => {
  const serverNodes = servers.value.length
  const k8sNodes = k8sClusters.value.reduce((sum, cluster) => sum + (cluster.node_count || 0), 0)
  return serverNodes + k8sNodes
})

// 定时刷新资源使用率
let refreshInterval = null

onMounted(() => {
  fetchServers()
  fetchK8sClusters()
  
  // 每30秒自动刷新一次服务器资源使用率
  refreshInterval = setInterval(() => {
    if (activeTab.value === 'servers' && servers.value.length > 0) {
      servers.value.forEach(server => {
        if (server.status === 'online') {
          fetchServerStatus(server.id)
        }
      })
    }
  }, 30000) // 30秒刷新一次
})

onBeforeUnmount(() => {
  // 清除定时器
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

const fetchServers = async () => {
  loading.value = true
  try {
    const response = await api.get('/servers')
    servers.value = response.data
    
    // 异步获取每个服务器的实时资源使用率
    servers.value.forEach(server => {
      fetchServerStatus(server.id)
    })
  } catch (error) {
    ElMessage.error('获取服务器列表失败')
  } finally {
    loading.value = false
  }
}

// 获取单个服务器的实时状态
const fetchServerStatus = async (serverId) => {
  try {
    const response = await api.get(`/servers/${serverId}/status`)
    // 更新对应服务器的资源使用率
    const server = servers.value.find(s => s.id === serverId)
    if (server && response.data) {
      server.cpu_percent = response.data.cpu_percent || 0
      server.memory_percent = response.data.memory_percent || 0
      server.disk_percent = response.data.disk_percent || 0
      server.uptime = response.data.uptime || 'unknown'
    }
  } catch (error) {
    // 静默失败，不影响列表显示
    console.error(`Failed to fetch status for server ${serverId}:`, error)
  }
}

const fetchK8sClusters = async () => {
  loading.value = true
  try {
    const response = await api.get('/k8s/clusters')
    k8sClusters.value = response.data
  } catch (error) {
    ElMessage.error('获取K8s集群列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = (type) => {
  if (type === 'server') {
    serverDialogVisible.value = true
  } else {
    k8sDialogVisible.value = true
  }
}

const createServer = async () => {
  saving.value = true
  try {
    await api.post('/servers', serverForm.value)
    ElMessage.success('服务器添加成功')
    serverDialogVisible.value = false
    fetchServers()
  } catch (error) {
    ElMessage.error('添加服务器失败')
  } finally {
    saving.value = false
  }
}

const createK8sCluster = async () => {
  saving.value = true
  try {
    await api.post('/k8s/clusters', k8sForm.value)
    ElMessage.success('K8s集群添加成功')
    k8sDialogVisible.value = false
    fetchK8sClusters()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加K8s集群失败')
  } finally {
    saving.value = false
  }
}

const syncK8sCluster = async (cluster) => {
  try {
    await api.post(`/k8s/clusters/${cluster.id}/sync`)
    ElMessage.success('同步任务已启动')
    setTimeout(() => fetchK8sClusters(), 3000)
  } catch (error) {
    ElMessage.error('同步失败')
  }
}

const deleteResource = async (type, resource) => {
  try {
    await ElMessageBox.confirm(`确定要删除${type === 'server' ? '服务器' : 'K8s集群'} "${resource.name}" 吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    if (type === 'server') {
      await api.delete(`/servers/${resource.id}`)
      ElMessage.success('服务器删除成功')
      fetchServers()
    } else {
      await api.delete(`/k8s/clusters/${resource.id}`)
      ElMessage.success('K8s集群删除成功')
      fetchK8sClusters()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 服务器详情相关
const serverDetailVisible = ref(false)
const currentDetailServer = ref(null)
const serverDetailInfo = ref(null)
const serverDetailLoading = ref(false)

const viewServerDetail = async (server) => {
  currentDetailServer.value = server
  serverDetailVisible.value = true
  await loadServerDetail(server.id)
}

const loadServerDetail = async (serverId) => {
  serverDetailLoading.value = true
  try {
    const response = await api.get(`/servers/${serverId}/status`)
    serverDetailInfo.value = response.data
  } catch (error) {
    ElMessage.error('加载服务器详情失败')
  } finally {
    serverDetailLoading.value = false
  }
}

const refreshServerInfo = async () => {
  if (!currentDetailServer.value) return
  
  try {
    await api.post(`/servers/${currentDetailServer.value.id}/refresh`)
    ElMessage.success('服务器信息已刷新')
    await loadServerDetail(currentDetailServer.value.id)
    fetchServers() // 刷新列表
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

// Web Terminal相关
const terminalDialogVisible = ref(false)
const terminalServer = ref(null)

const showWebTerminal = (server) => {
  if (server.status !== 'online') {
    ElMessage.warning('服务器离线，无法打开终端')
    return
  }
  terminalServer.value = server
  terminalDialogVisible.value = true
}

const testServerConnection = async (server) => {
  try {
    const response = await api.post(`/servers/${server.id}/test`)
    if (response.data.success) {
      ElMessage.success('连接测试成功')
      fetchServers() // 刷新列表以更新状态
    } else {
      ElMessage.error('连接测试失败：' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('连接测试失败')
  }
}

// K8s集群详情相关
const k8sDetailVisible = ref(false)
const currentCluster = ref(null)
const clusterNodes = ref([])
const clusterNamespaces = ref([])
const clusterPods = ref([])
const detailLoading = ref(false)
const detailTab = ref('overview')

const viewK8sDetail = async (cluster) => {
  currentCluster.value = cluster
  k8sDetailVisible.value = true
  detailTab.value = 'overview'
  
  // 加载详细信息
  await loadClusterDetails(cluster.id)
}

const loadClusterDetails = async (clusterId) => {
  detailLoading.value = true
  try {
    // 并行加载节点、命名空间、Pod信息
    const [nodesRes, nsRes, podsRes] = await Promise.all([
      api.get(`/k8s/clusters/${clusterId}/nodes`),
      api.get(`/k8s/clusters/${clusterId}/namespaces`),
      api.get(`/k8s/clusters/${clusterId}/pods`)
    ])
    
    clusterNodes.value = nodesRes.data
    clusterNamespaces.value = nsRes.data
    clusterPods.value = podsRes.data
  } catch (error) {
    ElMessage.error('加载集群详情失败')
  } finally {
    detailLoading.value = false
  }
}

const handleTabClick = () => {
  // Tab切换
}

const getProgressColor = (percent) => {
  if (percent > 80) return '#f56c6c'
  if (percent > 60) return '#e6a23c'
  return '#67c23a'
}

const getK8sStatusType = (status) => {
  const types = {
    connected: 'success',
    disconnected: 'danger',
    error: 'danger',
    unknown: 'info'
  }
  return types[status] || 'info'
}

const getK8sStatusText = (status) => {
  const texts = {
    connected: '已连接',
    disconnected: '未连接',
    error: '错误',
    unknown: '未知'
  }
  return texts[status] || status
}

const getEnvironmentText = (env) => {
  const texts = {
    dev: '开发环境',
    test: '测试环境',
    staging: '预发环境',
    prod: '生产环境'
  }
  return texts[env] || env
}

const getPodStatusType = (status) => {
  const types = {
    'Running': 'success',
    'Pending': 'warning',
    'Succeeded': 'success',
    'Failed': 'danger',
    'Unknown': 'info'
  }
  return types[status] || 'info'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  // 如果小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  // 如果小于1小时
  if (diff < 3600000) {
    return Math.floor(diff / 60000) + '分钟前'
  }
  // 如果小于1天
  if (diff < 86400000) {
    return Math.floor(diff / 3600000) + '小时前'
  }
  // 如果小于7天
  if (diff < 604800000) {
    return Math.floor(diff / 86400000) + '天前'
  }
  
  // 否则显示完整日期时间
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.resources-page {
  padding: 0;
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

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
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

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.content-card {
  margin-bottom: 20px;
}

.resource-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.resource-item span {
  width: 50px;
  font-size: 12px;
}

.k8s-stats {
  display: flex;
  gap: 8px;
}

/* K8s集群详情样式 */
.detail-info-card {
  margin-bottom: 20px;
}

.detail-info-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  line-height: 2;
}

.info-item label {
  font-weight: 500;
  color: #606266;
  margin-right: 10px;
  min-width: 100px;
}

.info-item span {
  color: #303133;
}

.info-item .stat-number {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

/* 资源图表样式 */
.resource-chart {
  padding: 10px 0;
}

.resource-label {
  margin-bottom: 10px;
  font-weight: 500;
  color: #606266;
}

.resource-detail {
  margin-top: 8px;
  text-align: center;
  font-size: 12px;
  color: #909399;
}
</style>

