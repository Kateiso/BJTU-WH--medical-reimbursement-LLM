#!/bin/bash

# 医疗报销智能助手 - 快速部署脚本
# 支持多种部署方式：本地、ngrok、Vercel

echo "🏥 医疗报销智能助手 - 快速部署"
echo "=================================="

# 设置API密钥
export DASHSCOPE_API_KEY="sk-2ea7b3f8fb7742828ff836eed6050f19"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi uvicorn pydantic python-multipart dashscope python-dotenv

# 创建环境变量文件
echo "⚙️ 创建环境配置..."
cat > .env << EOF
DASHSCOPE_API_KEY=sk-2ea7b3f8fb7742828ff836eed6050f19
DEBUG=false
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO
EOF

echo ""
echo "🎯 选择部署方式："
echo "1) 本地运行 (localhost:8080)"
echo "2) ngrok公网访问 (需要安装ngrok)"
echo "3) 生成Vercel部署包"
echo ""

read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo "🚀 启动本地服务..."
        echo "📱 访问地址: http://localhost:8080"
        echo "🌐 Web界面: http://localhost:8080/web"
        echo "📚 API文档: http://localhost:8080/docs"
        echo ""
        echo "按 Ctrl+C 停止服务"
        python3 main.py
        ;;
    2)
        echo "🌐 启动ngrok公网访问..."
        
        # 检查ngrok是否安装
        if ! command -v ngrok &> /dev/null; then
            echo "❌ ngrok未安装"
            echo "📥 请先安装ngrok:"
            echo "   macOS: brew install ngrok/ngrok/ngrok"
            echo "   或访问: https://ngrok.com/download"
            exit 1
        fi
        
        echo "🚀 启动应用服务..."
        python3 main.py &
        APP_PID=$!
        
        sleep 3
        
        echo "🌐 启动ngrok隧道..."
        echo "📱 公网访问地址将在下面显示"
        echo "按 Ctrl+C 停止服务"
        
        ngrok http 8080
        
        # 清理进程
        kill $APP_PID 2>/dev/null
        ;;
    3)
        echo "📦 生成Vercel部署包..."
        
        # 创建部署目录
        DEPLOY_DIR="vercel_deploy"
        mkdir -p $DEPLOY_DIR
        
        # 复制必要文件
        cp main.py $DEPLOY_DIR/
        cp -r src/ $DEPLOY_DIR/
        cp requirements_vercel.txt $DEPLOY_DIR/requirements.txt
        cp vercel.json $DEPLOY_DIR/
        cp README.md $DEPLOY_DIR/
        
        # 创建部署说明
        cat > $DEPLOY_DIR/DEPLOY.md << EOF
# Vercel部署说明

## 部署步骤

1. 注册Vercel账号: https://vercel.com
2. 安装Vercel CLI: npm install -g vercel
3. 进入部署目录: cd $DEPLOY_DIR
4. 登录Vercel: vercel login
5. 部署: vercel --prod

## 访问地址

部署完成后，你会得到一个类似这样的地址：
https://your-app-name.vercel.app

## 功能测试

- 主页: https://your-app-name.vercel.app
- Web界面: https://your-app-name.vercel.app/web
- API文档: https://your-app-name.vercel.app/docs
- 健康检查: https://your-app-name.vercel.app/api/v1/health

## 注意事项

- API密钥已预配置在vercel.json中
- 免费版本有使用限制，但足够测试使用
- 如需自定义域名，需要升级到付费版本
EOF
        
        echo "✅ Vercel部署包已生成到: $DEPLOY_DIR/"
        echo "📖 查看部署说明: cat $DEPLOY_DIR/DEPLOY.md"
        echo ""
        echo "🚀 下一步："
        echo "1. cd $DEPLOY_DIR"
        echo "2. vercel login"
        echo "3. vercel --prod"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

