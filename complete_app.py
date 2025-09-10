#!/usr/bin/env python3
"""
完整版医疗报销智能助手 - 包含RAG功能
"""
import os
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 设置API密钥
os.environ["DASHSCOPE_API_KEY"] = "sk-2ea7b3f8fb7742828ff836eed6050f19"

# 创建应用
app = FastAPI(
    title="医疗报销智能助手",
    version="1.0.0",
    description="基于RAG技术的医疗报销智能问答系统"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟知识库数据
KNOWLEDGE_BASE = {
    "reimbursement_policies": [
        {
            "id": "policy_001",
            "title": "门诊报销政策",
            "content": "北京交通大学威海校区学生门诊医疗费用报销比例为80%，教职工为90%。报销时间窗口为就诊后30天内。需要提供医疗费用发票原件、病历本或诊断证明、学生证或工作证复印件、银行卡复印件。",
            "tags": ["门诊", "报销", "比例"]
        },
        {
            "id": "policy_002", 
            "title": "住院报销政策",
            "content": "住院医疗费用报销比例为85%，需要提供住院证明、费用清单、医疗费用发票原件、病历本、学生证或工作证复印件、银行卡复印件。报销时间窗口为出院后60天内。",
            "tags": ["住院", "报销", "材料"]
        }
    ],
    "materials_requirements": [
        {
            "id": "material_001",
            "title": "门诊报销材料清单",
            "content": "门诊报销需要提供：1. 医疗费用发票原件 2. 病历本或诊断证明 3. 学生证或工作证复印件 4. 银行卡复印件 5. 报销申请表",
            "tags": ["门诊", "材料", "清单"]
        }
    ],
    "contacts": [
        {
            "id": "contact_001",
            "title": "医疗报销负责人",
            "content": "负责老师：张老师，办公地点：行政楼201室，联系电话：0631-5688888，办公时间：周一至周五 8:00-17:00",
            "tags": ["联系人", "报销", "老师"]
        }
    ],
    "hospitals": [
        {
            "id": "hospital_001",
            "title": "威海市中心医院",
            "content": "地址：威海市环翠区文化中路，电话：0631-3806666，挂号方式：现场挂号或网上预约，转诊要求：需要校医院转诊证明",
            "tags": ["医院", "威海", "转诊"]
        }
    ],
    "common_questions": [
        {
            "id": "faq_001",
            "title": "感冒药能报销吗？",
            "content": "普通感冒药属于门诊用药，可以按照门诊报销政策进行报销，报销比例为80%。需要提供正规医院的处方和发票。",
            "tags": ["感冒", "药品", "报销"]
        }
    ]
}

def search_knowledge(query: str, limit: int = 3):
    """简单知识库搜索"""
    query_lower = query.lower()
    results = []
    
    for category, items in KNOWLEDGE_BASE.items():
        for item in items:
            score = 0
            
            # 标题匹配
            if query_lower in item["title"].lower():
                score += 3
            
            # 内容匹配
            if query_lower in item["content"].lower():
                score += 1
            
            # 标签匹配
            for tag in item["tags"]:
                if query_lower in tag.lower():
                    score += 2
            
            if score > 0:
                item_copy = item.copy()
                item_copy["score"] = score
                item_copy["category"] = category
                results.append(item_copy)
    
    # 按分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

def generate_answer(question: str, context_items: list):
    """生成回答（简化版，后续可集成通义千问）"""
    if not context_items:
        return "抱歉，我没有找到相关的政策信息。请尝试其他问题或联系负责老师。"
    
    # 构建回答
    answer = f"根据相关政策，我来为您解答：\n\n"
    
    for item in context_items:
        answer += f"📋 {item['title']}\n"
        answer += f"{item['content']}\n\n"
    
    answer += "💡 如需更详细信息，请联系负责老师：张老师 (0631-5688888)"
    
    return answer

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "🏥 医疗报销智能助手运行中！",
        "status": "ok",
        "version": "1.0.0",
        "web_interface": "/web",
        "api_docs": "/docs"
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api_key": "已配置",
        "knowledge_items": sum(len(items) for items in KNOWLEDGE_BASE.values())
    }

@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    """Web界面"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>医疗报销智能助手</title>
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
                max-width: 800px;
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
                white-space: pre-wrap;
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
            
            .message-time {
                font-size: 11px;
                opacity: 0.7;
                margin-top: 5px;
            }
            
            .sources {
                margin-top: 10px;
                padding: 10px;
                background: #e3f2fd;
                border-radius: 8px;
                font-size: 12px;
            }
            
            .sources h4 {
                margin-bottom: 5px;
                color: #1976d2;
            }
            
            .source-item {
                margin: 3px 0;
                padding: 3px 6px;
                background: white;
                border-radius: 4px;
                border-left: 3px solid #2196f3;
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
                <h1>🏥 医疗报销智能助手</h1>
                <p>北京交通大学威海校区 | 智能咨询服务</p>
            </div>
            
            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="message assistant">
                        <div class="message-content">
                            <div>👋 您好！我是医疗报销智能助手，可以为您解答关于医疗费用报销的各种问题。</div>
                            <div class="message-time" id="welcome-time"></div>
                        </div>
                    </div>
                </div>
                
                <div class="loading" id="loading">
                    <div>🤔 AI正在思考中...</div>
                </div>
            </div>
            
            <div class="quick-questions">
                <h4>💡 常见问题</h4>
                <div class="quick-buttons">
                    <button class="quick-button" onclick="askQuestion('感冒药能报销吗？')">感冒药能报销吗？</button>
                    <button class="quick-button" onclick="askQuestion('住院需要什么材料？')">住院需要什么材料？</button>
                    <button class="quick-button" onclick="askQuestion('报销找哪个老师？')">报销找哪个老师？</button>
                    <button class="quick-button" onclick="askQuestion('威海市中心医院地址在哪？')">威海市中心医院地址在哪？</button>
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
            // 设置欢迎时间
            document.getElementById('welcome-time').textContent = new Date().toLocaleTimeString();
            
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
            async function sendMessage() {
                const input = document.getElementById('questionInput');
                const question = input.value.trim();
                
                if (!question) return;
                
                // 清空输入框
                input.value = '';
                
                // 添加用户消息
                addMessage(question, 'user');
                
                // 显示加载状态
                showLoading(true);
                
                try {
                    const response = await fetch('/api/v1/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            question: question
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    
                    // 添加AI回答
                    addMessage(data.answer, 'assistant', data.sources, data.response_time);
                    
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('抱歉，服务暂时不可用，请稍后再试。', 'assistant');
                } finally {
                    showLoading(false);
                }
            }
            
            // 添加消息到聊天界面
            function addMessage(content, type, sources = null, responseTime = null) {
                const messagesContainer = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                let messageContent = `<div class="message-content">${content}</div>`;
                
                if (sources && sources.length > 0) {
                    messageContent += `<div class="sources">
                        <h4>📚 信息来源</h4>
                        ${sources.map(source => 
                            `<div class="source-item">${source.title} (${source.category})</div>`
                        ).join('')}
                    </div>`;
                }
                
                const timeText = responseTime ? 
                    `响应时间: ${responseTime.toFixed(2)}秒 | ${new Date().toLocaleTimeString()}` : 
                    new Date().toLocaleTimeString();
                
                messageContent += `<div class="message-time">${timeText}</div>`;
                
                messageDiv.innerHTML = messageContent;
                messagesContainer.appendChild(messageDiv);
                
                // 滚动到底部
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
            
            // 页面加载完成后聚焦输入框
            window.addEventListener('load', function() {
                document.getElementById('questionInput').focus();
            });
        </script>
    </body>
    </html>
    """

@app.get("/api/v1/health")
async def api_health():
    """API健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "knowledge_base": "healthy",
            "rag_engine": "simplified"
        }
    }

@app.post("/api/v1/ask")
async def ask_question(request: dict):
    """智能问答接口"""
    question = request.get("question", "")
    
    if not question:
        return {"error": "问题不能为空"}
    
    start_time = time.time()
    
    try:
        # 1. 搜索知识库
        context_items = search_knowledge(question, limit=3)
        
        # 2. 生成回答
        answer = generate_answer(question, context_items)
        
        # 3. 准备来源信息
        sources = []
        for item in context_items:
            sources.append({
                "id": item["id"],
                "title": item["title"],
                "category": item["category"],
                "score": item["score"]
            })
        
        response_time = time.time() - start_time
        
        return {
            "answer": answer,
            "sources": sources,
            "session_id": "demo_session",
            "response_time": response_time
        }
        
    except Exception as e:
        return {
            "error": f"处理问题时出错: {str(e)}",
            "answer": "抱歉，系统暂时无法处理您的问题，请稍后再试。"
        }

if __name__ == "__main__":
    print("🏥 医疗报销智能助手 - 完整版启动")
    print("=" * 50)
    print("📱 主页: http://localhost:8080")
    print("🌐 Web界面: http://localhost:8080/web")
    print("📚 API文档: http://localhost:8080/docs")
    print("🔍 健康检查: http://localhost:8080/health")
    print("=" * 50)
    print("💡 按 Ctrl+C 停止服务")
    print("")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
