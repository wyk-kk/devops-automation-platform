from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.server import Server, ServerCreate, ServerUpdate, ServerStatus
from app.schemas.user import User
from app.services.server_service import ServerService
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/servers", tags=["服务器管理"])


@router.get("", response_model=List[Server])
def get_servers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取服务器列表"""
    return ServerService.get_servers(db, skip=skip, limit=limit)


@router.get("/{server_id}", response_model=Server)
def get_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取服务器详情"""
    server = ServerService.get_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.post("", response_model=Server)
def create_server(
    server: ServerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建服务器"""
    return ServerService.create_server(db, server)


@router.put("/{server_id}", response_model=Server)
def update_server(
    server_id: int,
    server: ServerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新服务器"""
    db_server = ServerService.update_server(db, server_id, server)
    if not db_server:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server


@router.delete("/{server_id}")
def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除服务器"""
    success = ServerService.delete_server(db, server_id)
    if not success:
        raise HTTPException(status_code=404, detail="Server not found")
    return {"message": "Server deleted successfully"}


@router.post("/{server_id}/test")
def test_connection(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """测试服务器连接"""
    result = ServerService.test_connection(db, server_id)
    return result


@router.post("/{server_id}/refresh")
def refresh_server_info(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """刷新服务器信息"""
    success = ServerService.update_server_info(db, server_id)
    if not success:
        return {"success": False, "message": "Failed to refresh server info"}
    return {"success": True, "message": "Server info refreshed"}


@router.get("/{server_id}/status", response_model=ServerStatus)
def get_server_status(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取服务器实时状态"""
    status = ServerService.get_server_status(db, server_id)
    if not status:
        raise HTTPException(status_code=404, detail="Server not found or offline")
    return status

