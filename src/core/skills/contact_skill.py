#!/usr/bin/env python3
"""
联系人技能 - 查询老师、部门、窗口信息
"""
from typing import Dict, List, Any
from .base_skill import BaseSkill, SkillResult

class ContactSkill(BaseSkill):
    """联系人Agent - 查询老师、部门、窗口信息"""
    
    def __init__(self):
        super().__init__(
            skill_name="联系人助手",
            knowledge_path="data/contacts"
        )
        self.skill_description = "专业查询老师、部门、窗口的联系方式和办公信息"
    
    async def process_query(self, query: str, entities: Dict[str, Any], 
                          filters: List[str]) -> SkillResult:
        """处理联系人相关查询"""
        try:
            # 搜索相关知识
            knowledge_results = self.search_knowledge(query, filters, limit=5)
            
            if not knowledge_results:
                return SkillResult(
                    success=False,
                    content="抱歉，我没有找到相关的联系人信息。请尝试更具体的问题，或者联系学校总机咨询。",
                    sources=[],
                    confidence=0.0,
                    metadata={"skill": "contact", "query": query}
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
                    "skill": "contact",
                    "query": query,
                    "entities": entities,
                    "filters": filters,
                    "results_count": len(knowledge_results)
                }
            )
            
        except Exception as e:
            return SkillResult(
                success=False,
                content=f"处理联系人查询时出错: {str(e)}",
                sources=[],
                confidence=0.0,
                metadata={"skill": "contact", "error": str(e)}
            )
    
    def _build_response(self, query: str, results: List[Dict[str, Any]], 
                       entities: Dict[str, Any]) -> str:
        """构建回答内容"""
        response_parts = []
        
        # 添加问候语
        response_parts.append("📞 **联系人助手**为您服务！")
        
        # 根据查询类型添加特定回复
        if any(keyword in query for keyword in ['老师', '教授', '导师']):
            response_parts.append("关于老师信息，我为您整理了以下联系方式：")
        elif any(keyword in query for keyword in ['部门', '学院', '处']):
            response_parts.append("关于部门信息，我为您整理了以下联系方式：")
        elif any(keyword in query for keyword in ['窗口', '服务', '办公']):
            response_parts.append("关于服务窗口，我为您整理了以下信息：")
        else:
            response_parts.append("根据您的问题，我为您整理了以下联系人信息：")
        
        # 添加具体内容
        for i, result in enumerate(results, 1):
            response_parts.append(f"\n**{i}. {result.get('title', '联系人信息')}**")
            
            # 处理联系人信息
            if 'name' in result:
                response_parts.append(f"👤 **姓名**: {result['name']}")
            
            if 'dept' in result:
                response_parts.append(f"🏢 **部门**: {result['dept']}")
            
            if 'position' in result or 'role' in result:
                position = result.get('position') or result.get('role', '')
                response_parts.append(f"💼 **职位**: {position}")
            
            if 'office' in result or 'office_location' in result:
                office = result.get('office') or result.get('office_location', '')
                response_parts.append(f"📍 **办公地点**: {office}")
            
            if 'contact' in result or 'phone' in result:
                contact = result.get('contact') or result.get('phone', '')
                response_parts.append(f"📱 **联系方式**: {contact}")
            
            if 'email' in result:
                response_parts.append(f"📧 **邮箱**: {result['email']}")
            
            if 'service_hours' in result or 'hours' in result:
                hours = result.get('service_hours') or result.get('hours', '')
                response_parts.append(f"🕒 **服务时间**: {hours}")
            
            # 添加内容描述
            content = result.get('content', '')
            if content:
                response_parts.append(f"📝 **说明**: {content}")
                # 在每条信息后显示来源
                source_info = f"\n📚 *来源: {result.get('title', '知识库')}*"
                response_parts.append(source_info)
            
            # 移除标签显示，改为在每条信息后显示来源
        
        # 添加通用联系信息
        response_parts.append("\n📞 **常用联系方式**")
        response_parts.append("- 学校总机：0631-3803000")
        response_parts.append("- 学生处：0631-3803001")
        response_parts.append("- 教务处：0631-3803002")
        response_parts.append("- 财务处：0631-3803003")
        
        # 添加注意事项
        response_parts.append("\n⚠️ **注意事项**")
        response_parts.append("- 建议在工作时间联系")
        response_parts.append("- 重要事务请提前预约")
        response_parts.append("- 企业微信联系更便捷")
        
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
        
        # 如果有完整联系信息，提高置信度
        complete_info_count = sum(
            1 for result in results 
            if result.get('name') and (result.get('contact') or result.get('phone'))
        )
        if complete_info_count > 0:
            confidence = min(confidence + 0.3, 1.0)
        
        return confidence
    
    def get_supported_queries(self) -> List[str]:
        """获取支持的查询类型"""
        return [
            "老师联系方式",
            "部门办公信息",
            "服务窗口查询",
            "办公地点地址",
            "服务时间查询",
            "紧急联系方式",
            "部门职责查询",
            "办公电话查询"
        ]
    
    def get_quick_actions(self) -> List[Dict[str, str]]:
        """获取快速操作"""
        return [
            {"title": "医保办联系", "query": "医保办常春艳老师联系方式？"},
            {"title": "学生处查询", "query": "学生处办公地点和电话？"},
            {"title": "教务处联系", "query": "教务处联系方式？"},
            {"title": "图书馆服务", "query": "图书馆开放时间和联系方式？"},
            {"title": "医务室信息", "query": "校医务室地址和电话？"}
        ]
