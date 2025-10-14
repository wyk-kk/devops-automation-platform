# Kubernetes集群管理功能指南

## 🎉 新功能介绍

本次更新为运维自动化平台增加了**Kubernetes集群管理**功能，这是一个重大的功能扩展，使平台能够管理容器化基础设施！

---

## ✨ 核心功能

### 1. K8s集群接入
- ✅ 支持多种认证方式：
  - **Kubeconfig**: 最常用的方式
  - **Token**: Bearer Token认证
  - **证书**: 客户端证书认证
- ✅ 多集群管理
- ✅ 环境分类（dev/test/staging/prod）
- ✅ 自动状态检测

### 2. 资源监控
- ✅ 节点（Node）信息采集
  - CPU、内存容量
  - 运行状态
  - Pod数量
  - 系统信息
- ✅ 命名空间（Namespace）管理
- ✅ Pod状态监控
- ✅ 集群资源统计

### 3. 统一资源管理
- ✅ 服务器 + K8s集群统一视图
- ✅ 资源对比分析
- ✅ 一键同步集群状态

---

## 🚀 快速开始

### 步骤1：安装依赖

#### 后端
```bash
cd backend
pip install kubernetes==28.1.0
```

#### 前端
前端已包含所需依赖（Element Plus图标库、ECharts等）

### 步骤2：启动服务

```bash
# 启动后端
cd backend
python main.py

# 启动前端
cd frontend
npm run dev
```

### 步骤3：添加K8s集群

1. 访问 http://localhost:5173
2. 登录系统
3. 点击左侧菜单 **"资源管理"**
4. 点击 **"添加K8s集群"** 按钮
5. 填写集群信息

---

## 📋 添加K8s集群详细步骤

### 方式1：使用Kubeconfig（推荐）

#### 1.1 获取Kubeconfig
```bash
# 查看当前kubeconfig
cat ~/.kube/config

# 或者从集群获取
kubectl config view --raw
```

#### 1.2 填写表单
- **集群名称**: 例如 `production-k8s`
- **API Server**: 例如 `https://kubernetes.example.com:6443`
- **认证方式**: 选择 `Kubeconfig`
- **Kubeconfig**: 粘贴完整的kubeconfig内容
- **环境**: 选择对应环境（如 `生产环境`）

#### 1.3 点击创建
系统会自动：
1. 验证连接
2. 获取Kubernetes版本
3. 统计节点、Pod、命名空间数量

### 方式2：使用Service Account Token

#### 2.1 创建Service Account
```bash
# 创建service account
kubectl create serviceaccount devops-admin -n kube-system

# 绑定cluster-admin角色
kubectl create clusterrolebinding devops-admin-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:devops-admin

# 获取token
kubectl -n kube-system create token devops-admin
```

#### 2.2 填写表单
- **集群名称**: `test-k8s`
- **API Server**: `https://k8s-api.example.com:6443`
- **认证方式**: 选择 `Token`
- **Token**: 粘贴上面获取的token
- **环境**: 选择 `测试环境`

---

## 🎯 功能说明

### 资源管理页面

#### 顶部统计卡片
- **服务器数**: 显示传统服务器总数
- **K8s集群数**: 显示Kubernetes集群总数
- **总节点数**: 服务器 + K8s节点总和

#### Tab切换

**服务器标签页**：
- 显示所有传统服务器
- 实时资源使用率（CPU、内存）
- 支持SSH连接和管理

**K8s集群标签页**：
- 集群列表
- 连接状态
- 资源统计（节点/Pod/命名空间）
- 操作：详情、同步、删除

### 集群同步功能

点击 **"同步"** 按钮后，系统会：
1. 连接到K8s集群
2. 获取最新的节点列表
3. 获取命名空间列表
4. 获取Pod状态（最多1000个）
5. 更新数据库

**注意**: 同步是后台任务，可能需要几秒钟完成。

---

## 🔧 API 端点

### K8s集群管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/k8s/clusters` | 获取集群列表 |
| POST | `/api/k8s/clusters` | 创建集群 |
| GET | `/api/k8s/clusters/{id}` | 获取集群详情 |
| PUT | `/api/k8s/clusters/{id}` | 更新集群 |
| DELETE | `/api/k8s/clusters/{id}` | 删除集群 |
| POST | `/api/k8s/clusters/{id}/check-status` | 检查连接状态 |
| POST | `/api/k8s/clusters/{id}/sync` | 同步集群资源 |

### K8s资源查询

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/k8s/clusters/{id}/nodes` | 获取节点列表 |
| GET | `/api/k8s/clusters/{id}/namespaces` | 获取命名空间 |
| GET | `/api/k8s/clusters/{id}/pods` | 获取Pod列表 |
| GET | `/api/k8s/statistics` | 获取统计信息 |

---

## 📊 数据模型

### K8sCluster（集群）
```python
- id: 集群ID
- name: 集群名称
- api_server: API Server地址
- auth_type: 认证方式
- version: Kubernetes版本
- node_count: 节点数
- pod_count: Pod数
- namespace_count: 命名空间数
- status: 连接状态
- environment: 环境类型
```

### K8sNode（节点）
```python
- node_name: 节点名称
- node_ip: 节点IP
- status: 状态（Ready/NotReady）
- roles: 角色（master/worker）
- cpu_capacity: CPU容量
- memory_capacity: 内存容量
- pod_count: 运行的Pod数
```

### K8sNamespace（命名空间）
```python
- namespace_name: 命名空间名称
- status: 状态
- pod_count: Pod数量
- service_count: Service数量
- deployment_count: Deployment数量
```

### K8sPod（Pod）
```python
- pod_name: Pod名称
- namespace: 所属命名空间
- node_name: 运行节点
- status: 状态
- ready_containers: 就绪容器数
- total_containers: 总容器数
- restart_count: 重启次数
```

---

## 🔐 权限说明

### K8s集群权限要求

添加集群时使用的凭证需要以下权限：

**最小权限**：
- `get`, `list`, `watch` 权限用于：
  - nodes
  - namespaces
  - pods
  - services
  - deployments

**推荐权限**：
- 使用 `cluster-admin` 角色（完整管理权限）
- 或者创建自定义 ClusterRole：

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: devops-reader
rules:
- apiGroups: [""]
  resources: ["nodes", "namespaces", "pods", "services"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets"]
  verbs: ["get", "list", "watch"]
```

---

## ⚠️ 注意事项

### 1. Kubeconfig安全
- ⚠️ Kubeconfig包含敏感凭证信息
- ✅ 数据库中已加密存储
- ✅ 仅管理员可以查看和管理

### 2. 网络连接
- 确保运维平台能够访问K8s API Server
- 如果API Server在内网，需要配置网络路由
- 支持HTTPS和非标准端口

### 3. 性能考虑
- 首次同步大集群可能需要较长时间
- Pod数据限制为1000条（避免数据库过大）
- 建议定期清理历史数据

### 4. 集群版本
- 支持Kubernetes 1.19+
- 推荐使用最新稳定版本

---

## 🐛 故障排除

### 问题1：连接失败

**错误信息**: `连接失败` 或 `status: disconnected`

**可能原因**：
1. API Server地址不正确
2. 网络不可达
3. 凭证过期或无效
4. 证书验证失败

**解决方法**：
```bash
# 测试连接
kubectl --kubeconfig=/path/to/config get nodes

# 检查API Server地址
kubectl cluster-info

# 验证证书
openssl s_client -connect k8s-api.example.com:6443
```

### 问题2：权限不足

**错误信息**: `Forbidden` 或 `403`

**解决方法**：
- 检查Service Account权限
- 确认ClusterRole绑定正确
- 使用具有足够权限的凭证

### 问题3：同步慢

**现象**: 点击同步后长时间无响应

**解决方法**：
- 同步是后台任务，等待几秒后刷新页面
- 大集群首次同步可能需要30秒以上
- 查看后端日志确认进度

---

## 📚 扩展功能（未来计划）

- [ ] Pod日志查看
- [ ] 容器终端（Web Shell）
- [ ] Deployment伸缩
- [ ] Service管理
- [ ] ConfigMap/Secret管理
- [ ] Helm Chart部署
- [ ] 资源使用率图表
- [ ] 告警规则支持K8s指标

---

## 💡 使用场景

### 场景1：多集群管理
管理开发、测试、生产多个K8s集群：
```
生产环境集群:
  - API: https://prod-k8s.company.com:6443
  - 节点: 10个
  - Pod: 500+

测试环境集群:
  - API: https://test-k8s.company.com:6443
  - 节点: 3个
  - Pod: 100+
```

### 场景2：混合基础设施
同时管理传统服务器和容器化应用：
```
资源管理:
  ├── 传统服务器: 20台
  └── K8s集群: 3个
      ├── 节点: 30个
      └── Pod: 1000+

总计管理节点: 50个
```

### 场景3：环境隔离
按环境分类管理：
```
开发环境: 2个集群
测试环境: 1个集群
预发环境: 1个集群
生产环境: 3个集群
```

---

## 🎓 论文要点

### 技术亮点
1. **多集群管理**: 支持管理多个Kubernetes集群
2. **认证适配**: 支持多种认证方式
3. **资源同步**: 自动同步集群资源状态
4. **统一管理**: 传统服务器+容器化基础设施统一管理
5. **Python Kubernetes客户端**: 使用官方Python SDK

### 架构设计
```
前端 (Vue3 + Element Plus)
    ↓
API层 (FastAPI REST)
    ↓
服务层 (K8sService)
    ↓
K8s客户端 (Python kubernetes库)
    ↓
Kubernetes集群
```

### 创新点
- 混合基础设施管理（虚拟机+容器）
- 多集群统一视图
- 实时状态同步
- 环境分类管理

---

## 📖 相关文档

- [Kubernetes官方文档](https://kubernetes.io/docs/)
- [Python Kubernetes客户端](https://github.com/kubernetes-client/python)
- [运维自动化平台API文档](./docs/API_DOCUMENTATION.md)

---

**版本**: v3.0  
**更新日期**: 2025-01-15  
**作者**: 运维自动化平台团队  
**适用于**: 本科毕业论文项目 - Kubernetes扩展功能

