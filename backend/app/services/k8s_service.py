from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import datetime
from app.models.kubernetes import K8sCluster, K8sNode, K8sNamespace, K8sPod
from app.schemas.kubernetes import (
    K8sClusterCreate, K8sClusterUpdate, K8sClusterStats
)
from app.utils.k8s_client import K8sClient


class K8sService:
    """Kubernetes集群服务"""
    
    @staticmethod
    def get_clusters(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[K8sCluster]:
        """获取集群列表"""
        query = db.query(K8sCluster)
        
        if is_active is not None:
            query = query.filter(K8sCluster.is_active == is_active)
        
        return query.order_by(K8sCluster.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_cluster(db: Session, cluster_id: int) -> Optional[K8sCluster]:
        """获取单个集群"""
        return db.query(K8sCluster).filter(K8sCluster.id == cluster_id).first()
    
    @staticmethod
    def create_cluster(db: Session, cluster: K8sClusterCreate, user_id: int) -> K8sCluster:
        """创建集群"""
        db_cluster = K8sCluster(
            **cluster.model_dump(),
            created_by=user_id
        )
        db.add(db_cluster)
        db.commit()
        db.refresh(db_cluster)
        
        # 尝试连接并更新状态
        K8sService.update_cluster_status(db, db_cluster)
        
        return db_cluster
    
    @staticmethod
    def update_cluster(
        db: Session, 
        cluster_id: int, 
        cluster: K8sClusterUpdate
    ) -> Optional[K8sCluster]:
        """更新集群"""
        db_cluster = K8sService.get_cluster(db, cluster_id)
        if not db_cluster:
            return None
        
        update_data = cluster.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cluster, field, value)
        
        db_cluster.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_cluster)
        
        # 更新状态
        K8sService.update_cluster_status(db, db_cluster)
        
        return db_cluster
    
    @staticmethod
    def delete_cluster(db: Session, cluster_id: int) -> bool:
        """删除集群"""
        db_cluster = K8sService.get_cluster(db, cluster_id)
        if not db_cluster:
            return False
        
        # 删除相关数据
        db.query(K8sPod).filter(K8sPod.cluster_id == cluster_id).delete()
        db.query(K8sNamespace).filter(K8sNamespace.cluster_id == cluster_id).delete()
        db.query(K8sNode).filter(K8sNode.cluster_id == cluster_id).delete()
        db.delete(db_cluster)
        db.commit()
        return True
    
    @staticmethod
    def update_cluster_status(db: Session, cluster: K8sCluster) -> K8sCluster:
        """更新集群状态"""
        try:
            # 创建K8s客户端
            k8s_client = K8sClient(
                api_server=cluster.api_server,
                auth_type=cluster.auth_type,
                kubeconfig=cluster.kubeconfig,
                token=cluster.token,
                ca_cert=cluster.ca_cert,
                client_cert=cluster.client_cert,
                client_key=cluster.client_key
            )
            
            # 尝试连接
            if k8s_client.connect():
                cluster.status = "connected"
                cluster.error_message = None
                
                # 获取版本
                version = k8s_client.get_version()
                if version:
                    cluster.version = version
                
                # 获取统计信息
                stats = k8s_client.get_cluster_stats()
                cluster.node_count = stats.get('node_count', 0)
                cluster.namespace_count = stats.get('namespace_count', 0)
                cluster.pod_count = stats.get('pod_count', 0)
                
                k8s_client.close()
            else:
                cluster.status = "disconnected"
                cluster.error_message = "连接失败"
            
        except Exception as e:
            cluster.status = "error"
            cluster.error_message = str(e)
        
        cluster.last_check_time = datetime.utcnow()
        db.commit()
        db.refresh(cluster)
        return cluster
    
    @staticmethod
    def sync_cluster_resources(db: Session, cluster_id: int) -> bool:
        """同步集群资源信息"""
        cluster = K8sService.get_cluster(db, cluster_id)
        if not cluster or cluster.status != "connected":
            return False
        
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
            
            if not k8s_client.connect():
                return False
            
            # 同步节点
            nodes = k8s_client.list_nodes()
            db.query(K8sNode).filter(K8sNode.cluster_id == cluster_id).delete()
            
            for node_data in nodes:
                db_node = K8sNode(cluster_id=cluster_id, **node_data)
                db.add(db_node)
            
            # 同步命名空间
            namespaces = k8s_client.list_namespaces()
            db.query(K8sNamespace).filter(K8sNamespace.cluster_id == cluster_id).delete()
            
            for ns_data in namespaces:
                db_ns = K8sNamespace(cluster_id=cluster_id, **ns_data)
                db.add(db_ns)
            
            # 同步Pods（仅保存最近的数据，避免数据量过大）
            pods = k8s_client.list_pods()
            db.query(K8sPod).filter(K8sPod.cluster_id == cluster_id).delete()
            
            for pod_data in pods[:1000]:  # 限制数量
                db_pod = K8sPod(cluster_id=cluster_id, **pod_data)
                db.add(db_pod)
            
            db.commit()
            k8s_client.close()
            
            # 更新集群统计
            cluster.node_count = len(nodes)
            cluster.namespace_count = len(namespaces)
            cluster.pod_count = len(pods)
            db.commit()
            
            return True
            
        except Exception as e:
            print(f"同步集群资源失败: {str(e)}")
            return False
    
    @staticmethod
    def get_cluster_stats(db: Session) -> K8sClusterStats:
        """获取集群统计信息"""
        total_clusters = db.query(func.count(K8sCluster.id)).scalar() or 0
        active_clusters = db.query(func.count(K8sCluster.id)).filter(
            K8sCluster.is_active == True
        ).scalar() or 0
        
        total_nodes = db.query(func.count(K8sNode.id)).scalar() or 0
        total_pods = db.query(func.count(K8sPod.id)).scalar() or 0
        total_namespaces = db.query(func.count(K8sNamespace.id)).scalar() or 0
        
        # 按环境分组
        env_results = db.query(
            K8sCluster.environment,
            func.count(K8sCluster.id)
        ).filter(
            K8sCluster.environment.isnot(None)
        ).group_by(K8sCluster.environment).all()
        
        clusters_by_env = {env: count for env, count in env_results}
        
        return K8sClusterStats(
            total_clusters=total_clusters,
            active_clusters=active_clusters,
            total_nodes=total_nodes,
            total_pods=total_pods,
            total_namespaces=total_namespaces,
            clusters_by_env=clusters_by_env
        )
    
    @staticmethod
    def get_cluster_nodes(db: Session, cluster_id: int) -> List[K8sNode]:
        """获取集群节点列表"""
        return db.query(K8sNode).filter(K8sNode.cluster_id == cluster_id).all()
    
    @staticmethod
    def get_cluster_namespaces(db: Session, cluster_id: int) -> List[K8sNamespace]:
        """获取集群命名空间列表"""
        return db.query(K8sNamespace).filter(K8sNamespace.cluster_id == cluster_id).all()
    
    @staticmethod
    def get_cluster_pods(
        db: Session, 
        cluster_id: int, 
        namespace: Optional[str] = None
    ) -> List[K8sPod]:
        """获取集群Pod列表"""
        query = db.query(K8sPod).filter(K8sPod.cluster_id == cluster_id)
        
        if namespace:
            query = query.filter(K8sPod.namespace == namespace)
        
        return query.order_by(K8sPod.created_at.desc()).limit(500).all()

