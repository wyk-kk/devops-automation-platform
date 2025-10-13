<template>
  <div class="tasks-page">
    <div class="page-header">
      <h1 class="page-title">任务调度</h1>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        新建任务
      </el-button>
    </div>
    
    <el-card>
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="task_type" label="类型" width="100" />
        <el-table-column prop="cron_expression" label="Cron表达式" width="150" />
        <el-table-column prop="is_enabled" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_enabled ? 'success' : 'info'">
              {{ scope.row.is_enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_status" label="上次状态" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.last_status" :type="getStatusType(scope.row.last_status)">
              {{ scope.row.last_status }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_run_time" label="上次运行" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button size="small" type="success" @click="executeTask(scope.row)">立即执行</el-button>
            <el-button size="small" type="warning" @click="editTask(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteTask(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="任务类型" prop="task_type">
          <el-radio-group v-model="form.task_type">
            <el-radio label="script">脚本</el-radio>
            <el-radio label="command">命令</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.task_type === 'script'" label="选择脚本" prop="script_id">
          <el-select v-model="form.script_id" placeholder="请选择脚本" style="width: 100%">
            <el-option 
              v-for="script in scripts" 
              :key="script.id" 
              :label="script.name" 
              :value="script.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.task_type === 'command'" label="命令" prop="command">
          <el-input v-model="form.command" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="目标服务器" prop="server_id">
          <el-select v-model="form.server_id" placeholder="请选择服务器" style="width: 100%">
            <el-option 
              v-for="server in servers" 
              :key="server.id" 
              :label="`${server.name} (${server.host})`" 
              :value="server.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Cron表达式" prop="cron_expression">
          <el-input v-model="form.cron_expression" placeholder="如: 0 2 * * *" />
          <div style="font-size: 12px; color: #999; margin-top: 5px;">
            示例：0 2 * * * (每天凌晨2点) | 0 */6 * * * (每6小时) | 0 0 * * 0 (每周日)
          </div>
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="form.is_enabled" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const tasks = ref([])
const scripts = ref([])
const servers = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新建任务')
const form = ref({
  name: '',
  task_type: 'script',
  script_id: null,
  command: '',
  server_id: null,
  cron_expression: '',
  is_enabled: true,
  description: ''
})
const formRef = ref(null)
const submitting = ref(false)
const editingId = ref(null)

const rules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  task_type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  server_id: [{ required: true, message: '请选择服务器', trigger: 'change' }],
  cron_expression: [{ required: true, message: '请输入Cron表达式', trigger: 'blur' }]
}

const getStatusType = (status) => {
  const types = {
    'success': 'success',
    'failed': 'danger',
    'running': 'warning'
  }
  return types[status] || 'info'
}

const fetchTasks = async () => {
  loading.value = true
  try {
    const response = await api.get('/tasks')
    tasks.value = response.data
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
  } finally {
    loading.value = false
  }
}

const fetchScripts = async () => {
  try {
    const response = await api.get('/scripts')
    scripts.value = response.data
  } catch (error) {
    console.error('Failed to fetch scripts:', error)
  }
}

const fetchServers = async () => {
  try {
    const response = await api.get('/servers')
    servers.value = response.data
  } catch (error) {
    console.error('Failed to fetch servers:', error)
  }
}

const showAddDialog = () => {
  dialogTitle.value = '新建任务'
  editingId.value = null
  form.value = {
    name: '',
    task_type: 'script',
    script_id: null,
    command: '',
    server_id: null,
    cron_expression: '',
    is_enabled: true,
    description: ''
  }
  dialogVisible.value = true
}

const editTask = (task) => {
  dialogTitle.value = '编辑任务'
  editingId.value = task.id
  form.value = { ...task }
  dialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (editingId.value) {
        await api.put(`/tasks/${editingId.value}`, form.value)
        ElMessage.success('更新成功')
      } else {
        await api.post('/tasks', form.value)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchTasks()
    } catch (error) {
      console.error('Failed to submit:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteTask = (task) => {
  ElMessageBox.confirm('确定要删除该任务吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/tasks/${task.id}`)
      ElMessage.success('删除成功')
      fetchTasks()
    } catch (error) {
      console.error('Failed to delete:', error)
    }
  })
}

const executeTask = async (task) => {
  try {
    await api.post(`/tasks/${task.id}/execute`)
    ElMessage.success('任务已触发执行')
    fetchTasks()
  } catch (error) {
    console.error('Failed to execute task:', error)
  }
}

onMounted(() => {
  fetchTasks()
  fetchScripts()
  fetchServers()
})
</script>

<style scoped>
.tasks-page {
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

