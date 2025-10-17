# 告警系统使用指南

## 📋 概述

本告警系统提供了**完整的自动化监控和通知功能**，能够实时监控服务器资源使用情况，并在超过阈值时自动触发告警和发送通知。

---

## 🔧 系统架构

### 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                    告警系统架构                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │  后台监控任务 │ ──▶ │ 服务器状态    │                │
│  │  (每分钟执行) │      │ 获取服务      │                │
│  └──────────────┘      └──────────────┘                │
│         │                      │                        │
│         ▼                      ▼                        │
│  ┌──────────────┐      ┌──────────────┐                │
│  │ 告警规则引擎  │ ◀── │ 资源使用数据  │                │
│  │ (规则匹配)   │      │ (CPU/内存/磁盘)│               │
│  └──────────────┘      └──────────────┘                │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │  告警创建     │                                      │
│  │  (数据库记录) │                                      │
│  └──────────────┘                                      │
│         │                                               │
│         ▼                                               │
│  ┌──────────────────────────┐                         │
│  │    通知发送               │                         │
│  ├──────────────────────────┤                         │
│  │  • 邮件通知               │                         │
│  │  • Webhook通知            │                         │
│  │  • 钉钉/Slack/企业微信    │                         │
│  └──────────────────────────┘                         │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │  静默期设置   │ (防止重复告警)                       │
│  └──────────────┘                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ 工作流程

### 1. 后台监控任务

**启动时机**: FastAPI应用启动时自动启动

**执行频率**: 每1分钟执行一次

**任务流程**:
```python
def _monitor_servers():
    1. 获取所有"在线"状态的服务器
    2. 对每个服务器:
       a. 通过SSH获取实时资源使用率（CPU/内存/磁盘）
       b. 构建metrics字典: {"cpu": 85.5, "memory": 70.2, "disk": 90.0}
       c. 调用告警规则引擎检查是否触发告警
       d. 如果触发告警，创建告警记录并发送通知
    3. 打印监控日志
```

**日志示例**:
```
✅ System monitoring job added: Check servers every 1 minute
⚠️  Triggered 2 alert(s) for server example01 (ID: 1)
   - [WARNING] CPU使用率告警: CPU使用率达到 88.5%，超过阈值 80.0%
   - [ERROR] 内存使用率告警: MEMORY使用率达到 92.3%，超过阈值 90.0%
```

### 2. 告警规则匹配

**规则类型**:
- **全局规则**: `server_id = NULL`，适用于所有服务器
- **服务器特定规则**: `server_id = 1`，只适用于指定服务器

**匹配逻辑**:
```python
for metric_type in ['cpu', 'memory', 'disk']:
    # 1. 获取适用的规则（全局 + 服务器特定）
    rules = get_applicable_rules(server_id, metric_type)
    
    for rule in rules:
        # 2. 检查是否在静默期（避免重复告警）
        if is_silenced(rule.id, server_id):
            continue
        
        # 3. 检查当前值是否满足规则条件
        if check_value_against_rule(current_value, threshold, operator):
            # 4. 创建告警
            create_alert(...)
            
            # 5. 发送通知
            send_notification(...)
            
            # 6. 设置静默期
            set_silence(rule.id, server_id, duration)
```

### 3. 阈值比较操作符

| 操作符 | 说明 | 示例 |
|--------|------|------|
| `gt` | 大于 | `cpu_percent > 80` |
| `gte` | 大于等于 | `memory_percent >= 90` |
| `lt` | 小于 | `disk_free < 10` |
| `lte` | 小于等于 | `load_avg <= 0.5` |
| `eq` | 等于 | `status == 0` |

### 4. 通知发送

**邮件通知**:
```python
if rule.enable_email and rule.email_recipients:
    send_email(
        to=rule.email_recipients,
        subject=f"[{alert.level.upper()}] {alert.title}",
        body=alert.message
    )
```

**Webhook通知**:
```python
if rule.enable_webhook and rule.webhook_url:
    requests.post(
        url=rule.webhook_url,
        json={
            "alert_id": alert.id,
            "level": alert.level,
            "title": alert.title,
            "message": alert.message,
            ...
        },
        headers=rule.webhook_headers
    )
```

### 5. 静默期机制

**目的**: 防止同一告警在短时间内重复触发

**实现**:
```python
# 设置静默期（例如300秒 = 5分钟）
AlertSilence.create(
    rule_id=rule.id,
    server_id=server.id,
    start_time=now,
    end_time=now + timedelta(seconds=rule.silence_duration)
)

# 检查是否在静默期
def is_silenced(rule_id, server_id):
    silence = db.query(AlertSilence).filter(
        AlertSilence.rule_id == rule_id,
        AlertSilence.server_id == server_id,
        AlertSilence.end_time > datetime.utcnow()
    ).first()
    return silence is not None
```

---

## 🚀 快速开始

### 第1步：启动后端服务

```bash
cd /Users/DZ0400191/project_2/backend
source venv/bin/activate  # 如果有虚拟环境
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**启动日志检查**:
```
INFO:     Application startup complete.
✅ System monitoring job added: Check servers every 1 minute
✅ Loaded 0 scheduled tasks
```

看到 `System monitoring job added` 说明后台监控任务已启动！

### 第2步：添加服务器

1. 登录前端管理界面
2. 进入"资源管理" → "服务器"标签页
3. 点击"添加服务器"，填写服务器信息
4. 确保服务器状态为"在线"

### 第3步：创建告警规则

1. 进入"告警管理" → "告警规则"
2. 点击"创建规则"
3. 配置规则参数：

**示例1: CPU使用率告警**
```yaml
名称: CPU使用率过高告警
描述: 当CPU使用率超过80%时触发
服务器: [全局规则] 或 [选择特定服务器]
监控指标: cpu
阈值: 80
比较操作符: 大于 (gt)
告警级别: warning
静默期: 300秒 (5分钟)
```

**示例2: 内存使用率告警**
```yaml
名称: 内存使用率危险
描述: 当内存使用率超过90%时触发
服务器: [全局规则]
监控指标: memory
阈值: 90
比较操作符: 大于等于 (gte)
告警级别: error
```

**示例3: 磁盘空间告警**
```yaml
名称: 磁盘空间不足
描述: 当磁盘使用率超过85%时告警
服务器: [全局规则]
监控指标: disk
阈值: 85
比较操作符: 大于 (gt)
告警级别: warning
```

### 第4步：配置通知方式

**邮件通知**:
```yaml
启用邮件: 是
收件人列表:
  - admin@example.com
  - ops@example.com
```

**Webhook通知（钉钉）**:
```yaml
启用Webhook: 是
Webhook URL: https://oapi.dingtalk.com/robot/send?access_token=xxxxx
请求头: 
  Content-Type: application/json
```

### 第5步：测试告警

**方法1: 模拟CPU负载（Linux）**
```bash
# SSH连接到服务器
ssh root@your-server

# 运行CPU压力测试（持续2分钟）
stress-ng --cpu 4 --timeout 120s

# 或者简单的死循环
for i in {1..4}; do while :; do :; done & done

# 停止测试
killall stress-ng
# 或
pkill -f "while :; do :; done"
```

**方法2: 模拟内存占用（Linux）**
```bash
# 占用1GB内存
stress-ng --vm 1 --vm-bytes 1G --timeout 120s
```

**方法3: 等待自动监控**
- 后台监控任务每1分钟自动检查一次
- 如果服务器资源使用率超过阈值，会自动触发告警
- 在"告警管理" → "告警列表"中查看触发的告警

---

## 📊 查看告警

### 告警列表

进入"告警管理" → "告警列表"，可以看到：

| 字段 | 说明 |
|------|------|
| 告警标题 | 规则名称 |
| 服务器 | 触发告警的服务器 |
| 类型 | cpu/memory/disk |
| 级别 | info/warning/error/critical |
| 当前值 | 实际资源使用率 |
| 阈值 | 规则配置的阈值 |
| 状态 | open/acknowledged/resolved |
| 触发时间 | 告警创建时间 |

### 告警统计

页面顶部显示：
- **总告警数**
- **待处理告警**（状态=open）
- **已确认告警**（状态=acknowledged）
- **已解决告警**（状态=resolved）

### 告警趋势图

使用ECharts显示最近7天的告警趋势

---

## 🔍 故障排查

### 问题1: 没有收到告警

**检查清单**:

1. **后端是否启动监控任务？**
   ```bash
   # 查看后端启动日志
   tail -f backend.log
   # 应该看到: ✅ System monitoring job added: Check servers every 1 minute
   ```

2. **服务器状态是否在线？**
   ```bash
   # 在前端检查服务器状态
   # 或通过API检查
   curl http://localhost:8000/api/servers
   ```

3. **告警规则是否启用？**
   ```bash
   # 检查数据库
   sqlite3 backend/app.db "SELECT id, name, is_active, metric_type, threshold_value FROM alert_rules;"
   ```

4. **资源使用率是否真的超过阈值？**
   ```bash
   # 手动查询服务器状态
   curl http://localhost:8000/api/servers/1/status
   ```

5. **是否在静默期？**
   ```bash
   # 检查数据库
   sqlite3 backend/app.db "SELECT * FROM alert_silences WHERE end_time > datetime('now');"
   ```

### 问题2: 通知没有发送

**检查清单**:

1. **规则是否配置了通知方式？**
   - 检查`enable_email`或`enable_webhook`是否为True
   - 检查`email_recipients`或`webhook_url`是否配置

2. **邮件服务是否配置？**
   ```python
   # 检查 backend/app/core/config.py
   SMTP_HOST = "smtp.gmail.com"
   SMTP_PORT = 587
   SMTP_USER = "your-email@gmail.com"
   SMTP_PASSWORD = "your-password"
   ```

3. **Webhook URL是否正确？**
   - 使用Postman或curl测试Webhook URL
   - 检查返回状态码

4. **查看通知记录**:
   ```bash
   sqlite3 backend/app.db "SELECT * FROM alert_notifications ORDER BY sent_at DESC LIMIT 10;"
   ```

### 问题3: 告警重复触发

**原因**: 静默期设置过短

**解决**: 增加规则的`silence_duration`值
```
推荐设置:
- warning级别: 300秒 (5分钟)
- error级别: 600秒 (10分钟)
- critical级别: 900秒 (15分钟)
```

---

## 📝 最佳实践

### 1. 告警规则分级

```yaml
# 预警级别
warning:
  cpu: 70%
  memory: 75%
  disk: 80%

# 严重级别  
error:
  cpu: 85%
  memory: 90%
  disk: 90%

# 紧急级别
critical:
  cpu: 95%
  memory: 95%
  disk: 95%
```

### 2. 静默期设置

```yaml
info: 180秒 (3分钟)
warning: 300秒 (5分钟)
error: 600秒 (10分钟)
critical: 900秒 (15分钟)
```

### 3. 通知策略

```yaml
# 低优先级：仅Webhook
info/warning:
  - Webhook (钉钉群消息)

# 高优先级：Webhook + 邮件
error:
  - Webhook (钉钉群消息)
  - Email (运维团队)

# 紧急：Webhook + 邮件 + 电话（需集成）
critical:
  - Webhook (钉钉群消息 + @所有人)
  - Email (运维团队 + 管理层)
  - SMS (值班手机)  # 待实现
```

### 4. 监控频率

```python
# 当前: 1分钟/次
# 如果服务器较多，可以调整为:
# - 3分钟/次 (节省资源)
# - 30秒/次 (更实时，但SSH连接频繁)

# 修改位置: scheduler_service.py
IntervalTrigger(minutes=1)  # 改为 minutes=3
```

---

## 🎯 总结

告警系统现在已经完整实现：

✅ **后台监控任务** - 每分钟自动检查服务器状态  
✅ **动态规则引擎** - 灵活配置告警规则  
✅ **静默期机制** - 防止重复告警  
✅ **多渠道通知** - 支持邮件和Webhook  
✅ **完整的告警生命周期** - 创建 → 确认 → 解决  

**重启后端服务后，告警系统将自动开始工作！** 🎉

