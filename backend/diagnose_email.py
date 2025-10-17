#!/usr/bin/env python3
"""
邮件配置诊断工具
快速检测SMTP配置问题
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def check_config():
    """检查配置"""
    print("=" * 60)
    print("📋 步骤1：检查配置文件")
    print("=" * 60)
    
    # 检查.env文件
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print("✅ .env 文件存在")
        with open(env_path, 'r') as f:
            content = f.read()
            if 'SMTP_ENABLED' in content:
                print("✅ 包含 SMTP_ENABLED 配置")
            else:
                print("❌ 缺少 SMTP_ENABLED 配置")
            
            if 'SMTP_USER' in content:
                print("✅ 包含 SMTP_USER 配置")
            else:
                print("❌ 缺少 SMTP_USER 配置")
            
            if 'SMTP_PASSWORD' in content:
                print("✅ 包含 SMTP_PASSWORD 配置")
            else:
                print("❌ 缺少 SMTP_PASSWORD 配置")
    else:
        print("❌ .env 文件不存在")
        print("   请运行: cp env.example .env")
        return False
    
    print()
    return True

def check_settings():
    """检查settings配置"""
    print("=" * 60)
    print("📋 步骤2：检查Settings配置")
    print("=" * 60)
    
    try:
        from app.core.config import settings
        
        print(f"SMTP_ENABLED: {settings.SMTP_ENABLED}")
        print(f"SMTP_HOST: {settings.SMTP_HOST}")
        print(f"SMTP_PORT: {settings.SMTP_PORT}")
        print(f"SMTP_USER: {settings.SMTP_USER if settings.SMTP_USER else '❌ 未配置'}")
        print(f"SMTP_PASSWORD: {'✅ 已配置 (****)' if settings.SMTP_PASSWORD else '❌ 未配置'}")
        print(f"SMTP_FROM_NAME: {settings.SMTP_FROM_NAME}")
        
        if not settings.SMTP_ENABLED:
            print("\n⚠️  警告: SMTP_ENABLED=False，邮件通知未启用！")
            print("   解决: 在.env文件中设置 SMTP_ENABLED=True")
            return False
        
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print("\n❌ 错误: SMTP账号或密码未配置！")
            print("   解决: 在.env文件中配置 SMTP_USER 和 SMTP_PASSWORD")
            return False
        
        print("\n✅ Settings配置正确")
        return True
        
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        return False

def test_smtp_connection():
    """测试SMTP连接"""
    print("\n" + "=" * 60)
    print("📋 步骤3：测试SMTP连接")
    print("=" * 60)
    
    try:
        from app.core.config import settings
        import smtplib
        
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print("❌ 跳过测试：SMTP账号未配置")
            return False
        
        print(f"正在连接到 {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        print("✅ 连接成功")
        
        print("启用TLS加密...")
        server.starttls()
        print("✅ TLS加密成功")
        
        print(f"正在登录 {settings.SMTP_USER}...")
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        print("✅ 登录成功")
        
        server.quit()
        print("\n✅ SMTP连接测试通过！")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ 认证失败: {e}")
        print("\n可能的原因：")
        print("1. Gmail: 没有使用应用专用密码")
        print("   - 访问: https://myaccount.google.com/apppasswords")
        print("   - 生成应用专用密码（16位）")
        print("2. QQ邮箱: 没有使用授权码")
        print("   - 在QQ邮箱设置中开启SMTP服务")
        print("   - 生成授权码（不是登录密码）")
        print("3. 邮箱地址或密码错误")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n可能的原因：")
        print("1. SMTP服务器地址错误")
        print("2. 网络问题或防火墙阻止")
        print("3. SMTP端口错误")
        return False
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

def send_test_email():
    """发送测试邮件"""
    print("\n" + "=" * 60)
    print("📋 步骤4：发送测试邮件")
    print("=" * 60)
    
    try:
        from app.core.config import settings
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print("❌ 跳过测试：SMTP账号未配置")
            return False
        
        # 询问收件人
        print(f"\n发件人: {settings.SMTP_USER}")
        recipient = input("请输入收件人邮箱 (直接回车发给自己): ").strip()
        if not recipient:
            recipient = settings.SMTP_USER
        
        print(f"\n正在发送测试邮件到 {recipient}...")
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "测试邮件 - 运维自动化平台"
        msg['From'] = settings.SMTP_USER
        msg['To'] = recipient
        
        text_content = """
这是一封测试邮件。

如果您收到这封邮件，说明SMTP配置正确！

发送时间: {datetime}
发件人: {sender}
SMTP服务器: {host}:{port}

此邮件由运维自动化平台自动发送。
        """.format(
            datetime=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            sender=settings.SMTP_USER,
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT
        )
        
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #67C23A;">✅ 测试邮件</h2>
            <p>如果您收到这封邮件，说明<strong>SMTP配置正确</strong>！</p>
            <table style="border-collapse: collapse; width: 100%; margin-top: 20px;">
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd; background: #f5f5f5;"><strong>发送时间</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd; background: #f5f5f5;"><strong>发件人</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{settings.SMTP_USER}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd; background: #f5f5f5;"><strong>SMTP服务器</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{settings.SMTP_HOST}:{settings.SMTP_PORT}</td>
              </tr>
            </table>
            <p style="margin-top: 20px; color: #999; font-size: 12px;">
              此邮件由运维自动化平台自动发送。
            </p>
          </body>
        </html>
        """
        
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        # 发送
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"\n✅ 测试邮件发送成功！")
        print(f"   收件人: {recipient}")
        print(f"   请检查邮箱（包括垃圾邮件文件夹）")
        return True
        
    except Exception as e:
        print(f"\n❌ 发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_notifications():
    """检查数据库中的通知记录"""
    print("\n" + "=" * 60)
    print("📋 步骤5：检查数据库通知记录")
    print("=" * 60)
    
    try:
        from app.core.database import SessionLocal
        from app.models.alert_rule import AlertNotification
        
        db = SessionLocal()
        
        # 查询最近10条邮件通知记录
        notifications = db.query(AlertNotification).filter(
            AlertNotification.notification_type == 'email'
        ).order_by(AlertNotification.created_at.desc()).limit(10).all()
        
        if not notifications:
            print("❌ 数据库中没有邮件通知记录")
            print("   说明告警可能没有触发，或者告警规则没有启用邮件通知")
        else:
            print(f"找到 {len(notifications)} 条邮件通知记录：\n")
            for n in notifications:
                status_icon = {
                    'sent': '✅',
                    'failed': '❌',
                    'pending': '⏳',
                    'skipped': '⚠️'
                }.get(n.status, '❓')
                
                print(f"{status_icon} ID:{n.id} | 状态:{n.status} | 收件人:{n.recipient}")
                if n.status == 'failed' or n.status == 'skipped':
                    print(f"   错误信息: {n.error_message}")
                if n.sent_at:
                    print(f"   发送时间: {n.sent_at}")
                print()
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🔍 邮件配置诊断工具")
    print("=" * 60)
    print()
    
    results = []
    
    # 1. 检查配置文件
    results.append(("配置文件", check_config()))
    
    # 2. 检查Settings
    results.append(("Settings配置", check_settings()))
    
    # 3. 测试SMTP连接
    results.append(("SMTP连接", test_smtp_connection()))
    
    # 4. 发送测试邮件
    if results[-1][1]:  # 如果SMTP连接成功
        send_test = input("\n是否发送测试邮件？(y/n): ").strip().lower()
        if send_test == 'y':
            results.append(("测试邮件", send_test_email()))
    
    # 5. 检查数据库记录
    results.append(("数据库记录", check_database_notifications()))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 诊断结果总结")
    print("=" * 60)
    for name, success in results:
        icon = "✅" if success else "❌"
        print(f"{icon} {name}")
    
    print("\n" + "=" * 60)
    
    # 给出建议
    if not all(r[1] for r in results[:3]):  # 前3项必须通过
        print("\n❌ 配置存在问题，请按照上述提示修复后重试")
        print("\n快速修复步骤：")
        print("1. cd /Users/DZ0400191/project_2/backend")
        print("2. cp env.example .env")
        print("3. 编辑.env文件，配置SMTP信息")
        print("4. 重启后端服务")
        print("5. 重新运行此诊断工具")
    else:
        print("\n✅ 配置正确！如果告警时仍未收到邮件，请检查：")
        print("1. 告警规则是否启用了邮件通知")
        print("2. 告警规则的收件人邮箱是否正确")
        print("3. 告警是否真的被触发了（查看告警列表）")
        print("4. 邮件是否进入了垃圾箱")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  诊断已取消")
    except Exception as e:
        print(f"\n❌ 诊断工具出错: {e}")
        import traceback
        traceback.print_exc()

