<template>
  <div class="web-terminal">
    <div class="terminal-header">
      <span>{{ title }}</span>
      <div class="terminal-controls">
        <el-tag v-if="isConnected" type="success" size="small">
          <el-icon><SuccessFilled /></el-icon> 已连接
        </el-tag>
        <el-tag v-else type="danger" size="small">
          <el-icon><CircleCloseFilled /></el-icon> 未连接
        </el-tag>
        <el-button @click="clearTerminal" size="small" type="info" link :icon="Delete">
          清屏
        </el-button>
      </div>
    </div>
    
    <div ref="terminalContainer" class="terminal-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import { 
  Delete,
  SuccessFilled, 
  CircleCloseFilled
} from '@element-plus/icons-vue'
import 'xterm/css/xterm.css'

const props = defineProps({
  serverId: {
    type: Number,
    required: true
  },
  title: {
    type: String,
    default: 'SSH Terminal'
  }
})

const emit = defineEmits(['connected', 'disconnected', 'error'])

const terminalContainer = ref(null)
let terminal = null
let fitAddon = null
let websocket = null
const isConnected = ref(false)

onMounted(() => {
  initTerminal()
  connectWebSocket()
})

onBeforeUnmount(() => {
  cleanup()
})

const initTerminal = () => {
  // 创建终端实例
  terminal = new Terminal({
    cursorBlink: true,
    cursorStyle: 'block',
    fontSize: 14,
    fontFamily: 'Monaco, Menlo, "Courier New", monospace',
    theme: {
      background: '#1e1e1e',
      foreground: '#d4d4d4',
      cursor: '#ffffff',
      selection: 'rgba(255, 255, 255, 0.3)',
      black: '#000000',
      red: '#cd3131',
      green: '#0dbc79',
      yellow: '#e5e510',
      blue: '#2472c8',
      magenta: '#bc3fbc',
      cyan: '#11a8cd',
      white: '#e5e5e5',
      brightBlack: '#666666',
      brightRed: '#f14c4c',
      brightGreen: '#23d18b',
      brightYellow: '#f5f543',
      brightBlue: '#3b8eea',
      brightMagenta: '#d670d6',
      brightCyan: '#29b8db',
      brightWhite: '#e5e5e5'
    },
    cols: 80,
    rows: 24
  })

  // 添加fit插件
  fitAddon = new FitAddon()
  terminal.loadAddon(fitAddon)

  // 打开终端
  terminal.open(terminalContainer.value)

  // 调整大小
  fitAddon.fit()

  // 监听用户输入
  terminal.onData(data => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({
        type: 'input',
        data: data
      }))
    }
  })

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

const connectWebSocket = () => {
  // 构建WebSocket URL
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.hostname
  const port = import.meta.env.VITE_API_PORT || '8000'
  const wsUrl = `${protocol}//${host}:${port}/api/ws/ssh/${props.serverId}`

  // 显示连接中状态，但不换行
  terminal.write('\x1b[90m正在连接...\x1b[0m')

  try {
    websocket = new WebSocket(wsUrl)

    websocket.onopen = () => {
      // WebSocket已打开，等待SSH连接
    }

    websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        
        switch (message.type) {
          case 'output':
            // 直接显示服务器输出（包括欢迎消息和命令提示符）
            terminal.write(message.data)
            break
          
          case 'connected':
            // SSH连接成功，清除"正在连接..."并标记为已连接
            terminal.write('\r\x1b[K')  // 清除当前行
            isConnected.value = true
            emit('connected')
            // 发送终端大小
            sendTerminalSize()
            break
          
          case 'error':
            terminal.write('\r\x1b[K')  // 清除"正在连接..."
            terminal.writeln(`\x1b[1;31m✗ 错误: ${message.message}\x1b[0m\r\n`)
            isConnected.value = false
            emit('error', message.message)
            break
          
          case 'disconnected':
            if (isConnected.value) {
              terminal.writeln('\r\n\x1b[1;33m连接已断开\x1b[0m')
            }
            isConnected.value = false
            emit('disconnected')
            break
        }
      } catch (e) {
        console.error('处理WebSocket消息失败:', e)
      }
    }

    websocket.onerror = (error) => {
      console.error('WebSocket错误:', error)
      terminal.write('\r\x1b[K')  // 清除"正在连接..."
      terminal.writeln('\x1b[1;31mWebSocket连接错误\x1b[0m')
      isConnected.value = false
      emit('error', 'WebSocket连接错误')
    }

    websocket.onclose = () => {
      isConnected.value = false
      emit('disconnected')
      terminal.writeln('\r\n\x1b[1;33m连接已关闭\x1b[0m\r\n')
    }

  } catch (e) {
    console.error('创建WebSocket失败:', e)
    terminal.writeln('\r\n\x1b[1;31m创建WebSocket连接失败\x1b[0m\r\n')
    emit('error', '创建WebSocket连接失败')
  }
}

const handleResize = () => {
  if (fitAddon && terminal) {
    fitAddon.fit()
    
    // 通知后端调整终端大小
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({
        type: 'resize',
        cols: terminal.cols,
        rows: terminal.rows
      }))
    }
  }
}

const clearTerminal = () => {
  if (terminal) {
    terminal.clear()
  }
}

const executeQuickCommand = (command) => {
  if (!command || !command.trim()) return
  
  if (websocket && websocket.readyState === WebSocket.OPEN && isConnected.value) {
    // 发送命令
    websocket.send(JSON.stringify({
      type: 'input',
      data: command + '\n'
    }))
    // 清空自定义命令输入框
    customCommand.value = ''
  } else {
    alert('终端未连接，请等待连接成功')
  }
}

const cleanup = () => {
  window.removeEventListener('resize', handleResize)
  
  if (websocket) {
    websocket.close()
    websocket = null
  }
  
  if (terminal) {
    terminal.dispose()
    terminal = null
  }
}

defineExpose({
  clearTerminal,
  isConnected
})
</script>

<style scoped>
.web-terminal {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1e1e1e;
  border-radius: 4px;
  overflow: hidden;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #2d2d30;
  color: #cccccc;
  font-size: 14px;
  border-bottom: 1px solid #3e3e42;
}

.terminal-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.terminal-container {
  flex: 1;
  padding: 10px;
  overflow: hidden;
}

/* 确保xterm适应容器 */
.terminal-container :deep(.xterm) {
  height: 100% !important;
}

.terminal-container :deep(.xterm-viewport) {
  overflow-y: auto;
}
</style>

