# 🐳 Docker部署指南

## 📋 简介

本项目支持完整的Docker容器化部署，只需一条命令即可在任何设备上运行！

### ✨ Docker部署的优势

- ✅ **一键部署** - 无需配置Python、Node.js环境
- ✅ **跨平台** - Windows、macOS、Linux都能运行
- ✅ **环境隔离** - 不会与系统环境冲突
- ✅ **易于迁移** - 换设备时直接复制项目即可
- ✅ **快速演示** - 答辩时快速启动展示
- ✅ **自动重启** - 服务崩溃自动恢复

---

## 🚀 快速开始（3步搞定）

### 前提条件

确保你的电脑已安装Docker：

```bash
# 检查Docker是否已安装
docker --version
docker-compose --version
```

如果未安装，请访问：
- **Windows/Mac**: https://www.docker.com/products/docker-desktop
- **Linux**: https://docs.docker.com/engine/install/

### 第一步：克隆项目（或复制项目文件夹）

```bash
git clone https://github.com/wyk-kk/devops-automation-platform.git
cd devops-automation-platform
```

### 第二步：一键启动

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

### 第三步：访问系统

等待约1-2分钟后，访问：

- **前端页面**: http://localhost
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

**默认账号**:
- 用户名: `admin`
- 密码: `admin123`

🎉 **完成！就是这么简单！**

---

## 📦 详细说明

### 项目结构

```
devops-automation-platform/
├── docker-compose.yml          # Docker编排配置
├── backend/
│   ├── Dockerfile             # 后端镜像配置
│   ├── .dockerignore          # Docker忽略文件
│   └── requirements.txt       # Python依赖
├── frontend/
│   ├── Dockerfile             # 前端镜像配置
│   ├── .dockerignore          # Docker忽略文件
│   ├── nginx.conf             # Nginx配置
│   └── package.json           # Node依赖
└── DOCKER_DEPLOYMENT.md       # 本文档
```

### Docker架构

```
┌─────────────────────────────────────────────┐
│           Docker Network (devops-network)   │
│                                             │
│  ┌──────────────┐      ┌──────────────┐   │
│  │   Frontend   │      │   Backend    │   │
│  │   (Nginx)    │─────▶│  (FastAPI)   │   │
│  │   Port: 80   │      │  Port: 8000  │   │
│  └──────────────┘      └──────────────┘   │
│                              │              │
│                              ▼              │
│                         ┌──────────┐        │
│                         │  SQLite  │        │
│                         │   (卷)   │        │
│                         └──────────┘        │
└─────────────────────────────────────────────┘
         │                      │
         ▼                      ▼
    http://localhost    http://localhost:8000
```

---

## 🛠️ 常用命令

### 启动服务

```bash
# 后台启动
docker-compose up -d

# 前台启动（查看日志）
docker-compose up

# 重新构建并启动
docker-compose up -d --build
```

### 停止服务

```bash
# 停止服务（保留容器）
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器、卷、镜像
docker-compose down -v --rmi all
```

### 查看状态

```bash
# 查看运行中的容器
docker-compose ps

# 查看日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看特定服务的日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 在容器内执行命令
docker-compose exec backend python -c "print('Hello')"
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart backend
docker-compose restart frontend
```

---

## 🔧 高级配置

### 修改端口

编辑 `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 将前端端口改为8080
  
  backend:
    ports:
      - "9000:8000"  # 将后端端口改为9000
```

### 使用MySQL而不是SQLite

1. 在 `docker-compose.yml` 中添加MySQL服务：

```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: devops-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: devops_db
      MYSQL_USER: devops
      MYSQL_PASSWORD: devops123
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - devops-network

volumes:
  mysql-data:
```

2. 修改后端环境变量：

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=mysql+pymysql://devops:devops123@mysql:3306/devops_db
```

### 环境变量配置

创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=sqlite:///./data/devops.db

# JWT密钥
SECRET_KEY=your-secret-key-here

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

然后在 `docker-compose.yml` 中使用：

```yaml
services:
  backend:
    env_file:
      - .env
```

### 数据持久化

默认配置已经持久化了以下数据：

```yaml
volumes:
  # 数据库文件
  - ./backend/data:/app/data
  
  # 日志文件
  - ./backend/logs:/app/logs
```

数据保存在：
- `backend/data/` - 数据库文件
- `backend/logs/` - 应用日志

---

## 📱 换设备部署

### 方法1：复制项目文件夹

```bash
# 在旧设备上打包
cd /path/to/devops-automation-platform
tar -czf devops-platform.tar.gz .

# 复制到新设备（使用U盘、网盘等）

# 在新设备上解压
tar -xzf devops-platform.tar.gz
cd devops-automation-platform

# 启动
docker-compose up -d
```

### 方法2：使用Git

```bash
# 在新设备上
git clone https://github.com/wyk-kk/devops-automation-platform.git
cd devops-automation-platform
docker-compose up -d
```

### 方法3：导出Docker镜像（无需重新构建）

```bash
# 在旧设备上导出镜像
docker save -o devops-images.tar \
  devops-automation-platform-backend:latest \
  devops-automation-platform-frontend:latest

# 复制 devops-images.tar 到新设备

# 在新设备上导入镜像
docker load -i devops-images.tar

# 启动
docker-compose up -d
```

---

## 🎯 答辩演示场景

### 场景1：快速启动展示

```bash
# 到达答辩教室
cd devops-automation-platform

# 一键启动（30秒内完成）
docker-compose up -d

# 等待服务就绪
docker-compose logs -f

# 看到 "Application startup complete" 后
# 访问 http://localhost 演示
```

### 场景2：实时监控演示

```bash
# 在演示时实时查看日志
docker-compose logs -f backend

# 展示容器状态
docker-compose ps

# 展示健康检查
docker inspect devops-backend | grep Health -A 10
```

### 场景3：故障恢复演示

```bash
# 模拟服务崩溃
docker-compose stop backend

# 展示自动重启（设置了restart: unless-stopped）
docker-compose start backend

# 查看恢复过程
docker-compose logs -f backend
```

---

## 🐛 故障排除

### 问题1：端口被占用

**错误**: `Error: port is already allocated`

**解决**:
```bash
# 查看端口占用
lsof -i :80
lsof -i :8000

# 修改docker-compose.yml中的端口
# 或停止占用端口的程序
```

### 问题2：构建失败

**错误**: `ERROR: failed to solve`

**解决**:
```bash
# 清理Docker缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 问题3：容器无法启动

**解决**:
```bash
# 查看详细日志
docker-compose logs backend
docker-compose logs frontend

# 检查容器状态
docker-compose ps

# 重启容器
docker-compose restart
```

### 问题4：前端无法访问后端

**解决**:
```bash
# 检查网络连接
docker network inspect devops-automation-platform_devops-network

# 测试后端连通性
docker-compose exec frontend wget -O- http://backend:8000/api/health

# 重新创建网络
docker-compose down
docker-compose up -d
```

### 问题5：数据库文件丢失

**解决**:
```bash
# 检查数据卷
docker volume ls
docker volume inspect devops-automation-platform_backend-data

# 备份数据
cp -r backend/data backend/data_backup

# 恢复数据
cp -r backend/data_backup/* backend/data/
```

---

## 📊 性能优化

### 减小镜像体积

后端镜像：
```dockerfile
# 使用slim版本而不是完整版本
FROM python:3.13-slim

# 多阶段构建（已实现）
# 清理缓存
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
```

前端镜像：
```dockerfile
# 使用alpine版本
FROM node:18-alpine AS builder
FROM nginx:alpine
```

当前镜像大小：
- 后端: ~400MB
- 前端: ~25MB

### 加速构建

```bash
# 使用国内镜像源
# 已在Dockerfile中配置
# - Python: 清华源
# - Node: 淘宝源

# 使用Docker层缓存
# 先复制依赖文件，后复制代码
```

---

## 🔒 安全建议

### 生产环境部署

1. **修改默认密码**
   ```bash
   # 进入容器修改管理员密码
   docker-compose exec backend python -c "
   from app.core.database import SessionLocal
   from app.models.user import User
   from app.core.security import get_password_hash
   
   db = SessionLocal()
   admin = db.query(User).filter(User.username == 'admin').first()
   admin.hashed_password = get_password_hash('new-secure-password')
   db.commit()
   "
   ```

2. **使用HTTPS**
   ```yaml
   # docker-compose.yml
   services:
     frontend:
       ports:
         - "443:443"
       volumes:
         - ./ssl:/etc/nginx/ssl
   ```

3. **限制访问**
   ```yaml
   # docker-compose.yml
   services:
     backend:
       ports:
         - "127.0.0.1:8000:8000"  # 只允许本地访问
   ```

4. **定期备份**
   ```bash
   # 创建备份脚本
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   tar -czf backup_$DATE.tar.gz backend/data/
   ```

---

## 📈 监控和日志

### 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看特定容器
docker stats devops-backend devops-frontend
```

### 日志管理

```bash
# 限制日志大小（在docker-compose.yml中）
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 健康检查

```bash
# 查看健康状态
docker-compose ps

# 查看详细健康检查
docker inspect devops-backend | grep Health -A 20
```

---

## 🎓 适合毕业答辩的优势

### 1. 演示便利性
- ✅ 一键启动，30秒内完成
- ✅ 无需担心环境配置问题
- ✅ 可以在任何电脑上演示

### 2. 技术加分项
- ✅ 展示Docker容器化能力
- ✅ 展示DevOps理念
- ✅ 展示微服务架构思维

### 3. 稳定性保障
- ✅ 自动重启机制
- ✅ 健康检查
- ✅ 环境隔离

### 4. 答辩PPT要点

可以在PPT中添加：

```
技术亮点 - 容器化部署

🐳 Docker容器化
- 前后端分离部署
- 一键启动，环境隔离
- 支持快速迁移

📊 架构优势
- 微服务架构设计
- 自动健康检查
- 服务自动恢复

🚀 部署便利性
- docker-compose一键部署
- 支持快速扩展
- 易于维护升级
```

---

## 📚 相关文档

- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [完整项目文档](./完整项目文档.md)
- [部署指南](./docs/DEPLOYMENT.md)

---

## 💡 常见问题

**Q: Docker占用空间太大怎么办？**
A: 定期清理：`docker system prune -a`

**Q: 可以同时运行多个实例吗？**
A: 可以，修改端口号即可：
```bash
# 第一个实例
docker-compose up -d

# 第二个实例（修改端口）
# 编辑docker-compose.yml，改为8080和9000端口
docker-compose -p devops2 up -d
```

**Q: 如何更新代码？**
A: 
```bash
git pull
docker-compose down
docker-compose up -d --build
```

**Q: 数据会丢失吗？**
A: 不会，数据保存在 `backend/data/` 目录中，不会随容器删除而丢失。

---

**版本**: v1.0  
**更新日期**: 2025-01-15  
**适用项目版本**: v3.1  
**Docker版本要求**: 20.10+  
**Docker Compose版本要求**: 2.0+

