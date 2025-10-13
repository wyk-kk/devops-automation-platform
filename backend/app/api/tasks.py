from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.task import Task, TaskCreate, TaskUpdate, TaskExecution
from app.schemas.user import User
from app.services.task_service import TaskService
from app.services.scheduler_service import scheduler_service
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/tasks", tags=["任务调度"])


@router.get("", response_model=List[Task])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取任务列表"""
    return TaskService.get_tasks(db, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取任务详情"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=Task)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建任务"""
    db_task = TaskService.create_task(db, task, current_user.id)
    
    # 添加到调度器
    if db_task.is_enabled:
        scheduler_service.add_task(db_task.id, db_task.cron_expression)
    
    return db_task


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新任务"""
    db_task = TaskService.update_task(db, task_id, task)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 更新调度器
    if db_task.is_enabled:
        scheduler_service.add_task(db_task.id, db_task.cron_expression)
    else:
        scheduler_service.remove_task(db_task.id)
    
    return db_task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除任务"""
    # 从调度器移除
    scheduler_service.remove_task(task_id)
    
    success = TaskService.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/execute", response_model=TaskExecution)
def execute_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """手动执行任务"""
    execution = TaskService.execute_task(db, task_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Task not found")
    return execution


@router.get("/{task_id}/executions", response_model=List[TaskExecution])
def get_task_executions(
    task_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取任务执行记录"""
    return TaskService.get_executions(db, task_id=task_id, skip=skip, limit=limit)

