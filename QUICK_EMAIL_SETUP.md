# 邮件通知快速配置（5分钟搞定）

## 🚀 最快配置方式：使用Gmail

### 第1步：获取Gmail应用密码（2分钟）

1. 访问：https://myaccount.google.com/apppasswords
2. 选择应用："邮件" + 设备："其他（自定义名称）"
3. 输入名称："DevOps Platform"
4. 点击"生成"，复制16位密码（格式：xxxx xxxx xxxx xxxx）

### 第2步：配置后端（1分钟）

```bash
# 进入backend目录
cd /Users/DZ0400191/project_2/backend

# 创建.env文件
cp env.example .env

# 编辑.env文件
nano .env  # 或使用VSCode: code .env
```

修改以下几行：
```bash
SMTP_ENABLED=True
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # 刚才复制的应用密码
```

### 第3步：重启后端（1分钟）

```bash
# 停止旧进程
pkill -f "uvicorn main:app"

# 启动后端
cd /Users/DZ0400191/project_2/backend
source venv/bin/activate  # 如果有虚拟环境
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 第4步：验证（1分钟）

**方式A：快速测试**
```bash
cd /Users/DZ0400191/project_2/backend
python3 << 'EOF'
import smtplib
from email.mime.text import MIMEText

# 改成你的配置
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"
RECIPIENT = "your-email@gmail.com"  # 发给自己测试

msg = MIMEText("测试邮件 from DevOps Platform")
msg['Subject'] = "测试"
msg['From'] = SMTP_USER
msg['To'] = RECIPIENT

try:
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("✅ 邮件发送成功！检查收件箱。")
except Exception as e:
    print(f"❌ 失败：{e}")
EOF
```

**方式B：通过系统测试**
1. 打开前端，进入"告警管理" → "告警规则"
2. 创建规则，启用邮件通知，填写收件人邮箱
3. 触发告警（让服务器资源使用率超过阈值）
4. 查看后端日志和邮箱

---

## 🎯 完成！

如果看到 `✅ 邮件发送成功`，恭喜！邮件通知已配置完成！

---

## ❓ 常见问题

### 问题1：认证失败

**错误**：`SMTPAuthenticationError: (535, ...)`

**解决**：
- 确认使用的是"应用专用密码"，不是Gmail登录密码
- 确认已启用Google两步验证

### 问题2：邮件被跳过

**日志**：`⚠️  邮件通知未启用，跳过发送`

**解决**：
确保 `.env` 文件中 `SMTP_ENABLED=True`

### 问题3：没有.env文件

```bash
cd /Users/DZ0400191/project_2/backend
cp env.example .env
```

---

## 📖 完整文档

更详细的配置（QQ邮箱、163邮箱、企业邮箱等）请参考：
- [EMAIL_CONFIGURATION_GUIDE.md](./EMAIL_CONFIGURATION_GUIDE.md)

