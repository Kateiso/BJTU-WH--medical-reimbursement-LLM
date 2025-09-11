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

class KnowledgeItemRequest(BaseModel):
    """知识项请求模型"""
    category: str = Field(..., description="分类", min_length=1, max_length=50)
    title: str = Field(..., description="标题", min_length=1, max_length=200)
    content: str = Field(..., description="内容", min_length=1, max_length=5000)
    tags: List[str] = Field(default=[], description="标签列表")
    metadata: Dict[str, Any] = Field(default={}, description="元数据")

class KnowledgeItemResponse(BaseModel):
    """知识项响应模型"""
    id: str = Field(..., description="条目ID")
    category: str = Field(..., description="分类")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    tags: List[str] = Field(..., description="标签列表")
    metadata: Dict[str, Any] = Field(..., description="元数据")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")

class KnowledgeItemUpdateRequest(BaseModel):
    """知识项更新请求模型"""
    category: Optional[str] = Field(None, description="分类", max_length=50)
    title: Optional[str] = Field(None, description="标题", max_length=200)
    content: Optional[str] = Field(None, description="内容", max_length=5000)
    tags: Optional[List[str]] = Field(None, description="标签列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")
    request_id: Optional[str] = Field(None, description="请求ID")