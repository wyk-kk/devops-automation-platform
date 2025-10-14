"""
Kubernetes客户端工具类
"""
import tempfile
import os
from typing import Optional, List, Dict, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml


class K8sClient:
    """Kubernetes客户端封装"""
    
    def __init__(
        self,
        api_server: Optional[str] = None,
        auth_type: str = "kubeconfig",
        kubeconfig: Optional[str] = None,
        token: Optional[str] = None,
        ca_cert: Optional[str] = None,
        client_cert: Optional[str] = None,
        client_key: Optional[str] = None
    ):
        """
        初始化K8s客户端
        
        Args:
            api_server: API Server地址
            auth_type: 认证方式 (kubeconfig, token, cert)
            kubeconfig: kubeconfig文件内容
            token: Bearer token
            ca_cert: CA证书
            client_cert: 客户端证书
            client_key: 客户端密钥
        """
        self.api_server = api_server
        self.auth_type = auth_type
        self.kubeconfig = kubeconfig
        self.token = token
        self.ca_cert = ca_cert
        self.client_cert = client_cert
        self.client_key = client_key
        
        self._api_client = None
        self._core_v1 = None
        self._apps_v1 = None
    
    def connect(self) -> bool:
        """连接到K8s集群"""
        try:
            configuration = client.Configuration()
            
            if self.auth_type == "kubeconfig" and self.kubeconfig:
                # 使用kubeconfig
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
                    f.write(self.kubeconfig)
                    kubeconfig_path = f.name
                
                try:
                    config.load_kube_config(config_file=kubeconfig_path)
                finally:
                    os.unlink(kubeconfig_path)
            
            elif self.auth_type == "token" and self.token:
                # 使用Token认证
                configuration.host = self.api_server
                configuration.api_key = {"authorization": f"Bearer {self.token}"}
                
                if self.ca_cert:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                        f.write(self.ca_cert)
                        configuration.ssl_ca_cert = f.name
                else:
                    configuration.verify_ssl = False
            
            elif self.auth_type == "cert":
                # 使用证书认证
                configuration.host = self.api_server
                
                if self.ca_cert:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                        f.write(self.ca_cert)
                        configuration.ssl_ca_cert = f.name
                
                if self.client_cert:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                        f.write(self.client_cert)
                        configuration.cert_file = f.name
                
                if self.client_key:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                        f.write(self.client_key)
                        configuration.key_file = f.name
            
            self._api_client = client.ApiClient(configuration)
            self._core_v1 = client.CoreV1Api(self._api_client)
            self._apps_v1 = client.AppsV1Api(self._api_client)
            
            # 测试连接
            self._core_v1.list_namespace(limit=1)
            return True
            
        except Exception as e:
            print(f"K8s连接失败: {str(e)}")
            return False
    
    def get_version(self) -> Optional[str]:
        """获取Kubernetes版本"""
        try:
            version_api = client.VersionApi(self._api_client)
            version_info = version_api.get_code()
            return version_info.git_version
        except Exception as e:
            print(f"获取版本失败: {str(e)}")
            return None
    
    def list_nodes(self) -> List[Dict[str, Any]]:
        """获取节点列表"""
        try:
            nodes = self._core_v1.list_node()
            result = []
            
            for node in nodes.items:
                node_info = {
                    'node_name': node.metadata.name,
                    'node_ip': self._get_node_ip(node),
                    'status': self._get_node_status(node),
                    'roles': self._get_node_roles(node),
                    'cpu_capacity': node.status.capacity.get('cpu', '0'),
                    'memory_capacity': node.status.capacity.get('memory', '0'),
                    'cpu_allocatable': node.status.allocatable.get('cpu', '0'),
                    'memory_allocatable': node.status.allocatable.get('memory', '0'),
                    'pod_capacity': int(node.status.capacity.get('pods', 0)),
                    'os_image': node.status.node_info.os_image,
                    'kernel_version': node.status.node_info.kernel_version,
                    'container_runtime': node.status.node_info.container_runtime_version,
                    'kubelet_version': node.status.node_info.kubelet_version,
                }
                result.append(node_info)
            
            return result
        except Exception as e:
            print(f"获取节点列表失败: {str(e)}")
            return []
    
    def list_namespaces(self) -> List[Dict[str, Any]]:
        """获取命名空间列表"""
        try:
            namespaces = self._core_v1.list_namespace()
            result = []
            
            for ns in namespaces.items:
                ns_info = {
                    'namespace_name': ns.metadata.name,
                    'status': ns.status.phase,
                    'labels': ns.metadata.labels or {},
                }
                result.append(ns_info)
            
            return result
        except Exception as e:
            print(f"获取命名空间列表失败: {str(e)}")
            return []
    
    def list_pods(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取Pod列表"""
        try:
            if namespace:
                pods = self._core_v1.list_namespaced_pod(namespace)
            else:
                pods = self._core_v1.list_pod_for_all_namespaces()
            
            result = []
            for pod in pods.items:
                pod_info = {
                    'pod_name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'node_name': pod.spec.node_name,
                    'status': pod.status.phase,
                    'pod_ip': pod.status.pod_ip,
                    'host_ip': pod.status.host_ip,
                    'labels': pod.metadata.labels or {},
                    'start_time': pod.status.start_time,
                    'ready_containers': self._count_ready_containers(pod),
                    'total_containers': len(pod.spec.containers),
                    'restart_count': self._get_restart_count(pod),
                }
                result.append(pod_info)
            
            return result
        except Exception as e:
            print(f"获取Pod列表失败: {str(e)}")
            return []
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """获取集群统计信息"""
        try:
            nodes = self.list_nodes()
            namespaces = self.list_namespaces()
            pods = self.list_pods()
            
            return {
                'node_count': len(nodes),
                'namespace_count': len(namespaces),
                'pod_count': len(pods),
            }
        except Exception as e:
            print(f"获取集群统计失败: {str(e)}")
            return {
                'node_count': 0,
                'namespace_count': 0,
                'pod_count': 0,
            }
    
    def _get_node_ip(self, node) -> str:
        """获取节点IP"""
        if node.status.addresses:
            for addr in node.status.addresses:
                if addr.type == "InternalIP":
                    return addr.address
        return ""
    
    def _get_node_status(self, node) -> str:
        """获取节点状态"""
        if node.status.conditions:
            for condition in node.status.conditions:
                if condition.type == "Ready":
                    return "Ready" if condition.status == "True" else "NotReady"
        return "Unknown"
    
    def _get_node_roles(self, node) -> List[str]:
        """获取节点角色"""
        roles = []
        if node.metadata.labels:
            for key in node.metadata.labels:
                if key.startswith("node-role.kubernetes.io/"):
                    role = key.split("/")[1]
                    roles.append(role)
        return roles or ["worker"]
    
    def _count_ready_containers(self, pod) -> int:
        """统计就绪的容器数"""
        if pod.status.container_statuses:
            return sum(1 for c in pod.status.container_statuses if c.ready)
        return 0
    
    def _get_restart_count(self, pod) -> int:
        """获取重启次数"""
        if pod.status.container_statuses:
            return sum(c.restart_count for c in pod.status.container_statuses)
        return 0
    
    def get_pod_logs(self, namespace: str, pod_name: str, container: Optional[str] = None, tail_lines: int = 100) -> str:
        """获取Pod日志"""
        try:
            logs = self._core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container,
                tail_lines=tail_lines
            )
            return logs
        except Exception as e:
            return f"获取日志失败: {str(e)}"
    
    def delete_pod(self, namespace: str, pod_name: str) -> bool:
        """删除Pod（重启）"""
        try:
            self._core_v1.delete_namespaced_pod(
                name=pod_name,
                namespace=namespace
            )
            return True
        except Exception as e:
            print(f"删除Pod失败: {str(e)}")
            return False
    
    def list_deployments(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取Deployment列表"""
        try:
            if namespace:
                deployments = self._apps_v1.list_namespaced_deployment(namespace)
            else:
                deployments = self._apps_v1.list_deployment_for_all_namespaces()
            
            result = []
            for deploy in deployments.items:
                deploy_info = {
                    'name': deploy.metadata.name,
                    'namespace': deploy.metadata.namespace,
                    'replicas': deploy.spec.replicas,
                    'ready_replicas': deploy.status.ready_replicas or 0,
                    'available_replicas': deploy.status.available_replicas or 0,
                    'labels': deploy.metadata.labels or {},
                    'created_at': deploy.metadata.creation_timestamp,
                }
                result.append(deploy_info)
            
            return result
        except Exception as e:
            print(f"获取Deployment列表失败: {str(e)}")
            return []
    
    def scale_deployment(self, namespace: str, deployment_name: str, replicas: int) -> bool:
        """伸缩Deployment"""
        try:
            # 获取deployment
            deployment = self._apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # 更新副本数
            deployment.spec.replicas = replicas
            
            # 应用更新
            self._apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            return True
        except Exception as e:
            print(f"伸缩Deployment失败: {str(e)}")
            return False
    
    def close(self):
        """关闭连接"""
        if self._api_client:
            self._api_client.rest_client.pool_manager.clear()

