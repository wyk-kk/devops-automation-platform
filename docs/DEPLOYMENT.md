# 部署文档

## 环境要求

### 后端
- Python 3.8+
- pip

### 前端
- Node.js 16+
- npm 或 yarn

### 可选
- MySQL 5.7+ (生产环境推荐)
- Nginx (生产环境反向代理)

## 开发环境部署

### 1. 后端部署

```bash
# 进入后端目录
cd backend

# 创建虚拟环境 (可选但推荐)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp .env.example .env

# 编辑配置文件（可选）
vim .env

# 启动服务
python main.py
```

后端服务将在 http://localhost:8000 启动

访问 API 文档: http://localhost:8000/docs

### 2. 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 http://localhost:5173 启动

## 生产环境部署

### 1. 后端生产部署

#### 使用 Uvicorn + Gunicorn

```bash
# 安装 gunicorn
pip install gunicorn

# 启动服务（4个worker进程）
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 使用 Systemd 管理服务

创建服务文件 `/etc/systemd/system/devops-backend.service`:

```ini
[Unit]
Description=DevOps Platform Backend
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/project_2/backend
Environment="PATH=/path/to/project_2/backend/venv/bin"
ExecStart=/path/to/project_2/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable devops-backend
sudo systemctl start devops-backend
sudo systemctl status devops-backend
```

### 2. 前端生产部署

```bash
# 构建生产版本
npm run build

# 构建产物位于 dist/ 目录
```

#### 使用 Nginx 部署

Nginx 配置示例 `/etc/nginx/sites-available/devops`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/project_2/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API 文档
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

启用站点:

```bash
sudo ln -s /etc/nginx/sites-available/devops /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. 使用 Docker 部署

#### 后端 Dockerfile

创建 `backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端 Dockerfile

创建 `frontend/Dockerfile`:

```dockerfile
FROM node:16 as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./devops.db
    volumes:
      - ./backend:/app
      - backend_data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  backend_data:
```

启动服务:

```bash
docker-compose up -d
```

## 数据库配置

### 使用 MySQL

1. 创建数据库:

```sql
CREATE DATABASE devops CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'devops'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON devops.* TO 'devops'@'localhost';
FLUSH PRIVILEGES;
```

2. 修改配置文件 `.env`:

```env
DATABASE_URL=mysql+pymysql://devops:your_password@localhost/devops
```

## 安全建议

### 1. 修改默认密码

首次部署后立即修改默认管理员密码

### 2. 使用 HTTPS

在生产环境中使用 Let's Encrypt 配置 SSL:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. 配置防火墙

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 4. 定期备份

备份数据库:

```bash
# SQLite
cp backend/devops.db /backup/devops_$(date +%Y%m%d).db

# MySQL
mysqldump -u devops -p devops > /backup/devops_$(date +%Y%m%d).sql
```

### 5. 更新密钥

修改 `.env` 中的 `SECRET_KEY`:

```bash
# 生成新的密钥
python -c "import secrets; print(secrets.token_hex(32))"
```

## 性能优化

1. **使用 Redis 缓存** (可选)
2. **配置 Nginx 缓存静态资源**
3. **使用 CDN 加速前端资源**
4. **数据库索引优化**
5. **启用 Gzip 压缩**

## 监控和日志

### 日志配置

后端日志配置:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/devops/backend.log'),
        logging.StreamHandler()
    ]
)
```

### 监控服务状态

```bash
# 检查后端服务
systemctl status devops-backend

# 查看日志
journalctl -u devops-backend -f

# 检查 Nginx
systemctl status nginx
tail -f /var/log/nginx/access.log
```

## 故障排查

### 后端无法启动

1. 检查Python版本
2. 检查依赖是否安装完整
3. 检查数据库连接
4. 查看日志文件

### 前端无法访问

1. 检查Nginx配置
2. 检查构建产物是否存在
3. 检查API代理配置
4. 查看浏览器控制台错误

### SSH连接失败

1. 检查服务器防火墙
2. 检查SSH密钥权限
3. 检查服务器凭证是否正确
4. 检查网络连通性

## 升级指南

### 后端升级

```bash
cd backend
git pull
pip install -r requirements.txt --upgrade
systemctl restart devops-backend
```

### 前端升级

```bash
cd frontend
git pull
npm install
npm run build
# 重新部署 dist 目录
```

## 技术支持

如遇到问题，请查看:
- API文档: http://localhost:8000/docs
- 项目README: README.md
- 日志文件: /var/log/devops/

