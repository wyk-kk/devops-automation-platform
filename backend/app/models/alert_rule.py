from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, DateTime
from datetime import datetime
from app.core.database import Base


class AlertRule(Base):
    """告警规则模型"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 规则基本信息
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    
    # 关联服务器（NULL表示全局规则）
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True)
    
    # 监控指标
    metric_type = Column(String(50), nullable=False)  # cpu, memory, disk, network
    
    # 阈值配置
    threshold_value = Column(Float, nullable=False)
    threshold_operator = Column(String(10), default="gt")  # gt, lt, gte, lte, eq
    
    # 持续时间（秒），连续超过阈值多久才触发
    duration = Column(Integer, default=60)
    
    # 告警级别
    alert_level = Column(String(20), default="warning")  # info, warning, error, critical
    
    # 通知配置
    enable_email = Column(Boolean, default=False)
    email_recipients = Column(JSON)  # ["email1@example.com", "email2@example.com"]
    
    enable_webhook = Column(Boolean, default=False)
    webhook_url = Column(String(500))
    webhook_headers = Column(JSON)  # {"Authorization": "Bearer token"}
    
    # 静默配置
    silence_duration = Column(Integer, default=300)  # 静默期（秒），避免重复告警
    
    # 规则状态
    is_active = Column(Boolean, default=True)
    
    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AlertRule {self.name} - {self.metric_type}>"


class AlertNotification(Base):
    """告警通知记录"""
    __tablename__ = "alert_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联告警
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    
    # 关联规则
    rule_id = Column(Integer, ForeignKey("alert_rules.id"))
    
    # 通知类型
    notification_type = Column(String(20), nullable=False)  # email, webhook
    
    # 通知目标
    recipient = Column(String(500))  # 邮箱地址或webhook URL
    
    # 通知状态
    status = Column(String(20), default="pending")  # pending, sent, failed
    
    # 错误信息
    error_message = Column(String(1000))
    
    # 发送时间
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AlertNotification {self.notification_type} - {self.status}>"


class AlertSilence(Base):
    """告警静默记录"""
    __tablename__ = "alert_silences"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联规则和服务器
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    
    # 最后告警时间
    last_alert_time = Column(DateTime, default=datetime.utcnow)
    
    # 静默结束时间
    silence_until = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<AlertSilence rule={self.rule_id} server={self.server_id}>"

