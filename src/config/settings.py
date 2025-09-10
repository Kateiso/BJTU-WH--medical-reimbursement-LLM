"""
配置管理模块 - 支持环境变量和配置文件
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    app_name: str = "医疗报销智能助手"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")
    
    # API配置
    api_prefix: str = "/api/v1"
    cors_origins: list = ["*"]
    
    # 通义千问配置
    dashscope_api_key: str = Field(..., env="DASHSCOPE_API_KEY")
    qwen_model: str = Field(default="qwen-plus", env="QWEN_MODEL")
    
    # RAG配置
    rag_engine: str = Field(default="qwen", env="RAG_ENGINE")
    max_context_length: int = Field(default=4000, env="MAX_CONTEXT_LENGTH")
    top_k_documents: int = Field(default=5, env="TOP_K_DOCUMENTS")
    
    # 知识库配置
    knowledge_source: str = Field(default="json", env="KNOWLEDGE_SOURCE")
    knowledge_path: str = Field(default="data/knowledge_base.json", env="KNOWLEDGE_PATH")
    
    # 缓存配置 (扩展预留)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # 数据库配置 (扩展预留)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# 全局配置实例
settings = Settings()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)