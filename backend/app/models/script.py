from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from app.core.database import Base


class Script(Base):
    """脚本模型"""
    __tablename__ = "scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    content = Column(Text, nullable=False)
    script_type = Column(String(20), default="shell")  # shell, python, etc.
    parameters = Column(Text)  # JSON格式的参数定义
    
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Script {self.name}>"


class ScriptExecution(Base):
    """脚本执行记录"""
    __tablename__ = "script_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=False)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    
    status = Column(String(20), default="pending")  # pending, running, success, failed
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    
    output = Column(Text)  # 执行输出
    error = Column(Text)  # 错误信息
    exit_code = Column(Integer)
    
    executed_by = Column(Integer, ForeignKey("users.id"))
    
    def __repr__(self):
        return f"<ScriptExecution {self.id} - {self.status}>"

