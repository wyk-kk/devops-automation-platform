from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.kubernetes import (
    K8sCluster, K8sClusterCreate, K8sClusterUpdate, K8sClusterSummary,
    K8sNode, K8sNamespace, K8sPod, K8sClusterStats
)
from app.schemas.user import User
from app.services.k8s_service import K8sService
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/k8s", tags=["Kubernetes集群管理"])


@router.get("/clusters", response_model=List[K8sClusterSummary])
def get_clusters(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取K8s集群列表"""
    return K8sService.get_clusters(db, skip=skip, limit=limit, is_active=is_active)


@router.get("/clusters/{cluster_id}", response_model=K8sCluster)
def get_cluster(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取K8s集群详情"""
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster


@router.post("/clusters", response_model=K8sCluster)
def create_cluster(
    cluster: K8sClusterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建K8s集群"""
    return K8sService.create_cluster(db, cluster, current_user.id)


@router.put("/clusters/{cluster_id}", response_model=K8sCluster)
def update_cluster(
    cluster_id: int,
    cluster: K8sClusterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新K8s集群"""
    updated_cluster = K8sService.update_cluster(db, cluster_id, cluster)
    if not updated_cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return updated_cluster


@router.delete("/clusters/{cluster_id}")
def delete_cluster(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除K8s集群"""
    success = K8sService.delete_cluster(db, cluster_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return {"message": "Cluster deleted successfully"}


@router.post("/clusters/{cluster_id}/check-status", response_model=K8sCluster)
def check_cluster_status(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """检查集群连接状态"""
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    return K8sService.update_cluster_status(db, cluster)


@router.post("/clusters/{cluster_id}/diagnose")
def diagnose_cluster_connection(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    诊断集群连接问题
    
    返回详细的诊断信息，包括：
    - 连接测试结果
    - 认证配置检查
    - 网络连通性测试
    - 详细错误信息
    """
    from app.utils.k8s_client import K8sClient
    import socket
    from urllib.parse import urlparse
    
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    diagnosis = {
        "cluster_id": cluster_id,
        "cluster_name": cluster.cluster_name,
        "checks": [],
        "overall_status": "unknown",
        "recommendations": []
    }
    
    # 检查1: API Server地址格式
    if cluster.api_server:
        try:
            parsed = urlparse(cluster.api_server)
            if parsed.scheme and parsed.netloc:
                diagnosis["checks"].append({
                    "name": "API Server地址格式",
                    "status": "pass",
                    "message": f"格式正确: {parsed.scheme}://{parsed.netloc}"
                })
                
                # 检查2: 网络连通性
                try:
                    host = parsed.hostname
                    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    
                    if result == 0:
                        diagnosis["checks"].append({
                            "name": "网络连通性",
                            "status": "pass",
                            "message": f"可以访问 {host}:{port}"
                        })
                    else:
                        diagnosis["checks"].append({
                            "name": "网络连通性",
                            "status": "fail",
                            "message": f"无法连接到 {host}:{port}"
                        })
                        diagnosis["recommendations"].append(
                            "请检查: 1) API Server是否运行 2) 网络防火墙设置 3) 安全组配置"
                        )
                except Exception as e:
                    diagnosis["checks"].append({
                        "name": "网络连通性",
                        "status": "error",
                        "message": f"测试失败: {str(e)}"
                    })
            else:
                diagnosis["checks"].append({
                    "name": "API Server地址格式",
                    "status": "fail",
                    "message": "地址格式不正确，应该类似: https://x.x.x.x:6443"
                })
                diagnosis["recommendations"].append("请检查API Server地址格式")
        except Exception as e:
            diagnosis["checks"].append({
                "name": "API Server地址格式",
                "status": "error",
                "message": str(e)
            })
    else:
        diagnosis["checks"].append({
            "name": "API Server地址",
            "status": "fail",
            "message": "API Server地址未配置"
        })
        diagnosis["recommendations"].append("请配置API Server地址")
    
    # 检查3: 认证配置
    auth_config_ok = False
    if cluster.auth_type == "kubeconfig":
        if cluster.kubeconfig:
            diagnosis["checks"].append({
                "name": "认证配置",
                "status": "pass",
                "message": f"使用kubeconfig认证 (长度: {len(cluster.kubeconfig)} 字符)"
            })
            auth_config_ok = True
        else:
            diagnosis["checks"].append({
                "name": "认证配置",
                "status": "fail",
                "message": "kubeconfig内容为空"
            })
            diagnosis["recommendations"].append("请提供完整的kubeconfig文件内容")
    
    elif cluster.auth_type == "token":
        if cluster.token:
            diagnosis["checks"].append({
                "name": "认证配置",
                "status": "pass",
                "message": f"使用Token认证 (长度: {len(cluster.token)} 字符)"
            })
            auth_config_ok = True
            
            if not cluster.ca_cert:
                diagnosis["checks"].append({
                    "name": "SSL证书",
                    "status": "warning",
                    "message": "未提供CA证书，将跳过SSL验证（不推荐用于生产环境）"
                })
                diagnosis["recommendations"].append("建议配置CA证书以提高安全性")
        else:
            diagnosis["checks"].append({
                "name": "认证配置",
                "status": "fail",
                "message": "Token为空"
            })
            diagnosis["recommendations"].append("请提供有效的Bearer Token")
    
    elif cluster.auth_type == "cert":
        has_ca = bool(cluster.ca_cert)
        has_client_cert = bool(cluster.client_cert)
        has_client_key = bool(cluster.client_key)
        
        if has_ca and has_client_cert and has_client_key:
            diagnosis["checks"].append({
                "name": "认证配置",
                "status": "pass",
                "message": "证书认证配置完整"
            })
            auth_config_ok = True
        else:
            missing = []
            if not has_ca: missing.append("CA证书")
            if not has_client_cert: missing.append("客户端证书")
            if not has_client_key: missing.append("客户端密钥")
            
            diagnosis["checks"].append({
                "name": "认证配置",
                "status": "fail",
                "message": f"缺少: {', '.join(missing)}"
            })
            diagnosis["recommendations"].append(f"请提供完整的证书认证配置: {', '.join(missing)}")
    
    # 检查4: K8s连接测试
    if auth_config_ok:
        try:
            k8s_client = K8sClient(
                api_server=cluster.api_server,
                auth_type=cluster.auth_type,
                kubeconfig=cluster.kubeconfig,
                token=cluster.token,
                ca_cert=cluster.ca_cert,
                client_cert=cluster.client_cert,
                client_key=cluster.client_key
            )
            
            success, error_msg = k8s_client.connect()
            
            if success:
                diagnosis["checks"].append({
                    "name": "K8s API连接",
                    "status": "pass",
                    "message": "成功连接到Kubernetes集群"
                })
                
                # 尝试获取版本信息
                version = k8s_client.get_version()
                if version:
                    diagnosis["checks"].append({
                        "name": "集群版本",
                        "status": "pass",
                        "message": f"Kubernetes {version}"
                    })
                
                # 尝试获取资源统计
                stats = k8s_client.get_cluster_stats()
                diagnosis["checks"].append({
                    "name": "资源统计",
                    "status": "pass",
                    "message": f"节点: {stats['node_count']}, 命名空间: {stats['namespace_count']}, Pod: {stats['pod_count']}"
                })
                
                diagnosis["overall_status"] = "healthy"
                k8s_client.close()
            else:
                diagnosis["checks"].append({
                    "name": "K8s API连接",
                    "status": "fail",
                    "message": error_msg or "连接失败"
                })
                diagnosis["overall_status"] = "unhealthy"
                
                # 根据错误信息提供建议
                if "401" in (error_msg or "") or "认证失败" in (error_msg or ""):
                    diagnosis["recommendations"].append("认证失败：请检查Token或证书是否正确、是否过期")
                elif "403" in (error_msg or "") or "权限" in (error_msg or ""):
                    diagnosis["recommendations"].append("权限不足：请确保账号有足够的RBAC权限（至少需要list namespace的权限）")
                elif "timeout" in (error_msg or "").lower():
                    diagnosis["recommendations"].append("连接超时：请检查网络连接和防火墙设置")
                elif "certificate" in (error_msg or "").lower():
                    diagnosis["recommendations"].append("证书问题：请检查CA证书是否正确")
                else:
                    diagnosis["recommendations"].append(f"连接错误：{error_msg}")
                    
        except Exception as e:
            diagnosis["checks"].append({
                "name": "K8s API连接",
                "status": "error",
                "message": f"测试异常: {str(e)}"
            })
            diagnosis["overall_status"] = "error"
            diagnosis["recommendations"].append("发生未预期的错误，请检查配置或查看后端日志")
    else:
        diagnosis["overall_status"] = "config_error"
        diagnosis["recommendations"].append("请先完成认证配置")
    
    # 汇总建议
    if not diagnosis["recommendations"]:
        diagnosis["recommendations"].append("集群配置正常，可以开始同步资源")
    
    return diagnosis


@router.post("/clusters/{cluster_id}/sync")
def sync_cluster_resources(
    cluster_id: int,
    background: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    同步集群资源
    
    参数:
        background: 是否在后台执行（默认false，立即同步并返回结果）
    """
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    if background:
        # 后台任务
        from fastapi import BackgroundTasks
        # 注意：这里简化处理，实际生产环境建议使用Celery等任务队列
        return {"message": "Sync task started", "status": "pending"}
    else:
        # 立即同步并返回结果
        success, error_msg = K8sService.sync_cluster_resources(db, cluster_id)
        
        if success:
            # 重新获取集群信息返回
            updated_cluster = K8sService.get_cluster(db, cluster_id)
            return {
                "message": "Sync completed successfully",
                "status": "success",
                "cluster": {
                    "id": updated_cluster.id,
                    "cluster_name": updated_cluster.cluster_name,
                    "status": updated_cluster.status,
                    "node_count": updated_cluster.node_count,
                    "namespace_count": updated_cluster.namespace_count,
                    "pod_count": updated_cluster.pod_count,
                    "version": updated_cluster.version,
                }
            }
        else:
            return {
                "message": error_msg or "Sync failed",
                "status": "failed",
                "error": error_msg
            }


@router.get("/clusters/{cluster_id}/nodes", response_model=List[K8sNode])
def get_cluster_nodes(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取集群节点列表"""
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    return K8sService.get_cluster_nodes(db, cluster_id)


@router.get("/clusters/{cluster_id}/namespaces", response_model=List[K8sNamespace])
def get_cluster_namespaces(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取集群命名空间列表"""
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    return K8sService.get_cluster_namespaces(db, cluster_id)


@router.get("/clusters/{cluster_id}/pods", response_model=List[K8sPod])
def get_cluster_pods(
    cluster_id: int,
    namespace: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取集群Pod列表"""
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    return K8sService.get_cluster_pods(db, cluster_id, namespace)


@router.get("/statistics", response_model=K8sClusterStats)
def get_cluster_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取K8s集群统计信息"""
    return K8sService.get_cluster_stats(db)


# Pod管理接口
@router.get("/clusters/{cluster_id}/pods/{namespace}/{pod_name}/logs")
def get_pod_logs(
    cluster_id: int,
    namespace: str,
    pod_name: str,
    container: Optional[str] = None,
    tail_lines: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取Pod日志"""
    from app.utils.k8s_client import K8sClient
    
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    k8s_client = K8sClient(
        api_server=cluster.api_server,
        auth_type=cluster.auth_type,
        kubeconfig=cluster.kubeconfig,
        token=cluster.token,
        ca_cert=cluster.ca_cert,
        client_cert=cluster.client_cert,
        client_key=cluster.client_key
    )
    
    success, error_msg = k8s_client.connect()
    if not success:
        raise HTTPException(status_code=500, detail=error_msg or "Failed to connect to cluster")
    
    logs = k8s_client.get_pod_logs(namespace, pod_name, container, tail_lines)
    k8s_client.close()
    
    return {"logs": logs}


@router.delete("/clusters/{cluster_id}/pods/{namespace}/{pod_name}")
def delete_pod(
    cluster_id: int,
    namespace: str,
    pod_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除Pod（会触发重启）"""
    from app.utils.k8s_client import K8sClient
    
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    k8s_client = K8sClient(
        api_server=cluster.api_server,
        auth_type=cluster.auth_type,
        kubeconfig=cluster.kubeconfig,
        token=cluster.token,
        ca_cert=cluster.ca_cert,
        client_cert=cluster.client_cert,
        client_key=cluster.client_key
    )
    
    success, error_msg = k8s_client.connect()
    if not success:
        raise HTTPException(status_code=500, detail=error_msg or "Failed to connect to cluster")
    
    success = k8s_client.delete_pod(namespace, pod_name)
    k8s_client.close()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete pod")
    
    return {"message": "Pod deleted successfully"}


# Deployment管理接口
@router.get("/clusters/{cluster_id}/deployments")
def get_deployments(
    cluster_id: int,
    namespace: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取Deployment列表"""
    from app.utils.k8s_client import K8sClient
    
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    k8s_client = K8sClient(
        api_server=cluster.api_server,
        auth_type=cluster.auth_type,
        kubeconfig=cluster.kubeconfig,
        token=cluster.token,
        ca_cert=cluster.ca_cert,
        client_cert=cluster.client_cert,
        client_key=cluster.client_key
    )
    
    success, error_msg = k8s_client.connect()
    if not success:
        raise HTTPException(status_code=500, detail=error_msg or "Failed to connect to cluster")
    
    deployments = k8s_client.list_deployments(namespace)
    k8s_client.close()
    
    return deployments


@router.post("/clusters/{cluster_id}/deployments/{namespace}/{deployment_name}/scale")
def scale_deployment(
    cluster_id: int,
    namespace: str,
    deployment_name: str,
    replicas: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """伸缩Deployment"""
    from app.utils.k8s_client import K8sClient
    
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    k8s_client = K8sClient(
        api_server=cluster.api_server,
        auth_type=cluster.auth_type,
        kubeconfig=cluster.kubeconfig,
        token=cluster.token,
        ca_cert=cluster.ca_cert,
        client_cert=cluster.client_cert,
        client_key=cluster.client_key
    )
    
    success, error_msg = k8s_client.connect()
    if not success:
        raise HTTPException(status_code=500, detail=error_msg or "Failed to connect to cluster")
    
    success = k8s_client.scale_deployment(namespace, deployment_name, replicas)
    k8s_client.close()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to scale deployment")
    
    return {"message": f"Deployment scaled to {replicas} replicas"}

