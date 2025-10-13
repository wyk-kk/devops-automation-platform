from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AlertBase(BaseModel):
    """告警基础模型"""
    server_id: int
    alert_type: str
    level: str = "warning"
    title: str
    message: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None


class AlertCreate(AlertBase):
    """创建告警"""
    pass


class Alert(AlertBase):
    """告警响应模型"""
    id: int
    status: str = "open"
    is_notified: bool = False
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[int] = None
    
    class Config:
        from_attributes = True

