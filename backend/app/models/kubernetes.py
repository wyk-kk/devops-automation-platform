from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from datetime import datetime
from app.core.database import Base


class K8sCluster(Base):
    """Kubernetes集群模型"""
    __tablename__ = "k8s_clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    
    # 连接配置
    api_server = Column(String(500), nullable=False)  # API Server地址
    auth_type = Column(String(50), default="kubeconfig")  # kubeconfig, token, cert
    
    # kubeconfig方式
    kubeconfig = Column(Text)  # kubeconfig文件内容
    
    # Token方式
    token = Column(Text)
    
    # 证书方式
    ca_cert = Column(Text)  # CA证书
    client_cert = Column(Text)  # 客户端证书
    client_key = Column(Text)  # 客户端密钥
    
    # 集群信息
    version = Column(String(50))  # Kubernetes版本
    node_count = Column(Integer, default=0)  # 节点数量
    namespace_count = Column(Integer, default=0)  # 命名空间数量
    pod_count = Column(Integer, default=0)  # Pod数量
    
    # 连接状态
    status = Column(String(20), default="unknown")  # connected, disconnected, error, unknown
    last_check_time = Column(DateTime)
    error_message = Column(Text)
    
    # 标签和分类
    environment = Column(String(50))  # dev, test, staging, prod
    tags = Column(JSON)  # ["tag1", "tag2"]
    
    # 管理信息
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<K8sCluster {self.name}>"


class K8sNode(Base):
    """Kubernetes节点模型"""
    __tablename__ = "k8s_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联集群
    cluster_id = Column(Integer, ForeignKey("k8s_clusters.id"), nullable=False)
    
    # 节点信息
    node_name = Column(String(200), nullable=False)
    node_ip = Column(String(100))
    
    # 节点状态
    status = Column(String(50))  # Ready, NotReady, Unknown
    roles = Column(JSON)  # ["master", "worker"]
    
    # 资源信息
    cpu_capacity = Column(String(50))  # 例如: "4"
    memory_capacity = Column(String(50))  # 例如: "8Gi"
    cpu_allocatable = Column(String(50))
    memory_allocatable = Column(String(50))
    
    # 使用情况
    cpu_usage_percent = Column(Integer)
    memory_usage_percent = Column(Integer)
    pod_count = Column(Integer, default=0)
    pod_capacity = Column(Integer)
    
    # 系统信息
    os_image = Column(String(200))
    kernel_version = Column(String(100))
    container_runtime = Column(String(100))
    kubelet_version = Column(String(50))
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<K8sNode {self.node_name}>"


class K8sNamespace(Base):
    """Kubernetes命名空间模型"""
    __tablename__ = "k8s_namespaces"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联集群
    cluster_id = Column(Integer, ForeignKey("k8s_clusters.id"), nullable=False)
    
    # 命名空间信息
    namespace_name = Column(String(200), nullable=False)
    status = Column(String(50))  # Active, Terminating
    
    # 资源统计
    pod_count = Column(Integer, default=0)
    service_count = Column(Integer, default=0)
    deployment_count = Column(Integer, default=0)
    configmap_count = Column(Integer, default=0)
    secret_count = Column(Integer, default=0)
    
    # 标签
    labels = Column(JSON)
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<K8sNamespace {self.namespace_name}>"


class K8sPod(Base):
    """Kubernetes Pod模型（简化版，用于监控）"""
    __tablename__ = "k8s_pods"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联
    cluster_id = Column(Integer, ForeignKey("k8s_clusters.id"), nullable=False)
    namespace = Column(String(200), nullable=False)
    
    # Pod信息
    pod_name = Column(String(200), nullable=False)
    node_name = Column(String(200))
    
    # 状态
    status = Column(String(50))  # Running, Pending, Failed, Succeeded, Unknown
    ready_containers = Column(Integer, default=0)
    total_containers = Column(Integer, default=1)
    
    # 资源
    cpu_request = Column(String(50))
    memory_request = Column(String(50))
    cpu_limit = Column(String(50))
    memory_limit = Column(String(50))
    
    # IP信息
    pod_ip = Column(String(100))
    host_ip = Column(String(100))
    
    # 重启次数
    restart_count = Column(Integer, default=0)
    
    # 标签
    labels = Column(JSON)
    
    # 时间信息
    start_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<K8sPod {self.namespace}/{self.pod_name}>"

