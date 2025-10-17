# 邮件通知配置指南

## 📧 概述

本指南将帮助您配置SMTP邮件服务，使告警系统能够自动发送邮件通知。

---

## ⚙️ 配置步骤

### 第1步：选择邮件服务提供商

常见的邮件服务提供商配置：

| 服务商 | SMTP服务器 | 端口 | 需要应用密码 |
|--------|-----------|------|-------------|
| **Gmail** | `smtp.gmail.com` | 587 | ✅ 是 |
| **QQ邮箱** | `smtp.qq.com` | 587 | ✅ 是（授权码） |
| **163邮箱** | `smtp.163.com` | 25/465 | ✅ 是（授权密码） |
| **Outlook** | `smtp-mail.outlook.com` | 587 | ❌ 否 |
| **企业邮箱** | 咨询IT部门 | 通常587 | 视情况而定 |

---

## 📝 详细配置教程

### 方式1：使用Gmail（推荐）

#### 1.1 获取Gmail应用专用密码

1. **启用两步验证**
   - 访问：https://myaccount.google.com/security
   - 找到"两步验证"并启用

2. **生成应用专用密码**
   - 访问：https://myaccount.google.com/apppasswords
   - 选择应用：选择"邮件"
   - 选择设备：选择"其他"，输入"DevOps Platform"
   - 点击"生成"
   - **复制生成的16位密码**（格式：xxxx xxxx xxxx xxxx）

#### 1.2 配置环境变量

**方法A：创建.env文件**（推荐）

```bash
# 进入backend目录
cd /Users/DZ0400191/project_2/backend

# 复制示例文件
cp .env.example .env

# 编辑.env文件
nano .env  # 或使用 vim、VSCode等编辑器
```

修改以下配置：
```bash
# 启用邮件通知
SMTP_ENABLED=True

# Gmail配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # 刚才生成的应用专用密码
SMTP_FROM_NAME=运维自动化平台
```

**方法B：直接修改config.py**（不推荐，仅用于测试）

编辑 `backend/app/core/config.py`：
```python
# SMTP邮件配置
SMTP_ENABLED: bool = True
SMTP_HOST: str = "smtp.gmail.com"
SMTP_PORT: int = 587
SMTP_USER: str = "your-email@gmail.com"
SMTP_PASSWORD: str = "xxxx xxxx xxxx xxxx"
SMTP_FROM_NAME: str = "运维自动化平台"
```

---

### 方式2：使用QQ邮箱

#### 2.1 获取QQ邮箱授权码

1. **登录QQ邮箱**
   - 访问：https://mail.qq.com

2. **开启SMTP服务**
   - 点击顶部"设置" → "账户"
   - 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
   - 开启"IMAP/SMTP服务"或"POP3/SMTP服务"

3. **生成授权码**
   - 点击"生成授权码"
   - 发送短信验证
   - **复制生成的授权码**

#### 2.2 配置环境变量

```bash
# .env文件配置
SMTP_ENABLED=True
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your-qq-number@qq.com
SMTP_PASSWORD=your-authorization-code  # 刚才生成的授权码
SMTP_FROM_NAME=运维自动化平台
```

---

### 方式3：使用163邮箱

#### 3.1 获取163邮箱授权密码

1. **登录163邮箱**
   - 访问：https://mail.163.com

2. **开启SMTP服务**
   - 点击顶部"设置" → "POP3/SMTP/IMAP"
   - 开启"IMAP/SMTP服务"

3. **设置授权密码**
   - 点击"客户端授权密码"
   - 发送短信验证
   - 设置并记住授权密码

#### 3.2 配置环境变量

```bash
# .env文件配置
SMTP_ENABLED=True
SMTP_HOST=smtp.163.com
SMTP_PORT=25  # 或使用465（SSL加密）
SMTP_USER=your-email@163.com
SMTP_PASSWORD=your-client-password  # 客户端授权密码
SMTP_FROM_NAME=运维自动化平台
```

---

### 方式4：使用企业邮箱

#### 4.1 获取SMTP信息

联系您的IT部门或邮件管理员，询问：
- SMTP服务器地址
- SMTP端口
- 是否需要TLS/SSL
- 认证方式

#### 4.2 常见企业邮箱配置

**腾讯企业邮箱**：
```bash
SMTP_HOST=smtp.exmail.qq.com
SMTP_PORT=587
```

**阿里企业邮箱**：
```bash
SMTP_HOST=smtp.mxhichina.com
SMTP_PORT=465
```

---

## 🚀 测试邮件配置

### 方法1：使用Python脚本测试

创建测试脚本 `backend/test_email.py`：

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置信息（从.env或config.py读取）
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
RECIPIENT = "recipient@example.com"  # 收件人邮箱

def test_email():
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['Subject'] = "测试邮件 - 运维自动化平台"
        msg['From'] = SMTP_USER
        msg['To'] = RECIPIENT
        
        body = "这是一封测试邮件，用于验证SMTP配置是否正确。"
        msg.attach(MIMEText(body, 'plain'))
        
        # 连接SMTP服务器
        print(f"正在连接到 {SMTP_HOST}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        
        # 启用TLS加密
        print("启用TLS加密...")
        server.starttls()
        
        # 登录
        print(f"正在登录 {SMTP_USER}...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        # 发送邮件
        print(f"正在发送邮件到 {RECIPIENT}...")
        server.send_message(msg)
        
        # 关闭连接
        server.quit()
        
        print("✅ 邮件发送成功！请检查收件箱。")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ 认证失败：{e}")
        print("请检查：")
        print("1. 邮箱地址是否正确")
        print("2. 密码是否正确（Gmail需要使用应用专用密码）")
        print("3. 是否启用了两步验证")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP错误：{e}")
        return False
        
    except Exception as e:
        print(f"❌ 发送失败：{e}")
        return False

if __name__ == "__main__":
    test_email()
```

运行测试：
```bash
cd /Users/DZ0400191/project_2/backend
source venv/bin/activate  # 如果使用虚拟环境
python test_email.py
```

### 方法2：通过API测试

**1. 先创建一个告警规则（启用邮件通知）**

**2. 触发告警**（让资源使用率超过阈值）

**3. 查看后端日志**：
```bash
# 应该看到类似以下输出
📧 正在发送邮件到 recipient@example.com...
   SMTP服务器: smtp.gmail.com:587
   发件人: your-email@gmail.com
✅ 邮件发送成功到 recipient@example.com
```

---

## 🔍 常见问题排查

### 问题1：认证失败 (SMTPAuthenticationError)

**可能原因**：
1. **Gmail**：没有使用应用专用密码，而是使用了普通密码
2. **QQ邮箱**：没有开启SMTP服务或使用了登录密码而非授权码
3. 邮箱地址或密码输入错误

**解决方案**：
- Gmail：确保使用16位应用专用密码
- QQ邮箱：使用授权码，不是登录密码
- 检查SMTP_USER和SMTP_PASSWORD是否正确

### 问题2：连接超时

**可能原因**：
1. 防火墙阻止了SMTP端口
2. SMTP服务器地址错误
3. 网络问题

**解决方案**：
```bash
# 测试端口是否可达
telnet smtp.gmail.com 587

# 或使用nc
nc -zv smtp.gmail.com 587
```

### 问题3：邮件被跳过

**后端日志显示**：
```
⚠️  邮件通知未启用，跳过发送到 xxx@example.com
```

**解决方案**：
确保 `SMTP_ENABLED=True`

### 问题4：SSL/TLS错误

**解决方案**：
- 确认使用正确的端口（587用于TLS，465用于SSL）
- Gmail和大部分邮箱使用587端口

### 问题5：邮件进入垃圾箱

**解决方案**：
1. 添加发件人到通讯录
2. 标记为"非垃圾邮件"
3. 考虑使用企业邮箱

---

## ✅ 验证清单

配置完成后，请确认：

- [x] SMTP服务器地址和端口正确
- [x] 使用了正确的认证凭据（应用专用密码/授权码）
- [x] `SMTP_ENABLED=True`
- [x] SMTP_USER和SMTP_PASSWORD已填写
- [x] 后端服务已重启
- [x] 告警规则中启用了邮件通知
- [x] 告警规则中配置了收件人邮箱
- [x] 测试邮件发送成功

---

## 📊 邮件通知记录

可以通过以下方式查看邮件发送记录：

### 方法1：查看数据库

```bash
cd /Users/DZ0400191/project_2/backend
sqlite3 devops.db

# 查询通知记录
SELECT 
    id,
    notification_type,
    recipient,
    status,
    error_message,
    sent_at
FROM alert_notifications
WHERE notification_type = 'email'
ORDER BY created_at DESC
LIMIT 10;
```

### 方法2：查看后端日志

邮件发送时会输出详细日志：
```
📧 正在发送邮件到 admin@example.com...
   SMTP服务器: smtp.gmail.com:587
   发件人: your-email@gmail.com
✅ 邮件发送成功到 admin@example.com
```

---

## 🎯 最佳实践

1. **使用应用专用密码**
   - 不要在配置文件中使用主密码
   - 定期轮换应用密码

2. **环境变量管理**
   - 使用`.env`文件，不要提交到Git
   - `.env`应该在`.gitignore`中

3. **邮件内容优化**
   - 邮件主题清晰明确
   - 包含告警级别和服务器信息
   - 提供必要的上下文

4. **发送频率控制**
   - 使用静默期防止邮件轰炸
   - warning级别：5分钟静默期
   - error级别：10分钟静默期

5. **监控邮件发送状态**
   - 定期检查通知记录
   - 关注失败的邮件发送
   - 设置邮件发送失败的告警（meta-alert）

---

## 🔒 安全建议

1. **不要将密码提交到代码仓库**
   ```bash
   # 确保.env在.gitignore中
   echo ".env" >> .gitignore
   ```

2. **使用专用邮箱**
   - 创建一个专门用于系统通知的邮箱
   - 不要使用个人主邮箱

3. **限制应用密码权限**
   - 如果可能，使用只读或仅发送权限的凭据

4. **定期审计**
   - 定期检查邮件发送日志
   - 监控异常的发送活动

---

## 📧 邮件模板示例

告警邮件的实际效果：

**主题**：`[ERROR] 内存使用率危险`

**内容**：
```
告警通知

告警标题: 内存使用率危险
告警级别: error
告警类型: memory
当前值: 92.5%
阈值: 90.0%
告警时间: 2025-10-17 12:34:56
详细信息: MEMORY使用率达到 92.5%，超过阈值 90.0%

此邮件由运维自动化平台自动发送，请勿回复。
```

---

## 🎉 完成！

配置完成后：
1. **重启后端服务**
2. **触发一个测试告警**
3. **检查邮箱是否收到邮件**

如果收到邮件，恭喜！邮件通知系统已正常工作！🎊

