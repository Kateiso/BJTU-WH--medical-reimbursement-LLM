#!/usr/bin/env python3
"""
基础技能类 - 所有Agent Skills的基类
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
import json
import yaml
from pathlib import Path

@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    content: str
    sources: List[Dict[str, Any]]
    confidence: float
    metadata: Dict[str, Any]

class BaseSkill(ABC):
    """基础技能类 - 定义所有Skills的通用接口"""
    
    def __init__(self, skill_name: str, knowledge_path: str):
        self.skill_name = skill_name
        self.knowledge_path = knowledge_path
        self.knowledge_base = {}
        self._load_knowledge()
    
    def _load_knowledge(self):
        """加载知识库"""
        try:
            knowledge_dir = Path(self.knowledge_path)
            if not knowledge_dir.exists():
                print(f"⚠️ 知识库目录不存在: {knowledge_dir}")
                return
            
            # 加载YAML文件
            for yaml_file in knowledge_dir.glob("*.yml"):
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data:
                        category = yaml_file.stem
                        self.knowledge_base[category] = data
                        print(f"✅ 加载知识库: {category} ({len(data)} 条)")
            
            # 加载Markdown文件
            for md_file in knowledge_dir.glob("*.md"):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    category = md_file.stem
                    self.knowledge_base[category] = {
                        "content": content,
                        "type": "markdown"
                    }
                    print(f"✅ 加载政策文档: {category}")
            
            print(f"📚 {self.skill_name} 知识库加载完成，共 {len(self.knowledge_base)} 个分类")
            
        except Exception as e:
            print(f"❌ 加载知识库失败: {e}")
            self.knowledge_base = {}
    
    @abstractmethod
    async def process_query(self, query: str, entities: Dict[str, Any], 
                          filters: List[str]) -> SkillResult:
        """处理查询 - 子类必须实现"""
        pass
    
    def search_knowledge(self, query: str, filters: List[str] = None, 
                        limit: int = 5) -> List[Dict[str, Any]]:
        """搜索知识库"""
        if not self.knowledge_base:
            return []
        
        results = []
        query_lower = query.lower()
        
        # 确定搜索范围
        search_categories = self._get_search_categories(filters)
        
        for category in search_categories:
            if category not in self.knowledge_base:
                continue
            
            category_data = self.knowledge_base[category]
            
            # 处理不同类型的数据
            if isinstance(category_data, list):
                # YAML列表数据
                for item in category_data:
                    score = self._calculate_relevance_score(item, query_lower)
                    if score > 0:
                        item_copy = item.copy()
                        item_copy['score'] = score
                        item_copy['category'] = category
                        results.append(item_copy)
            
            elif isinstance(category_data, dict) and category_data.get('type') == 'markdown':
                # Markdown文档
                content = category_data.get('content', '')
                if self._text_contains_keywords(content, query_lower):
                    results.append({
                        'title': category,
                        'content': content[:500] + '...' if len(content) > 500 else content,
                        'category': category,
                        'score': 0.8,
                        'type': 'markdown'
                    })
        
        # 按分数排序并返回前N个结果
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def _get_search_categories(self, filters: List[str] = None) -> List[str]:
        """根据过滤器确定搜索分类"""
        if not filters:
            return list(self.knowledge_base.keys())
        
        # 映射过滤器到分类
        filter_mapping = {
            'procedure': ['reimbursement', 'procedures', 'steps', 'process'],
            'materials': ['reimbursement', 'materials', 'requirements', 'checklist'],
            'contacts': ['teachers', 'contacts', 'departments'],
            'policies': ['policies', 'regulations', 'rules'],
            'enrollment': ['enrollment', 'registration', 'courses'],
            'grades': ['grades', 'scores', 'gpa'],
            'exams': ['exams', 'tests', 'schedules']
        }
        
        categories = set()
        for filter_name in filters:
            if filter_name in filter_mapping:
                categories.update(filter_mapping[filter_name])
        
        # 如果过滤器没有匹配到分类，返回所有分类
        if not categories:
            categories = set(self.knowledge_base.keys())
        
        return list(categories)
    
    def _calculate_relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """计算相关性分数"""
        score = 0.0
        query_lower = query.lower()
        
        # 提取查询关键词
        query_words = [word for word in query_lower.split() if len(word) > 1]
        
        # 标题匹配
        title = item.get('title', '').lower()
        if query_lower in title:
            score += 2.0
        elif any(word in title for word in query_words):
            score += 1.0
        
        # 内容匹配
        content = item.get('content', '').lower()
        if query_lower in content:
            score += 1.5
        elif any(word in content for word in query_words):
            score += 0.5
        
        # 问题匹配（FAQ类型）
        question = item.get('question', '').lower()
        if question and query_lower in question:
            score += 2.5
        elif question and any(word in question for word in query_words):
            score += 1.0
        
        # 标签匹配
        tags = item.get('tags', [])
        for tag in tags:
            tag_lower = tag.lower()
            if query_lower in tag_lower:
                score += 1.0
            elif any(word in tag_lower for word in query_words):
                score += 0.5
        
        # 关键词匹配
        keywords = item.get('keywords', [])
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if query_lower in keyword_lower:
                score += 0.8
            elif any(word in keyword_lower for word in query_words):
                score += 0.3
        
        # 特殊匹配逻辑 - 报销相关
        if any(word in query_lower for word in ['报销', '医疗', '医药', '看病', '就医']):
            if any(word in content for word in ['报销', '医疗', '医药']):
                score += 1.0
        
        # 特殊匹配逻辑 - 材料相关
        if any(word in query_lower for word in ['材料', '需要', '要求', '准备']):
            if any(word in content for word in ['材料', '需要', '要求', '准备']):
                score += 1.0
        
        # 特殊匹配逻辑 - 流程相关
        if any(word in query_lower for word in ['流程', '步骤', '怎么', '如何']):
            if any(word in content for word in ['流程', '步骤', '办理']):
                score += 1.0
        
        # 特殊匹配逻辑 - 联系人相关
        if any(word in query_lower for word in ['老师', '教授', '导师', '联系', '电话', '邮箱']):
            if any(word in content for word in ['老师', '教授', '导师', '联系', '电话', '邮箱']):
                score += 1.0
        
        # 特殊匹配逻辑 - 姓名匹配
        name = item.get('name', '')
        if name and name.lower() in query_lower:
            score += 2.0
        
        # 特殊匹配逻辑 - 部门匹配
        dept = item.get('dept', '')
        if dept and dept.lower() in query_lower:
            score += 1.5
        
        return score
    
    def _text_contains_keywords(self, text: str, query: str) -> bool:
        """检查文本是否包含查询关键词"""
        text_lower = text.lower()
        query_words = query.split()
        
        # 完全匹配
        if query in text_lower:
            return True
        
        # 部分匹配
        return any(word in text_lower for word in query_words if len(word) > 1)
    
    def get_skill_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return {
            "name": self.skill_name,
            "knowledge_categories": list(self.knowledge_base.keys()),
            "total_items": sum(
                len(data) if isinstance(data, list) else 1 
                for data in self.knowledge_base.values()
            ),
            "status": "active" if self.knowledge_base else "inactive"
        }
    
    def add_knowledge(self, category: str, data: Any):
        """动态添加知识"""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = []
        
        if isinstance(self.knowledge_base[category], list):
            self.knowledge_base[category].append(data)
        else:
            self.knowledge_base[category] = data
    
    def remove_knowledge(self, category: str, item_id: str = None):
        """移除知识"""
        if category not in self.knowledge_base:
            return False
        
        if item_id and isinstance(self.knowledge_base[category], list):
            # 移除指定ID的项目
            self.knowledge_base[category] = [
                item for item in self.knowledge_base[category]
                if item.get('id') != item_id
            ]
        else:
            # 移除整个分类
            del self.knowledge_base[category]
        
        return True
