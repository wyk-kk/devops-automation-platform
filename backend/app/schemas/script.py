from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScriptBase(BaseModel):
    """脚本基础模型"""
    name: str
    description: Optional[str] = None
    content: str
    script_type: str = "shell"
    parameters: Optional[str] = None


class ScriptCreate(ScriptBase):
    """创建脚本"""
    pass


class Script(ScriptBase):
    """脚本响应模型"""
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ScriptExecutionCreate(BaseModel):
    """执行脚本"""
    script_id: int
    server_id: int


class ScriptExecution(BaseModel):
    """脚本执行记录"""
    id: int
    script_id: int
    server_id: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    executed_by: Optional[int] = None
    
    class Config:
        from_attributes = True

