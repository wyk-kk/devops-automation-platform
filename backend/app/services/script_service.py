from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.script import Script, ScriptExecution
from app.models.server import Server
from app.schemas.script import ScriptCreate
from app.utils.ssh_client import SSHClient
import tempfile
import os


class ScriptService:
    """脚本服务"""
    
    @staticmethod
    def get_scripts(db: Session, skip: int = 0, limit: int = 100) -> List[Script]:
        """获取脚本列表"""
        return db.query(Script).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_script(db: Session, script_id: int) -> Optional[Script]:
        """获取单个脚本"""
        return db.query(Script).filter(Script.id == script_id).first()
    
    @staticmethod
    def create_script(db: Session, script: ScriptCreate, user_id: int) -> Script:
        """创建脚本"""
        db_script = Script(**script.model_dump(), created_by=user_id)
        db.add(db_script)
        db.commit()
        db.refresh(db_script)
        return db_script
    
    @staticmethod
    def update_script(db: Session, script_id: int, script: ScriptCreate) -> Optional[Script]:
        """更新脚本"""
        db_script = ScriptService.get_script(db, script_id)
        if not db_script:
            return None
        
        update_data = script.model_dump()
        for field, value in update_data.items():
            setattr(db_script, field, value)
        
        db.commit()
        db.refresh(db_script)
        return db_script
    
    @staticmethod
    def delete_script(db: Session, script_id: int) -> bool:
        """删除脚本"""
        db_script = ScriptService.get_script(db, script_id)
        if not db_script:
            return False
        
        db.delete(db_script)
        db.commit()
        return True
    
    @staticmethod
    def execute_script(db: Session, script_id: int, server_id: int, user_id: int) -> Optional[ScriptExecution]:
        """执行脚本"""
        script = ScriptService.get_script(db, script_id)
        if not script:
            return None
        
        server = db.query(Server).filter(Server.id == server_id).first()
        if not server:
            return None
        
        # 创建执行记录
        execution = ScriptExecution(
            script_id=script_id,
            server_id=server_id,
            status="running",
            executed_by=user_id,
            start_time=datetime.utcnow()
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        # 连接服务器并执行脚本
        ssh = SSHClient(
            host=server.host,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        )
        
        if not ssh.connect():
            execution.status = "failed"
            execution.error = "Failed to connect to server"
            execution.end_time = datetime.utcnow()
            db.commit()
            return execution
        
        try:
            # 将脚本上传到远程服务器
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script.content)
                local_path = f.name
            
            remote_path = f"/tmp/script_{execution.id}.sh"
            
            if not ssh.upload_file(local_path, remote_path):
                execution.status = "failed"
                execution.error = "Failed to upload script"
                execution.end_time = datetime.utcnow()
                db.commit()
                return execution
            
            # 执行脚本
            stdout, stderr, exit_code = ssh.execute_command(f"bash {remote_path}")
            
            # 清理远程脚本文件
            ssh.execute_command(f"rm {remote_path}")
            
            # 更新执行记录
            execution.output = stdout
            execution.error = stderr
            execution.exit_code = exit_code
            execution.status = "success" if exit_code == 0 else "failed"
            execution.end_time = datetime.utcnow()
            
            # 清理本地临时文件
            os.unlink(local_path)
            
        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            execution.end_time = datetime.utcnow()
        finally:
            ssh.close()
        
        db.commit()
        db.refresh(execution)
        return execution
    
    @staticmethod
    def get_executions(db: Session, skip: int = 0, limit: int = 100) -> List[ScriptExecution]:
        """获取执行记录列表"""
        return db.query(ScriptExecution).order_by(ScriptExecution.start_time.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_execution(db: Session, execution_id: int) -> Optional[ScriptExecution]:
        """获取单个执行记录"""
        return db.query(ScriptExecution).filter(ScriptExecution.id == execution_id).first()

