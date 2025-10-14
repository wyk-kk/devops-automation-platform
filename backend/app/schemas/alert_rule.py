from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime


class AlertRuleBase(BaseModel):
    """告警规则基础Schema"""
    name: str = Field(..., description="规则名称")
    description: Optional[str] = Field(None, description="规则描述")
    server_id: Optional[int] = Field(None, description="服务器ID，NULL表示全局规则")
    metric_type: str = Field(..., description="监控指标: cpu, memory, disk, network")
    threshold_value: float = Field(..., description="阈值")
    threshold_operator: str = Field("gt", description="比较操作符: gt, lt, gte, lte, eq")
    duration: int = Field(60, description="持续时间（秒）")
    alert_level: str = Field("warning", description="告警级别: info, warning, error, critical")
    
    enable_email: bool = Field(False, description="启用邮件通知")
    email_recipients: Optional[List[str]] = Field(None, description="邮件接收者列表")
    
    enable_webhook: bool = Field(False, description="启用Webhook通知")
    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    webhook_headers: Optional[Dict[str, str]] = Field(None, description="Webhook请求头")
    
    silence_duration: int = Field(300, description="静默期（秒）")
    is_active: bool = Field(True, description="规则是否启用")
    
    @field_validator('metric_type')
    @classmethod
    def validate_metric_type(cls, v):
        allowed = ['cpu', 'memory', 'disk', 'network']
        if v not in allowed:
            raise ValueError(f'metric_type must be one of {allowed}')
        return v
    
    @field_validator('threshold_operator')
    @classmethod
    def validate_operator(cls, v):
        allowed = ['gt', 'lt', 'gte', 'lte', 'eq']
        if v not in allowed:
            raise ValueError(f'threshold_operator must be one of {allowed}')
        return v
    
    @field_validator('alert_level')
    @classmethod
    def validate_alert_level(cls, v):
        allowed = ['info', 'warning', 'error', 'critical']
        if v not in allowed:
            raise ValueError(f'alert_level must be one of {allowed}')
        return v


class AlertRuleCreate(AlertRuleBase):
    """创建告警规则"""
    pass


class AlertRuleUpdate(BaseModel):
    """更新告警规则"""
    name: Optional[str] = None
    description: Optional[str] = None
    server_id: Optional[int] = None
    metric_type: Optional[str] = None
    threshold_value: Optional[float] = None
    threshold_operator: Optional[str] = None
    duration: Optional[int] = None
    alert_level: Optional[str] = None
    enable_email: Optional[bool] = None
    email_recipients: Optional[List[str]] = None
    enable_webhook: Optional[bool] = None
    webhook_url: Optional[str] = None
    webhook_headers: Optional[Dict[str, str]] = None
    silence_duration: Optional[int] = None
    is_active: Optional[bool] = None


class AlertRule(AlertRuleBase):
    """告警规则响应"""
    id: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class AlertNotificationBase(BaseModel):
    """告警通知基础Schema"""
    notification_type: str = Field(..., description="通知类型: email, webhook")
    recipient: str = Field(..., description="接收者")


class AlertNotificationCreate(AlertNotificationBase):
    """创建告警通知"""
    alert_id: int
    rule_id: Optional[int] = None


class AlertNotification(AlertNotificationBase):
    """告警通知响应"""
    id: int
    alert_id: int
    rule_id: Optional[int]
    status: str
    error_message: Optional[str]
    sent_at: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class AlertStatistics(BaseModel):
    """告警统计"""
    total_alerts: int = Field(..., description="总告警数")
    open_alerts: int = Field(..., description="未处理告警数")
    acknowledged_alerts: int = Field(..., description="已确认告警数")
    resolved_alerts: int = Field(..., description="已解决告警数")
    
    critical_alerts: int = Field(..., description="严重告警数")
    error_alerts: int = Field(..., description="错误告警数")
    warning_alerts: int = Field(..., description="警告告警数")
    info_alerts: int = Field(..., description="信息告警数")
    
    alerts_by_type: Dict[str, int] = Field(..., description="按类型分组的告警数")
    alerts_by_server: Dict[str, int] = Field(..., description="按服务器分组的告警数")


class AlertTrend(BaseModel):
    """告警趋势"""
    date: str = Field(..., description="日期")
    count: int = Field(..., description="告警数量")
    critical: int = Field(0, description="严重告警数")
    error: int = Field(0, description="错误告警数")
    warning: int = Field(0, description="警告告警数")
    info: int = Field(0, description="信息告警数")

