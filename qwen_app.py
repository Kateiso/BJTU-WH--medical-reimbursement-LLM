#!/usr/bin/env python3
"""
通义千问集成版 - 医疗报销智能助手
"""
import os
import json
import time
from typing import List, Dict, Any
from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

# 导入通义千问集成模块
from src.core.rag.qwen_integration import QwenLLM

# 设置API密钥
os.environ["DASHSCOPE_API_KEY"] = "sk-2ea7b3f8fb7742828ff836eed6050f19"

# 创建应用
app = FastAPI(
    title="医疗报销智能助手",
    version="1.0.0",
    description="基于通义千问的医疗报销智能问答系统"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建通义千问实例
qwen_llm = QwenLLM()

# 加载知识库
def load_knowledge_base(file_path: str = "data/knowledge_base.json") -> Dict:
    """加载知识库"""
    try:
        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 使用示例知识库
            with open("data/knowledge_format.json", 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载知识库失败: {e}")
        return {"knowledge_base": {}}

# 加载知识库
knowledge_base = load_knowledge_base()

def search_knowledge(query: str, limit: int = 3) -> List[Dict]:
    """搜索知识库"""
    query_lower = query.lower()
    results = []
    
    for category, items in knowledge_base.get("knowledge_base", {}).items():
        for item in items:
            score = 0
            
            # 标题匹配
            if query_lower in item.get("title", "").lower():
                score += 3
            
            # 内容匹配
            if query_lower in item.get("content", "").lower():
                score += 1
            
            # 标签匹配
            for tag in item.get("tags", []):
                if query_lower in tag.lower():
                    score += 2
            
            if score > 0:
                item_copy = item.copy()
                item_copy["score"] = score
                item_copy["category"] = category
                results.append(item_copy)
    
    # 按分数排序
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results[:limit]

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
    # 检查通义千问API
    qwen_status = qwen_llm.health_check()
    
    return {
        "status": "healthy" if qwen_status["status"] == "healthy" else "degraded",
        "version": "1.0.0",
        "qwen_api": qwen_status,
        "knowledge_items": sum(len(items) for items in knowledge_base.get("knowledge_base", {}).values())
    }

@app.post("/api/v1/ask")
async def ask_question(request: Dict = Body(...)):
    """智能问答接口"""
    question = request.get("question", "")
    
    if not question:
        return {"error": "问题不能为空"}
    
    start_time = time.time()
    
    try:
        # 1. 搜索知识库
        context_items = search_knowledge(question, limit=3)
        
        # 2. 构建上下文
        context = ""
        for item in context_items:
            context += f"【{item['title']}】\n{item['content']}\n\n"
        
        # 3. 调用通义千问生成回答
        answer = qwen_llm.rag_generate(question, context)
        
        # 4. 准备来源信息
        sources = []
        for item in context_items:
            sources.append({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "category": item.get("category", ""),
                "score": item.get("score", 0)
            })
        
        response_time = time.time() - start_time
        
        return {
            "answer": answer,
            "sources": sources,
            "session_id": "qwen_session",
            "response_time": response_time
        }
        
    except Exception as e:
        return {
            "error": f"处理问题时出错: {str(e)}",
            "answer": "抱歉，系统暂时无法处理您的问题，请稍后再试。"
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
                <h1>🏥 医疗报销智能助手</h1>
                <p>北京交通大学威海校区 | 通义千问驱动</p>
            </div>
            
            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="message assistant">
                        <div class="message-content">
                            <div>👋 您好！我是医疗报销智能助手，由通义千问大模型驱动。我可以为您解答关于北京交通大学威海校区医疗报销的各种问题。</div>
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

if __name__ == "__main__":
    print("🏥 医疗报销智能助手 - 通义千问版启动")
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
