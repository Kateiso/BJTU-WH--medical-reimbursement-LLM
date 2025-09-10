#!/usr/bin/env python3
"""
超简化测试应用 - 确保基础功能正常
"""
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# 设置API密钥
os.environ["DASHSCOPE_API_KEY"] = "sk-2ea7b3f8fb7742828ff836eed6050f19"

# 创建应用
app = FastAPI(title="医疗报销智能助手")

@app.get("/")
async def root():
    return {
        "message": "🏥 医疗报销智能助手运行中！",
        "status": "ok",
        "api_key": "已配置",
        "web_interface": "/web"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api_key": "已配置"
    }

@app.get("/web", response_class=HTMLResponse)
async def web():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>医疗报销智能助手</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { color: #2c3e50; text-align: center; }
            .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🏥 医疗报销智能助手</h1>
            <div class="status">
                ✅ 系统运行正常！API密钥已配置。
            </div>
            <p>基础功能已就绪，RAG功能正在完善中...</p>
            <p><a href="/docs">查看API文档</a></p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("🏥 医疗报销智能助手 - 测试版启动")
    print("=" * 50)
    print("📱 主页: http://localhost:8080")
    print("🌐 Web界面: http://localhost:8080/web")
    print("📚 API文档: http://localhost:8080/docs")
    print("🔍 健康检查: http://localhost:8080/health")
    print("=" * 50)
    print("💡 按 Ctrl+C 停止服务")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
