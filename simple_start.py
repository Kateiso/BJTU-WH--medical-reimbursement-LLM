#!/usr/bin/env python3
"""
医疗报销智能助手 - 简化启动脚本
不依赖复杂配置，直接运行
"""
import os
import sys
import uvicorn
from pathlib import Path

# 设置API密钥
os.environ["DASHSCOPE_API_KEY"] = "sk-2ea7b3f8fb7742828ff836eed6050f19"

def main():
    print("🏥 医疗报销智能助手 - 简化启动")
    print("=" * 50)
    print("📱 Web界面: http://localhost:8080/web")
    print("📚 API文档: http://localhost:8080/docs")
    print("🔍 健康检查: http://localhost:8080/api/v1/health")
    print("=" * 50)
    print("💡 提示: 按 Ctrl+C 停止服务")
    print("")
    
    try:
        # 直接启动FastAPI应用
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8080,
            reload=False,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install fastapi uvicorn dashscope")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

