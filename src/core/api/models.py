"""
API数据模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class QuestionRequest(BaseModel):
    """问答请求模型"""
    question: str = Field(..., description="用户问题", min_length=1, max_length=500)
    session_id: Optional[str] = Field(None, description="会话ID")
    context: Optional[str] = Field(None, description="上下文信息")

class AnswerResponse(BaseModel):
    """回答响应模型"""
    answer: str = Field(..., description="AI生成的回答")
    sources: List[Dict[str, Any]] = Field(default=[], description="信息来源")
    session_id: str = Field(..., description="会话ID")
    response_time: float = Field(..., description="响应时间(秒)")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本号")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    components: Dict[str, Any] = Field(default={}, description="组件状态")

class KnowledgeSearchRequest(BaseModel):
    """知识库搜索请求模型"""
    query: str = Field(..., description="搜索查询", min_length=1, max_length=200)
    category: Optional[str] = Field(None, description="分类过滤")
    limit: int = Field(default=10, description="返回数量限制", ge=1, le=50)

class KnowledgeSearchResponse(BaseModel):
    """知识库搜索响应模型"""
    items: List[Dict[str, Any]] = Field(..., description="搜索结果")
    total_count: int = Field(..., description="总数量")
    query: str = Field(..., description="搜索查询")
    search_time: float = Field(..., description="搜索时间(秒)")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")
    request_id: Optional[str] = Field(None, description="请求ID")