"""
简化版主应用 - 避免复杂依赖问题
"""
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pathlib import Path

# 设置API密钥
os.environ["DASHSCOPE_API_KEY"] = "sk-2ea7b3f8fb7742828ff836eed6050f19"

# 创建FastAPI应用
app = FastAPI(
    title="医疗报销智能助手",
    version="1.0.0",
    description="基于RAG技术的医疗报销智能问答系统"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置模板
templates_path = Path(__file__).parent / "src" / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_path))

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "医疗报销智能助手运行中！",
        "status": "ok",
        "version": "1.0.0",
        "web_interface": "/web",
        "api_docs": "/docs"
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "api_key": "已配置",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/web", response_class=HTMLResponse)
async def web_interface(request: Request):
    """Web界面"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        # 如果模板加载失败，返回简单HTML
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>医疗报销智能助手</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ color: #2c3e50; text-align: center; }}
                .status {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .api-list {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .api-item {{ margin: 10px 0; padding: 10px; background: white; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="header">🏥 医疗报销智能助手</h1>
                <div class="status">
                    ✅ 系统运行正常！API密钥已配置。
                </div>
                
                <h2>📋 可用功能</h2>
                <div class="api-list">
                    <div class="api-item">
                        <strong>主页</strong>: <a href="/">/</a>
                    </div>
                    <div class="api-item">
                        <strong>健康检查</strong>: <a href="/health">/health</a>
                    </div>
                    <div class="api-item">
                        <strong>API文档</strong>: <a href="/docs">/docs</a>
                    </div>
                </div>
                
                <h2>🚀 下一步</h2>
                <p>系统基础功能已就绪，RAG功能正在完善中...</p>
                <p>错误信息: {str(e)}</p>
            </div>
        </body>
        </html>
        """)

@app.get("/api/v1/health")
async def api_health():
    """API健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "config": "healthy"
        }
    }

@app.post("/api/v1/ask")
async def ask_question(request: dict):
    """智能问答接口（简化版）"""
    question = request.get("question", "")
    
    if not question:
        return {"error": "问题不能为空"}
    
    # 简化版回答（后续会集成RAG）
    return {
        "answer": f"您的问题「{question}」已收到。RAG功能正在完善中，请稍后再试。",
        "sources": [],
        "session_id": "demo_session",
        "response_time": 0.1
    }

if __name__ == "__main__":
    print("🏥 医疗报销智能助手 - 简化版启动")
    print("=" * 50)
    print("📱 主页: http://localhost:8080")
    print("🌐 Web界面: http://localhost:8080/web")
    print("📚 API文档: http://localhost:8080/docs")
    print("🔍 健康检查: http://localhost:8080/health")
    print("=" * 50)
    print("💡 按 Ctrl+C 停止服务")
    print("")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
