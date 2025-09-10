"""
知识库管理抽象接口 - 支持多数据源扩展
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class KnowledgeItem(BaseModel):
    """知识项模型"""
    id: str
    category: str
    title: str
    content: str
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class KnowledgeBase(ABC):
    """知识库抽象基类"""
    
    @abstractmethod
    async def load(self) -> bool:
        """加载知识库"""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[KnowledgeItem]:
        """搜索知识项"""
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[KnowledgeItem]:
        """根据ID获取知识项"""
        pass
    
    @abstractmethod
    async def get_by_category(self, category: str) -> List[KnowledgeItem]:
        """根据分类获取知识项"""
        pass
    
    @abstractmethod
    async def add_item(self, item: KnowledgeItem) -> bool:
        """添加知识项"""
        pass
    
    @abstractmethod
    async def update_item(self, item: KnowledgeItem) -> bool:
        """更新知识项"""
        pass
    
    @abstractmethod
    async def delete_item(self, item_id: str) -> bool:
        """删除知识项"""
        pass
    
    @abstractmethod
    async def get_categories(self) -> List[str]:
        """获取所有分类"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        pass