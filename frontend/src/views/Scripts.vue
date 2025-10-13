<template>
  <div class="scripts-page">
    <div class="page-header">
      <h1 class="page-title">脚本管理</h1>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        创建脚本
      </el-button>
    </div>
    
    <el-card>
      <el-table :data="scripts" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="script_type" label="类型" width="100" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewScript(scope.row)">查看</el-button>
            <el-button size="small" type="success" @click="executeScript(scope.row)">执行</el-button>
            <el-button size="small" type="warning" @click="editScript(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteScript(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="脚本名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="脚本类型" prop="script_type">
          <el-select v-model="form.script_type" style="width: 100%">
            <el-option label="Shell" value="shell" />
            <el-option label="Python" value="python" />
            <el-option label="Bash" value="bash" />
          </el-select>
        </el-form-item>
        <el-form-item label="脚本内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="15" placeholder="请输入脚本内容" />
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
    
    <!-- 执行脚本对话框 -->
    <el-dialog v-model="executeDialogVisible" title="执行脚本" width="600px">
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="选择服务器">
          <el-select v-model="executeForm.server_id" placeholder="请选择服务器" style="width: 100%">
            <el-option 
              v-for="server in servers" 
              :key="server.id" 
              :label="`${server.name} (${server.host})`" 
              :value="server.id" 
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitExecute" :loading="executing">执行</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看脚本对话框 -->
    <el-dialog v-model="viewDialogVisible" title="脚本详情" width="800px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="名称">{{ viewingScript?.name }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ viewingScript?.script_type }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ viewingScript?.description }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ viewingScript?.created_at }}</el-descriptions-item>
      </el-descriptions>
      <div style="margin-top: 20px;">
        <h3>脚本内容：</h3>
        <pre style="background-color: #f5f7fa; padding: 15px; border-radius: 4px; overflow-x: auto;">{{ viewingScript?.content }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const scripts = ref([])
const servers = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('创建脚本')
const form = ref({
  name: '',
  script_type: 'shell',
  content: '',
  description: ''
})
const formRef = ref(null)
const submitting = ref(false)
const editingId = ref(null)

const executeDialogVisible = ref(false)
const executeForm = ref({
  script_id: null,
  server_id: null
})
const executing = ref(false)

const viewDialogVisible = ref(false)
const viewingScript = ref(null)

const rules = {
  name: [{ required: true, message: '请输入脚本名称', trigger: 'blur' }],
  script_type: [{ required: true, message: '请选择脚本类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入脚本内容', trigger: 'blur' }]
}

const fetchScripts = async () => {
  loading.value = true
  try {
    const response = await api.get('/scripts')
    scripts.value = response.data
  } catch (error) {
    console.error('Failed to fetch scripts:', error)
  } finally {
    loading.value = false
  }
}

const fetchServers = async () => {
  try {
    const response = await api.get('/servers')
    servers.value = response.data.filter(s => s.status === 'online')
  } catch (error) {
    console.error('Failed to fetch servers:', error)
  }
}

const showAddDialog = () => {
  dialogTitle.value = '创建脚本'
  editingId.value = null
  form.value = {
    name: '',
    script_type: 'shell',
    content: '',
    description: ''
  }
  dialogVisible.value = true
}

const editScript = (script) => {
  dialogTitle.value = '编辑脚本'
  editingId.value = script.id
  form.value = { ...script }
  dialogVisible.value = true
}

const viewScript = (script) => {
  viewingScript.value = script
  viewDialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (editingId.value) {
        await api.put(`/scripts/${editingId.value}`, form.value)
        ElMessage.success('更新成功')
      } else {
        await api.post('/scripts', form.value)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchScripts()
    } catch (error) {
      console.error('Failed to submit:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteScript = (script) => {
  ElMessageBox.confirm('确定要删除该脚本吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/scripts/${script.id}`)
      ElMessage.success('删除成功')
      fetchScripts()
    } catch (error) {
      console.error('Failed to delete:', error)
    }
  })
}

const executeScript = (script) => {
  executeForm.value = {
    script_id: script.id,
    server_id: null
  }
  executeDialogVisible.value = true
}

const submitExecute = async () => {
  if (!executeForm.value.server_id) {
    ElMessage.warning('请选择服务器')
    return
  }
  
  executing.value = true
  try {
    const response = await api.post('/scripts/execute', executeForm.value)
    ElMessage.success('脚本执行中...')
    executeDialogVisible.value = false
    
    // 显示执行结果
    setTimeout(() => {
      if (response.data.status === 'success') {
        ElMessage.success('脚本执行成功')
      } else {
        ElMessage.error('脚本执行失败')
      }
    }, 1000)
  } catch (error) {
    console.error('Failed to execute:', error)
  } finally {
    executing.value = false
  }
}

onMounted(() => {
  fetchScripts()
  fetchServers()
})
</script>

<style scoped>
.scripts-page {
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

