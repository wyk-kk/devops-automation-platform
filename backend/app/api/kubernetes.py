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


@router.post("/clusters/{cluster_id}/sync")
def sync_cluster_resources(
    cluster_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """同步集群资源（后台任务）"""
    cluster = K8sService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # 在后台同步
    background_tasks.add_task(K8sService.sync_cluster_resources, db, cluster_id)
    
    return {"message": "Sync task started"}


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
    
    if not k8s_client.connect():
        raise HTTPException(status_code=500, detail="Failed to connect to cluster")
    
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
    
    if not k8s_client.connect():
        raise HTTPException(status_code=500, detail="Failed to connect to cluster")
    
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
    
    if not k8s_client.connect():
        raise HTTPException(status_code=500, detail="Failed to connect to cluster")
    
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
    
    if not k8s_client.connect():
        raise HTTPException(status_code=500, detail="Failed to connect to cluster")
    
    success = k8s_client.scale_deployment(namespace, deployment_name, replicas)
    k8s_client.close()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to scale deployment")
    
    return {"message": f"Deployment scaled to {replicas} replicas"}

