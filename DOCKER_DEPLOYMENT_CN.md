# 🐳 Docker部署指南 - 国内服务器版

## 📋 问题说明

如果你在国内服务器上部署时遇到以下错误：

```
Get https://registry-1.docker.io/v2/: dial tcp: i/o timeout
```

这是因为国内网络访问Docker Hub速度慢或超时。本文档提供完整的解决方案。

---

## 🚀 快速解决方案（3步）

### 第一步：配置Docker镜像加速器

在服务器上执行：

```bash
# 创建Docker配置目录
sudo mkdir -p /etc/docker

# 创建配置文件
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://registry.docker-cn.com"
  ]
}
EOF

# 重启Docker服务
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证配置
docker info | grep -A 5 "Registry Mirrors"
```

### 第二步：重新拉取镜像

```bash
# 清理之前失败的镜像
docker system prune -a -f

# 重新启动
cd /path/to/devops-automation-platform
docker-compose up -d
```

### 第三步：等待构建完成

首次构建大约需要5-10分钟，请耐心等待。

---

## 🔧 详细配置说明

### 方法1：使用自动配置脚本

在项目中提供了自动配置脚本：

```bash
# 赋予执行权限
chmod +x docker-mirror-setup.sh

# 执行配置（需要root权限）
sudo ./docker-mirror-setup.sh
```

### 方法2：手动配置各个镜像源

#### 2.1 阿里云镜像加速

```bash
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://YOUR_ID.mirror.aliyuncs.com"]
}
EOF
```

> 注意：需要在阿里云控制台获取专属加速地址

#### 2.2 腾讯云镜像加速

```bash
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://mirror.ccs.tencentyun.com"]
}
EOF
```

#### 2.3 网易云镜像加速

```bash
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://hub-mirror.c.163.com"]
}
EOF
```

---

## 📦 已优化的Dockerfile

项目的Dockerfile已经做了以下优化：

### 后端Dockerfile优化
- ✅ APT源已配置为阿里云镜像
- ✅ pip源已配置为清华镜像
- ✅ 减少了构建时间

### 前端Dockerfile优化
- ✅ npm源已配置为淘宝镜像
- ✅ 使用alpine精简镜像
- ✅ 多阶段构建减小体积

---

## 🌐 国内常用镜像源列表

### Docker镜像源
```
中科大: https://docker.mirrors.ustc.edu.cn
网易: https://hub-mirror.c.163.com
百度云: https://mirror.baidubce.com
Docker中国: https://registry.docker-cn.com
```

### Python pip源
```
清华: https://pypi.tuna.tsinghua.edu.cn/simple
阿里云: https://mirrors.aliyun.com/pypi/simple/
中科大: https://pypi.mirrors.ustc.edu.cn/simple/
豆瓣: https://pypi.douban.com/simple/
```

### npm源
```
淘宝: https://registry.npmmirror.com
华为云: https://repo.huaweicloud.com/repository/npm/
腾讯云: https://mirrors.cloud.tencent.com/npm/
```

---

## 🐛 常见问题排查

### 问题1：timeout错误

**症状**：
```
dial tcp xxx.xxx.xxx.xxx:443: i/o timeout
```

**解决**：
1. 配置Docker镜像加速器（见上文）
2. 检查服务器防火墙设置
3. 检查服务器DNS配置

```bash
# 测试网络连通性
ping -c 3 docker.mirrors.ustc.edu.cn

# 测试HTTPS连接
curl -I https://docker.mirrors.ustc.edu.cn
```

### 问题2：镜像拉取速度慢

**解决**：
1. 尝试更换不同的镜像源
2. 使用国内云服务商的服务器
3. 考虑使用代理

### 问题3：镜像拉取失败

**症状**：
```
manifest unknown
```

**解决**：
```bash
# 清理Docker缓存
docker system prune -a -f

# 手动拉取基础镜像
docker pull python:3.13-slim
docker pull node:18-alpine
docker pull nginx:alpine

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 问题4：构建卡在某个步骤

**解决**：
```bash
# 查看详细日志
docker-compose build --progress=plain --no-cache

# 如果是pip或npm安装卡住
# 检查Dockerfile中的镜像源配置
```

---

## 📊 构建进度说明

正常构建过程：

```
Step 1/12 : FROM python:3.13-slim
 ---> Pulling from library/python
 ---> [进度条] 

Step 2/12 : WORKDIR /app
 ---> Running in xxx
 ---> [成功]

... (中间步骤)

Step 12/12 : CMD ["python", "main.py"]
 ---> [成功]

Successfully built xxxxx
```

**预计时间**：
- 首次构建：5-10分钟
- 后续构建：1-3分钟（有缓存）

---

## 🎯 完整部署流程（国内服务器）

### 1. 环境准备

```bash
# 更新系统
sudo yum update -y  # CentOS/RHEL
# 或
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian

# 安装Docker
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

# 安装Docker Compose
sudo curl -L "https://get.daocloud.io/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 配置镜像加速

```bash
# 自动配置（推荐）
sudo ./docker-mirror-setup.sh

# 或手动配置
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF
sudo systemctl restart docker
```

### 3. 部署应用

```bash
# 克隆项目
git clone https://github.com/wyk-kk/devops-automation-platform.git
cd devops-automation-platform

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 4. 验证部署

```bash
# 检查容器状态
docker-compose ps

# 测试后端API
curl http://localhost:8000/api/health

# 测试前端
curl http://localhost
```

---

## 🔐 生产环境建议

### 1. 使用专属镜像加速

推荐使用阿里云容器镜像服务：
1. 登录阿里云控制台
2. 找到"容器镜像服务"
3. 获取专属加速地址
4. 配置到Docker

### 2. 安全配置

```bash
# 修改默认端口
# 编辑 docker-compose.yml
ports:
  - "8080:80"     # 前端
  - "9000:8000"   # 后端

# 配置防火墙
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=9000/tcp
sudo firewall-cmd --reload
```

### 3. 定期备份

```bash
# 备份数据
tar -czf backup-$(date +%Y%m%d).tar.gz backend/data/

# 备份到远程
rsync -avz backend/data/ user@backup-server:/backups/
```

---

## 💡 性能优化建议

### 1. 使用本地镜像仓库（大型部署）

```bash
# 搭建私有镜像仓库
docker run -d -p 5000:5000 --restart=always --name registry registry:2

# 推送镜像到私有仓库
docker tag devops-backend localhost:5000/devops-backend
docker push localhost:5000/devops-backend
```

### 2. 预先拉取镜像

```bash
# 在部署前预先拉取所有需要的镜像
docker pull python:3.13-slim
docker pull node:18-alpine
docker pull nginx:alpine
```

### 3. 使用Docker缓存

```bash
# 构建时使用缓存
docker-compose build

# 不使用缓存（解决问题时）
docker-compose build --no-cache
```

---

## 📞 获取帮助

如果遇到问题：

1. **查看日志**：
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. **检查网络**：
   ```bash
   docker network inspect devops-automation-platform_devops-network
   ```

3. **检查容器**：
   ```bash
   docker inspect devops-backend
   docker inspect devops-frontend
   ```

4. **完全重置**：
   ```bash
   docker-compose down -v
   docker system prune -a -f
   docker-compose up -d --build
   ```

---

## 📚 相关文档

- [Docker部署指南](./DOCKER_DEPLOYMENT.md)
- [完整项目文档](./完整项目文档.md)
- [故障排除](./DOCKER_DEPLOYMENT.md#故障排除)

---

**版本**: v1.0  
**适用于**: 国内服务器（阿里云、腾讯云、华为云等）  
**更新日期**: 2025-01-15

