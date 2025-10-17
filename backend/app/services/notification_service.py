from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.alert_rule import AlertNotification
from app.models.alert import Alert
from app.core.config import settings


class NotificationService:
    """通知服务"""
    
    @staticmethod
    def send_email(
        db: Session,
        alert: Alert,
        rule_id: Optional[int],
        recipient: str,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None
    ) -> AlertNotification:
        """
        发送邮件通知
        
        注意：需要配置 SMTP 服务器信息
        """
        # 从配置文件读取SMTP设置
        smtp_host = smtp_host or settings.SMTP_HOST
        smtp_port = smtp_port or settings.SMTP_PORT
        smtp_user = smtp_user or settings.SMTP_USER
        smtp_password = smtp_password or settings.SMTP_PASSWORD
        
        notification = AlertNotification(
            alert_id=alert.id,
            rule_id=rule_id,
            notification_type="email",
            recipient=recipient,
            status="pending"
        )
        db.add(notification)
        db.commit()
        
        try:
            # 检查SMTP是否已配置
            if not settings.SMTP_ENABLED:
                notification.status = "skipped"
                notification.error_message = "邮件通知未启用 (SMTP_ENABLED=False)"
                print(f"⚠️  邮件通知未启用，跳过发送到 {recipient}")
                db.commit()
                db.refresh(notification)
                return notification
            
            if not smtp_user or not smtp_password:
                notification.status = "skipped"
                notification.error_message = "SMTP账号未配置 (SMTP_USER或SMTP_PASSWORD为空)"
                print(f"⚠️  SMTP账号未配置，跳过发送邮件到 {recipient}")
                db.commit()
                db.refresh(notification)
                return notification
            # 创建邮件内容
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.level.upper()}] {alert.title}"
            msg['From'] = smtp_user
            msg['To'] = recipient
            
            # HTML内容
            html_content = f"""
            <html>
              <body>
                <h2 style="color: {'#f56c6c' if alert.level == 'critical' else '#e6a23c'};">
                    告警通知
                </h2>
                <table style="border-collapse: collapse; width: 100%;">
                  <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>告警标题</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{alert.title}</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>告警级别</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{alert.level}</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>告警类型</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{alert.alert_type}</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>当前值</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{alert.current_value}%</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>阈值</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{alert.threshold_value}%</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>告警时间</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{alert.triggered_at}</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>详细信息</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{alert.message}</td>
                  </tr>
                </table>
                <p style="margin-top: 20px; color: #999;">
                  此邮件由运维自动化平台自动发送，请勿回复。
                </p>
              </body>
            </html>
            """
            
            # 纯文本内容（备用）
            text_content = f"""
告警通知

告警标题: {alert.title}
告警级别: {alert.level}
告警类型: {alert.alert_type}
当前值: {alert.current_value}%
阈值: {alert.threshold_value}%
告警时间: {alert.triggered_at}
详细信息: {alert.message}

此邮件由运维自动化平台自动发送，请勿回复。
            """
            
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # 发送邮件
            print(f"📧 正在发送邮件到 {recipient}...")
            print(f"   SMTP服务器: {smtp_host}:{smtp_port}")
            print(f"   发件人: {smtp_user}")
            
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            # 更新状态为已发送
            notification.status = "sent"
            notification.sent_at = datetime.utcnow()
            print(f"✅ 邮件发送成功到 {recipient}")
            
        except smtplib.SMTPAuthenticationError as e:
            notification.status = "failed"
            notification.error_message = f"SMTP认证失败: {str(e)}"
            print(f"❌ 邮件发送失败 (认证错误): {str(e)}")
        except smtplib.SMTPException as e:
            notification.status = "failed"
            notification.error_message = f"SMTP错误: {str(e)}"
            print(f"❌ 邮件发送失败 (SMTP错误): {str(e)}")
        except Exception as e:
            notification.status = "failed"
            notification.error_message = str(e)
            print(f"❌ 邮件发送失败: {str(e)}")
        
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def send_webhook(
        db: Session,
        alert: Alert,
        rule_id: Optional[int],
        webhook_url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> AlertNotification:
        """发送Webhook通知"""
        notification = AlertNotification(
            alert_id=alert.id,
            rule_id=rule_id,
            notification_type="webhook",
            recipient=webhook_url,
            status="pending"
        )
        db.add(notification)
        db.commit()
        
        try:
            # 构建webhook payload
            payload = {
                "alert_id": alert.id,
                "server_id": alert.server_id,
                "title": alert.title,
                "message": alert.message,
                "alert_type": alert.alert_type,
                "level": alert.level,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "status": alert.status,
                "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 设置请求头
            request_headers = {
                "Content-Type": "application/json",
                "User-Agent": "DevOps-Platform/1.0"
            }
            if headers:
                request_headers.update(headers)
            
            # 发送POST请求
            response = requests.post(
                webhook_url,
                json=payload,
                headers=request_headers,
                timeout=10
            )
            
            if response.status_code in [200, 201, 202, 204]:
                notification.status = "sent"
                notification.sent_at = datetime.utcnow()
            else:
                notification.status = "failed"
                notification.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
                
        except requests.exceptions.Timeout:
            notification.status = "failed"
            notification.error_message = "请求超时"
        except requests.exceptions.RequestException as e:
            notification.status = "failed"
            notification.error_message = f"请求失败: {str(e)}"
        except Exception as e:
            notification.status = "failed"
            notification.error_message = str(e)
        
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def send_notification_by_rule(
        db: Session,
        alert: Alert,
        rule
    ) -> list:
        """根据规则配置发送通知"""
        notifications = []
        
        # 发送邮件通知
        if rule.enable_email and rule.email_recipients:
            for recipient in rule.email_recipients:
                notification = NotificationService.send_email(
                    db=db,
                    alert=alert,
                    rule_id=rule.id,
                    recipient=recipient
                )
                notifications.append(notification)
        
        # 发送Webhook通知
        if rule.enable_webhook and rule.webhook_url:
            notification = NotificationService.send_webhook(
                db=db,
                alert=alert,
                rule_id=rule.id,
                webhook_url=rule.webhook_url,
                headers=rule.webhook_headers
            )
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def get_notifications(
        db: Session,
        alert_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ):
        """获取通知记录"""
        query = db.query(AlertNotification)
        
        if alert_id:
            query = query.filter(AlertNotification.alert_id == alert_id)
        
        return query.order_by(AlertNotification.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def retry_failed_notification(db: Session, notification_id: int) -> Optional[AlertNotification]:
        """重试失败的通知"""
        notification = db.query(AlertNotification).filter(
            AlertNotification.id == notification_id
        ).first()
        
        if not notification or notification.status != "failed":
            return None
        
        # 获取关联的告警
        alert = db.query(Alert).filter(Alert.id == notification.alert_id).first()
        if not alert:
            return None
        
        # 根据类型重新发送
        if notification.notification_type == "email":
            return NotificationService.send_email(
                db=db,
                alert=alert,
                rule_id=notification.rule_id,
                recipient=notification.recipient
            )
        elif notification.notification_type == "webhook":
            return NotificationService.send_webhook(
                db=db,
                alert=alert,
                rule_id=notification.rule_id,
                webhook_url=notification.recipient
            )
        
        return None

