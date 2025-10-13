# 运维自动化平台

## 项目简介

这是一个基于Python开发的运维自动化平台，旨在简化日常运维工作，提高运维效率。

## 核心功能

### 1. 服务器管理
- 服务器信息管理（IP、端口、凭证）
- SSH远程连接
- 服务器状态监控（CPU、内存、磁盘）

### 2. 脚本执行
- 远程脚本执行
- 批量执行
- 执行历史记录

### 3. 文件管理
- 文件上传/下载
- 文件分发（批量传输）

### 4. 监控告警
- 实时监控服务器资源
- 阈值告警配置
- 告警历史记录

### 5. 任务调度
- 定时任务配置
- Cron表达式支持
- 任务执行日志

### 6. 日志管理
- 操作日志记录
- 日志查询和分析

### 7. 用户管理
- 用户认证
- 角色权限管理

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: SQLAlchemy + SQLite/MySQL
- **任务调度**: APScheduler
- **SSH连接**: Paramiko
- **认证**: JWT

### 前端
- **框架**: Vue.js 3
- **UI库**: Element Plus
- **HTTP客户端**: Axios

## 项目结构

```
project_2/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   └── api/            # API调用
│   └── package.json        # 前端依赖
├── docs/                   # 文档
└── README.md
```

## 快速开始

### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

访问 http://localhost:8000/docs 查看API文档

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173

## 默认账号

- 用户名: admin
- 密码: admin123

## 功能特性

### 已实现功能
- ✅ 用户认证和权限管理
- ✅ 服务器信息管理和SSH连接
- ✅ 实时监控服务器资源（CPU、内存、磁盘）
- ✅ 脚本管理和远程执行
- ✅ 定时任务调度（Cron表达式）
- ✅ 告警管理和阈值监控
- ✅ 操作日志记录
- ✅ 响应式Web界面

### 未来计划
- [ ] 文件上传下载功能
- [ ] 邮件/短信告警通知
- [ ] 批量服务器操作
- [ ] 可视化数据报表
- [ ] 容器管理集成
- [ ] Ansible集成
- [ ] 单元测试覆盖

## 许可证

MIT License

