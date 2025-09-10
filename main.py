"""
医疗报销智能助手 - 主应用入口
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path

from src.core.api.router import router
from src.config.settings import settings

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.log_file) if settings.log_file else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于RAG技术的医疗报销智能问答系统",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_path = Path(__file__).parent / "src" / "web" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 配置模板
templates_path = Path(__file__).parent / "src" / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# 注册API路由
app.include_router(router)

# Web界面路由
@app.get("/web", response_class=HTMLResponse)
async def web_interface(request: Request):
    """Web界面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径重定向到Web界面"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>医疗报销智能助手</title>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="0; url=/web">
    </head>
    <body>
        <p>正在跳转到 <a href="/web">Web界面</a>...</p>
    </body>
    </html>
    """)

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} 启动中...")
    logger.info(f"📊 配置信息:")
    logger.info(f"   - 主机: {settings.host}:{settings.port}")
    logger.info(f"   - 调试模式: {settings.debug}")
    logger.info(f"   - RAG引擎: {settings.rag_engine}")
    logger.info(f"   - 知识库: {settings.knowledge_source}")
    logger.info(f"✅ 应用启动完成！")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("🛑 应用正在关闭...")

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return {
        "error": "服务器内部错误",
        "detail": str(exc) if settings.debug else "请联系管理员",
        "path": str(request.url)
    }

if __name__ == "__main__":
    # 开发环境启动
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )