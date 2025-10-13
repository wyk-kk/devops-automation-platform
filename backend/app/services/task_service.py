from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.task import Task, TaskExecution
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """任务服务"""
    
    @staticmethod
    def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
        """获取任务列表"""
        return db.query(Task).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """获取单个任务"""
        return db.query(Task).filter(Task.id == task_id).first()
    
    @staticmethod
    def create_task(db: Session, task: TaskCreate, user_id: int) -> Task:
        """创建任务"""
        db_task = Task(**task.model_dump(), created_by=user_id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def update_task(db: Session, task_id: int, task: TaskUpdate) -> Optional[Task]:
        """更新任务"""
        db_task = TaskService.get_task(db, task_id)
        if not db_task:
            return None
        
        update_data = task.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        """删除任务"""
        db_task = TaskService.get_task(db, task_id)
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
    
    @staticmethod
    def execute_task(db: Session, task_id: int) -> Optional[TaskExecution]:
        """执行任务（手动触发）"""
        task = TaskService.get_task(db, task_id)
        if not task:
            return None
        
        execution = TaskExecution(
            task_id=task_id,
            status="running",
            start_time=datetime.utcnow()
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        # TODO: 实际执行任务逻辑（调用脚本执行服务）
        
        return execution
    
    @staticmethod
    def get_executions(db: Session, task_id: Optional[int] = None, 
                      skip: int = 0, limit: int = 100) -> List[TaskExecution]:
        """获取任务执行记录"""
        query = db.query(TaskExecution)
        
        if task_id:
            query = query.filter(TaskExecution.task_id == task_id)
        
        return query.order_by(TaskExecution.start_time.desc()).offset(skip).limit(limit).all()

