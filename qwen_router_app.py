#!/usr/bin/env python3
"""
新架构主应用 - 单入口对话+意图路由+多Ops-Skills
"""
import os
import json
import time
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, AsyncGenerator
from fastapi import FastAPI, Request, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

# 导入新架构组件
from src.core.router.intent_router import IntentRouter, SkillType, route_query
from src.core.skills.process_skill import ProcessSkill
from src.core.skills.contact_skill import ContactSkill
from src.core.skills.course_skill import CourseSkill
from src.core.skills.greeting_skill import GreetingSkill
from src.core.rag.qwen_stream_integration import QwenStreamLLM

# 创建应用
app = FastAPI(
    title="校园智能助手",
    version="2.0.0",
    description="基于意图路由的多域智能助手系统"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
intent_router = IntentRouter()
qwen_llm = QwenStreamLLM()

def get_skill_display_name(skill_type):
    """获取技能的中文显示名称"""
    skill_names = {
        SkillType.PROCESS: "办事流程助手",
        SkillType.CONTACT: "联系人助手", 
        SkillType.COURSE: "课程学习助手",
        SkillType.POLICY: "政策条款助手",
        SkillType.GREETING: "通用对话助手",
        SkillType.UNKNOWN: "未知技能"
    }
    return skill_names.get(skill_type, "处理中")

# 初始化Skills
skills = {
    SkillType.PROCESS: ProcessSkill(),
    SkillType.CONTACT: ContactSkill(),
    SkillType.COURSE: CourseSkill(),
    SkillType.GREETING: GreetingSkill(),
    # TODO: 后续添加 PolicySkill
}

# ==================== 访问统计功能 ====================
access_stats = {
    "total_visits": 0,
    "daily_visits": defaultdict(int),
    "hourly_visits": defaultdict(int),
    "unique_ips": set(),
    "endpoint_stats": defaultdict(int),
    "user_agents": Counter(),
    "skill_usage": defaultdict(int),
    "intent_accuracy": defaultdict(float),
    "last_reset": datetime.now().date()
}

def record_visit(request: Request, endpoint: str = "", skill_used: str = None):
    """记录访问统计"""
    global access_stats
    
    # 获取客户端IP
    client_ip = request.client.host
    if hasattr(request, 'headers') and 'x-forwarded-for' in request.headers:
        client_ip = request.headers['x-forwarded-for'].split(',')[0].strip()
    
    # 获取User-Agent
    user_agent = request.headers.get('user-agent', 'Unknown')
    
    # 记录统计
    access_stats["total_visits"] += 1
    access_stats["daily_visits"][datetime.now().date()] += 1
    access_stats["hourly_visits"][datetime.now().hour] += 1
    access_stats["unique_ips"].add(client_ip)
    access_stats["endpoint_stats"][endpoint] += 1
    access_stats["user_agents"][user_agent] += 1
    
    if skill_used:
        access_stats["skill_usage"][skill_used] += 1
    
    # 清理旧数据（保留最近30天）
    cutoff_date = datetime.now().date() - timedelta(days=30)
    access_stats["daily_visits"] = {
        d: v for d, v in access_stats["daily_visits"].items() 
        if d >= cutoff_date
    }
    
    # 打印访问日志
    print(f"📊 访问统计: {endpoint} | IP: {client_ip} | 技能: {skill_used} | 总访问: {access_stats['total_visits']}")

# ==================== 访问控制功能 ====================
rate_limit = {
    "requests": defaultdict(list),
    "max_requests_per_minute": 60,
    "max_requests_per_hour": 1000,
    "blocked_ips": set(),
    "whitelist": {
        "127.0.0.1",
        "::1",
    }
}

def check_rate_limit(client_ip: str) -> bool:
    """检查访问频率限制"""
    global rate_limit
    
    if client_ip in rate_limit["whitelist"]:
        return True
    
    if client_ip in rate_limit["blocked_ips"]:
        return False
    
    current_time = time.time()
    
    # 清理旧的时间戳
    rate_limit["requests"][client_ip] = [
        ts for ts in rate_limit["requests"][client_ip] 
        if current_time - ts < 3600
    ]
    
    # 检查每小时限制
    if len(rate_limit["requests"][client_ip]) >= rate_limit["max_requests_per_hour"]:
        rate_limit["blocked_ips"].add(client_ip)
        print(f"🚫 IP {client_ip} 因超过每小时限制被阻止")
        return False
    
    # 检查每分钟限制
    recent_requests = [
        ts for ts in rate_limit["requests"][client_ip] 
        if current_time - ts < 60
    ]
    
    if len(recent_requests) >= rate_limit["max_requests_per_minute"]:
        print(f"⚠️ IP {client_ip} 超过每分钟限制，但未阻止")
        return True
    
    # 记录当前请求
    rate_limit["requests"][client_ip].append(current_time)
    return True

# 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

# ==================== 核心路由逻辑 ====================
async def process_query_with_router(query: str) -> Dict[str, Any]:
    """使用意图路由器处理查询"""
    try:
        # 1. 意图识别
        intent_result = route_query(query)
        print(f"🎯 意图识别: {intent_result.skill.value} (置信度: {intent_result.confidence:.2f})")
        
        # 2. 路由到对应Skill
        if intent_result.skill in skills:
            skill = skills[intent_result.skill]
            skill_result = await skill.process_query(
                query, 
                intent_result.entities, 
                intent_result.filters
            )
            
            # 记录技能使用统计
            access_stats["skill_usage"][intent_result.skill.value] += 1
            access_stats["intent_accuracy"][intent_result.skill.value] = intent_result.confidence
            
            return {
                "success": skill_result.success,
                "content": skill_result.content,
                "sources": skill_result.sources,
                "confidence": skill_result.confidence,
                "skill_used": get_skill_display_name(intent_result.skill),
                "intent_confidence": intent_result.confidence,
                "entities": intent_result.entities,
                "metadata": skill_result.metadata
            }
        else:
            # 3. 兜底处理 - 使用通用LLM
            print(f"⚠️ 未找到对应技能，使用通用LLM处理")
            return await fallback_to_llm(query, intent_result)
            
    except Exception as e:
        print(f"❌ 路由处理出错: {e}")
        return {
            "success": False,
            "content": f"处理查询时出错: {str(e)}",
            "sources": [],
            "confidence": 0.0,
            "skill_used": "error",
            "intent_confidence": 0.0,
            "entities": {},
            "metadata": {"error": str(e)}
        }

async def fallback_to_llm(query: str, intent_result) -> Dict[str, Any]:
    """兜底处理 - 使用通用LLM"""
    try:
        # 构建通用上下文
        context = f"用户查询: {query}\n"
        context += f"识别意图: {intent_result.skill.value}\n"
        context += f"置信度: {intent_result.confidence}\n"
        context += f"实体: {intent_result.entities}\n"
        
        # 使用智能回复生成（不依赖外部LLM）
        response = generate_intelligent_response(query, intent_result)
        
        return {
            "success": True,
            "content": response,
            "sources": [],
            "confidence": 0.5,
            "skill_used": "intelligent_fallback",
            "intent_confidence": intent_result.confidence,
            "entities": intent_result.entities,
            "metadata": {"fallback": True}
        }
    except Exception as e:
        return {
            "success": False,
            "content": f"系统暂时无法处理您的查询，请稍后再试。",
            "sources": [],
            "confidence": 0.0,
            "skill_used": "error",
            "intent_confidence": 0.0,
            "entities": {},
            "metadata": {"error": str(e)}
        }

def generate_intelligent_response(query: str, intent_result) -> str:
    """生成智能回复"""
    query_lower = query.lower()
    skill_type = intent_result.skill.value
    
    # 根据意图类型生成相应回复
    if skill_type == "greeting":
        return generate_greeting_response(query)
    elif skill_type == "process":
        return generate_process_response(query)
    elif skill_type == "contact":
        return generate_contact_response(query)
    elif skill_type == "course":
        return generate_course_response(query)
    else:
        return generate_general_response(query)

def generate_greeting_response(query: str) -> str:
    """生成问候回复"""
    if any(word in query.lower() for word in ['你好', 'hello', 'hi', '嗨']):
        return """👋 **通用对话助手**为您服务！

您好！我是校园智能助手，很高兴为您服务！

🎯 **我可以帮您处理**：
- 🏥 **医疗报销** - 报销流程、材料要求、比例标准
- 📞 **联系人查询** - 老师联系方式、部门信息
- 🎓 **学习指导** - 升学规划、专业发展、科研指导
- 💬 **日常对话** - 聊天交流、问题解答

请告诉我您需要什么帮助，我会尽力为您提供准确的信息！"""
    elif any(word in query.lower() for word in ['谢谢', '感谢', 'thank']):
        return """😊 **通用对话助手**为您服务！

不客气！很高兴能帮助到您！

如果您还有其他问题，随时可以问我。我会继续为您提供校园生活各方面的帮助。

祝您学习生活愉快！✨"""
    else:
        return f"""💬 **通用对话助手**为您服务！

我理解您的问题："{query}"

作为校园智能助手，我主要专注于校园生活相关的服务。请告诉我您具体需要什么帮助？"""

def generate_process_response(query: str) -> str:
    """生成办事流程回复"""
    if any(word in query.lower() for word in ['报销', '医疗', '医药费']):
        return """🏥 **办事流程助手**为您服务！

关于医疗报销，我为您整理了以下信息：

**1. 门诊报销流程**
1. 企业微信联系常春艳老师预约办理时间
2. 按预约时间携资料到思源东楼812B登记
3. 审核入账 → 款项打入学校备案银行卡

**2. 报销比例**
- 学生：南海新区医院/校医务室报销90%
- 合同医院/专科报销85%
- 住院报销95%

**3. 所需材料**
- 发票或电子发票（医院章）
- 处方笺（手写或打印）
- 检查报告单（≥200元检查须附结果）

📚 *来源: 报销流程知识库*

📞 **联系方式**
- 医保办：常春艳老师，思源东楼812B
- 企业微信联系（优先）"""
    else:
        return f"""🏥 **办事流程助手**为您服务！

关于您的问题："{query}"

我主要处理医疗报销、学籍管理、宿舍申请等办事流程相关的问题。

请告诉我您具体需要办理什么手续，我会为您提供详细的流程指导。"""

def generate_contact_response(query: str) -> str:
    """生成联系人回复"""
    if any(word in query.lower() for word in ['常春艳', '医保办', '报销']):
        return """📞 **联系人助手**为您服务！

关于老师信息，我为您整理了以下联系方式：

**1. 医保办联系人**
👤 **姓名**: 常春艳
🏢 **部门**: 医保办
💼 **职位**: 预约与受理
📍 **办公地点**: 思源东楼812B
📱 **联系方式**: 企业微信（优先）；电话未公开
🕒 **服务时间**: 未固定对外时段，先预约

📚 *来源: 联系人知识库*

📞 **常用联系方式**
- 学校总机：0631-3803000
- 学生处：0631-3803001"""
    else:
        return f"""📞 **联系人助手**为您服务！

关于您的问题："{query}"

我可以帮您查询老师联系方式、部门信息、办公地点等。

请告诉我您需要联系哪位老师或哪个部门，我会为您提供准确的联系信息。"""

def generate_course_response(query: str) -> str:
    """生成课程学习回复"""
    if any(word in query.lower() for word in ['保研', '考研', '留学', '升学']):
        return """🎓 **课程学习助手**为您服务！

关于升学规划，我为您整理了以下指导信息：

**1. 申请材料四件套清单**
1) 成绩单：保研重均分/专业排名；海外申请重视成绩但不纠结细枝末节
2) 英语成绩：国内保研一般接受CET-6/IELTS/TOEFL之一
3) 推荐信：2-3封，来自导师或实习导师
4) 个人陈述：突出研究兴趣和学术背景

**2. 决策框架**
优先自问5题：
1) 经济承受力（学费+生活费）
2) 准备与等待周期能否接受
3) 文化适应度与成长空间
4) 职业长期收益（认可度、毕业周期）
5) 个人兴趣与专业匹配度

📚 *来源: 职业规划知识库*

**建议**：根据个人情况综合考虑，选择最适合的发展路径。"""
    elif any(word in query.lower() for word in ['cs', '计算机', '专业', '方向']):
        return """🎓 **课程学习助手**为您服务！

关于CS专业发展，我为您整理了以下指导：

**1. CS方向选择与组合**
评估三要素：
1) 学习难度与周期（达成目标所需时间）
2) 项目获取便捷度（实习/科研/自建途径）
3) 与职业路径的直接相关度

**2. 建议组合拳**
- Software+Web+Cloud+Mobile
- AI+Robotics/AI+Security
- 形成可讲述的跨域"故事线"

**3. 学习资源推荐**
- CS自学指南、Coursera
- 公开GitHub课程仓库
- MIT Missing Semester课程

📚 *来源: 学习资源知识库*

**建议**：选择感兴趣的方向深入学习，同时保持技术栈的多样性。"""
    else:
        return f"""🎓 **课程学习助手**为您服务！

关于您的问题："{query}"

我主要提供升学规划、专业发展、学习资源等方面的指导。

请告诉我您具体想了解哪个方面的学习指导，我会为您提供详细的建议。"""

def generate_general_response(query: str) -> str:
    """生成通用回复"""
    return f"""🤖 **通用对话助手**为您服务！

我理解您的问题："{query}"

作为校园智能助手，我主要专注于校园生活相关的服务，包括：
- 医疗报销和办事流程
- 联系人和部门查询  
- 学习规划和专业指导

如果您有这些方面的问题，我会为您提供详细帮助。如果是其他话题，我也可以尝试与您交流。

请告诉我您具体需要什么帮助？"""

# ==================== API端点 ====================
@app.get("/")
async def root(request: Request):
    """根路径 - 自动重定向到Web界面"""
    record_visit(request, "/")
    return RedirectResponse(url="/web", status_code=302)

@app.get("/web", response_class=HTMLResponse)
async def web_interface(request: Request):
    """Web界面 - 重定向到新的统一对话界面"""
    record_visit(request, "/web")
    return RedirectResponse(url="/ask", status_code=302)

@app.get("/ask", response_class=HTMLResponse)
async def ask_interface(request: Request):
    """新的统一对话界面"""
    record_visit(request, "/ask")
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>校园智能助手</title>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/styles/github.css">
        <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/lib/highlight.min.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                width: 90%;
                max-width: 900px;
                max-height: 90vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 24px;
                margin-bottom: 5px;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 14px;
            }
            
            .skill-indicator {
                background: rgba(255,255,255,0.2);
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 12px;
                margin-top: 10px;
                display: inline-block;
            }
            
            .chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                min-height: 400px;
            }
            
            .messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                max-height: 400px;
            }
            
            .message {
                margin-bottom: 15px;
                display: flex;
                align-items: flex-start;
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message-content {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                word-wrap: break-word;
            }
            
            .message.user .message-content {
                background: #007bff;
                color: white;
                border-bottom-right-radius: 5px;
            }
            
            .message.assistant .message-content {
                background: #f8f9fa;
                color: #333;
                border: 1px solid #e9ecef;
                border-bottom-left-radius: 5px;
            }
            
            .skill-badge {
                background: #e3f2fd;
                color: #1976d2;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 11px;
                margin-bottom: 8px;
                display: inline-block;
            }
            
            .markdown-body {
                font-size: 14px;
                line-height: 1.6;
            }
            
            .sources {
                margin-top: 10px;
                padding: 10px;
                background: #e8f5e8;
                border-radius: 8px;
                font-size: 12px;
            }
            
            .sources h4 {
                margin-bottom: 5px;
                color: #2e7d32;
            }
            
            .source-item {
                margin: 3px 0;
                padding: 3px 6px;
                background: white;
                border-radius: 4px;
                border-left: 3px solid #4caf50;
            }
            
            .input-container {
                padding: 20px;
                border-top: 1px solid #e9ecef;
                background: #f8f9fa;
            }
            
            .input-group {
                display: flex;
                gap: 10px;
            }
            
            .input-field {
                flex: 1;
                padding: 12px 16px;
                border: 2px solid #e9ecef;
                border-radius: 25px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            .input-field:focus {
                border-color: #007bff;
            }
            
            .send-button {
                padding: 12px 24px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: background 0.3s;
            }
            
            .send-button:hover:not(:disabled) {
                background: #0056b3;
            }
            
            .send-button:disabled {
                background: #6c757d;
                cursor: not-allowed;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #6c757d;
            }
            
            .loading.show {
                display: block;
            }
            
            .typing-indicator {
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }
            
            .typing-dot {
                width: 8px;
                height: 8px;
                background: #007bff;
                border-radius: 50%;
                animation: typing 1.4s infinite;
            }
            
            .typing-dot:nth-child(2) {
                animation-delay: 0.2s;
            }
            
            .typing-dot:nth-child(3) {
                animation-delay: 0.4s;
            }
            
            @keyframes typing {
                0%, 60%, 100% {
                    transform: translateY(0);
                }
                30% {
                    transform: translateY(-10px);
                }
            }
            
            .quick-questions {
                padding: 15px 20px;
                background: #f8f9fa;
                border-top: 1px solid #e9ecef;
            }
            
            .quick-questions h4 {
                margin-bottom: 10px;
                color: #495057;
                font-size: 14px;
            }
            
            .quick-buttons {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }
            
            .quick-button {
                padding: 6px 12px;
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 15px;
                cursor: pointer;
                font-size: 12px;
                color: #495057;
                transition: all 0.3s;
            }
            
            .quick-button:hover {
                background: #007bff;
                color: white;
                border-color: #007bff;
            }
            
            @media (max-width: 600px) {
                .container {
                    width: 95%;
                    margin: 10px;
                }
                
                .message-content {
                    max-width: 85%;
                }
                
                .input-group {
                    flex-direction: column;
                }
                
                .send-button {
                    align-self: flex-end;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 校园智能助手</h1>
                <p>北京交通大学威海校区 | 智能路由+多域Agent</p>
                <div class="skill-indicator" id="skillIndicator">准备就绪</div>
            </div>
            
            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="message assistant">
                        <div class="message-content">
                            <div class="skill-badge">系统助手</div>
                            <div class="markdown-body">👋 您好！我是校园智能助手，采用最新的意图路由技术，可以智能识别您的需求并调用专业Agent为您服务。</div>
                            <div class="message-time" id="welcome-time"></div>
                        </div>
                    </div>
                </div>
                
                <div class="loading" id="loading">
                    <div class="typing-indicator">
                        <span>AI正在思考</span>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
            
            <div class="quick-questions">
                <h4>💡 快速体验</h4>
                <div class="quick-buttons">
                    <button class="quick-button" onclick="askQuestion('感冒药能报销吗？')">医疗报销</button>
                    <button class="quick-button" onclick="askQuestion('常春艳老师联系方式？')">联系人查询</button>
                    <button class="quick-button" onclick="askQuestion('保研考研留学怎么选择？')">升学规划</button>
                    <button class="quick-button" onclick="askQuestion('CS专业有哪些发展方向？')">专业指导</button>
                    <button class="quick-button" onclick="askQuestion('如何开始科研项目？')">科研指导</button>
                    <button class="quick-button" onclick="askQuestion('你好，小助')">问候测试</button>
                </div>
            </div>
            
            <div class="input-container">
                <div class="input-group">
                    <input 
                        type="text" 
                        class="input-field" 
                        id="questionInput" 
                        placeholder="请输入您的问题..."
                        maxlength="500"
                    >
                    <button class="send-button" id="sendButton" onclick="sendMessage()">
                        发送
                    </button>
                </div>
            </div>
        </div>

        <script>
            // 初始化WebSocket连接
            let socket = null;
            let currentMessageDiv = null;
            let currentMessageContent = "";
            
            // 连接WebSocket
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                socket = new WebSocket(wsUrl);
                
                socket.onopen = function(e) {
                    console.log("WebSocket连接已建立");
                    document.getElementById('sendButton').disabled = false;
                    document.getElementById('sendButton').textContent = '发送';
                    document.getElementById('skillIndicator').textContent = '连接成功';
                    showLoading(false);
                };
                
                socket.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
                
                socket.onclose = function(event) {
                    console.log("WebSocket连接已关闭");
                    document.getElementById('sendButton').disabled = true;
                    document.getElementById('skillIndicator').textContent = '连接断开';
                    showLoading(false);
                    setTimeout(connectWebSocket, 2000);
                };
                
                socket.onerror = function(error) {
                    console.error("WebSocket错误:", error);
                    document.getElementById('skillIndicator').textContent = '连接错误';
                    showLoading(false);
                };
            }
            
            // 处理WebSocket消息
            function handleWebSocketMessage(data) {
                console.log("收到WebSocket消息:", data.type);
                
                switch(data.type) {
                    case "start":
                        currentMessageDiv = document.createElement('div');
                        currentMessageDiv.className = "message assistant";
                        currentMessageContent = "";
                        
                        const contentDiv = document.createElement('div');
                        contentDiv.className = "message-content";
                        
                        const skillBadge = document.createElement('div');
                        skillBadge.className = "skill-badge";
                        skillBadge.textContent = data.skill_used || "处理中";
                        contentDiv.appendChild(skillBadge);
                        
                        const markdownDiv = document.createElement('div');
                        markdownDiv.className = "markdown-body";
                        markdownDiv.id = "current-markdown";
                        contentDiv.appendChild(markdownDiv);
                        
                        currentMessageDiv.appendChild(contentDiv);
                        document.getElementById('messages').appendChild(currentMessageDiv);
                        showLoading(true);
                        break;
                        
                    case "chunk":
                        if (!document.getElementById("current-markdown")) {
                            handleWebSocketMessage({type: "start"});
                        }
                        
                        currentMessageContent += data.content;
                        try {
                            document.getElementById("current-markdown").innerHTML = marked.parse(currentMessageContent);
                            document.querySelectorAll('pre code').forEach((block) => {
                                hljs.highlightBlock(block);
                            });
                            
                            const messagesContainer = document.getElementById('messages');
                            messagesContainer.scrollTop = messagesContainer.scrollHeight;
                        } catch (error) {
                            console.error("渲染Markdown时出错:", error);
                        }
                        break;
                        
                    case "sources":
                        if (currentMessageDiv && data.content && data.content.length > 0) {
                            const messageContent = currentMessageDiv.querySelector('.message-content');
                            
                            const sourcesDiv = document.createElement('div');
                            sourcesDiv.className = "sources";
                            
                            const sourcesTitle = document.createElement('h4');
                            sourcesTitle.textContent = "📚 信息来源";
                            sourcesDiv.appendChild(sourcesTitle);
                            
                            data.content.forEach(source => {
                                const sourceItem = document.createElement('div');
                                sourceItem.className = "source-item";
                                sourceItem.textContent = `${source.title} (${source.category})`;
                                sourcesDiv.appendChild(sourceItem);
                            });
                            
                            messageContent.appendChild(sourcesDiv);
                        }
                        break;
                        
                    case "end":
                        if (currentMessageDiv) {
                            const messageContent = currentMessageDiv.querySelector('.message-content');
                            
                            const timeDiv = document.createElement('div');
                            timeDiv.className = "message-time";
                            timeDiv.textContent = new Date().toLocaleTimeString();
                            
                            messageContent.appendChild(timeDiv);
                            
                            const markdownDiv = document.getElementById("current-markdown");
                            if (markdownDiv) {
                                markdownDiv.removeAttribute("id");
                            }
                            
                            currentMessageDiv = null;
                            showLoading(false);
                        } else {
                            showLoading(false);
                        }
                        break;
                        
                    case "error":
                        addMessage(data.content, 'assistant');
                        showLoading(false);
                        break;
                        
                    default:
                        console.warn("未知的消息类型:", data.type);
                        showLoading(false);
                }
            }
            
            // 设置欢迎时间
            document.getElementById('welcome-time').textContent = new Date().toLocaleTimeString();
            
            // 连接WebSocket
            connectWebSocket();
            
            // 回车发送消息
            document.getElementById('questionInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // 快速提问
            function askQuestion(question) {
                document.getElementById('questionInput').value = question;
                sendMessage();
            }
            
            // 发送消息
            function sendMessage() {
                const input = document.getElementById('questionInput');
                const question = input.value.trim();
                
                if (!question) {
                    return;
                }
                
                if (!socket || socket.readyState !== WebSocket.OPEN) {
                    alert("服务器连接已断开，请刷新页面重试");
                    return;
                }
                
                input.value = '';
                addMessage(question, 'user');
                showLoading(true);
                
                try {
                    socket.send(JSON.stringify({
                        question: question
                    }));
                } catch (error) {
                    console.error("发送消息失败:", error);
                    showLoading(false);
                    alert("发送消息失败，请刷新页面重试");
                }
            }
            
            // 添加消息到聊天界面
            function addMessage(content, type) {
                const messagesContainer = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = "message-content";
                
                if (type === 'user') {
                    contentDiv.textContent = content;
                } else {
                    const markdownDiv = document.createElement('div');
                    markdownDiv.className = "markdown-body";
                    markdownDiv.innerHTML = marked.parse(content);
                    contentDiv.appendChild(markdownDiv);
                }
                
                const timeDiv = document.createElement('div');
                timeDiv.className = "message-time";
                timeDiv.textContent = new Date().toLocaleTimeString();
                contentDiv.appendChild(timeDiv);
                
                messageDiv.appendChild(contentDiv);
                messagesContainer.appendChild(messageDiv);
                
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            // 显示/隐藏加载状态
            function showLoading(show) {
                const loading = document.getElementById('loading');
                const sendButton = document.getElementById('sendButton');
                
                if (show) {
                    loading.classList.add('show');
                    sendButton.disabled = true;
                    sendButton.textContent = '发送中...';
                } else {
                    loading.classList.remove('show');
                    sendButton.disabled = false;
                    sendButton.textContent = '发送';
                }
            }
            
            // 初始化Markdown渲染器
            marked.setOptions({
                renderer: new marked.Renderer(),
                highlight: function(code, language) {
                    const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
                    return hljs.highlight(validLanguage, code).value;
                },
                pedantic: false,
                gfm: true,
                breaks: true,
                sanitize: false,
                smartLists: true,
                smartypants: false,
                xhtml: false
            });
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health(request: Request):
    """健康检查"""
    record_visit(request, "/health")
    
    # 检查各组件状态
    qwen_status = qwen_llm.health_check()
    skills_status = {}
    
    for skill_type, skill in skills.items():
        skills_status[skill_type.value] = skill.get_skill_info()
    
    return {
        "status": "healthy" if qwen_status["status"] == "healthy" else "degraded",
        "version": "2.0.0",
        "architecture": "intent_router_multi_skills",
        "qwen_api": qwen_status,
        "skills": skills_status,
        "total_skills": len(skills)
    }

@app.get("/stats")
async def get_stats(request: Request):
    """获取访问统计"""
    global access_stats
    
    record_visit(request, "/stats")
    
    # 计算今日访问量
    today = datetime.now().date()
    today_visits = access_stats["daily_visits"].get(today, 0)
    
    # 计算昨日访问量
    yesterday = today - timedelta(days=1)
    yesterday_visits = access_stats["daily_visits"].get(yesterday, 0)
    
    # 计算本周访问量
    week_start = today - timedelta(days=today.weekday())
    week_visits = sum(
        v for d, v in access_stats["daily_visits"].items() 
        if d >= week_start
    )
    
    # 计算最活跃的小时
    most_active_hour = max(access_stats["hourly_visits"].items(), key=lambda x: x[1]) if access_stats["hourly_visits"] else (0, 0)
    
    # 计算最受欢迎的端点
    most_popular_endpoint = max(access_stats["endpoint_stats"].items(), key=lambda x: x[1]) if access_stats["endpoint_stats"] else ("", 0)
    
    # 计算最常用的技能
    most_used_skill = max(access_stats["skill_usage"].items(), key=lambda x: x[1]) if access_stats["skill_usage"] else ("", 0)
    
    return {
        "total_visits": access_stats["total_visits"],
        "unique_visitors": len(access_stats["unique_ips"]),
        "today_visits": today_visits,
        "yesterday_visits": yesterday_visits,
        "week_visits": week_visits,
        "most_active_hour": f"{most_active_hour[0]}:00-{most_active_hour[0]+1}:00",
        "most_popular_endpoint": most_popular_endpoint[0],
        "most_used_skill": most_used_skill[0],
        "endpoint_stats": dict(access_stats["endpoint_stats"]),
        "skill_usage": dict(access_stats["skill_usage"]),
        "intent_accuracy": dict(access_stats["intent_accuracy"]),
        "daily_visits_last_7_days": {
            str(d): v for d, v in sorted(access_stats["daily_visits"].items())[-7:]
        },
        "hourly_distribution": dict(access_stats["hourly_visits"]),
        "top_user_agents": dict(access_stats["user_agents"].most_common(5)),
        "last_updated": datetime.now().isoformat()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点 - 支持流式输出"""
    # 获取客户端IP
    client_ip = websocket.client.host
    if hasattr(websocket, 'headers') and 'x-forwarded-for' in websocket.headers:
        client_ip = websocket.headers['x-forwarded-for'].split(',')[0].strip()
    
    # 检查访问频率限制
    if not check_rate_limit(client_ip):
        await websocket.close(code=1008, reason="访问频率过高，请稍后再试")
        return
    
    await manager.connect(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                request_data = json.loads(data)
                question = request_data.get("question", "").strip()
                
                # 输入验证
                if not question:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "问题不能为空"
                    }))
                    continue
                
                if len(question) > 500:
                    await websocket.send_text(json.dumps({
                        "type": "error", 
                        "message": "问题长度不能超过500字符"
                    }))
                    continue
                
                # 恶意输入检测
                dangerous_patterns = ['<script', 'javascript:', 'eval(', 'exec(', 'import os', 'subprocess']
                if any(pattern in question.lower() for pattern in dangerous_patterns):
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "输入包含不安全内容，请重新输入"
                    }))
                    continue
                
                # 发送开始标记
                await manager.send_message(json.dumps({
                    "type": "start",
                    "question": question
                }), websocket)
                
                try:
                    # 使用新的路由系统处理查询
                    result = await process_query_with_router(question)
                    
                    # 发送技能信息
                    await manager.send_message(json.dumps({
                        "type": "skill_info",
                        "skill_used": result.get("skill_used", "unknown"),
                        "intent_confidence": result.get("intent_confidence", 0.0),
                        "entities": result.get("entities", {})
                    }), websocket)
                    
                    # 发送源信息
                    if result.get("sources"):
                        await manager.send_message(json.dumps({
                            "type": "sources",
                            "content": result["sources"]
                        }), websocket)
                    
                    # 流式发送回答内容
                    content = result.get("content", "")
                    if content:
                        # 模拟流式输出
                        words = content.split()
                        for i in range(0, len(words), 3):  # 每次发送3个词
                            chunk = " ".join(words[i:i+3])
                            if i + 3 < len(words):
                                chunk += " "
                            
                            await manager.send_message(json.dumps({
                                "type": "chunk",
                                "content": chunk
                            }), websocket)
                            
                            # 添加小延迟模拟流式效果
                            await asyncio.sleep(0.05)
                    
                    # 发送完成标记
                    await manager.send_message(json.dumps({
                        "type": "end",
                        "confidence": result.get("confidence", 0.0)
                    }), websocket)
                    
                except Exception as e:
                    await manager.send_message(json.dumps({
                        "type": "error",
                        "content": f"处理问题时出错: {str(e)}"
                    }), websocket)
                
            except WebSocketDisconnect:
                print("WebSocket连接已断开")
                break
            except Exception as e:
                print(f"处理WebSocket消息时出错: {str(e)}")
                try:
                    await manager.send_message(json.dumps({
                        "type": "error",
                        "content": "服务器处理请求时出错，请刷新页面重试"
                    }), websocket)
                except Exception:
                    print("无法发送错误消息，连接可能已断开")
                    break
                
    except WebSocketDisconnect:
        print("WebSocket连接已断开")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket处理过程中出错: {str(e)}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("🎓 校园智能助手 - 新架构启动")
    print("=" * 50)
    print("🏗️ 架构: 单入口对话 + 意图路由 + 多Ops-Skills")
    print("🎯 技能: Process, Contact, Course, Policy")
    print("📚 知识库: 分片存储，智能检索")
    print("=" * 50)
    
    # 从环境变量读取端口
    PORT = int(os.getenv("PORT", "8081"))
    
    print(f"📱 主页: http://localhost:{PORT}")
    print(f"🌐 对话界面: http://localhost:{PORT}/ask")
    print(f"📚 API文档: http://localhost:{PORT}/docs")
    print(f"🔍 健康检查: http://localhost:{PORT}/health")
    print(f"📊 访问统计: http://localhost:{PORT}/stats")
    print("=" * 50)
    print("💡 按 Ctrl+C 停止服务")
    print("")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
