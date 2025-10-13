from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.script import Script, ScriptCreate, ScriptExecution, ScriptExecutionCreate
from app.schemas.user import User
from app.services.script_service import ScriptService
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/scripts", tags=["脚本管理"])


@router.get("", response_model=List[Script])
def get_scripts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取脚本列表"""
    return ScriptService.get_scripts(db, skip=skip, limit=limit)


@router.get("/{script_id}", response_model=Script)
def get_script(
    script_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取脚本详情"""
    script = ScriptService.get_script(db, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@router.post("", response_model=Script)
def create_script(
    script: ScriptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建脚本"""
    return ScriptService.create_script(db, script, current_user.id)


@router.put("/{script_id}", response_model=Script)
def update_script(
    script_id: int,
    script: ScriptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新脚本"""
    db_script = ScriptService.update_script(db, script_id, script)
    if not db_script:
        raise HTTPException(status_code=404, detail="Script not found")
    return db_script


@router.delete("/{script_id}")
def delete_script(
    script_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除脚本"""
    success = ScriptService.delete_script(db, script_id)
    if not success:
        raise HTTPException(status_code=404, detail="Script not found")
    return {"message": "Script deleted successfully"}


@router.post("/execute", response_model=ScriptExecution)
def execute_script(
    execution: ScriptExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """执行脚本"""
    result = ScriptService.execute_script(
        db, 
        execution.script_id, 
        execution.server_id, 
        current_user.id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Script or server not found")
    return result


@router.get("/executions/list", response_model=List[ScriptExecution])
def get_executions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取执行记录列表"""
    return ScriptService.get_executions(db, skip=skip, limit=limit)


@router.get("/executions/{execution_id}", response_model=ScriptExecution)
def get_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取执行记录详情"""
    execution = ScriptService.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

