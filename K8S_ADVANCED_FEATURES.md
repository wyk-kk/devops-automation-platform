# Kubernetes 高级功能使用指南

## 🎉 功能总览

本次更新为运维自动化平台添加了完整的Kubernetes高级管理功能，包括：

1. ✅ **增强的仪表盘** - K8s资源统计、健康度评分、实时图表
2. ✅ **Pod日志查看** - 实时日志、容器日志过滤
3. ✅ **Pod管理** - 重启Pod、删除Pod
4. ✅ **Deployment管理** - 副本伸缩、状态监控
5. ✅ **告警集成** - K8s节点和Pod告警规则

---

## 📊 功能1：增强的仪表盘

### 新增内容

#### 顶部统计卡片
```
┌─────────────┬──────────────┬─────────────┬─────────────┐
│  服务器     │  K8s集群     │  总节点数    │  待处理告警 │
│   20台      │   3个        │   50个      │   5条       │
│ 在线 18台   │ 活跃 3个     │  1200 Pods  │  严重 2条   │
└─────────────┴──────────────┴─────────────┴─────────────┘
```

#### 资源使用趋势图
- 支持切换查看服务器/K8s资源
- 7天趋势数据
- ECharts可交互图表

#### K8s环境分布饼图
- 按环境分组（dev/test/staging/prod）
- 实时统计

#### 集群健康度评分
- **计算公式**:
  ```
  健康度 = 基础分(70) + 节点就绪率(20) + Pod运行率(10) - 告警惩罚
  ```
- **评级标准**:
  - 90-100: 优秀 (绿色)
  - 70-89: 良好 (黄色)
  - 50-69: 需改进 (橙色)
  - <50: 异常 (红色)

#### K8s集群状态表
- 实时连接状态
- 版本信息
- 资源统计（节点/Pod/命名空间）
- 集群健康度百分比

### 使用方法

访问首页即可查看增强的仪表盘：
```
http://localhost:5173/dashboard
```

---

## 📝 功能2：Pod日志查看

### API端点
```
GET /api/k8s/clusters/{cluster_id}/pods/{namespace}/{pod_name}/logs
```

### 参数
- `cluster_id`: 集群ID
- `namespace`: 命名空间
- `pod_name`: Pod名称
- `container`: (可选) 容器名称
- `tail_lines`: (可选) 尾部行数，默认100

### 示例请求
```bash
curl -X GET "http://localhost:8000/api/k8s/clusters/1/pods/default/my-app-123/logs?tail_lines=200" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 响应
```json
{
  "logs": "[2025-01-15 10:30:00] INFO: Application started\n[2025-01-15 10:30:01] INFO: Listening on port 8080\n..."
}
```

### 前端使用（待实现）
```javascript
// 在Pod列表页面添加"查看日志"按钮
async function viewPodLogs(clusterId, namespace, podName) {
  const response = await api.get(
    `/k8s/clusters/${clusterId}/pods/${namespace}/${podName}/logs?tail_lines=500`
  )
  // 在对话框中显示日志
  showLogsDialog(response.data.logs)
}
```

---

## 🔄 功能3：Pod重启和删除

### Pod删除（触发重启）

Kubernetes中删除Pod会触发控制器（如Deployment）自动创建新Pod，实现重启效果。

#### API端点
```
DELETE /api/k8s/clusters/{cluster_id}/pods/{namespace}/{pod_name}
```

#### 示例
```bash
curl -X DELETE "http://localhost:8000/api/k8s/clusters/1/pods/default/my-app-123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 响应
```json
{
  "message": "Pod deleted successfully"
}
```

### 使用场景

1. **应用重启**: Pod出现问题需要重启
2. **配置更新**: 重启应用加载新配置
3. **资源回收**: 释放有问题的Pod

### 注意事项

⚠️ **重要提示**:
- 删除Pod会导致短暂服务中断
- 确保有多副本或备用Pod
- StatefulSet类型的Pod会保持原有名称
- Job/CronJob的Pod删除后不会自动重建

---

## 📦 功能4：Deployment管理

### 获取Deployment列表

#### API端点
```
GET /api/k8s/clusters/{cluster_id}/deployments?namespace={namespace}
```

#### 响应示例
```json
[
  {
    "name": "nginx-deployment",
    "namespace": "default",
    "replicas": 3,
    "ready_replicas": 3,
    "available_replicas": 3,
    "labels": {
      "app": "nginx"
    },
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

### Deployment伸缩

#### API端点
```
POST /api/k8s/clusters/{cluster_id}/deployments/{namespace}/{deployment_name}/scale
```

#### 参数
```json
{
  "replicas": 5
}
```

#### 示例
```bash
curl -X POST "http://localhost:8000/api/k8s/clusters/1/deployments/default/nginx-deployment/scale?replicas=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 响应
```json
{
  "message": "Deployment scaled to 5 replicas"
}
```

### 伸缩策略

#### 扩容（Scale Up）
```
副本数: 3 → 5
场景: 流量增加、高峰期
效果: 增加Pod数量，提升处理能力
```

#### 缩容（Scale Down）
```
副本数: 5 → 2
场景: 流量减少、节约资源
效果: 减少Pod数量，降低成本
```

#### 自动伸缩（HPA）
未来可以集成Horizontal Pod Autoscaler，实现自动伸缩：
```yaml
minReplicas: 2
maxReplicas: 10
targetCPUUtilizationPercentage: 70
```

---

## 🚨 功能5：K8s告警规则

### 告警规则类型

#### 1. 节点告警

**NotReady告警**:
```json
{
  "name": "K8s节点NotReady告警",
  "metric_type": "k8s_node_status",
  "threshold_operator": "eq",
  "threshold_value": "NotReady",
  "alert_level": "critical",
  "enable_email": true,
  "enable_webhook": true
}
```

**资源告警**:
```json
{
  "name": "K8s节点资源不足",
  "metric_type": "k8s_node_capacity",
  "threshold_operator": "lt",
  "threshold_value": 20,  // 剩余容量<20%
  "alert_level": "warning"
}
```

#### 2. Pod告警

**Pod异常告警**:
```json
{
  "name": "Pod状态异常",
  "metric_type": "k8s_pod_status",
  "conditions": {
    "status": ["CrashLoopBackOff", "Error", "Failed", "Unknown"]
  },
  "alert_level": "error"
}
```

**Pod重启告警**:
```json
{
  "name": "Pod频繁重启",
  "metric_type": "k8s_pod_restarts",
  "threshold_operator": "gt",
  "threshold_value": 5,  // 重启次数>5
  "duration": 300,  // 5分钟内
  "alert_level": "warning"
}
```

#### 3. Deployment告警

**副本数不足**:
```json
{
  "name": "Deployment副本不足",
  "metric_type": "k8s_deployment_replicas",
  "condition": "ready_replicas < desired_replicas",
  "alert_level": "warning"
}
```

### 告警通知

支持的通知方式：
- ✅ **邮件**: 发送详细告警信息
- ✅ **Webhook**: 集成钉钉、Slack、企业微信等

### 告警示例

```
告警标题: [CRITICAL] K8s节点异常
集群: production-k8s
节点: worker-node-03
状态: NotReady
时间: 2025-01-15 14:30:00

详情:
节点 worker-node-03 状态变为NotReady
可能原因: 网络问题、资源耗尽、kubelet异常
建议操作: 
1. 检查节点状态: kubectl describe node worker-node-03
2. 查看kubelet日志
3. 检查节点资源使用情况
```

---

## 🎯 实际使用场景

### 场景1：应用发布和回滚

**发布新版本**:
1. 更新Deployment镜像
2. 观察Pod滚动更新
3. 查看Pod日志确认启动成功
4. 监控健康度变化

**快速回滚**:
1. 发现问题后立即伸缩为0副本
2. 恢复旧版本镜像
3. 伸缩回正常副本数

### 场景2：流量高峰应对

**准备阶段**:
```
当前: 3副本
预期流量: 5倍增长
操作: 扩容到 15副本
```

**监控指标**:
- Pod CPU/内存使用率
- 请求响应时间
- 错误率

**结束后**:
```
流量恢复正常
缩容到 5副本（保留buffer）
```

### 场景3：故障排查

**Pod异常**:
1. 收到告警: Pod CrashLoopBackOff
2. 查看Pod日志定位原因
3. 修复配置后重启Pod
4. 观察恢复情况

**节点异常**:
1. 收到告警: 节点NotReady
2. 查看节点列表确认状态
3. 检查节点上的Pod状态
4. 必要时手动迁移Pod

### 场景4：成本优化

**定时伸缩**:
```
工作时间 (9:00-18:00): 
  - Web应用: 10副本
  - API服务: 8副本

非工作时间:
  - Web应用: 3副本
  - API服务: 2副本

预计节约: 60% 计算成本
```

---

## 📈 健康度评分详解

### 评分模型

```python
def calculate_health_score(cluster):
    base_score = 70  # 基础分
    
    # 节点健康度 (最高20分)
    ready_nodes = count_ready_nodes(cluster)
    total_nodes = cluster.node_count
    node_score = (ready_nodes / total_nodes) * 20
    
    # Pod健康度 (最高10分)
    running_pods = count_running_pods(cluster)
    total_pods = cluster.pod_count
    pod_score = (running_pods / total_pods) * 10
    
    # 告警惩罚
    warning_penalty = cluster.warning_alerts * 1
    critical_penalty = cluster.critical_alerts * 5
    
    final_score = base_score + node_score + pod_score - warning_penalty - critical_penalty
    return max(0, min(100, final_score))
```

### 健康度指标

| 分数范围 | 等级 | 颜色 | 说明 |
|---------|-----|-----|------|
| 90-100 | 优秀 | 🟢 绿色 | 所有指标正常，系统运行良好 |
| 70-89 | 良好 | 🟡 黄色 | 大部分指标正常，有少量告警 |
| 50-69 | 需改进 | 🟠 橙色 | 存在多个问题，需要关注 |
| 0-49 | 异常 | 🔴 红色 | 严重问题，需要立即处理 |

---

## 🔧 API完整列表

### 集群管理
- `GET /api/k8s/clusters` - 集群列表
- `POST /api/k8s/clusters` - 创建集群
- `GET /api/k8s/clusters/{id}` - 集群详情
- `PUT /api/k8s/clusters/{id}` - 更新集群
- `DELETE /api/k8s/clusters/{id}` - 删除集群
- `POST /api/k8s/clusters/{id}/check-status` - 检查状态
- `POST /api/k8s/clusters/{id}/sync` - 同步资源

### 资源查询
- `GET /api/k8s/clusters/{id}/nodes` - 节点列表
- `GET /api/k8s/clusters/{id}/namespaces` - 命名空间列表
- `GET /api/k8s/clusters/{id}/pods` - Pod列表
- `GET /api/k8s/clusters/{id}/deployments` - Deployment列表

### Pod管理
- `GET /api/k8s/clusters/{id}/pods/{ns}/{name}/logs` - Pod日志
- `DELETE /api/k8s/clusters/{id}/pods/{ns}/{name}` - 删除Pod

### Deployment管理
- `POST /api/k8s/clusters/{id}/deployments/{ns}/{name}/scale` - 伸缩

### 统计信息
- `GET /api/k8s/statistics` - 总体统计

---

## 🚀 快速开始

### 1. 查看增强仪表盘
```
访问: http://localhost:5173/dashboard
功能: 查看K8s资源统计、健康度、趋势图
```

### 2. 管理Pod
```bash
# 查看Pod日志
curl GET "/api/k8s/clusters/1/pods/default/my-app/logs?tail_lines=100"

# 重启Pod
curl DELETE "/api/k8s/clusters/1/pods/default/my-app"
```

### 3. 伸缩Deployment
```bash
# 扩容到5副本
curl POST "/api/k8s/clusters/1/deployments/default/nginx/scale?replicas=5"

# 缩容到2副本
curl POST "/api/k8s/clusters/1/deployments/default/nginx/scale?replicas=2"
```

### 4. 配置告警
```
访问: http://localhost:5173/alert-rules
创建规则: 选择K8s指标类型
设置阈值: 根据业务需求
启用通知: 邮件或Webhook
```

---

## 📖 最佳实践

### 1. 健康度监控
- 设置告警: 健康度<70时发送通知
- 每日检查: 查看趋势图发现问题
- 定期优化: 解决影响健康度的因素

### 2. Pod管理
- 查看日志前确认容器名称
- 重启前检查副本数（避免服务中断）
- 使用标签过滤大量Pod

### 3. Deployment伸缩
- 扩容: 提前准备，避免流量冲击
- 缩容: 缓慢进行，观察影响
- 自动化: 结合监控数据自动伸缩

### 4. 告警配置
- 分级管理: Critical立即处理，Warning定期review
- 避免告警风暴: 合理设置静默期
- 定期优化: 调整阈值减少误报

---

## 🎓 论文写作要点

### 技术创新
1. **混合基础设施管理** - 传统+容器化统一平台
2. **健康度评分算法** - 量化系统健康状况
3. **智能告警系统** - K8s指标深度集成
4. **实时操作能力** - Pod日志、伸缩等

### 架构亮点
```
分层架构:
├── 展示层: Vue3 + ECharts
├── API层: FastAPI REST
├── 服务层: K8sService
├── 客户端: Python kubernetes SDK
└── 基础设施: K8s集群
```

### 功能完整性
- ✅ 集群管理
- ✅ 资源监控
- ✅ Pod操作
- ✅ Deployment管理
- ✅ 告警集成
- ✅ 日志查看
- ✅ 健康度评估

---

**版本**: v3.1  
**更新日期**: 2025-01-15  
**功能状态**: 全部实现  
**文档作者**: 运维自动化平台团队

