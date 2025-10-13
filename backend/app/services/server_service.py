from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.server import Server
from app.schemas.server import ServerCreate, ServerUpdate, ServerStatus
from app.utils.ssh_client import SSHClient


class ServerService:
    """服务器服务"""
    
    @staticmethod
    def get_servers(db: Session, skip: int = 0, limit: int = 100) -> List[Server]:
        """获取服务器列表"""
        return db.query(Server).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_server(db: Session, server_id: int) -> Optional[Server]:
        """获取单个服务器"""
        return db.query(Server).filter(Server.id == server_id).first()
    
    @staticmethod
    def create_server(db: Session, server: ServerCreate) -> Server:
        """创建服务器"""
        db_server = Server(**server.model_dump())
        db.add(db_server)
        db.commit()
        db.refresh(db_server)
        
        # 尝试连接并获取系统信息
        try:
            ServerService.update_server_info(db, db_server.id)
        except:
            pass
        
        return db_server
    
    @staticmethod
    def update_server(db: Session, server_id: int, server: ServerUpdate) -> Optional[Server]:
        """更新服务器"""
        db_server = ServerService.get_server(db, server_id)
        if not db_server:
            return None
        
        update_data = server.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_server, field, value)
        
        db.commit()
        db.refresh(db_server)
        return db_server
    
    @staticmethod
    def delete_server(db: Session, server_id: int) -> bool:
        """删除服务器"""
        db_server = ServerService.get_server(db, server_id)
        if not db_server:
            return False
        
        db.delete(db_server)
        db.commit()
        return True
    
    @staticmethod
    def test_connection(db: Session, server_id: int) -> dict:
        """测试服务器连接"""
        server = ServerService.get_server(db, server_id)
        if not server:
            return {"success": False, "message": "Server not found"}
        
        ssh = SSHClient(
            host=server.host,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        )
        
        if ssh.connect():
            ssh.close()
            server.status = "online"
            server.last_check_time = datetime.utcnow()
            db.commit()
            return {"success": True, "message": "Connection successful"}
        else:
            server.status = "offline"
            server.last_check_time = datetime.utcnow()
            db.commit()
            return {"success": False, "message": "Connection failed"}
    
    @staticmethod
    def update_server_info(db: Session, server_id: int) -> bool:
        """更新服务器信息"""
        server = ServerService.get_server(db, server_id)
        if not server:
            return False
        
        ssh = SSHClient(
            host=server.host,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        )
        
        if not ssh.connect():
            server.status = "offline"
            server.last_check_time = datetime.utcnow()
            db.commit()
            return False
        
        try:
            info = ssh.get_system_info()
            server.os_type = info.get('os_type')
            server.os_version = info.get('os_version')
            server.cpu_cores = info.get('cpu_cores')
            server.memory_total = info.get('memory_total')
            server.disk_total = info.get('disk_total')
            server.status = "online"
            server.last_check_time = datetime.utcnow()
            db.commit()
            return True
        except Exception as e:
            print(f"Failed to update server info: {str(e)}")
            return False
        finally:
            ssh.close()
    
    @staticmethod
    def get_server_status(db: Session, server_id: int) -> Optional[ServerStatus]:
        """获取服务器状态"""
        server = ServerService.get_server(db, server_id)
        if not server:
            return None
        
        ssh = SSHClient(
            host=server.host,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        )
        
        if not ssh.connect():
            return ServerStatus(
                server_id=server_id,
                status="offline",
                check_time=datetime.utcnow()
            )
        
        try:
            usage = ssh.get_resource_usage()
            return ServerStatus(
                server_id=server_id,
                status="online",
                cpu_percent=usage.get('cpu_percent'),
                memory_percent=usage.get('memory_percent'),
                memory_used=usage.get('memory_used'),
                memory_total=usage.get('memory_total'),
                disk_percent=usage.get('disk_percent'),
                disk_used=usage.get('disk_used'),
                disk_total=usage.get('disk_total'),
                uptime=usage.get('uptime'),
                check_time=datetime.utcnow()
            )
        except Exception as e:
            print(f"Failed to get server status: {str(e)}")
            return None
        finally:
            ssh.close()

