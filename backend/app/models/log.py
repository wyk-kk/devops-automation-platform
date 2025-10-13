from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from app.core.database import Base


class OperationLog(Base):
    """操作日志模型"""
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 操作信息
    operation = Column(String(100), nullable=False)  # 操作类型
    module = Column(String(50))  # 模块名称
    description = Column(Text)
    
    # 操作对象
    target_type = Column(String(50))  # server, script, task等
    target_id = Column(Integer)
    
    # 操作结果
    status = Column(String(20), default="success")  # success, failed
    error_message = Column(Text)
    
    # 请求信息
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    
    # 操作用户
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # 时间
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<OperationLog {self.operation}>"

