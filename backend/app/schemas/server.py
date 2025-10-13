from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ServerBase(BaseModel):
    """服务器基础模型"""
    name: str
    host: str
    port: int = 22
    username: str
    password: Optional[str] = None
    ssh_key: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class ServerCreate(ServerBase):
    """创建服务器"""
    pass


class ServerUpdate(BaseModel):
    """更新服务器"""
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    ssh_key: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Server(ServerBase):
    """服务器响应模型"""
    id: int
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    memory_total: Optional[int] = None
    disk_total: Optional[int] = None
    status: str = "unknown"
    last_check_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ServerStatus(BaseModel):
    """服务器状态"""
    server_id: int
    status: str
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    memory_used: Optional[int] = None
    memory_total: Optional[int] = None
    disk_percent: Optional[float] = None
    disk_used: Optional[int] = None
    disk_total: Optional[int] = None
    uptime: Optional[str] = None
    check_time: datetime

