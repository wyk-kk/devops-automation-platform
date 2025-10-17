# 🚨 立即配置邮件通知（3分钟）

## 当前状态
- ❌ .env文件已创建，但**还需要配置**
- ❌ SMTP_ENABLED=False（需要改为True）
- ❌ SMTP账号未配置（需要填写）

---

## 🚀 方案A：使用QQ邮箱（最快，推荐中国用户）

### 第1步：获取QQ邮箱授权码（1分钟）

1. **访问QQ邮箱**：https://mail.qq.com
2. **点击"设置"** → "账户"
3. **找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"**
4. **开启"IMAP/SMTP服务"**（如果没开启）
5. **点击"生成授权码"**
6. **发送短信验证**
7. **复制授权码**（例如：abcdefghijklmnop）

### 第2步：配置.env文件（1分钟）

```bash
# 进入backend目录
cd /Users/DZ0400191/project_2/backend

# 编辑.env文件
nano .env
# 或使用VSCode: code .env
# 或使用vim: vim .env
```

**修改以下内容**（找到对应行并修改）：

```bash
# 改这一行：将False改为True
SMTP_ENABLED=True

# 改这一行：填写你的QQ邮箱
SMTP_USER=your-qq-number@qq.com

# 改这一行：填写刚才获取的授权码
SMTP_PASSWORD=abcdefghijklmnop

# 如果使用QQ邮箱，还要改这两行：
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
```

**示例**：
```bash
SMTP_ENABLED=True
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=2483771013@qq.com
SMTP_PASSWORD=abcdefghijklmnop
```

保存并退出：
- nano: 按 `Ctrl+X`，然后 `Y`，然后 `Enter`
- vim: 按 `ESC`，输入 `:wq`，然后 `Enter`

### 第3步：重启后端（1分钟）

```bash
# 停止旧的后端进程
pkill -f "uvicorn main:app"

# 启动后端
cd /Users/DZ0400191/project_2/backend
source venv/bin/activate  # 如果有虚拟环境
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 第4步：测试（1分钟）

```bash
# 运行诊断工具
cd /Users/DZ0400191/project_2/backend
python3 diagnose_email.py
```

诊断工具会：
1. ✅ 检查配置
2. ✅ 测试SMTP连接
3. ✅ 询问是否发送测试邮件（输入y发送）

---

## 🚀 方案B：使用Gmail（推荐国际用户）

### 第1步：获取Gmail应用密码

1. **启用两步验证**：https://myaccount.google.com/security
2. **生成应用密码**：https://myaccount.google.com/apppasswords
3. **选择应用："邮件"，设备："其他"**
4. **复制16位密码**（格式：xxxx xxxx xxxx xxxx）

### 第2步：配置.env

```bash
SMTP_ENABLED=True
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

### 第3步：重启后端并测试（同上）

---

## 📋 完整的.env文件示例

```bash
# 数据库配置
DATABASE_URL=sqlite:///./devops.db

# JWT配置
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com

# CORS配置
CORS_ORIGINS=["*"]

# 项目信息
PROJECT_NAME=运维自动化平台
VERSION=1.0.0
DESCRIPTION=基于FastAPI的运维自动化管理平台

# ========== 重点：配置这部分 ==========
# SMTP邮件配置
SMTP_ENABLED=True
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=2483771013@qq.com
SMTP_PASSWORD=your-authorization-code-here
SMTP_FROM_NAME=运维自动化平台
# =====================================
```

---

## ✅ 验证清单

配置完成后，确认：

- [x] `.env`文件已创建
- [x] `SMTP_ENABLED=True` （不是False）
- [x] `SMTP_USER`填写了邮箱地址
- [x] `SMTP_PASSWORD`填写了授权码（QQ）或应用密码（Gmail）
- [x] 后端服务已重启
- [x] 运行`python3 diagnose_email.py`全部通过
- [x] 收到测试邮件

---

## 🎯 常见错误

### 错误1：密码填错了
- QQ邮箱：必须使用**授权码**，不是登录密码
- Gmail：必须使用**应用专用密码**（16位），不是登录密码

### 错误2：SMTP_ENABLED还是False
- 确保编辑的是`backend/.env`文件
- 确保`SMTP_ENABLED=True`没有空格
- 保存后重启后端

### 错误3：.env文件位置错误
- 必须在`backend/`目录下，不是项目根目录

---

## 📞 需要帮助？

运行诊断工具查看详细错误：
```bash
cd /Users/DZ0400191/project_2/backend
python3 diagnose_email.py
```

诊断工具会告诉你具体哪里配置错误。

