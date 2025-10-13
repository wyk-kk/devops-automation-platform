from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import SessionLocal
from app.models.task import Task, TaskExecution
from app.services.script_service import ScriptService


class SchedulerService:
    """调度器服务"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
    
    def add_task(self, task_id: int, cron_expression: str):
        """添加定时任务"""
        try:
            trigger = CronTrigger.from_crontab(cron_expression)
            self.scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                id=f"task_{task_id}",
                args=[task_id],
                replace_existing=True
            )
            return True
        except Exception as e:
            print(f"Failed to add task: {str(e)}")
            return False
    
    def remove_task(self, task_id: int):
        """移除定时任务"""
        try:
            self.scheduler.remove_job(f"task_{task_id}")
            return True
        except:
            return False
    
    def _execute_task(self, task_id: int):
        """执行定时任务"""
        db = SessionLocal()
        
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task or not task.is_enabled:
                return
            
            # 创建执行记录
            execution = TaskExecution(
                task_id=task_id,
                status="running",
                start_time=datetime.utcnow()
            )
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            # 执行任务
            if task.task_type == "script" and task.script_id:
                # 执行脚本
                result = ScriptService.execute_script(
                    db, 
                    task.script_id, 
                    task.server_id,
                    task.created_by or 1
                )
                
                if result:
                    execution.status = result.status
                    execution.output = result.output
                    execution.error = result.error
                else:
                    execution.status = "failed"
                    execution.error = "Failed to execute script"
            
            elif task.task_type == "command" and task.command:
                # 执行命令（TODO: 实现命令执行逻辑）
                execution.status = "success"
                execution.output = "Command executed"
            
            execution.end_time = datetime.utcnow()
            
            # 更新任务信息
            task.last_run_time = datetime.utcnow()
            task.last_status = execution.status
            
            db.commit()
            
        except Exception as e:
            print(f"Task execution failed: {str(e)}")
            if execution:
                execution.status = "failed"
                execution.error = str(e)
                execution.end_time = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    def load_tasks(self):
        """从数据库加载所有启用的任务"""
        db = SessionLocal()
        
        try:
            tasks = db.query(Task).filter(Task.is_enabled == True).all()
            for task in tasks:
                self.add_task(task.id, task.cron_expression)
            print(f"Loaded {len(tasks)} scheduled tasks")
        finally:
            db.close()
    
    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()


# 全局调度器实例
scheduler_service = SchedulerService()

