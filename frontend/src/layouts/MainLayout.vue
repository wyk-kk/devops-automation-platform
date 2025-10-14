<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>运维平台</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        :default-openeds="['alerts']"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/resources">
          <el-icon><Box /></el-icon>
          <span>资源管理</span>
        </el-menu-item>
        <el-menu-item index="/scripts">
          <el-icon><Document /></el-icon>
          <span>脚本管理</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><Clock /></el-icon>
          <span>任务调度</span>
        </el-menu-item>
        
        <!-- 告警管理子菜单 -->
        <el-sub-menu index="alerts">
          <template #title>
            <el-icon><Bell /></el-icon>
            <span>告警管理</span>
          </template>
          <el-menu-item index="/alerts">
            <el-icon><Warning /></el-icon>
            <span>告警列表</span>
          </el-menu-item>
          <el-menu-item index="/alert-rules">
            <el-icon><Setting /></el-icon>
            <span>告警规则</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/users" v-if="authStore.user?.is_superuser">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ authStore.user?.username }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  Odometer, 
  Monitor, 
  Box,
  Document, 
  Clock, 
  Bell, 
  Warning,
  Setting,
  User,
  ArrowDown 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  const path = route.path
  // 如果是告警相关的路由，返回具体的路径
  if (path.startsWith('/alerts') || path.startsWith('/alert-rules')) {
    return path
  }
  return path
})

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    // 跳转到个人信息页面
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  height: 100vh;
  overflow-y: auto;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4a;
}

.logo h2 {
  color: #fff;
  font-size: 20px;
  font-weight: 600;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}

/* 子菜单样式 */
:deep(.el-sub-menu__title) {
  color: #bfcbd9 !important;
}

:deep(.el-sub-menu__title:hover) {
  background-color: rgba(0, 0, 0, 0.2) !important;
}

:deep(.el-menu--inline) {
  background-color: #1f2d3d !important;
}

:deep(.el-menu-item) {
  min-width: 200px;
}

:deep(.el-sub-menu .el-menu-item) {
  padding-left: 50px !important;
  background-color: #1f2d3d !important;
}

:deep(.el-sub-menu .el-menu-item:hover) {
  background-color: rgba(0, 0, 0, 0.3) !important;
}
</style>

