#!/usr/bin/env python3
"""
课程学习技能 - 处理选课、成绩、考试、学习指导等学习相关事务
"""
from typing import Dict, List, Any
from .base_skill import BaseSkill, SkillResult

class CourseSkill(BaseSkill):
    """课程学习Agent - 处理选课、成绩、考试、学习指导等学习事务"""
    
    def __init__(self):
        super().__init__(
            skill_name="课程学习助手",
            knowledge_path="data/course"
        )
        self.skill_description = "专业处理选课、成绩查询、考试安排、学习指导、职业规划等学习相关事务"
    
    async def process_query(self, query: str, entities: Dict[str, Any], 
                          filters: List[str]) -> SkillResult:
        """处理课程学习相关查询"""
        try:
            # 搜索相关知识
            knowledge_results = self.search_knowledge(query, filters, limit=5)
            
            if not knowledge_results:
                return SkillResult(
                    success=False,
                    content="抱歉，我没有找到相关的学习指导信息。请尝试更具体的问题，或者联系教务处咨询。",
                    sources=[],
                    confidence=0.0,
                    metadata={"skill": "course", "query": query}
                )
            
            # 构建回答内容
            content = self._build_response(query, knowledge_results, entities)
            
            # 构建来源信息
            sources = [
                {
                    "title": item.get("title", ""),
                    "category": item.get("category", ""),
                    "score": item.get("score", 0)
                }
                for item in knowledge_results
            ]
            
            # 计算置信度
            confidence = self._calculate_confidence(knowledge_results, query)
            
            return SkillResult(
                success=True,
                content=content,
                sources=sources,
                confidence=confidence,
                metadata={
                    "skill": "course",
                    "query": query,
                    "entities": entities,
                    "filters": filters,
                    "results_count": len(knowledge_results)
                }
            )
            
        except Exception as e:
            return SkillResult(
                success=False,
                content=f"处理学习指导查询时出错: {str(e)}",
                sources=[],
                confidence=0.0,
                metadata={"skill": "course", "error": str(e)}
            )
    
    def _build_response(self, query: str, results: List[Dict[str, Any]], 
                       entities: Dict[str, Any]) -> str:
        """构建回答内容"""
        response_parts = []
        
        # 添加问候语
        response_parts.append("🎓 **课程学习助手**为您服务！")
        
        # 根据查询类型添加特定回复
        if any(keyword in query for keyword in ['保研', '考研', '留学', '申请']):
            response_parts.append("关于升学规划，我为您整理了以下指导信息：")
        elif any(keyword in query for keyword in ['选课', '课程', '成绩', '考试']):
            response_parts.append("关于课程学习，我为您整理了以下信息：")
        elif any(keyword in query for keyword in ['科研', '项目', '实习']):
            response_parts.append("关于科研实践，我为您整理了以下指导：")
        elif any(keyword in query for keyword in ['学习', '自学', '资源']):
            response_parts.append("关于学习资源，我为您整理了以下推荐：")
        else:
            response_parts.append("根据您的问题，我为您整理了以下学习指导：")
        
        # 添加具体内容
        for i, result in enumerate(results, 1):
            response_parts.append(f"\n**{i}. {result.get('title', '学习指导')}**")
            
            # 处理不同类型的内容
            if result.get('type') == 'markdown':
                # Markdown文档
                content = result.get('content', '')
                response_parts.append(content)
            elif 'question' in result and 'answer' in result:
                # FAQ格式
                response_parts.append(f"**问题**: {result['question']}")
                response_parts.append(f"**回答**: {result['answer']}")
            else:
                # 普通内容
                content = result.get('content', '')
                if content:
                    response_parts.append(content)
                    # 在每条信息后显示来源
                    source_info = f"\n📚 *来源: {result.get('title', '知识库')}*"
                    response_parts.append(source_info)
            
            # 移除标签显示，改为在每条信息后显示来源
            
            # 添加优先级信息
            priority = result.get('metadata', {}).get('priority', '')
            if priority:
                priority_map = {'high': '🔥 高优先级', 'medium': '⭐ 中优先级', 'low': '📝 参考'}
                response_parts.append(f"*{priority_map.get(priority, '')}*")
        
        # 添加学习建议
        response_parts.append("\n💡 **学习建议**")
        response_parts.append("- 制定长期学习计划，分阶段实现目标")
        response_parts.append("- 注重实践项目，积累可展示的作品")
        response_parts.append("- 积极参与科研和竞赛，提升综合能力")
        response_parts.append("- 保持英语学习，为国际化发展做准备")
        
        # 添加联系信息
        response_parts.append("\n📞 **获取帮助**")
        response_parts.append("- 教务处：课程安排、成绩查询")
        response_parts.append("- 学生处：学习指导、职业规划")
        response_parts.append("- 导师：科研指导、学术发展")
        response_parts.append("- 校友网络：经验分享、职业建议")
        
        return "\n".join(response_parts)
    
    def _calculate_confidence(self, results: List[Dict[str, Any]], query: str) -> float:
        """计算回答置信度"""
        if not results:
            return 0.0
        
        # 基于结果数量和分数计算置信度
        total_score = sum(result.get('score', 0) for result in results)
        avg_score = total_score / len(results)
        
        # 归一化到0-1范围
        confidence = min(avg_score / 2.0, 1.0)
        
        # 如果有高优先级结果，提高置信度
        high_priority_count = sum(
            1 for result in results 
            if result.get('metadata', {}).get('priority') == 'high'
        )
        if high_priority_count > 0:
            confidence = min(confidence + 0.2, 1.0)
        
        return confidence
    
    def get_supported_queries(self) -> List[str]:
        """获取支持的查询类型"""
        return [
            "升学规划指导",
            "保研考研留学决策",
            "CS专业方向选择",
            "学习资源推荐",
            "科研项目指导",
            "申请材料准备",
            "时间管理建议",
            "职业发展规划",
            "课程学习指导",
            "成绩提升建议"
        ]
    
    def get_quick_actions(self) -> List[Dict[str, str]]:
        """获取快速操作"""
        return [
            {"title": "升学规划", "query": "保研考研留学怎么选择？"},
            {"title": "CS方向", "query": "计算机专业有哪些发展方向？"},
            {"title": "学习资源", "query": "有什么好的CS学习资源推荐？"},
            {"title": "科研指导", "query": "如何开始科研项目？"},
            {"title": "申请材料", "query": "升学申请需要准备哪些材料？"}
        ]

