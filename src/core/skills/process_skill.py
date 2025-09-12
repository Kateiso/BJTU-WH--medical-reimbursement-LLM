#!/usr/bin/env python3
"""
办事流程技能 - 处理报销、申请、办理等事务
"""
from typing import Dict, List, Any
from .base_skill import BaseSkill, SkillResult

class ProcessSkill(BaseSkill):
    """办事流程Agent - 专业处理报销、申请等流程"""
    
    def __init__(self):
        super().__init__(
            skill_name="办事流程助手",
            knowledge_path="data/process"
        )
        self.skill_description = "专业处理医疗报销、学籍管理、宿舍申请、证明开具等办事流程"
    
    async def process_query(self, query: str, entities: Dict[str, Any], 
                          filters: List[str]) -> SkillResult:
        """处理办事流程相关查询"""
        try:
            # 搜索相关知识
            knowledge_results = self.search_knowledge(query, filters, limit=3)
            
            if not knowledge_results:
                return SkillResult(
                    success=False,
                    content="抱歉，我没有找到相关的办事流程信息。请尝试更具体的问题，或者联系相关部门咨询。",
                    sources=[],
                    confidence=0.0,
                    metadata={"skill": "process", "query": query}
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
                    "skill": "process",
                    "query": query,
                    "entities": entities,
                    "filters": filters,
                    "results_count": len(knowledge_results)
                }
            )
            
        except Exception as e:
            return SkillResult(
                success=False,
                content=f"处理办事流程查询时出错: {str(e)}",
                sources=[],
                confidence=0.0,
                metadata={"skill": "process", "error": str(e)}
            )
    
    def _build_response(self, query: str, results: List[Dict[str, Any]], 
                       entities: Dict[str, Any]) -> str:
        """构建回答内容"""
        response_parts = []
        
        # 添加问候语
        response_parts.append("🏥 **办事流程助手**为您服务！")
        
        # 根据查询类型添加特定回复
        if any(keyword in query for keyword in ['报销', '医疗', '医药费']):
            response_parts.append("关于医疗报销，我为您整理了以下信息：")
        elif any(keyword in query for keyword in ['申请', '办理', '手续']):
            response_parts.append("关于申请办理，我为您整理了以下流程：")
        elif any(keyword in query for keyword in ['材料', '需要', '要求']):
            response_parts.append("关于所需材料，我为您整理了以下清单：")
        else:
            response_parts.append("根据您的问题，我为您整理了以下信息：")
        
        # 添加具体内容
        for i, result in enumerate(results, 1):
            response_parts.append(f"\n**{i}. {result.get('title', '相关信息')}**")
            
            # 处理不同类型的内容
            if result.get('type') == 'markdown':
                # Markdown文档
                content = result.get('content', '')
                response_parts.append(content)
            elif 'question' in result and 'answer' in result:
                # FAQ格式
                response_parts.append(f"**问题**: {result['question']}")
                response_parts.append(f"**回答**: {result['answer']}")
            elif 'scenario' in result and 'solution' in result:
                # 场景解决方案
                response_parts.append(f"**场景**: {result['scenario']}")
                response_parts.append(f"**解决方案**: {result['solution']}")
            else:
                # 普通内容
                content = result.get('content', '')
                if content:
                    response_parts.append(content)
                    # 在每条信息后显示来源
                    source_info = f"\n📚 *来源: {result.get('title', '知识库')}*"
                    response_parts.append(source_info)
            
            # 移除标签显示，改为在每条信息后显示来源
        
        # 添加联系信息
        if any(keyword in query for keyword in ['联系', '电话', '老师', '咨询']):
            response_parts.append("\n📞 **联系方式**")
            response_parts.append("- 医保办：常春艳老师，思源东楼812B")
            response_parts.append("- 企业微信预约（推荐）")
        
        # 添加注意事项
        response_parts.append("\n⚠️ **注意事项**")
        response_parts.append("- 请提前预约办理时间")
        response_parts.append("- 携带完整材料，避免多次往返")
        response_parts.append("- 如有疑问，建议先电话咨询")
        
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
        
        # 如果有高分结果，提高置信度
        high_score_count = sum(1 for result in results if result.get('score', 0) > 1.5)
        if high_score_count > 0:
            confidence = min(confidence + 0.2, 1.0)
        
        return confidence
    
    def get_supported_queries(self) -> List[str]:
        """获取支持的查询类型"""
        return [
            "医疗报销流程",
            "报销材料要求", 
            "报销比例标准",
            "学籍管理申请",
            "宿舍申请流程",
            "证明开具手续",
            "办事流程步骤",
            "申请材料清单",
            "办理时间地点",
            "联系方式查询"
        ]
    
    def get_quick_actions(self) -> List[Dict[str, str]]:
        """获取快速操作"""
        return [
            {"title": "医疗报销流程", "query": "医疗报销需要什么流程？"},
            {"title": "报销材料清单", "query": "报销需要准备哪些材料？"},
            {"title": "报销比例查询", "query": "门诊和住院的报销比例是多少？"},
            {"title": "联系医保办", "query": "医保办老师的联系方式？"},
            {"title": "办理时间地点", "query": "报销在哪里办理？什么时间？"}
        ]
