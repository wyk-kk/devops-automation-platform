from sqlalchemy.orm import Session
from typing import List, Optional
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
    def check_server_alerts(db: Session, server_id: int, 
                           cpu_percent: float, memory_percent: float, 
                           disk_percent: float) -> List[Alert]:
        """检查服务器告警"""
        alerts = []
        
        # CPU告警阈值
        cpu_threshold = 80.0
        if cpu_percent > cpu_threshold:
            alert = AlertCreate(
                server_id=server_id,
                alert_type="cpu",
                level="warning" if cpu_percent < 90 else "critical",
                title=f"CPU使用率过高",
                message=f"CPU使用率达到 {cpu_percent}%",
                current_value=cpu_percent,
                threshold_value=cpu_threshold
            )
            alerts.append(AlertService.create_alert(db, alert))
        
        # 内存告警阈值
        memory_threshold = 80.0
        if memory_percent > memory_threshold:
            alert = AlertCreate(
                server_id=server_id,
                alert_type="memory",
                level="warning" if memory_percent < 90 else "critical",
                title=f"内存使用率过高",
                message=f"内存使用率达到 {memory_percent}%",
                current_value=memory_percent,
                threshold_value=memory_threshold
            )
            alerts.append(AlertService.create_alert(db, alert))
        
        # 磁盘告警阈值
        disk_threshold = 80.0
        if disk_percent > disk_threshold:
            alert = AlertCreate(
                server_id=server_id,
                alert_type="disk",
                level="warning" if disk_percent < 90 else "critical",
                title=f"磁盘使用率过高",
                message=f"磁盘使用率达到 {disk_percent}%",
                current_value=disk_percent,
                threshold_value=disk_threshold
            )
            alerts.append(AlertService.create_alert(db, alert))
        
        return alerts

