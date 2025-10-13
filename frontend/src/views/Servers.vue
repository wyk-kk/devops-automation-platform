<template>
  <div class="servers-page">
    <div class="page-header">
      <h1 class="page-title">服务器管理</h1>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加服务器
      </el-button>
    </div>
    
    <el-card>
      <el-table :data="servers" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="host" label="主机地址" />
        <el-table-column prop="port" label="端口" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="os_type" label="系统" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="testConnection(scope.row)">测试连接</el-button>
            <el-button size="small" type="primary" @click="showStatus(scope.row)">查看状态</el-button>
            <el-button size="small" type="warning" @click="editServer(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteServer(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="服务器名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="主机地址" prop="host">
          <el-input v-model="form.host" placeholder="IP地址或域名" />
        </el-form-item>
        <el-form-item label="SSH端口" prop="port">
          <el-input-number v-model="form.port" :min="1" :max="65535" style="width: 100%" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 服务器状态对话框 -->
    <el-dialog v-model="statusDialogVisible" title="服务器状态" width="600px">
      <div v-if="serverStatus" class="status-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(serverStatus.status)">{{ serverStatus.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="检查时间">
            {{ serverStatus.check_time }}
          </el-descriptions-item>
          <el-descriptions-item label="CPU使用率">
            <el-progress :percentage="serverStatus.cpu_percent" :color="getProgressColor(serverStatus.cpu_percent)" />
          </el-descriptions-item>
          <el-descriptions-item label="内存使用率">
            <el-progress :percentage="serverStatus.memory_percent" :color="getProgressColor(serverStatus.memory_percent)" />
          </el-descriptions-item>
          <el-descriptions-item label="磁盘使用率">
            <el-progress :percentage="serverStatus.disk_percent" :color="getProgressColor(serverStatus.disk_percent)" />
          </el-descriptions-item>
          <el-descriptions-item label="运行时间">
            {{ serverStatus.uptime }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const servers = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('添加服务器')
const form = ref({
  name: '',
  host: '',
  port: 22,
  username: '',
  password: '',
  description: ''
})
const formRef = ref(null)
const submitting = ref(false)
const editingId = ref(null)

const statusDialogVisible = ref(false)
const serverStatus = ref(null)

const rules = {
  name: [{ required: true, message: '请输入服务器名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
}

const getStatusType = (status) => {
  const types = {
    'online': 'success',
    'offline': 'danger',
    'unknown': 'info'
  }
  return types[status] || 'info'
}

const getProgressColor = (percent) => {
  if (percent >= 90) return '#F56C6C'
  if (percent >= 70) return '#E6A23C'
  return '#67C23A'
}

const fetchServers = async () => {
  loading.value = true
  try {
    const response = await api.get('/servers')
    servers.value = response.data
  } catch (error) {
    console.error('Failed to fetch servers:', error)
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  dialogTitle.value = '添加服务器'
  editingId.value = null
  form.value = {
    name: '',
    host: '',
    port: 22,
    username: '',
    password: '',
    description: ''
  }
  dialogVisible.value = true
}

const editServer = (server) => {
  dialogTitle.value = '编辑服务器'
  editingId.value = server.id
  form.value = { ...server }
  dialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (editingId.value) {
        await api.put(`/servers/${editingId.value}`, form.value)
        ElMessage.success('更新成功')
      } else {
        await api.post('/servers', form.value)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      fetchServers()
    } catch (error) {
      console.error('Failed to submit:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteServer = (server) => {
  ElMessageBox.confirm('确定要删除该服务器吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/servers/${server.id}`)
      ElMessage.success('删除成功')
      fetchServers()
    } catch (error) {
      console.error('Failed to delete:', error)
    }
  })
}

const testConnection = async (server) => {
  const loading = ElMessage({
    message: '正在测试连接...',
    type: 'info',
    duration: 0
  })
  
  try {
    const response = await api.post(`/servers/${server.id}/test`)
    loading.close()
    
    if (response.data.success) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error('连接失败：' + response.data.message)
    }
    fetchServers()
  } catch (error) {
    loading.close()
    console.error('Failed to test connection:', error)
  }
}

const showStatus = async (server) => {
  try {
    const response = await api.get(`/servers/${server.id}/status`)
    serverStatus.value = response.data
    statusDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取服务器状态失败')
    console.error('Failed to get status:', error)
  }
}

onMounted(() => {
  fetchServers()
})
</script>

<style scoped>
.servers-page {
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

.status-content {
  padding: 20px 0;
}
</style>

