#!/usr/bin/env python3
"""
通义千问集成版 - 医疗报销智能助手 (流式输出 + Markdown渲染)
"""
import os
import json
import time
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from fastapi import FastAPI, Request, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

# 导入通义千问集成模块
from src.core.rag.qwen_stream_integration import QwenStreamLLM

# 从环境变量读取API密钥（部署时通过环境变量注入）
# 本地开发时可在shell中执行：export DASHSCOPE_API_KEY=your_key
# 或在.env文件中设置（需要python-dotenv包）

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
qwen_llm = QwenStreamLLM()

# 加载知识库
def load_knowledge_base(file_path: str = "data/knowledge_base.json") -> Dict:
    """加载知识库 - 强制使用真实数据"""
    print("\n" + "="*50)
    print("开始加载知识库...")
    
    # 强制使用指定的知识库文件
    if not Path(file_path).exists():
        raise FileNotFoundError(f"严重错误: 知识库文件不存在: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f"正在读取知识库文件: {file_path}")
            file_content = f.read()
            print(f"文件大小: {len(file_content)} 字节")
            
            # 解析JSON
            data = json.loads(file_content)
            
            # 验证知识库结构
            if 'knowledge_base' not in data:
                raise ValueError("知识库文件缺少 'knowledge_base' 字段")
            
            # 获取知识库数据
            knowledge_items = data.get('knowledge_base', [])
            if not knowledge_items:
                raise ValueError("知识库为空")
            
            # 按分类组织知识库
            categorized_data = {}
            for item in knowledge_items:
                category = item.get("category", "unknown")
                if category not in categorized_data:
                    categorized_data[category] = []
                categorized_data[category].append(item)
            
            # 打印详细统计信息
            print("\n知识库加载统计:")
            total_items = 0
            for category, items in categorized_data.items():
                item_count = len(items)
                total_items += item_count
                print(f"- {category}: {item_count} 条")
            
            print(f"\n知识库加载成功! 共 {total_items} 条知识项")
            print("="*50 + "\n")
            
            # 返回重组后的数据
            return {"knowledge_base": categorized_data}
            
    except json.JSONDecodeError as je:
        error_msg = f"知识库文件JSON格式错误: {je}"
        print(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"加载知识库时出错: {e}"
        print(error_msg)
        raise RuntimeError(error_msg)

# 加载知识库 - 使用绝对路径确保正确加载
KNOWLEDGE_BASE_PATH = str(Path(__file__).parent / "data" / "knowledge_base.json")
print(f"知识库绝对路径: {KNOWLEDGE_BASE_PATH}")
knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_PATH)

def search_knowledge(query: str, limit: int = 5) -> List[Dict]:
    """搜索知识库 - 彻底重写版"""
    print("\n" + "-"*50)
    print(f"收到用户查询: '{query}'")
    
    # 确保知识库已加载
    if not knowledge_base or not knowledge_base.get("knowledge_base"):
        print("错误: 知识库未正确加载")
        return []
    
    query_lower = query.lower()
    results = []
    
    # 1. 提取关键词
    keywords = extract_keywords(query_lower)
    print(f"提取关键词: {keywords}")
    
    # 2. 特殊关键词处理 - 针对北交威海校区特定词汇
    special_keywords = detect_special_keywords(query_lower)
    if special_keywords:
        print(f"检测到特殊关键词: {special_keywords}")
        keywords.extend(special_keywords)
    
    # 3. 搜索所有知识分类
    print("\n开始搜索知识库...")
    for category, items in knowledge_base.get("knowledge_base", {}).items():
        print(f"搜索分类: {category} ({len(items)}条)")
        
        for item in items:
            score = calculate_item_score(item, query_lower, keywords, category)
            
            if score > 0:
                item_copy = item.copy()
                item_copy["score"] = score
                item_copy["category"] = category
                results.append(item_copy)
    
    # 4. 按分数排序
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # 5. 打印搜索结果
    print(f"\n找到 {len(results)} 条匹配结果")
    if results:
        print("\n排名前 {min(limit, len(results))} 条结果:")
        for i, result in enumerate(results[:limit]):
            print(f"结果 {i+1}: [{result.get('category')}] {result.get('title')} (分数: {result.get('score')})")
            # 打印匹配的内容摘要
            content = result.get('content', '')
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"   内容: {content}")
    else:
        print("未找到匹配结果")
    
    print("-"*50 + "\n")
    
    # 6. 如果没有找到结果，返回一些默认项
    if not results:
        # 添加一些默认的常见问题作为兜底
        for category, items in knowledge_base.get("knowledge_base", {}).items():
            if category == "common_questions" and items:
                for item in items[:2]:  # 取前两个常见问题
                    item_copy = item.copy()
                    item_copy["score"] = 0.1  # 很低的分数
                    item_copy["category"] = category
                    item_copy["is_fallback"] = True  # 标记为兜底结果
                    results.append(item_copy)
    
    return results[:limit]

def calculate_item_score(item: Dict, query: str, keywords: List[str], category: str) -> float:
    """计算知识项的匹配分数"""
    score = 0
    
    # 获取各字段的小写版本
    title_lower = item.get("title", "").lower()
    content_lower = item.get("content", "").lower()
    tags = [tag.lower() for tag in item.get("tags", [])]
    
    # 1. 完全匹配加高分
    if query in title_lower:
        score += 10
        print(f"  - 标题完全匹配: {item.get('title')} (+10)")
    
    if query in content_lower:
        score += 6
        print(f"  - 内容完全匹配: {item.get('id')} (+6)")
    
    # 2. 关键词匹配
    for keyword in keywords:
        # 标题关键词匹配
        if keyword in title_lower:
            score += 5
            print(f"  - 标题关键词匹配: {keyword} in {item.get('title')} (+5)")
        
        # 内容关键词匹配
        if keyword in content_lower:
            score += 3
            print(f"  - 内容关键词匹配: {keyword} in {item.get('id')} (+3)")
        
        # 标签关键词匹配
        for tag in tags:
            if keyword in tag:
                score += 4
                print(f"  - 标签关键词匹配: {keyword} in {tag} (+4)")
    
    # 3. 特定字段匹配
    
    # 问候匹配
    if category == "greetings" and "scenarios" in item:
        scenarios = item.get("scenarios", [])
        for scenario in scenarios:
            input_text = scenario.get("input", "").lower()
            if query == input_text or query in input_text:
                score += 20  # 问候完全匹配给最高分
                print(f"  - 问候完全匹配: {input_text} (+20)")
                break
            
            # 问候关键词匹配
            for keyword in keywords:
                if keyword in input_text:
                    score += 10
                    print(f"  - 问候关键词匹配: {keyword} in {input_text} (+10)")
    
    # FAQ问题匹配
    if "question" in item:
        question_lower = item.get("question", "").lower()
        if query in question_lower:
            score += 12  # FAQ问题完全匹配给较高分
            print(f"  - FAQ问题完全匹配: {item.get('question')} (+12)")
        
        # FAQ问题关键词匹配
        for keyword in keywords:
            if keyword in question_lower:
                score += 6
                print(f"  - FAQ问题关键词匹配: {keyword} (+6)")
    
    # 特殊场景匹配
    if "scenario" in item:
        scenario_lower = item.get("scenario", "").lower()
        if query in scenario_lower:
            score += 8
            print(f"  - 场景完全匹配: {item.get('scenario')} (+8)")
        
        # 场景关键词匹配
        for keyword in keywords:
            if keyword in scenario_lower:
                score += 4
                print(f"  - 场景关键词匹配: {keyword} (+4)")
    
    # 4. 特殊处理 - 人名匹配
    if "name" in item and any(keyword in item.get("name", "").lower() for keyword in keywords):
        score += 15  # 人名匹配给最高分
        print(f"  - 人名匹配: {item.get('name')} (+15)")
    
    # 5. 特殊处理 - 联系人部门匹配
    if "dept" in item and any(keyword in item.get("dept", "").lower() for keyword in keywords):
        score += 8
        print(f"  - 部门匹配: {item.get('dept')} (+8)")
    
    # 6. 特殊处理 - 医院名称匹配
    if category == "hospitals" and "name" in item:
        hospital_name = item.get("name", "").lower()
        if any(keyword in hospital_name for keyword in keywords):
            score += 10
            print(f"  - 医院名称匹配: {item.get('name')} (+10)")
    
    # 7. 特殊处理 - 报销比例匹配
    if "ratio" in item and ("比例" in query or "百分比" in query or "报销比例" in query):
        score += 7
        print(f"  - 报销比例匹配: {item.get('ratio')} (+7)")
    
    return score

def detect_special_keywords(query: str) -> List[str]:
    """检测特殊关键词"""
    special_keywords = []
    
    # 问候匹配
    greetings = ["你好", "早上好", "中午好", "下午好", "晚上好", "嗨", "hi", "hello", "谢谢", "感谢", "再见", "拜拜"]
    for greeting in greetings:
        if greeting in query.lower():
            special_keywords.append("问候")
            special_keywords.append(greeting)
            break
    
    # 医院查询
    if "哪些医院" in query or "什么医院" in query or "医院列表" in query:
        special_keywords.append("医院列表")
    
    # 人名匹配
    if "常春艳" in query or "常老师" in query:
        special_keywords.extend(["常春艳", "医保办"])
    
    # 医院匹配
    if "南海" in query:
        special_keywords.append("南海新区医院")
    elif "中心医院" in query or "中心" in query:
        special_keywords.append("威海市中心医院")
        special_keywords.append("中心医院")
    elif "市立医院" in query:
        special_keywords.append("威海市立医院")
    
    # 报销类型匹配
    if "门诊" in query:
        special_keywords.append("门诊")
    if "住院" in query:
        special_keywords.append("住院")
    if "急诊" in query:
        special_keywords.append("急诊")
    
    # 特殊情况匹配
    if "寒假" in query or "暑假" in query or "假期" in query:
        special_keywords.append("寒暑假")
    if "转诊" in query:
        special_keywords.append("转诊单")
    if "材料" in query or "资料" in query or "需要带" in query:
        special_keywords.append("材料")
    if "截止" in query or "期限" in query or "时间" in query:
        special_keywords.append("截止日期")
    
    # 特殊查询匹配
    if "到账" in query or "多久" in query or "周期" in query:
        special_keywords.append("到账")
        special_keywords.append("报销周期")
    if "联系" in query or "咨询" in query or "办理" in query:
        special_keywords.append("联系方式")
    if "在哪" in query or "地点" in query or "地址" in query or "办公" in query:
        special_keywords.append("办公地点")
    
    return special_keywords

def get_category_chinese_name(category: str) -> str:
    """获取分类的中文名称"""
    category_map = {
        "policy": "报销政策",
        "materials": "材料要求",
        "procedure": "报销流程",
        "contacts": "联系人信息",
        "common_questions": "常见问题",
        "special_cases": "特殊情况",
        "hospitals": "医院信息",
        "greetings": "问候回复"
    }
    return category_map.get(category, category)

def extract_keywords(text: str) -> List[str]:
    """提取关键词"""
    # 简单的中文分词
    import re
    
    # 移除标点符号
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 停用词
    stop_words = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '吗', '么', '什么', '怎么', '可以', '这个', '那个', '能', '为', '吧'}
    
    # 分词 (简单按空格和常见标点分割)
    words = []
    for word in re.split(r'[\s,，.。!！?？:：;；]', text):
        word = word.strip()
        if word and word not in stop_words and len(word) > 1:  # 过滤停用词和单字词
            words.append(word)
    
    # 如果没有提取到关键词，返回原始查询分割后的词
    if not words:
        words = [w for w in text.split() if w and len(w) > 1]
    
    # 如果还是没有关键词，返回原始查询中的单字
    if not words and len(text) > 0:
        words = [text]
    
    return words

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点 - 支持流式输出"""
    await manager.connect(websocket)
    try:
        while True:
            # 接收客户端消息
            try:
                data = await websocket.receive_text()
                request_data = json.loads(data)
                question = request_data.get("question", "")
                
                if not question:
                    await manager.send_message(json.dumps({
                        "type": "error",
                        "content": "问题不能为空"
                    }), websocket)
                    continue
                
                # 发送开始标记
                await manager.send_message(json.dumps({
                    "type": "start",
                    "question": question
                }), websocket)
                
                try:
                    # 搜索知识库
                    context_items = search_knowledge(question, limit=3)
                    
                    # 构建结构化上下文
                    context = ""
                    sources = []
                    
                    # 检查是否有高分匹配结果
                    has_high_score = any(item.get("score", 0) >= 5 for item in context_items)
                    
                    # 根据匹配分数调整上下文构建
                    for i, item in enumerate(context_items):
                        # 获取分类名称的中文表示
                        category_name = get_category_chinese_name(item.get("category", ""))
                        
                        # 构建结构化的知识条目
                        context += f"【知识条目 {i+1}】\n"
                        context += f"分类: {category_name}\n"
                        
                        # 对于FAQ类型，优先使用question作为标题
                        if item.get("category") == "common_questions" and "question" in item:
                            context += f"标题: {item.get('question', '')}\n"
                        else:
                            title = item.get('title', '')
                            if title:
                                context += f"标题: {title}\n"
                        
                        # 添加特定字段
                        if item.get("category") == "common_questions":
                            if "question" in item and not context.find(f"标题: {item.get('question', '')}") >= 0:
                                context += f"问题: {item.get('question', '')}\n"
                            if "answer" in item:
                                context += f"回答: {item.get('answer', '')}\n"
                        elif item.get("category") == "greetings":
                            if "scenarios" in item:
                                scenarios = item.get("scenarios", [])
                                for scenario in scenarios:
                                    if query.lower() == scenario.get("input", "").lower() or query.lower() in scenario.get("input", "").lower():
                                        context += f"问候类型: {scenario.get('input', '')}\n"
                                        context += f"回复: {scenario.get('response', '')}\n"
                                        break
                        elif item.get("category") == "contacts":
                            if "name" in item:
                                context += f"姓名: {item.get('name', '')}\n"
                            if "dept" in item:
                                context += f"部门: {item.get('dept', '')}\n"
                            if "role" in item:
                                context += f"职责: {item.get('role', '')}\n"
                            if "office_location" in item:
                                context += f"办公地点: {item.get('office_location', '')}\n"
                        elif item.get("category") == "hospitals":
                            if "name" in item:
                                context += f"医院名称: {item.get('name', '')}\n"
                            if "address" in item:
                                context += f"医院地址: {item.get('address', '')}\n"
                            if "phone" in item:
                                context += f"联系电话: {item.get('phone', '')}\n"
                            if "service_hours" in item:
                                context += f"服务时间: {item.get('service_hours', '')}\n"
                            if "complaint_phone" in item:
                                context += f"投诉电话: {item.get('complaint_phone', '')}\n"
                            if "appointment_channels" in item:
                                context += f"预约渠道: {item.get('appointment_channels', '')}\n"
                            if "contract_status" in item:
                                context += f"合同状态: {item.get('contract_status', '')}\n"
                        elif item.get("category") == "materials_requirements":
                            if "checklist" in item:
                                context += "所需材料清单:\n"
                                for material in item.get("checklist", []):
                                    context += f"- {material}\n"
                        
                        # 添加通用内容
                        context += f"内容: {item.get('content', '')}\n"
                        
                        # 添加重要的额外字段
                        if "ratio" in item:
                            context += f"报销比例: {item.get('ratio', '')}\n"
                        if "notes" in item:
                            context += f"注意事项: {item.get('notes', '')}\n"
                        if "tags" in item:
                            context += f"标签: {', '.join(item.get('tags', []))}\n"
                        
                        # 添加分隔符
                        context += "\n---\n\n"
                        
                        # 构建前端展示的来源信息
                        sources.append({
                            "id": item.get("id", ""),
                            "title": item.get("title", ""),
                            "category": category_name,
                            "score": item.get("score", 0)
                        })
                    
                    # 发送源信息
                    try:
                        await manager.send_message(json.dumps({
                            "type": "sources",
                            "content": sources
                        }), websocket)
                    except WebSocketDisconnect:
                        print("WebSocket已断开，无法发送源信息")
                        break
                    
                    # 使用通义千问的流式RAG生成
                    print(f"开始流式RAG生成回答，上下文长度: {len(context)}")
                    async for chunk in qwen_llm.rag_generate_stream(question, context):
                        try:
                            await manager.send_message(json.dumps({
                                "type": "chunk",
                                "content": chunk
                            }), websocket)
                        except Exception as chunk_error:
                            print(f"发送文本块时出错: {str(chunk_error)}")
                            break
                    
                    # 发送完成标记
                    try:
                        await manager.send_message(json.dumps({
                            "type": "end"
                        }), websocket)
                    except Exception as end_error:
                        print(f"发送结束标记时出错: {str(end_error)}")
                    
                except Exception as e:
                    try:
                        await manager.send_message(json.dumps({
                            "type": "error",
                            "content": f"处理问题时出错: {str(e)}"
                        }), websocket)
                    except Exception:
                        print(f"发送错误消息时出错，原始错误: {str(e)}")
                
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

@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    """Web界面 - 支持Markdown渲染和流式输出"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>医疗报销智能助手</title>
        <!-- 引入Markdown渲染库 -->
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <!-- 引入代码高亮库 -->
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
            
            /* Markdown样式 */
            .markdown-body {
                font-size: 14px;
                line-height: 1.6;
            }
            
            .markdown-body h1,
            .markdown-body h2,
            .markdown-body h3,
            .markdown-body h4 {
                margin-top: 16px;
                margin-bottom: 8px;
            }
            
            .markdown-body p {
                margin-bottom: 8px;
            }
            
            .markdown-body ul,
            .markdown-body ol {
                padding-left: 20px;
                margin-bottom: 8px;
            }
            
            .markdown-body code {
                background: #f0f0f0;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: monospace;
            }
            
            .markdown-body pre {
                background: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
                margin-bottom: 8px;
            }
            
            .markdown-body blockquote {
                border-left: 4px solid #ddd;
                padding-left: 10px;
                color: #666;
                margin-bottom: 8px;
            }
            
            .markdown-body table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 8px;
            }
            
            .markdown-body table th,
            .markdown-body table td {
                border: 1px solid #ddd;
                padding: 6px;
            }
            
            .markdown-body table th {
                background: #f0f0f0;
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
                            <div class="markdown-body">👋 您好！我是医疗报销智能助手，由通义千问大模型驱动。我可以为您解答关于北京交通大学威海校区医疗报销的各种问题。</div>
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
                    // 连接成功时启用发送按钮
                    document.getElementById('sendButton').disabled = false;
                    document.getElementById('sendButton').textContent = '发送';
                    
                    // 移除连接状态指示器
                    const connectionStatus = document.getElementById('connection-status');
                    if (connectionStatus) {
                        connectionStatus.remove();
                    }
                    
                    // 如果之前显示了连接错误，现在移除
                    const connectionError = document.getElementById('connection-error');
                    if (connectionError) {
                        connectionError.remove();
                    }
                    
                    // 确保加载状态隐藏
                    showLoading(false);
                };
                
                socket.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
                
                socket.onclose = function(event) {
                    console.log("WebSocket连接已关闭");
                    // 禁用发送按钮
                    document.getElementById('sendButton').disabled = true;
                    
                    // 显示连接错误消息
                    showConnectionError("连接已断开，正在尝试重新连接...");
                    
                    // 隐藏加载状态
                    showLoading(false);
                    
                    // 尝试重新连接
                    setTimeout(connectWebSocket, 2000);
                };
                
                socket.onerror = function(error) {
                    console.error("WebSocket错误:", error);
                    // 显示连接错误消息
                    showConnectionError("连接出错，请稍后再试...");
                    
                    // 隐藏加载状态
                    showLoading(false);
                };
            }
            
            // 显示连接错误消息
            function showConnectionError(message) {
                // 检查是否已存在错误消息
                let errorDiv = document.getElementById('connection-error');
                
                if (!errorDiv) {
                    // 创建错误消息
                    errorDiv = document.createElement('div');
                    errorDiv.id = 'connection-error';
                    errorDiv.style.backgroundColor = '#ffebee';
                    errorDiv.style.color = '#d32f2f';
                    errorDiv.style.padding = '10px';
                    errorDiv.style.margin = '10px 0';
                    errorDiv.style.borderRadius = '5px';
                    errorDiv.style.textAlign = 'center';
                    errorDiv.style.fontSize = '14px';
                    
                    // 添加到消息容器顶部
                    const messagesContainer = document.getElementById('messages');
                    messagesContainer.insertBefore(errorDiv, messagesContainer.firstChild);
                }
                
                // 设置错误消息
                errorDiv.textContent = message;
            }
            
            // 处理WebSocket消息
            function handleWebSocketMessage(data) {
                console.log("收到WebSocket消息:", data.type);
                
                switch(data.type) {
                    case "start":
                        // 创建新的消息容器
                        currentMessageDiv = document.createElement('div');
                        currentMessageDiv.className = "message assistant";
                        currentMessageContent = "";
                        
                        const contentDiv = document.createElement('div');
                        contentDiv.className = "message-content";
                        
                        const markdownDiv = document.createElement('div');
                        markdownDiv.className = "markdown-body";
                        markdownDiv.id = "current-markdown";
                        
                        contentDiv.appendChild(markdownDiv);
                        currentMessageDiv.appendChild(contentDiv);
                        
                        document.getElementById('messages').appendChild(currentMessageDiv);
                        showLoading(true);
                        break;
                        
                    case "chunk":
                        // 追加文本块
                        if (!document.getElementById("current-markdown")) {
                            console.error("找不到当前Markdown容器");
                            // 如果找不到当前的Markdown容器，可能是因为连接断开后重连
                            // 在这种情况下，我们需要创建一个新的消息容器
                            handleWebSocketMessage({type: "start"});
                        }
                        
                        currentMessageContent += data.content;
                        try {
                            document.getElementById("current-markdown").innerHTML = marked.parse(currentMessageContent);
                            // 应用代码高亮
                            document.querySelectorAll('pre code').forEach((block) => {
                                hljs.highlightBlock(block);
                            });
                            
                            // 滚动到底部
                            const messagesContainer = document.getElementById('messages');
                            messagesContainer.scrollTop = messagesContainer.scrollHeight;
                        } catch (error) {
                            console.error("渲染Markdown时出错:", error);
                        }
                        break;
                        
                    case "sources":
                        // 添加来源信息
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
                        // 完成消息，添加时间戳
                        if (currentMessageDiv) {
                            const messageContent = currentMessageDiv.querySelector('.message-content');
                            
                            const timeDiv = document.createElement('div');
                            timeDiv.className = "message-time";
                            timeDiv.textContent = new Date().toLocaleTimeString();
                            
                            messageContent.appendChild(timeDiv);
                            
                            // 移除当前ID
                            const markdownDiv = document.getElementById("current-markdown");
                            if (markdownDiv) {
                                markdownDiv.removeAttribute("id");
                            }
                            
                            currentMessageDiv = null;
                            showLoading(false);
                        } else {
                            // 如果没有当前消息容器，也要确保加载状态被隐藏
                            showLoading(false);
                        }
                        break;
                        
                    case "error":
                        // 显示错误消息
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
                    return; // 空问题不处理
                }
                
                if (!socket || socket.readyState !== WebSocket.OPEN) {
                    // 如果WebSocket未连接，显示错误
                    showConnectionError("服务器连接已断开，请刷新页面重试");
                    return;
                }
                
                // 清空输入框
                input.value = '';
                
                // 添加用户消息
                addMessage(question, 'user');
                
                // 立即显示加载状态，提供即时反馈
                showLoading(true);
                
                try {
                    // 发送到WebSocket
                    socket.send(JSON.stringify({
                        question: question
                    }));
                } catch (error) {
                    console.error("发送消息失败:", error);
                    showLoading(false);
                    showConnectionError("发送消息失败，请刷新页面重试");
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
            
            // 初始化WebSocket连接
            function initWebSocket() {
                // 初始WebSocket连接前禁用发送按钮
                document.getElementById('sendButton').disabled = true;
                document.getElementById('sendButton').textContent = '连接中...';
                
                // 创建专门的连接状态指示器
                const messagesContainer = document.getElementById('messages');
                let connectionStatus = document.getElementById('connection-status');
                
                // 如果已存在则更新，否则创建新的
                if (!connectionStatus) {
                    connectionStatus = document.createElement('div');
                    connectionStatus.id = 'connection-status';
                    connectionStatus.style.textAlign = 'center';
                    connectionStatus.style.padding = '10px';
                    connectionStatus.style.margin = '10px 0';
                    connectionStatus.style.color = '#666';
                    connectionStatus.style.fontSize = '14px';
                    connectionStatus.style.backgroundColor = '#f0f8ff';
                    connectionStatus.style.borderRadius = '5px';
                    messagesContainer.appendChild(connectionStatus);
                }
                
                connectionStatus.textContent = '正在连接服务器...';
                
                // 建立WebSocket连接
                connectWebSocket();
                
                // 5秒后检查连接状态
                setTimeout(function() {
                    if (!socket || socket.readyState !== WebSocket.OPEN) {
                        connectionStatus = document.getElementById('connection-status');
                        if (connectionStatus) {
                            connectionStatus.textContent = '连接服务器超时，正在重试...';
                            connectionStatus.style.backgroundColor = '#fff3cd';
                            connectionStatus.style.color = '#856404';
                        }
                    }
                }, 5000);
            }
            
            // 页面加载完成后聚焦输入框
            window.addEventListener('load', function() {
                document.getElementById('questionInput').focus();
                
                // 初始化WebSocket
                initWebSocket();
                
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
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("🏥 医疗报销智能助手 - 通义千问流式版启动")
    print("=" * 50)
    # 从环境变量读取端口，PaaS会自动设置
    PORT = int(os.getenv("PORT", "8081"))
    
    print(f"📱 主页: http://localhost:{PORT}")
    print(f"🌐 Web界面: http://localhost:{PORT}/web")
    print(f"📚 API文档: http://localhost:{PORT}/docs")
    print(f"🔍 健康检查: http://localhost:{PORT}/health")
    print("=" * 50)
    print("💡 按 Ctrl+C 停止服务")
    print("")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
