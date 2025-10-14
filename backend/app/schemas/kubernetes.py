from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ==================== K8s Cluster ====================

class K8sClusterBase(BaseModel):
    """K8s集群基础Schema"""
    name: str = Field(..., description="集群名称")
    description: Optional[str] = Field(None, description="集群描述")
    api_server: str = Field(..., description="API Server地址")
    auth_type: str = Field("kubeconfig", description="认证方式: kubeconfig, token, cert")
    kubeconfig: Optional[str] = Field(None, description="Kubeconfig内容")
    token: Optional[str] = Field(None, description="Token")
    ca_cert: Optional[str] = Field(None, description="CA证书")
    client_cert: Optional[str] = Field(None, description="客户端证书")
    client_key: Optional[str] = Field(None, description="客户端密钥")
    environment: Optional[str] = Field(None, description="环境: dev, test, staging, prod")
    tags: Optional[List[str]] = Field(None, description="标签")
    is_active: bool = Field(True, description="是否启用")


class K8sClusterCreate(K8sClusterBase):
    """创建K8s集群"""
    pass


class K8sClusterUpdate(BaseModel):
    """更新K8s集群"""
    name: Optional[str] = None
    description: Optional[str] = None
    api_server: Optional[str] = None
    auth_type: Optional[str] = None
    kubeconfig: Optional[str] = None
    token: Optional[str] = None
    ca_cert: Optional[str] = None
    client_cert: Optional[str] = None
    client_key: Optional[str] = None
    environment: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class K8sCluster(K8sClusterBase):
    """K8s集群响应"""
    id: int
    version: Optional[str]
    node_count: int
    namespace_count: int
    pod_count: int
    status: str
    last_check_time: Optional[datetime]
    error_message: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class K8sClusterSummary(BaseModel):
    """K8s集群摘要"""
    id: int
    name: str
    api_server: str
    version: Optional[str]
    node_count: int
    namespace_count: int
    pod_count: int
    status: str
    environment: Optional[str]
    
    model_config = {"from_attributes": True}


# ==================== K8s Node ====================

class K8sNodeBase(BaseModel):
    """K8s节点基础Schema"""
    node_name: str
    node_ip: Optional[str]
    status: str
    roles: Optional[List[str]]
    cpu_capacity: Optional[str]
    memory_capacity: Optional[str]
    cpu_allocatable: Optional[str]
    memory_allocatable: Optional[str]
    cpu_usage_percent: Optional[int]
    memory_usage_percent: Optional[int]
    pod_count: int = 0
    pod_capacity: Optional[int]
    os_image: Optional[str]
    kernel_version: Optional[str]
    container_runtime: Optional[str]
    kubelet_version: Optional[str]


class K8sNode(K8sNodeBase):
    """K8s节点响应"""
    id: int
    cluster_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== K8s Namespace ====================

class K8sNamespaceBase(BaseModel):
    """K8s命名空间基础Schema"""
    namespace_name: str
    status: str
    pod_count: int = 0
    service_count: int = 0
    deployment_count: int = 0
    configmap_count: int = 0
    secret_count: int = 0
    labels: Optional[Dict[str, str]]


class K8sNamespace(K8sNamespaceBase):
    """K8s命名空间响应"""
    id: int
    cluster_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== K8s Pod ====================

class K8sPodBase(BaseModel):
    """K8s Pod基础Schema"""
    pod_name: str
    namespace: str
    node_name: Optional[str]
    status: str
    ready_containers: int = 0
    total_containers: int = 1
    cpu_request: Optional[str]
    memory_request: Optional[str]
    cpu_limit: Optional[str]
    memory_limit: Optional[str]
    pod_ip: Optional[str]
    host_ip: Optional[str]
    restart_count: int = 0
    labels: Optional[Dict[str, str]]
    start_time: Optional[datetime]


class K8sPod(K8sPodBase):
    """K8s Pod响应"""
    id: int
    cluster_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== K8s 统计信息 ====================

class K8sClusterStats(BaseModel):
    """K8s集群统计"""
    total_clusters: int = Field(..., description="总集群数")
    active_clusters: int = Field(..., description="活跃集群数")
    total_nodes: int = Field(..., description="总节点数")
    total_pods: int = Field(..., description="总Pod数")
    total_namespaces: int = Field(..., description="总命名空间数")
    clusters_by_env: Dict[str, int] = Field(..., description="按环境分组")


class K8sResourceUsage(BaseModel):
    """K8s资源使用情况"""
    cluster_id: int
    cluster_name: str
    total_cpu_capacity: str
    total_memory_capacity: str
    cpu_usage_percent: float
    memory_usage_percent: float
    pod_usage_percent: float


class K8sClusterDetail(BaseModel):
    """K8s集群详情"""
    cluster: K8sCluster
    nodes: List[K8sNode]
    namespaces: List[K8sNamespace]
    resource_usage: K8sResourceUsage

