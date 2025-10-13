#!/bin/bash
# 运维自动化平台后端启动脚本

echo "🚀 正在启动运维自动化平台后端..."
echo ""

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  警告: 未检测到虚拟环境"
    echo "建议在虚拟环境中运行"
    echo ""
fi

# 显示Python版本
echo "📌 Python版本: $(python --version)"
echo ""

# 启动服务
echo "✨ 启动FastAPI服务..."
echo "📡 后端地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python main.py

