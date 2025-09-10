"""
RAG引擎抽象接口 - 支持多模型扩展
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Document(BaseModel):
    """文档模型"""
    id: str
    title: str
    content: str
    metadata: Dict[str, Any] = {}
    score: Optional[float] = None

class SearchResult(BaseModel):
    """搜索结果模型"""
    documents: List[Document]
    query: str
    total_count: int
    search_time: float

class RAGEngine(ABC):
    """RAG引擎抽象基类"""
    
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> SearchResult:
        """搜索相关文档"""
        pass
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> bool:
        """添加文档到知识库"""
        pass
    
    @abstractmethod
    async def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        pass
    
    @abstractmethod
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """获取单个文档"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        pass

class LLMProvider(ABC):
    """大语言模型提供者抽象基类"""
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        context: str = "", 
        max_tokens: int = 1000
    ) -> str:
        """生成回答"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        pass