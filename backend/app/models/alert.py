from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from datetime import datetime
from app.core.database import Base


class Alert(Base):
    """告警模型"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    
    # 告警类型
    alert_type = Column(String(50), nullable=False)  # cpu, memory, disk, network
    
    # 告警级别
    level = Column(String(20), default="warning")  # info, warning, error, critical
    
    # 告警内容
    title = Column(String(200), nullable=False)
    message = Column(Text)
    
    # 当前值和阈值
    current_value = Column(Float)
    threshold_value = Column(Float)
    
    # 状态
    status = Column(String(20), default="open")  # open, acknowledged, resolved
    is_notified = Column(Boolean, default=False)
    
    # 时间信息
    triggered_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    
    def __repr__(self):
        return f"<Alert {self.alert_type} - {self.level}>"

