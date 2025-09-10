#!/usr/bin/env python3
"""
医疗报销智能助手启动脚本
"""
import os
import sys
from pathlib import Path

def check_requirements():
    """检查依赖和配置"""
    print("🔍 检查系统要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要3.8+")
        return False
    
    # 检查环境变量
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ 未设置DASHSCOPE_API_KEY环境变量")
        print("请设置通义千问API密钥:")
        print("export DASHSCOPE_API_KEY=your_api_key_here")
        return False
    
    # 检查依赖
    try:
        import fastapi
        import uvicorn
        import dashscope
        print("✅ 核心依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def create_env_file():
    """创建环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 创建环境变量文件...")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"""# 医疗报销智能助手环境配置
DASHSCOPE_API_KEY={os.getenv('DASHSCOPE_API_KEY', 'your_api_key_here')}
DEBUG=false
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO
""")
        print("✅ 环境变量文件已创建")

def main():
    """主函数"""
    print("🏥 医疗报销智能助手启动器")
    print("=" * 50)
    
    # 检查系统要求
    if not check_requirements():
        sys.exit(1)
    
    # 创建环境文件
    create_env_file()
    
    # 启动应用
    print("🚀 启动应用...")
    print("📱 Web界面: http://localhost:8080/web")
    print("📚 API文档: http://localhost:8080/docs")
    print("🔍 健康检查: http://localhost:8080/api/v1/health")
    print("=" * 50)
    
    try:
        import uvicorn
        from src.config.settings import settings
        
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()