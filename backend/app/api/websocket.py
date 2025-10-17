"""
WebSocket API endpoints
支持Web Terminal实时SSH连接
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from app.core.database import get_db
from app.services.server_service import ServerService
from app.utils.ssh_session import SSHSession
from typing import Dict

router = APIRouter()

# 存储活动的SSH会话
active_sessions: Dict[str, SSHSession] = {}


@router.websocket("/ws/ssh/{server_id}")
async def websocket_ssh_endpoint(
    websocket: WebSocket, 
    server_id: int,
    db: Session = Depends(get_db)
):
    """
    WebSocket SSH终端endpoint
    
    消息格式：
    - 客户端 -> 服务器:
      {"type": "input", "data": "命令内容"}
      {"type": "resize", "cols": 80, "rows": 24}
    
    - 服务器 -> 客户端:
      {"type": "output", "data": "输出内容"}
      {"type": "error", "message": "错误信息"}
      {"type": "connected"}
      {"type": "disconnected"}
    """
    await websocket.accept()
    
    session_id = f"{server_id}_{id(websocket)}"
    ssh_session: SSHSession = None
    
    try:
        # 获取服务器信息
        server = ServerService.get_server(db, server_id)
        if not server:
            await websocket.send_json({
                "type": "error",
                "message": "服务器不存在"
            })
            await websocket.close()
            return
        
        # 创建SSH会话
        ssh_session = SSHSession(
            host=server.host,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        )
        
        # 设置输出回调 - 使用同步方式
        import asyncio
        
        def output_callback(data: str):
            try:
                # 创建异步任务发送数据
                asyncio.create_task(websocket.send_json({
                    "type": "output",
                    "data": data
                }))
            except:
                pass
        
        ssh_session.output_callback = output_callback
        
        # 连接SSH
        success, error_msg = ssh_session.connect()
        
        if not success:
            await websocket.send_json({
                "type": "error",
                "message": error_msg or "SSH连接失败"
            })
            await websocket.close()
            return
        
        # 保存会话
        active_sessions[session_id] = ssh_session
        
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": f"已连接到 {server.host}"
        })
        
        # 处理WebSocket消息
        while True:
            try:
                # 接收客户端消息
                message = await websocket.receive_text()
                data = json.loads(message)
                
                msg_type = data.get('type')
                
                if msg_type == 'input':
                    # 处理用户输入
                    input_data = data.get('data', '')
                    ssh_session.send_input(input_data)
                
                elif msg_type == 'resize':
                    # 调整终端大小
                    cols = data.get('cols', 80)
                    rows = data.get('rows', 24)
                    ssh_session.resize(cols, rows)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "无效的JSON格式"
                })
            except Exception as e:
                print(f"处理消息错误: {e}")
                break
    
    except Exception as e:
        print(f"WebSocket错误: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    
    finally:
        # 清理SSH会话
        if ssh_session:
            ssh_session.close()
        
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        try:
            await websocket.send_json({"type": "disconnected"})
        except:
            pass
        
        try:
            await websocket.close()
        except:
            pass


@router.get("/ws/sessions")
async def get_active_sessions():
    """获取活动的SSH会话数量"""
    return {
        "active_sessions": len(active_sessions),
        "sessions": list(active_sessions.keys())
    }

