@echo off
REM 运维自动化平台 - Docker快速启动脚本 (Windows)
REM 版本: v1.0

echo.
echo =====================================================
echo   Docker 运维自动化平台 - 快速启动
echo =====================================================
echo.

REM 检查Docker是否安装
echo [INFO] 检查Docker环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker未安装，请先安装Docker Desktop
    echo 访问 https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose未安装
    pause
    exit /b 1
)

echo [SUCCESS] Docker环境检查通过
docker --version
docker-compose --version
echo.

REM 启动服务
echo [INFO] 启动服务...
docker-compose up -d --build

if errorlevel 1 (
    echo [ERROR] 服务启动失败
    pause
    exit /b 1
)

echo [SUCCESS] 服务启动中...
echo.
echo [INFO] 等待服务就绪（预计30-60秒）...
timeout /t 10 /nobreak >nul

REM 显示状态
echo.
echo [INFO] 服务状态:
docker-compose ps

REM 显示访问信息
echo.
echo =====================================================
echo   部署完成！
echo =====================================================
echo.
echo   前端页面:  http://localhost
echo   后端API:   http://localhost:8000
echo   API文档:   http://localhost:8000/docs
echo.
echo   默认账号:  admin
echo   默认密码:  admin123
echo.
echo =====================================================
echo.
echo 常用命令:
echo   - 查看日志:    docker-compose logs -f
echo   - 停止服务:    docker-compose stop
echo   - 重启服务:    docker-compose restart
echo   - 完全删除:    docker-compose down
echo.

pause

