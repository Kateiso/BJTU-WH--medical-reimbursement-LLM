"""
简化配置模块 - 避免Pydantic兼容性问题
"""
import os
from pathlib import Path

class SimpleSettings:
    """简化配置类"""
    
    def __init__(self):
        # 应用基础配置
        self.app_name = "医疗报销智能助手"
        self.app_version = "1.0.0"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # 服务器配置
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8080"))
        
        # API配置
        self.api_prefix = "/api/v1"
        self.cors_origins = ["*"]
        
        # 通义千问配置
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY", "sk-2ea7b3f8fb7742828ff836eed6050f19")
        self.qwen_model = os.getenv("QWEN_MODEL", "qwen-plus")
        
        # RAG配置
        self.rag_engine = os.getenv("RAG_ENGINE", "qwen")
        self.max_context_length = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
        self.top_k_documents = int(os.getenv("TOP_K_DOCUMENTS", "5"))
        
        # 知识库配置
        self.knowledge_source = os.getenv("KNOWLEDGE_SOURCE", "json")
        self.knowledge_path = os.getenv("KNOWLEDGE_PATH", "data/knowledge_base.json")
        
        # 日志配置
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE")

# 全局配置实例
settings = SimpleSettings()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
