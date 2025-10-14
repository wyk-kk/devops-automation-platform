from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.models.alert_rule import AlertRule, AlertSilence, AlertNotification
from app.models.alert import Alert
from app.schemas.alert_rule import AlertRuleCreate, AlertRuleUpdate, AlertStatistics, AlertTrend


class AlertRuleService:
    """告警规则服务"""
    
    @staticmethod
    def get_alert_rules(db: Session, skip: int = 0, limit: int = 100, 
                       is_active: Optional[bool] = None,
                       server_id: Optional[int] = None) -> List[AlertRule]:
        """获取告警规则列表"""
        query = db.query(AlertRule)
        
        if is_active is not None:
            query = query.filter(AlertRule.is_active == is_active)
        
        if server_id is not None:
            # 获取特定服务器的规则和全局规则
            query = query.filter(
                or_(AlertRule.server_id == server_id, AlertRule.server_id.is_(None))
            )
        
        return query.order_by(AlertRule.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_alert_rule(db: Session, rule_id: int) -> Optional[AlertRule]:
        """获取单个告警规则"""
        return db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    
    @staticmethod
    def create_alert_rule(db: Session, rule: AlertRuleCreate, user_id: int) -> AlertRule:
        """创建告警规则"""
        db_rule = AlertRule(**rule.model_dump(), created_by=user_id)
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        return db_rule
    
    @staticmethod
    def update_alert_rule(db: Session, rule_id: int, rule: AlertRuleUpdate) -> Optional[AlertRule]:
        """更新告警规则"""
        db_rule = AlertRuleService.get_alert_rule(db, rule_id)
        if not db_rule:
            return None
        
        update_data = rule.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rule, field, value)
        
        db_rule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_rule)
        return db_rule
    
    @staticmethod
    def delete_alert_rule(db: Session, rule_id: int) -> bool:
        """删除告警规则"""
        db_rule = AlertRuleService.get_alert_rule(db, rule_id)
        if not db_rule:
            return False
        
        db.delete(db_rule)
        db.commit()
        return True
    
    @staticmethod
    def check_value_against_rule(value: float, threshold: float, operator: str) -> bool:
        """检查值是否满足规则条件"""
        operators = {
            'gt': lambda v, t: v > t,
            'gte': lambda v, t: v >= t,
            'lt': lambda v, t: v < t,
            'lte': lambda v, t: v <= t,
            'eq': lambda v, t: abs(v - t) < 0.001,
        }
        return operators.get(operator, operators['gt'])(value, threshold)
    
    @staticmethod
    def is_silenced(db: Session, rule_id: int, server_id: int) -> bool:
        """检查规则是否在静默期"""
        silence = db.query(AlertSilence).filter(
            and_(
                AlertSilence.rule_id == rule_id,
                AlertSilence.server_id == server_id,
                AlertSilence.silence_until > datetime.utcnow()
            )
        ).first()
        return silence is not None
    
    @staticmethod
    def set_silence(db: Session, rule_id: int, server_id: int, duration: int):
        """设置静默期"""
        silence_until = datetime.utcnow() + timedelta(seconds=duration)
        
        # 检查是否已存在静默记录
        silence = db.query(AlertSilence).filter(
            and_(
                AlertSilence.rule_id == rule_id,
                AlertSilence.server_id == server_id
            )
        ).first()
        
        if silence:
            silence.last_alert_time = datetime.utcnow()
            silence.silence_until = silence_until
        else:
            silence = AlertSilence(
                rule_id=rule_id,
                server_id=server_id,
                last_alert_time=datetime.utcnow(),
                silence_until=silence_until
            )
            db.add(silence)
        
        db.commit()
    
    @staticmethod
    def get_applicable_rules(db: Session, server_id: int, metric_type: str) -> List[AlertRule]:
        """获取适用于指定服务器和指标的规则"""
        rules = db.query(AlertRule).filter(
            and_(
                AlertRule.is_active == True,
                AlertRule.metric_type == metric_type,
                or_(
                    AlertRule.server_id == server_id,
                    AlertRule.server_id.is_(None)  # 全局规则
                )
            )
        ).all()
        
        return rules
    
    @staticmethod
    def get_alert_statistics(db: Session, days: int = 7) -> AlertStatistics:
        """获取告警统计信息"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 基础统计
        total_alerts = db.query(func.count(Alert.id)).filter(
            Alert.triggered_at >= start_date
        ).scalar()
        
        open_alerts = db.query(func.count(Alert.id)).filter(
            and_(Alert.status == "open", Alert.triggered_at >= start_date)
        ).scalar()
        
        acknowledged_alerts = db.query(func.count(Alert.id)).filter(
            and_(Alert.status == "acknowledged", Alert.triggered_at >= start_date)
        ).scalar()
        
        resolved_alerts = db.query(func.count(Alert.id)).filter(
            and_(Alert.status == "resolved", Alert.triggered_at >= start_date)
        ).scalar()
        
        # 按级别统计
        critical_alerts = db.query(func.count(Alert.id)).filter(
            and_(Alert.level == "critical", Alert.triggered_at >= start_date)
        ).scalar()
        
        error_alerts = db.query(func.count(Alert.id)).filter(
            and_(Alert.level == "error", Alert.triggered_at >= start_date)
        ).scalar()
        
        warning_alerts = db.query(func.count(Alert.id)).filter(
            and_(Alert.level == "warning", Alert.triggered_at >= start_date)
        ).scalar()
        
        info_alerts = db.query(func.count(Alert.id)).filter(
            and_(Alert.level == "info", Alert.triggered_at >= start_date)
        ).scalar()
        
        # 按类型统计
        alerts_by_type = {}
        type_results = db.query(
            Alert.alert_type, func.count(Alert.id)
        ).filter(
            Alert.triggered_at >= start_date
        ).group_by(Alert.alert_type).all()
        
        for alert_type, count in type_results:
            alerts_by_type[alert_type] = count
        
        # 按服务器统计
        alerts_by_server = {}
        server_results = db.query(
            Alert.server_id, func.count(Alert.id)
        ).filter(
            Alert.triggered_at >= start_date
        ).group_by(Alert.server_id).all()
        
        for server_id, count in server_results:
            alerts_by_server[str(server_id)] = count
        
        return AlertStatistics(
            total_alerts=total_alerts or 0,
            open_alerts=open_alerts or 0,
            acknowledged_alerts=acknowledged_alerts or 0,
            resolved_alerts=resolved_alerts or 0,
            critical_alerts=critical_alerts or 0,
            error_alerts=error_alerts or 0,
            warning_alerts=warning_alerts or 0,
            info_alerts=info_alerts or 0,
            alerts_by_type=alerts_by_type,
            alerts_by_server=alerts_by_server
        )
    
    @staticmethod
    def get_alert_trends(db: Session, days: int = 7) -> List[AlertTrend]:
        """获取告警趋势"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 按日期分组统计
        trends = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            
            # 当天总告警数
            count = db.query(func.count(Alert.id)).filter(
                and_(
                    Alert.triggered_at >= date,
                    Alert.triggered_at < next_date
                )
            ).scalar() or 0
            
            # 按级别统计
            critical = db.query(func.count(Alert.id)).filter(
                and_(
                    Alert.triggered_at >= date,
                    Alert.triggered_at < next_date,
                    Alert.level == "critical"
                )
            ).scalar() or 0
            
            error = db.query(func.count(Alert.id)).filter(
                and_(
                    Alert.triggered_at >= date,
                    Alert.triggered_at < next_date,
                    Alert.level == "error"
                )
            ).scalar() or 0
            
            warning = db.query(func.count(Alert.id)).filter(
                and_(
                    Alert.triggered_at >= date,
                    Alert.triggered_at < next_date,
                    Alert.level == "warning"
                )
            ).scalar() or 0
            
            info = db.query(func.count(Alert.id)).filter(
                and_(
                    Alert.triggered_at >= date,
                    Alert.triggered_at < next_date,
                    Alert.level == "info"
                )
            ).scalar() or 0
            
            trends.append(AlertTrend(
                date=date.strftime('%Y-%m-%d'),
                count=count,
                critical=critical,
                error=error,
                warning=warning,
                info=info
            ))
        
        return trends

