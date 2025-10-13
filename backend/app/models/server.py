from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from app.core.database import Base


class Server(Base):
    """服务器模型"""
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    host = Column(String(100), nullable=False)
    port = Column(Integer, default=22)
    username = Column(String(50), nullable=False)
    password = Column(String(255))  # 加密存储
    ssh_key = Column(Text)  # SSH密钥
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # 服务器信息
    os_type = Column(String(50))  # Linux, Windows等
    os_version = Column(String(100))
    cpu_cores = Column(Integer)
    memory_total = Column(Integer)  # MB
    disk_total = Column(Integer)  # GB
    
    # 状态信息
    status = Column(String(20), default="unknown")  # online, offline, unknown
    last_check_time = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Server {self.name} - {self.host}>"

