#!/bin/bash

# ngrok快速部署脚本
# 让任何人都能通过公网访问你的应用

echo "🌐 ngrok公网部署 - 医疗报销智能助手"
echo "====================================="

# 设置API密钥
export DASHSCOPE_API_KEY="sk-2ea7b3f8fb7742828ff836eed6050f19"

# 检查ngrok是否安装
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok未安装"
    echo ""
    echo "📥 安装ngrok:"
    echo "  macOS: brew install ngrok/ngrok/ngrok"
    echo "  Linux: wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
    echo "  Windows: 下载 https://ngrok.com/download"
    echo ""
    echo "🔑 注册ngrok账号获取token: https://ngrok.com"
    echo "   ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

# 检查Python依赖
echo "🔍 检查Python依赖..."
python3 -c "import fastapi, uvicorn, dashscope" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装依赖..."
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi uvicorn dashscope python-dotenv
fi

# 创建环境配置
echo "⚙️ 配置环境变量..."
cat > .env << EOF
DASHSCOPE_API_KEY=sk-2ea7b3f8fb7742828ff836eed6050f19
DEBUG=false
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO
EOF

echo ""
echo "🚀 启动应用服务..."
python3 main.py &
APP_PID=$!

# 等待应用启动
sleep 3

echo "🌐 启动ngrok公网隧道..."
echo ""
echo "📱 公网访问地址将在下面显示"
echo "💡 分享这个地址给其他人使用"
echo "⚠️  按 Ctrl+C 停止服务"
echo ""

# 启动ngrok
ngrok http 8080

# 清理进程
echo ""
echo "🛑 正在停止服务..."
kill $APP_PID 2>/dev/null
echo "✅ 服务已停止"

