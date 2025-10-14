# 运维自动化平台

## 项目简介

这是一个基于Python开发的运维自动化平台，旨在简化日常运维工作，提高运维效率。

## 核心功能

### 1. 资源管理 ⭐v3.0 重大升级
**服务器管理**：
- 服务器信息管理（IP、端口、凭证）
- SSH远程连接
- 服务器状态监控（CPU、内存、磁盘）

**Kubernetes集群管理** ⭐v3.1 完整功能：
- ✅ **集群管理**：
  - 多集群接入管理
  - 支持Kubeconfig、Token、证书等多种认证方式
  - 集群健康度评分系统
  - 环境分类（dev/test/staging/prod）
  
- ✅ **资源监控**：
  - 节点（Node）状态监控和资源统计
  - 命名空间（Namespace）管理
  - Pod实时状态监控
  - 集群资源实时同步
  - 统一资源视图（服务器+K8s）

- ✅ **Pod管理**：
  - Pod日志实时查看（支持容器过滤）
  - Pod重启功能（删除触发自动重建）
  - Pod状态详情查询
  
- ✅ **Deployment管理**：
  - Deployment列表和状态查询
  - 副本数动态伸缩（Scale Up/Down）
  - 滚动更新支持
  
- ✅ **高级功能**：
  - K8s资源使用趋势图表
  - 环境分布统计
  - 告警规则集成（节点/Pod异常告警）
  - 健康度自动评估

### 2. 脚本执行
- 远程脚本执行
- 批量执行
- 执行历史记录

### 3. 文件管理
- 文件上传/下载
- 文件分发（批量传输）

### 4. 监控告警 ⭐新增
- **动态告警规则**：自定义监控指标和阈值
- **多级告警**：支持info、warning、error、critical四个级别
- **智能静默**：避免重复告警，支持持续时间检测
- **多渠道通知**：邮件、Webhook通知
- **告警统计**：实时统计和趋势分析
- **全局/特定规则**：支持全局规则和服务器特定规则

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

### 🐳 方式一：Docker部署（推荐，适合演示和答辩）

**一键启动，无需配置环境！**

```bash
# Linux/Mac
./docker-start.sh

# Windows
docker-start.bat

# 或手动启动
docker-compose up -d
```

访问：
- 前端页面: http://localhost
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

详见：[Docker部署指南](./DOCKER_DEPLOYMENT.md)

### 💻 方式二：本地开发部署

#### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

访问 http://localhost:8000/docs 查看API文档

#### 前端启动

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
- [ ] WebSocket实时通信
- [ ] 容器终端（Web Shell）
- [ ] Helm Chart部署
- [ ] 深色主题
- [ ] 国际化支持
- [ ] HPA自动伸缩

## 📖 文档索引

### 🌟 推荐阅读（论文参考）
- **[📘 完整项目文档](./完整项目文档.md)** ⭐ 一站式完整文档，包含所有功能说明、API、部署、开发指南

### 快速开始
- [启动指南](./启动指南.md) - 详细的项目启动步骤
- [QUICK_START.md](./QUICK_START.md) - 快速入门指南

### 功能说明
- [功能总结](./FEATURES_SUMMARY.md) - 完整功能清单和统计（论文用）
- [项目总结](./PROJECT_SUMMARY.md) - 项目总结和技术亮点
- [K8s基础功能](./K8S_FEATURE_GUIDE.md) - Kubernetes集群管理
- [K8s高级功能](./K8S_ADVANCED_FEATURES.md) - Pod管理、Deployment伸缩
- [告警规则指南](./docs/ALERT_RULES_GUIDE.md) - 动态告警规则系统

### 技术文档
- [API文档](./docs/API_DOCUMENTATION.md) - REST API接口说明
- [开发指南](./docs/DEVELOPMENT.md) - 开发环境搭建和代码规范
- [部署指南](./docs/DEPLOYMENT.md) - 生产环境部署
- [用户手册](./docs/USER_MANUAL.md) - 功能使用手册

### 版本说明
- [升级指南v2.0](./UPGRADE_GUIDE_V2.md) - 告警系统重大升级
- [Git使用指南](./GIT_GUIDE.md) - Git操作指南

## 项目统计

```
代码量: 10,500+ 行
├── 后端: ~6,000 行 Python
├── 前端: ~4,500 行 Vue/JavaScript
├── 数据表: 15 个
├── API接口: 55+ 个
├── 前端页面: 12 个
└── 文档: 13 份

功能模块: 6 大核心模块
├── 资源管理（服务器 + K8s集群）
├── 脚本执行
├── 任务调度
├── 监控告警
├── 用户管理
└── 操作日志
```

## 许可证

MIT License

