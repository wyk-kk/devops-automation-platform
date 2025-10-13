from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OperationLogBase(BaseModel):
    """操作日志基础模型"""
    operation: str
    module: Optional[str] = None
    description: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    status: str = "success"
    error_message: Optional[str] = None


class OperationLog(OperationLogBase):
    """操作日志响应模型"""
    id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

