from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from app.models.alert import Alert
from app.schemas.alert import AlertCreate


class AlertService:
    """告警服务"""
    
    @staticmethod
    def get_alerts(db: Session, skip: int = 0, limit: int = 100, 
                   status: Optional[str] = None) -> List[Alert]:
        """获取告警列表"""
        query = db.query(Alert)
        
        if status:
            query = query.filter(Alert.status == status)
        
        return query.order_by(Alert.triggered_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
        """获取单个告警"""
        return db.query(Alert).filter(Alert.id == alert_id).first()
    
    @staticmethod
    def create_alert(db: Session, alert: AlertCreate) -> Alert:
        """创建告警"""
        db_alert = Alert(**alert.model_dump())
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert
    
    @staticmethod
    def acknowledge_alert(db: Session, alert_id: int, user_id: int) -> Optional[Alert]:
        """确认告警"""
        alert = AlertService.get_alert(db, alert_id)
        if not alert:
            return None
        
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = user_id
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def resolve_alert(db: Session, alert_id: int) -> Optional[Alert]:
        """解决告警"""
        alert = AlertService.get_alert(db, alert_id)
        if not alert:
            return None
        
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def check_server_alerts_with_rules(
        db: Session, 
        server_id: int, 
        metrics: Dict[str, float]
    ) -> List[Alert]:
        """
        使用动态规则检查服务器告警
        
        Args:
            db: 数据库会话
            server_id: 服务器ID
            metrics: 指标数据字典 {"cpu": 85.5, "memory": 70.2, "disk": 90.0}
        
        Returns:
            触发的告警列表
        """
        from app.services.alert_rule_service import AlertRuleService
        from app.services.notification_service import NotificationService
        
        alerts = []
        
        # 遍历所有指标
        for metric_type, current_value in metrics.items():
            # 获取适用的规则
            rules = AlertRuleService.get_applicable_rules(db, server_id, metric_type)
            
            for rule in rules:
                # 检查是否在静默期
                if AlertRuleService.is_silenced(db, rule.id, server_id):
                    continue
                
                # 检查值是否满足规则条件
                if AlertRuleService.check_value_against_rule(
                    current_value, 
                    rule.threshold_value, 
                    rule.threshold_operator
                ):
                    # 创建告警
                    alert = AlertCreate(
                        server_id=server_id,
                        alert_type=metric_type,
                        level=rule.alert_level,
                        title=f"{rule.name}",
                        message=f"{metric_type.upper()}使用率达到 {current_value}%，超过阈值 {rule.threshold_value}%",
                        current_value=current_value,
                        threshold_value=rule.threshold_value
                    )
                    
                    db_alert = AlertService.create_alert(db, alert)
                    alerts.append(db_alert)
                    
                    # 发送通知
                    NotificationService.send_notification_by_rule(db, db_alert, rule)
                    
                    # 设置静默期
                    AlertRuleService.set_silence(db, rule.id, server_id, rule.silence_duration)
        
        return alerts
    
    @staticmethod
    def check_server_alerts(db: Session, server_id: int, 
                           cpu_percent: float, memory_percent: float, 
                           disk_percent: float) -> List[Alert]:
        """
        检查服务器告警（兼容旧接口）
        使用动态规则系统
        """
        metrics = {
            "cpu": cpu_percent,
            "memory": memory_percent,
            "disk": disk_percent
        }
        
        return AlertService.check_server_alerts_with_rules(db, server_id, metrics)

