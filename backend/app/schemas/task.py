from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    """任务基础模型"""
    name: str
    description: Optional[str] = None
    task_type: str = "script"
    script_id: Optional[int] = None
    command: Optional[str] = None
    server_id: int
    cron_expression: str
    is_enabled: bool = True


class TaskCreate(TaskBase):
    """创建任务"""
    pass


class TaskUpdate(BaseModel):
    """更新任务"""
    name: Optional[str] = None
    description: Optional[str] = None
    cron_expression: Optional[str] = None
    is_enabled: Optional[bool] = None


class Task(TaskBase):
    """任务响应模型"""
    id: int
    last_run_time: Optional[datetime] = None
    next_run_time: Optional[datetime] = None
    last_status: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskExecution(BaseModel):
    """任务执行记录"""
    id: int
    task_id: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    output: Optional[str] = None
    error: Optional[str] = None
    
    class Config:
        from_attributes = True

