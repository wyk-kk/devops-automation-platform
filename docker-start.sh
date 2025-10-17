#!/bin/bash

# 运维自动化平台 - Docker快速启动脚本
# 版本: v1.0

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    print_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        echo "访问 https://www.docker.com/products/docker-desktop 下载安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装"
        exit 1
    fi
    
    print_success "Docker环境检查通过"
    docker --version
    docker-compose --version
}

# 检查端口占用
check_ports() {
    print_info "检查端口占用..."
    
    if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口80已被占用，请修改docker-compose.yml中的端口配置"
        lsof -i :80
    fi
    
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口8000已被占用，请修改docker-compose.yml中的端口配置"
        lsof -i :8000
    fi
}

# 启动服务
start_services() {
    print_info "启动服务..."
    
    # 禁用BuildKit以提高兼容性
    export DOCKER_BUILDKIT=0
    export COMPOSE_DOCKER_CLI_BUILD=0
    
    # 构建并启动
    docker-compose up -d --build
    
    print_success "服务启动中..."
    echo ""
    print_info "等待服务就绪（预计30-60秒）..."
    
    # 等待服务启动
    sleep 10
    
    # 显示日志
    print_info "服务日志："
    docker-compose logs --tail=20
}

# 检查服务状态
check_status() {
    echo ""
    print_info "检查服务状态..."
    docker-compose ps
}

# 显示访问信息
show_access_info() {
    echo ""
    print_success "✨ 部署完成！"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  🌐 前端页面:  http://localhost"
    echo "  🚀 后端API:   http://localhost:8000"
    echo "  📚 API文档:   http://localhost:8000/docs"
    echo ""
    echo "  👤 默认账号:  admin"
    echo "  🔑 默认密码:  admin123"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    print_info "常用命令："
    echo "  - 查看日志:    docker-compose logs -f"
    echo "  - 停止服务:    docker-compose stop"
    echo "  - 重启服务:    docker-compose restart"
    echo "  - 完全删除:    docker-compose down"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🐳 运维自动化平台 - Docker 快速启动"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    check_docker
    check_ports
    start_services
    check_status
    show_access_info
    
    print_info "提示: 按 Ctrl+C 不会停止服务，使用 docker-compose stop 停止"
}

# 执行主函数
main

