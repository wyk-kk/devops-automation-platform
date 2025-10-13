# API 文档

## 基础信息

- 基础URL: `http://localhost:8000/api`
- 认证方式: Bearer Token (JWT)
- 内容类型: `application/json`

## 认证接口

### 用户注册
```
POST /auth/register
```

**请求体:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "is_active": true,
  "is_superuser": false
}
```

### 用户登录
```
POST /auth/login
```

**请求体 (Form Data):**
```
username: string
password: string
```

**响应:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### 获取当前用户信息
```
GET /auth/me
```

**需要认证**: 是

## 服务器管理

### 获取服务器列表
```
GET /servers
```

**查询参数:**
- `skip`: 跳过的记录数 (默认: 0)
- `limit`: 返回的记录数 (默认: 100)

### 获取服务器详情
```
GET /servers/{server_id}
```

### 创建服务器
```
POST /servers
```

**请求体:**
```json
{
  "name": "string",
  "host": "string",
  "port": 22,
  "username": "string",
  "password": "string",
  "ssh_key": "string",
  "description": "string",
  "is_active": true
}
```

### 更新服务器
```
PUT /servers/{server_id}
```

### 删除服务器
```
DELETE /servers/{server_id}
```

### 测试服务器连接
```
POST /servers/{server_id}/test
```

### 刷新服务器信息
```
POST /servers/{server_id}/refresh
```

### 获取服务器实时状态
```
GET /servers/{server_id}/status
```

**响应:**
```json
{
  "server_id": 1,
  "status": "online",
  "cpu_percent": 45.2,
  "memory_percent": 68.5,
  "memory_used": 2048,
  "memory_total": 4096,
  "disk_percent": 55.3,
  "disk_used": 50,
  "disk_total": 100,
  "uptime": "up 7 days, 3 hours",
  "check_time": "2024-01-15T10:30:00"
}
```

## 脚本管理

### 获取脚本列表
```
GET /scripts
```

### 获取脚本详情
```
GET /scripts/{script_id}
```

### 创建脚本
```
POST /scripts
```

**请求体:**
```json
{
  "name": "string",
  "description": "string",
  "content": "#!/bin/bash\necho 'Hello'",
  "script_type": "shell",
  "parameters": "string"
}
```

### 更新脚本
```
PUT /scripts/{script_id}
```

### 删除脚本
```
DELETE /scripts/{script_id}
```

### 执行脚本
```
POST /scripts/execute
```

**请求体:**
```json
{
  "script_id": 1,
  "server_id": 1
}
```

### 获取执行记录列表
```
GET /scripts/executions/list
```

### 获取执行记录详情
```
GET /scripts/executions/{execution_id}
```

## 任务调度

### 获取任务列表
```
GET /tasks
```

### 获取任务详情
```
GET /tasks/{task_id}
```

### 创建任务
```
POST /tasks
```

**请求体:**
```json
{
  "name": "string",
  "description": "string",
  "task_type": "script",
  "script_id": 1,
  "command": "string",
  "server_id": 1,
  "cron_expression": "0 2 * * *",
  "is_enabled": true
}
```

### 更新任务
```
PUT /tasks/{task_id}
```

### 删除任务
```
DELETE /tasks/{task_id}
```

### 手动执行任务
```
POST /tasks/{task_id}/execute
```

### 获取任务执行记录
```
GET /tasks/{task_id}/executions
```

## 告警管理

### 获取告警列表
```
GET /alerts
```

**查询参数:**
- `status`: 告警状态 (open, acknowledged, resolved)
- `skip`: 跳过的记录数
- `limit`: 返回的记录数

### 获取告警详情
```
GET /alerts/{alert_id}
```

### 确认告警
```
POST /alerts/{alert_id}/acknowledge
```

### 解决告警
```
POST /alerts/{alert_id}/resolve
```

## 用户管理

### 获取用户列表
```
GET /users
```

**需要权限**: 超级管理员

### 获取用户详情
```
GET /users/{user_id}
```

### 更新用户
```
PUT /users/{user_id}
```

### 删除用户
```
DELETE /users/{user_id}
```

**需要权限**: 超级管理员

## 错误响应

所有API在出错时返回标准错误格式:

```json
{
  "detail": "错误描述"
}
```

**常见HTTP状态码:**
- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器错误

## Cron表达式说明

Cron表达式格式: `分 时 日 月 周`

**示例:**
- `0 2 * * *`: 每天凌晨2点
- `0 */6 * * *`: 每6小时
- `0 0 * * 0`: 每周日凌晨
- `30 8 * * 1-5`: 工作日早上8:30
- `0 0 1 * *`: 每月1号凌晨

## 认证流程

1. 调用 `/auth/login` 获取访问令牌
2. 在后续请求的 Header 中添加: `Authorization: Bearer <token>`
3. Token默认有效期为24小时

