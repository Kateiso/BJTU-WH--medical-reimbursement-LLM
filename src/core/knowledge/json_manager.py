"""
JSON知识库管理器实现
"""
import json
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .base import KnowledgeBase, KnowledgeItem
from ...config.settings import settings, PROJECT_ROOT

class JSONKnowledgeManager(KnowledgeBase):
    """JSON文件知识库管理器"""
    
    def __init__(self, file_path: str = None):
        self.file_path = Path(file_path or PROJECT_ROOT / settings.knowledge_path)
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.loaded = False
    
    async def load(self) -> bool:
        """加载知识库"""
        try:
            if not self.file_path.exists():
                # 创建默认知识库
                await self._create_default_knowledge_base()
                return True
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 解析知识库数据
            self.knowledge_items = {}
            for category, items in data.get("knowledge_base", {}).items():
                for item_data in items:
                    item = KnowledgeItem(
                        id=item_data.get("id", str(uuid.uuid4())),
                        category=category,
                        title=item_data.get("title", ""),
                        content=item_data.get("content", ""),
                        tags=item_data.get("tags", []),
                        metadata=item_data.get("metadata", {}),
                        created_at=item_data.get("created_at"),
                        updated_at=item_data.get("updated_at")
                    )
                    self.knowledge_items[item.id] = item
            
            self.loaded = True
            return True
            
        except Exception as e:
            print(f"加载知识库失败: {str(e)}")
            return False
    
    async def _create_default_knowledge_base(self) -> None:
        """创建默认知识库"""
        default_data = {
            "knowledge_base": {
                "reimbursement_policies": [
                    {
                        "id": "policy_001",
                        "title": "门诊报销政策",
                        "content": "北京交通大学威海校区学生门诊医疗费用报销比例为80%，教职工为90%。报销时间窗口为就诊后30天内。",
                        "tags": ["门诊", "报销", "比例"],
                        "metadata": {"type": "policy", "priority": "high"}
                    },
                    {
                        "id": "policy_002", 
                        "title": "住院报销政策",
                        "content": "住院医疗费用报销比例为85%，需要提供住院证明、费用清单等材料。报销时间窗口为出院后60天内。",
                        "tags": ["住院", "报销", "材料"],
                        "metadata": {"type": "policy", "priority": "high"}
                    }
                ],
                "materials_requirements": [
                    {
                        "id": "material_001",
                        "title": "门诊报销材料清单",
                        "content": "门诊报销需要提供：1. 医疗费用发票原件 2. 病历本或诊断证明 3. 学生证或工作证复印件 4. 银行卡复印件",
                        "tags": ["门诊", "材料", "清单"],
                        "metadata": {"type": "material", "priority": "high"}
                    }
                ],
                "contacts": [
                    {
                        "id": "contact_001",
                        "title": "医疗报销负责人",
                        "content": "负责老师：张老师，办公地点：行政楼201室，联系电话：0631-5688888，办公时间：周一至周五 8:00-17:00",
                        "tags": ["联系人", "报销", "老师"],
                        "metadata": {"type": "contact", "priority": "high"}
                    }
                ],
                "hospitals": [
                    {
                        "id": "hospital_001",
                        "title": "威海市中心医院",
                        "content": "地址：威海市环翠区文化中路，电话：0631-3806666，挂号方式：现场挂号或网上预约，转诊要求：需要校医院转诊证明",
                        "tags": ["医院", "威海", "转诊"],
                        "metadata": {"type": "hospital", "priority": "medium"}
                    }
                ],
                "common_questions": [
                    {
                        "id": "faq_001",
                        "title": "感冒药能报销吗？",
                        "content": "普通感冒药属于门诊用药，可以按照门诊报销政策进行报销，报销比例为80%。需要提供正规医院的处方和发票。",
                        "tags": ["感冒", "药品", "报销"],
                        "metadata": {"type": "faq", "priority": "high"}
                    }
                ]
            }
        }
        
        # 确保目录存在
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存默认数据
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    async def search(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[KnowledgeItem]:
        """搜索知识项"""
        if not self.loaded:
            await self.load()
        
        query_lower = query.lower()
        results = []
        
        for item in self.knowledge_items.values():
            # 分类过滤
            if category and item.category != category:
                continue
            
            # 简单关键词匹配
            score = 0
            if query_lower in item.title.lower():
                score += 3
            if query_lower in item.content.lower():
                score += 1
            for tag in item.tags:
                if query_lower in tag.lower():
                    score += 2
            
            if score > 0:
                item.metadata["search_score"] = score
                results.append(item)
        
        # 按分数排序
        results.sort(key=lambda x: x.metadata.get("search_score", 0), reverse=True)
        
        return results[:limit]
    
    async def get_by_id(self, item_id: str) -> Optional[KnowledgeItem]:
        """根据ID获取知识项"""
        if not self.loaded:
            await self.load()
        
        return self.knowledge_items.get(item_id)
    
    async def get_by_category(self, category: str) -> List[KnowledgeItem]:
        """根据分类获取知识项"""
        if not self.loaded:
            await self.load()
        
        return [item for item in self.knowledge_items.values() if item.category == category]
    
    async def add_item(self, item: KnowledgeItem) -> bool:
        """添加知识项"""
        try:
            if not item.id:
                item.id = str(uuid.uuid4())
            
            item.created_at = datetime.now().isoformat()
            item.updated_at = item.created_at
            
            self.knowledge_items[item.id] = item
            await self._save_to_file()
            return True
            
        except Exception as e:
            print(f"添加知识项失败: {str(e)}")
            return False
    
    async def update_item(self, item: KnowledgeItem) -> bool:
        """更新知识项"""
        try:
            if item.id not in self.knowledge_items:
                return False
            
            item.updated_at = datetime.now().isoformat()
            self.knowledge_items[item.id] = item
            await self._save_to_file()
            return True
            
        except Exception as e:
            print(f"更新知识项失败: {str(e)}")
            return False
    
    async def delete_item(self, item_id: str) -> bool:
        """删除知识项"""
        try:
            if item_id in self.knowledge_items:
                del self.knowledge_items[item_id]
                await self._save_to_file()
                return True
            return False
            
        except Exception as e:
            print(f"删除知识项失败: {str(e)}")
            return False
    
    async def get_categories(self) -> List[str]:
        """获取所有分类"""
        if not self.loaded:
            await self.load()
        
        categories = set()
        for item in self.knowledge_items.values():
            categories.add(item.category)
        
        return list(categories)
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.loaded:
            await self.load()
        
        categories = {}
        for item in self.knowledge_items.values():
            if item.category not in categories:
                categories[item.category] = 0
            categories[item.category] += 1
        
        return {
            "total_items": len(self.knowledge_items),
            "categories": categories,
            "file_path": str(self.file_path),
            "loaded": self.loaded
        }
    
    async def _save_to_file(self) -> None:
        """保存到文件"""
        data = {"knowledge_base": {}}
        
        for item in self.knowledge_items.values():
            if item.category not in data["knowledge_base"]:
                data["knowledge_base"][item.category] = []
            
            data["knowledge_base"][item.category].append({
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "tags": item.tags,
                "metadata": item.metadata,
                "created_at": item.created_at,
                "updated_at": item.updated_at
            })
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)