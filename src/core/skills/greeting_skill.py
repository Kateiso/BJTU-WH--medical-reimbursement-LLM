"""
问候和通用对话技能
"""
from typing import Dict, Any, List
from .base_skill import BaseSkill, SkillResult

class GreetingSkill(BaseSkill):
    """问候和通用对话技能"""
    
    def __init__(self):
        super().__init__("通用对话助手", "data/greeting")
        self.skill_name = "通用对话助手"
    
    async def process_query(self, query: str, entities: Dict[str, Any], 
                          filters: List[str]) -> SkillResult:
        """处理问候和通用对话"""
        query_lower = query.lower()
        
        # 问候语处理
        if any(greeting in query_lower for greeting in ['你好', 'hello', 'hi', '嗨']):
            content = self._handle_greeting()
        elif any(thanks in query_lower for thanks in ['谢谢', '感谢', 'thank']):
            content = self._handle_thanks()
        elif any(goodbye in query_lower for goodbye in ['再见', '拜拜', 'bye', 'goodbye']):
            content = self._handle_goodbye()
        elif any(help_word in query_lower for help_word in ['帮助', '介绍', '功能', '能做什么']):
            content = self._handle_help()
        else:
            content = self._handle_general_chat(query)
        
        return SkillResult(
            success=True,
            content=content,
            sources=[],
            confidence=0.8,
            metadata={"skill": "greeting", "type": "general_chat"}
        )
    
    def _handle_greeting(self) -> str:
        """处理问候"""
        return """👋 **通用对话助手**为您服务！

您好！我是校园智能助手，很高兴为您服务！

🎯 **我可以帮您处理**：
- 🏥 **医疗报销** - 报销流程、材料要求、比例标准
- 📞 **联系人查询** - 老师联系方式、部门信息
- 🎓 **学习指导** - 升学规划、专业发展、科研指导
- 💬 **日常对话** - 聊天交流、问题解答

请告诉我您需要什么帮助，我会尽力为您提供准确的信息！"""
    
    def _handle_thanks(self) -> str:
        """处理感谢"""
        return """😊 **通用对话助手**为您服务！

不客气！很高兴能帮助到您！

如果您还有其他问题，随时可以问我。我会继续为您提供校园生活各方面的帮助。

祝您学习生活愉快！✨"""
    
    def _handle_goodbye(self) -> str:
        """处理告别"""
        return """👋 **通用对话助手**为您服务！

再见！很高兴为您服务！

如果以后有任何校园生活相关的问题，随时欢迎回来咨询。

祝您一切顺利！🌟"""
    
    def _handle_help(self) -> str:
        """处理帮助请求"""
        return """🤖 **通用对话助手**为您服务！

我是北京交通大学威海校区的校园智能助手，采用最新的意图路由技术，可以智能识别您的需求并调用专业Agent为您服务。

🎯 **主要功能**：

**🏥 办事流程助手**
- 医疗报销流程和材料要求
- 学籍管理、宿舍申请
- 证明开具、手续办理

**📞 联系人助手**  
- 老师联系方式查询
- 部门窗口信息
- 办公地点和时间

**🎓 课程学习助手**
- 升学规划指导（保研/考研/留学）
- CS专业发展方向
- 学习资源推荐
- 科研项目指导

**💬 通用对话**
- 日常聊天交流
- 问题解答
- 校园生活咨询

请直接说出您的问题，我会自动识别并为您提供专业帮助！"""
    
    def _handle_general_chat(self, query: str) -> str:
        """处理通用对话"""
        return f"""💬 **通用对话助手**为您服务！

我理解您的问题："{query}"

作为校园智能助手，我主要专注于校园生活相关的服务，包括：
- 医疗报销和办事流程
- 联系人和部门查询  
- 学习规划和专业指导

如果您有这些方面的问题，我会为您提供详细帮助。如果是其他话题，我也可以尝试与您交流，但可能无法提供专业建议。

请告诉我您具体需要什么帮助？"""
    
    def get_skill_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return {
            "name": self.skill_name,
            "knowledge_categories": ["greeting", "general_chat"],
            "total_items": 0,
            "status": "active"
        }
    
    def get_supported_queries(self) -> List[str]:
        """获取支持的查询类型"""
        return [
            "问候语处理",
            "感谢回应", 
            "告别处理",
            "帮助请求",
            "通用对话"
        ]
    
    def get_quick_actions(self) -> List[Dict[str, str]]:
        """获取快速操作"""
        return [
            {"title": "问候", "query": "你好"},
            {"title": "帮助", "query": "你能做什么？"},
            {"title": "感谢", "query": "谢谢"},
            {"title": "告别", "query": "再见"}
        ]
