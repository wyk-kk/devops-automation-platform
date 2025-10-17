# K8s集群接入故障排除指南

## 📋 概述

本文档帮助你解决Kubernetes集群接入平台后无法连接或状态同步失败的问题。

---

## 🔍 快速诊断工具

### 使用内置诊断功能

平台提供了强大的诊断工具，可以自动检测常见问题：

**API接口**:
```http
POST /api/k8s/clusters/{cluster_id}/diagnose
```

**前端操作**:
1. 进入"资源管理"页面
2. 找到你的K8s集群
3. 点击"诊断"按钮
4. 查看详细的检测结果和建议

诊断工具会自动检查：
- ✅ API Server地址格式
- ✅ 网络连通性
- ✅ 认证配置完整性
- ✅ K8s API连接测试
- ✅ 集群版本信息
- ✅ 资源统计

---

## 🛠️ 常见问题和解决方案

### 问题1: 状态显示"未连接" (disconnected)

**症状**:
- 集群状态显示为"disconnected"或"未连接"
- 无法同步集群资源
- 错误信息提示连接失败

**可能原因及解决方案**:

#### 原因1.1: API Server地址错误

**检查**:
```bash
# 确认你的API Server地址
kubectl cluster-info

# 应该类似于:
# Kubernetes control plane is running at https://192.168.1.100:6443
```

**正确格式**:
- ✅ `https://192.168.1.100:6443`
- ✅ `https://cluster.example.com:6443`
- ❌ `192.168.1.100:6443` (缺少协议)
- ❌ `https://192.168.1.100` (缺少端口)

#### 原因1.2: 网络不通

**检查网络连通性**:
```bash
# 测试是否可以访问API Server
curl -k https://你的API地址:6443

# 如果返回类似以下内容说明网络通：
# {
#   "kind": "Status",
#   "message": "Unauthorized"
# }
```

**常见原因**:
- 防火墙阻止
- 安全组规则限制
- API Server未对外暴露
- VPN/内网访问限制

**解决方法**:
```bash
# 方法1: 开放防火墙端口（以6443为例）
sudo firewall-cmd --permanent --add-port=6443/tcp
sudo firewall-cmd --reload

# 方法2: 检查安全组（云服务器）
# 在云服务商控制台添加入站规则：
# - 端口: 6443
# - 协议: TCP
# - 来源: 你的平台服务器IP

# 方法3: 使用kubectl proxy（仅用于测试）
kubectl proxy --address=0.0.0.0 --port=8001 --accept-hosts='.*'
# 然后使用: http://your-ip:8001 作为API Server地址
```

#### 原因1.3: 认证配置错误

根据你的认证方式，选择对应的解决方案：

---

### 认证方式1: Token认证（推荐）

**获取有效的Token**:

```bash
# 方法1: 创建ServiceAccount并获取Token
kubectl create serviceaccount devops-admin -n kube-system

# 创建ClusterRoleBinding
kubectl create clusterrolebinding devops-admin-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:devops-admin

# 获取Token（Kubernetes 1.24+）
kubectl create token devops-admin -n kube-system --duration=87600h

# 获取Token（Kubernetes 1.23-）
SECRET_NAME=$(kubectl get serviceaccount devops-admin -n kube-system -o jsonpath='{.secrets[0].name}')
kubectl get secret $SECRET_NAME -n kube-system -o jsonpath='{.data.token}' | base64 -d

# 获取CA证书（可选但推荐）
kubectl get secret $SECRET_NAME -n kube-system -o jsonpath='{.data.ca\.crt}' | base64 -d > ca.crt
```

**配置说明**:
- **API Server**: `https://your-k8s-api:6443`
- **认证方式**: Token
- **Token**: 粘贴上面获取的完整Token
- **CA证书**: 粘贴ca.crt的内容（可选，不填会跳过SSL验证）

---

### 认证方式2: Kubeconfig认证

**获取Kubeconfig**:

```bash
# 方法1: 使用现有的kubeconfig
cat ~/.kube/config

# 方法2: 为平台创建专用的kubeconfig
kubectl config view --minify --raw > devops-platform-config.yaml
cat devops-platform-config.yaml
```

**配置说明**:
- **认证方式**: Kubeconfig
- **Kubeconfig内容**: 粘贴完整的YAML内容

**注意事项**:
- 确保kubeconfig中的server地址可以从平台服务器访问
- 如果是内网地址，需要确保网络互通
- 检查kubeconfig中的证书是否过期

---

### 认证方式3: 证书认证

**获取证书文件**:

```bash
# 获取CA证书
kubectl config view --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d > ca.crt

# 获取客户端证书
kubectl config view --raw -o jsonpath='{.users[0].user.client-certificate-data}' | base64 -d > client.crt

# 获取客户端密钥
kubectl config view --raw -o jsonpath='{.users[0].user.client-key-data}' | base64 -d > client.key

# 查看内容
cat ca.crt
cat client.crt
cat client.key
```

**配置说明**:
- **API Server**: `https://your-k8s-api:6443`
- **认证方式**: 证书
- **CA证书**: 粘贴ca.crt的内容
- **客户端证书**: 粘贴client.crt的内容
- **客户端密钥**: 粘贴client.key的内容

---

### 问题2: 认证失败 (401 Unauthorized)

**症状**:
```
错误信息: "认证失败：Token或证书无效"
```

**解决方案**:

#### 2.1 Token过期或无效

```bash
# 重新创建长期有效的Token
kubectl create token devops-admin -n kube-system --duration=87600h

# 或者检查现有Token是否有效
curl -k https://your-api:6443/api/v1/namespaces \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 2.2 证书过期

```bash
# 检查证书有效期
openssl x509 -in client.crt -noout -dates

# 如果过期，需要重新生成证书或使用Token认证
```

---

### 问题3: 权限不足 (403 Forbidden)

**症状**:
```
错误信息: "权限不足：请检查账号权限"
```

**解决方案**:

```bash
# 检查当前权限
kubectl auth can-i list namespaces --as=system:serviceaccount:kube-system:devops-admin

# 授予cluster-admin权限
kubectl create clusterrolebinding devops-admin-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:devops-admin

# 或者创建自定义角色（最小权限原则）
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind:ClusterRole
metadata:
  name: devops-platform-role
rules:
- apiGroups: [""]
  resources: ["namespaces", "nodes", "pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets"]
  verbs: ["get", "list", "watch", "update", "patch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["delete"]
EOF

# 绑定角色
kubectl create clusterrolebinding devops-platform-binding \
  --clusterrole=devops-platform-role \
  --serviceaccount=kube-system:devops-admin
```

---

### 问题4: 资源无法同步

**症状**:
- 集群状态显示"已连接"
- 但节点数、Pod数等显示为0
- 或者数据一直不更新

**解决方案**:

#### 4.1 手动触发同步

**通过API**:
```bash
curl -X POST "http://your-platform:8000/api/k8s/clusters/{cluster_id}/sync" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**通过前端**:
1. 进入"资源管理"页面
2. 找到对应集群
3. 点击"同步"按钮

#### 4.2 检查同步日志

```bash
# 查看后端日志
tail -f /path/to/backend/logs/app.log

# 或者如果使用Docker
docker logs -f devops-backend

# 查找相关错误信息
grep "同步集群资源失败" logs/app.log
```

#### 4.3 权限问题导致

确保ServiceAccount有以下权限：
- list/get namespaces
- list/get nodes
- list/get pods (所有命名空间)
- list/get deployments (所有命名空间)

---

### 问题5: SSL证书验证失败

**症状**:
```
错误信息: "certificate verify failed" 或类似SSL错误
```

**解决方案**:

#### 方案1: 提供CA证书（推荐）

```bash
# 获取K8s集群的CA证书
kubectl config view --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d > ca.crt

# 将ca.crt的内容粘贴到平台的"CA证书"字段
cat ca.crt
```

#### 方案2: 跳过SSL验证（仅测试环境）

在使用Token认证时，不填写CA证书字段，平台会自动跳过SSL验证。

**注意**: 生产环境不推荐使用此方法！

---

## 📊 完整的接入检查清单

在添加K8s集群前，请确认以下所有项目：

### 1. 网络连通性
- [ ] 平台服务器可以访问K8s API Server的IP和端口
- [ ] 防火墙/安全组已开放相应端口
- [ ] 使用curl或telnet测试连通性

### 2. API Server地址
- [ ] 地址格式正确：`https://ip:port`
- [ ] 端口号正确（通常是6443）
- [ ] 协议是https（不是http）

### 3. 认证信息
- [ ] 选择了正确的认证方式
- [ ] Token/证书/Kubeconfig内容完整
- [ ] 认证信息未过期
- [ ] CA证书已提供（或确认可以跳过验证）

### 4. 权限配置
- [ ] ServiceAccount已创建
- [ ] ClusterRoleBinding已配置
- [ ] 至少有list namespace的权限
- [ ] 建议有cluster-admin或自定义足够的权限

### 5. 测试验证
- [ ] 使用诊断工具检测
- [ ] 手动触发一次同步
- [ ] 查看是否能正常获取节点、Pod等资源

---

## 🔧 高级故障排除

### 查看详细的后端日志

```bash
# 如果使用Docker部署
docker logs -f devops-backend | grep -i k8s

# 如果直接运行
tail -f logs/app.log | grep -i "集群"
```

### 使用kubectl命令行测试

```bash
# 测试Token是否有效
export KUBE_TOKEN="your-token-here"
curl -k https://your-api:6443/api/v1/namespaces \
  -H "Authorization: Bearer $KUBE_TOKEN"

# 测试权限
kubectl auth can-i list pods --all-namespaces \
  --as=system:serviceaccount:kube-system:devops-admin

# 测试证书
curl --cert client.crt --key client.key --cacert ca.crt \
  https://your-api:6443/api/v1/namespaces
```

### 抓包分析（高级）

```bash
# 使用tcpdump抓包分析
sudo tcpdump -i any port 6443 -w k8s-api.pcap

# 使用Wireshark打开k8s-api.pcap分析
```

---

## 📞 获取帮助

如果以上方法都无法解决问题，请收集以下信息：

1. **集群信息**:
   - Kubernetes版本：`kubectl version`
   - 集群部署方式（kubeadm/k3s/云服务商托管等）

2. **错误信息**:
   - 诊断工具的完整输出
   - 后端日志中的错误信息
   - 浏览器控制台的错误（F12）

3. **配置信息**（脱敏后）:
   - API Server地址格式
   - 认证方式
   - 网络拓扑（是否跨网络）

4. **测试结果**:
   - curl测试API Server的结果
   - kubectl命令的输出

---

## 📚 参考文档

### Kubernetes官方文档
- [访问集群](https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/)
- [认证](https://kubernetes.io/docs/reference/access-authn-authz/authentication/)
- [授权](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

### 平台相关文档
- [完整项目文档](./完整项目文档.md)
- [API文档](http://your-platform:8000/docs)

---

## ✅ 成功接入示例

### 示例1: 使用Token认证（推荐）

```bash
# 1. 创建ServiceAccount
kubectl create serviceaccount devops-admin -n kube-system

# 2. 授权
kubectl create clusterrolebinding devops-admin-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:devops-admin

# 3. 获取Token（K8s 1.24+）
TOKEN=$(kubectl create token devops-admin -n kube-system --duration=87600h)
echo $TOKEN

# 4. 在平台配置
# API Server: https://192.168.1.100:6443
# 认证方式: Token
# Token: 粘贴上面的TOKEN
# CA证书: （可选）

# 5. 测试连接 -> 同步资源 -> 完成！
```

### 示例2: 使用Kubeconfig

```bash
# 1. 导出kubeconfig
kubectl config view --minify --raw > devops-config.yaml

# 2. 确保server地址可访问
# 编辑devops-config.yaml，修改server地址为外部可访问的地址

# 3. 在平台配置
# 认证方式: Kubeconfig
# Kubeconfig内容: 粘贴完整的YAML

# 4. 测试连接 -> 同步资源 -> 完成！
```

---

**版本**: v1.0  
**更新日期**: 2025-01-15  
**适用平台版本**: v3.1+

