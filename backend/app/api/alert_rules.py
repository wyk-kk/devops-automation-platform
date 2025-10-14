from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.alert_rule import (
    AlertRule, AlertRuleCreate, AlertRuleUpdate,
    AlertNotification, AlertStatistics, AlertTrend
)
from app.schemas.user import User
from app.services.alert_rule_service import AlertRuleService
from app.services.notification_service import NotificationService
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/alert-rules", tags=["告警规则"])


@router.get("", response_model=List[AlertRule])
def get_alert_rules(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    server_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取告警规则列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **is_active**: 筛选激活状态
    - **server_id**: 筛选服务器（包括全局规则）
    """
    return AlertRuleService.get_alert_rules(
        db, skip=skip, limit=limit, is_active=is_active, server_id=server_id
    )


@router.get("/{rule_id}", response_model=AlertRule)
def get_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取告警规则详情"""
    rule = AlertRuleService.get_alert_rule(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return rule


@router.post("", response_model=AlertRule)
def create_alert_rule(
    rule: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建告警规则
    
    支持的指标类型：
    - cpu: CPU使用率
    - memory: 内存使用率
    - disk: 磁盘使用率
    - network: 网络流量
    
    支持的操作符：
    - gt: 大于
    - gte: 大于等于
    - lt: 小于
    - lte: 小于等于
    - eq: 等于
    
    告警级别：
    - info: 信息
    - warning: 警告
    - error: 错误
    - critical: 严重
    """
    return AlertRuleService.create_alert_rule(db, rule, current_user.id)


@router.put("/{rule_id}", response_model=AlertRule)
def update_alert_rule(
    rule_id: int,
    rule: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新告警规则"""
    updated_rule = AlertRuleService.update_alert_rule(db, rule_id, rule)
    if not updated_rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return updated_rule


@router.delete("/{rule_id}")
def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除告警规则"""
    success = AlertRuleService.delete_alert_rule(db, rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return {"message": "Alert rule deleted successfully"}


@router.post("/{rule_id}/toggle")
def toggle_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """启用/禁用告警规则"""
    rule = AlertRuleService.get_alert_rule(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    update = AlertRuleUpdate(is_active=not rule.is_active)
    updated_rule = AlertRuleService.update_alert_rule(db, rule_id, update)
    
    return {
        "message": f"Alert rule {'enabled' if updated_rule.is_active else 'disabled'}",
        "is_active": updated_rule.is_active
    }


@router.get("/statistics/overview", response_model=AlertStatistics)
def get_alert_statistics(
    days: int = Query(7, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取告警统计信息
    
    - **days**: 统计最近多少天的数据
    """
    return AlertRuleService.get_alert_statistics(db, days)


@router.get("/statistics/trends", response_model=List[AlertTrend])
def get_alert_trends(
    days: int = Query(7, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取告警趋势数据
    
    - **days**: 统计最近多少天的数据
    """
    return AlertRuleService.get_alert_trends(db, days)


# 告警通知相关接口
@router.get("/notifications/list", response_model=List[AlertNotification])
def get_notifications(
    alert_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取告警通知记录
    
    - **alert_id**: 筛选特定告警的通知
    """
    return NotificationService.get_notifications(db, alert_id, skip, limit)


@router.post("/notifications/{notification_id}/retry", response_model=AlertNotification)
def retry_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """重试失败的通知"""
    notification = NotificationService.retry_failed_notification(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=404, 
            detail="Notification not found or cannot be retried"
        )
    return notification


@router.post("/test-webhook")
def test_webhook(
    webhook_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    测试Webhook配置
    
    发送一个测试消息到指定的Webhook URL
    """
    import requests
    from datetime import datetime
    
    try:
        test_payload = {
            "test": True,
            "message": "这是一条来自运维自动化平台的测试消息",
            "timestamp": datetime.utcnow().isoformat(),
            "user": current_user.username
        }
        
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        return {
            "success": response.status_code in [200, 201, 202, 204],
            "status_code": response.status_code,
            "response": response.text[:500]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

