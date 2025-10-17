#!/bin/bash

# Docker镜像加速器配置脚本
# 适用于国内服务器

echo "================================"
echo "  Docker镜像加速器配置"
echo "================================"
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "请使用root权限运行此脚本: sudo ./docker-mirror-setup.sh"
    exit 1
fi

# 备份原配置
if [ -f /etc/docker/daemon.json ]; then
    echo "[INFO] 备份现有配置..."
    cp /etc/docker/daemon.json /etc/docker/daemon.json.backup
fi

# 创建Docker配置目录
mkdir -p /etc/docker

# 写入镜像加速配置
echo "[INFO] 配置国内镜像加速器..."
cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://registry.docker-cn.com"
  ],
  "insecure-registries": [],
  "debug": false,
  "experimental": false,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

echo "[SUCCESS] 配置文件已更新"
cat /etc/docker/daemon.json

# 重启Docker服务
echo ""
echo "[INFO] 重启Docker服务..."
systemctl daemon-reload
systemctl restart docker

# 检查状态
if systemctl is-active --quiet docker; then
    echo "[SUCCESS] Docker服务重启成功"
    docker info | grep -A 5 "Registry Mirrors"
else
    echo "[ERROR] Docker服务重启失败"
    exit 1
fi

echo ""
echo "================================"
echo "  配置完成！"
echo "================================"
echo ""
echo "现在可以运行："
echo "  docker-compose up -d"
echo ""

