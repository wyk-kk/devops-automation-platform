from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from datetime import datetime
from app.core.database import Base


class Task(Base):
    """定时任务模型"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    
    # 任务类型和内容
    task_type = Column(String(20), default="script")  # script, command
    script_id = Column(Integer, ForeignKey("scripts.id"))
    command = Column(Text)
    
    # 目标服务器
    server_id = Column(Integer, ForeignKey("servers.id"))
    
    # 调度配置
    cron_expression = Column(String(100))  # Cron表达式
    is_enabled = Column(Boolean, default=True)
    
    # 执行信息
    last_run_time = Column(DateTime)
    next_run_time = Column(DateTime)
    last_status = Column(String(20))
    
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Task {self.name}>"


class TaskExecution(Base):
    """任务执行记录"""
    __tablename__ = "task_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    
    status = Column(String(20), default="pending")  # pending, running, success, failed
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    
    output = Column(Text)
    error = Column(Text)
    
    def __repr__(self):
        return f"<TaskExecution {self.id} - {self.status}>"

