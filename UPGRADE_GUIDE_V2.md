# 运维自动化平台 v2.0 升级指南

## 🎉 重大更新

本次更新实现了**完整的告警规则系统**，这是论文的一个重要亮点功能！

### 新增功能总览

1. ✅ **动态告警规则管理**
2. ✅ **多渠道通知系统**（邮件/Webhook）
3. ✅ **告警统计与趋势分析**
4. ✅ **智能静默机制**
5. ✅ **可视化告警面板**

---

## 📦 新增文件清单

### 后端文件

```
backend/app/
├── models/
│   └── alert_rule.py              # 告警规则、通知、静默记录模型
├── schemas/
│   └── alert_rule.py              # 告警规则Schema定义
├── services/
│   ├── alert_rule_service.py      # 告警规则服务
│   └── notification_service.py    # 通知服务
└── api/
    └── alert_rules.py             # 告警规则API接口
```

### 前端文件

```
frontend/src/
├── views/
│   ├── AlertRules.vue             # 告警规则管理页面（新增）
│   └── Alerts.vue                 # 告警管理页面（增强）
└── router/
    └── index.js                   # 路由配置（已更新）
```

### 文档文件

```
docs/
└── ALERT_RULES_GUIDE.md          # 告警规则使用指南
```

---

## 🔄 数据库变更

### 新增数据表

#### 1. alert_rules 表
告警规则配置表

```sql
CREATE TABLE alert_rules (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description VARCHAR(500),
    server_id INTEGER,  -- NULL表示全局规则
    metric_type VARCHAR(50) NOT NULL,  -- cpu, memory, disk, network
    threshold_value FLOAT NOT NULL,
    threshold_operator VARCHAR(10) DEFAULT 'gt',
    duration INTEGER DEFAULT 60,
    alert_level VARCHAR(20) DEFAULT 'warning',
    enable_email BOOLEAN DEFAULT 0,
    email_recipients JSON,
    enable_webhook BOOLEAN DEFAULT 0,
    webhook_url VARCHAR(500),
    webhook_headers JSON,
    silence_duration INTEGER DEFAULT 300,
    is_active BOOLEAN DEFAULT 1,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);
```

#### 2. alert_notifications 表
告警通知记录表

```sql
CREATE TABLE alert_notifications (
    id INTEGER PRIMARY KEY,
    alert_id INTEGER NOT NULL,
    rule_id INTEGER,
    notification_type VARCHAR(20) NOT NULL,  -- email, webhook
    recipient VARCHAR(500),
    status VARCHAR(20) DEFAULT 'pending',  -- pending, sent, failed
    error_message VARCHAR(1000),
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES alerts (id),
    FOREIGN KEY (rule_id) REFERENCES alert_rules (id)
);
```

#### 3. alert_silences 表
告警静默记录表

```sql
CREATE TABLE alert_silences (
    id INTEGER PRIMARY KEY,
    rule_id INTEGER NOT NULL,
    server_id INTEGER NOT NULL,
    last_alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    silence_until TIMESTAMP NOT NULL,
    FOREIGN KEY (rule_id) REFERENCES alert_rules (id),
    FOREIGN KEY (server_id) REFERENCES servers (id)
);
```

### 数据库迁移

数据表会在应用启动时**自动创建**（通过SQLAlchemy的`Base.metadata.create_all()`），无需手动迁移。

如果使用Alembic进行迁移，可以运行：

```bash
cd backend
alembic revision --autogenerate -m "添加告警规则表"
alembic upgrade head
```

---

## 📥 依赖更新

### 后端依赖

更新 `backend/requirements.txt`：

```txt
requests==2.31.0  # 新增：用于Webhook HTTP请求
```

安装新依赖：

```bash
cd backend
pip install requests==2.31.0
```

### 前端依赖

更新 `frontend/package.json`：

```json
{
  "dependencies": {
    "@element-plus/icons-vue": "^2.3.1",  // 新增：图标库
    "echarts": "^5.4.3"                   // 新增：图表库
  }
}
```

安装新依赖：

```bash
cd frontend
npm install
```

---

## 🚀 升级步骤

### 1. 备份数据（重要！）

```bash
# 备份数据库
cp backend/devops.db backend/devops.db.backup

# 或导出数据
sqlite3 backend/devops.db .dump > backup.sql
```

### 2. 拉取最新代码

```bash
git pull origin main
```

### 3. 更新后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 更新前端依赖

```bash
cd ../frontend
npm install
```

### 5. 启动服务

```bash
# 启动后端
cd backend
python main.py

# 启动前端（新终端）
cd frontend
npm run dev
```

### 6. 验证升级

访问 http://localhost:5173，检查：
- ✅ 左侧菜单是否显示"告警规则"
- ✅ 访问"告警管理"页面是否显示统计卡片和趋势图
- ✅ 访问"告警规则"页面是否正常

---

## 🎯 使用新功能

### 1. 创建默认告警规则

系统不会自动创建默认规则，建议手动创建以下规则：

```
规则1: CPU使用率告警
  - 监控指标: CPU
  - 阈值: > 80%
  - 持续: 60秒
  - 级别: warning
  - 应用范围: 全局规则

规则2: 内存使用率告警
  - 监控指标: Memory
  - 阈值: > 85%
  - 持续: 60秒
  - 级别: warning
  - 应用范围: 全局规则

规则3: 磁盘空间告警
  - 监控指标: Disk
  - 阈值: > 85%
  - 持续: 0秒（立即触发）
  - 级别: error
  - 应用范围: 全局规则
```

### 2. 配置通知（可选）

#### 邮件通知配置
在规则中开启邮件通知并添加收件人。

⚠️ 需要在 `backend/app/services/notification_service.py` 中配置SMTP服务器：

```python
# 默认配置
smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_user = "your-email@gmail.com"  # 需要配置
smtp_password = "your-app-password"  # 需要配置
```

#### Webhook通知配置
在规则中开启Webhook并填写目标URL。

可以使用以下服务测试：
- [Webhook.site](https://webhook.site/) - 测试Webhook接收
- 钉钉机器人
- 企业微信机器人

---

## 🔧 API 变更

### 新增API端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/alert-rules` | 获取告警规则列表 |
| POST | `/api/alert-rules` | 创建告警规则 |
| GET | `/api/alert-rules/{id}` | 获取规则详情 |
| PUT | `/api/alert-rules/{id}` | 更新告警规则 |
| DELETE | `/api/alert-rules/{id}` | 删除告警规则 |
| POST | `/api/alert-rules/{id}/toggle` | 启用/禁用规则 |
| GET | `/api/alert-rules/statistics/overview` | 获取告警统计 |
| GET | `/api/alert-rules/statistics/trends` | 获取告警趋势 |
| GET | `/api/alert-rules/notifications/list` | 获取通知记录 |
| POST | `/api/alert-rules/test-webhook` | 测试Webhook |

### 修改的API

`AlertService.check_server_alerts()` 现在使用动态规则系统，但保持向后兼容。

---

## ⚠️ 注意事项

### 1. 兼容性
- ✅ 完全向后兼容，不会影响现有功能
- ✅ 旧的告警逻辑仍然工作（但使用新的规则系统）

### 2. 性能影响
- 新增的数据库查询对性能影响minimal
- 告警检查逻辑更加高效（使用索引和条件过滤）

### 3. 默认行为变更
- ⚠️ 如果没有配置任何规则，服务器监控将**不会**触发告警
- 建议升级后立即创建基础告警规则

### 4. SMTP配置
- 如果不配置SMTP，邮件通知将被标记为"skipped"
- 不影响其他功能正常使用

---

## 🐛 已知问题

### 问题1：首次加载告警趋势图报错
**原因**：没有历史告警数据  
**解决**：等待系统运行一段时间后自动恢复

### 问题2：Webhook测试一直显示失败
**原因**：目标URL不可访问或超时  
**解决**：检查URL是否正确，使用 webhook.site 进行测试

---

## 📚 相关文档

- [告警规则使用指南](./docs/ALERT_RULES_GUIDE.md) - 详细的功能说明和最佳实践
- [API 文档](./docs/API_DOCUMENTATION.md) - 完整的API接口文档
- [部署指南](./docs/DEPLOYMENT.md) - 生产环境部署说明

---

## 🎓 论文要点

本次更新是毕业论文的**核心创新点**之一，可以在论文中重点描述：

### 技术亮点
1. **灵活的规则引擎**：支持多种操作符和监控指标
2. **智能告警策略**：持续时间检测 + 静默期机制
3. **多渠道通知**：邮件和Webhook双通道
4. **数据可视化**：ECharts实时趋势分析
5. **RESTful API**：完整的CRUD操作

### 架构设计
```
前端 (Vue3 + Element Plus + ECharts)
         ↓
  API层 (FastAPI REST)
         ↓
  服务层 (AlertRuleService + NotificationService)
         ↓
  数据层 (SQLAlchemy ORM)
         ↓
  数据库 (SQLite/MySQL)
```

---

## ✅ 升级检查清单

- [ ] 备份数据库
- [ ] 更新代码
- [ ] 安装后端依赖（`pip install -r requirements.txt`）
- [ ] 安装前端依赖（`npm install`）
- [ ] 启动后端服务
- [ ] 启动前端服务
- [ ] 访问"告警规则"页面
- [ ] 创建测试规则
- [ ] 触发测试告警
- [ ] 查看告警统计
- [ ] （可选）配置邮件通知
- [ ] （可选）配置Webhook通知

---

## 🤝 技术支持

如有问题，请查看：
1. [启动指南](./启动指南.md)
2. [故障排除](./docs/ALERT_RULES_GUIDE.md#故障排除)
3. GitHub Issues

---

**升级版本**: v1.0 → v2.0  
**更新日期**: 2025-01-15  
**作者**: 运维自动化平台团队  
**适用于**: 本科毕业论文项目

