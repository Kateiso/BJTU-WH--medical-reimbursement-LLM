"""
API路由定义
"""
import time
import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse

from .models import (
    QuestionRequest, AnswerResponse, HealthResponse,
    KnowledgeSearchRequest, KnowledgeSearchResponse, ErrorResponse,
    KnowledgeItemRequest, KnowledgeItemResponse, KnowledgeItemUpdateRequest
)
from ..rag.qwen_engine import QwenRAGEngine
from ..knowledge.json_manager import JSONKnowledgeManager
from ...config.settings import settings

# 创建路由器
router = APIRouter(prefix=settings.api_prefix)

# 全局实例 (生产环境建议使用依赖注入)
rag_engine: QwenRAGEngine = None
knowledge_manager: JSONKnowledgeManager = None

async def get_rag_engine() -> QwenRAGEngine:
    """获取RAG引擎实例"""
    global rag_engine
    if rag_engine is None:
        rag_engine = QwenRAGEngine(
            api_key=settings.dashscope_api_key,
            model=settings.qwen_model
        )
    return rag_engine

async def get_knowledge_manager() -> JSONKnowledgeManager:
    """获取知识库管理器实例"""
    global knowledge_manager
    if knowledge_manager is None:
        knowledge_manager = JSONKnowledgeManager()
        await knowledge_manager.load()
    return knowledge_manager

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    try:
        rag_engine = await get_rag_engine()
        knowledge_manager = await get_knowledge_manager()
        
        # 检查各组件状态
        rag_health = await rag_engine.health_check()
        knowledge_stats = await knowledge_manager.get_stats()
        
        components = {
            "rag_engine": rag_health,
            "knowledge_base": knowledge_stats
        }
        
        # 判断整体状态
        overall_status = "healthy"
        if rag_health.get("status") != "healthy":
            overall_status = "degraded"
        
        return HealthResponse(
            status=overall_status,
            version=settings.app_version,
            components=components
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"健康检查失败: {str(e)}"
        )

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    rag_engine: QwenRAGEngine = Depends(get_rag_engine),
    knowledge_manager: JSONKnowledgeManager = Depends(get_knowledge_manager)
):
    """智能问答接口"""
    start_time = time.time()
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # 1. 从知识库搜索相关文档
        knowledge_items = await knowledge_manager.search(
            query=request.question,
            limit=settings.top_k_documents
        )
        
        # 2. 转换为RAG文档格式
        from ..rag.base import Document
        documents = []
        for item in knowledge_items:
            doc = Document(
                id=item.id,
                title=item.title,
                content=item.content,
                metadata={
                    "category": item.category,
                    "tags": item.tags,
                    **item.metadata
                }
            )
            documents.append(doc)
        
        # 3. 添加到RAG引擎
        if documents:
            await rag_engine.add_documents(documents)
        
        # 4. 搜索相关文档
        search_result = await rag_engine.search(
            query=request.question,
            top_k=settings.top_k_documents
        )
        
        # 5. 构建上下文
        context = ""
        sources = []
        for doc in search_result.documents:
            context += f"标题: {doc.title}\n内容: {doc.content}\n\n"
            sources.append({
                "id": doc.id,
                "title": doc.title,
                "category": doc.metadata.get("category", ""),
                "score": doc.score
            })
        
        # 6. 生成回答
        answer = await rag_engine.llm_provider.generate(
            prompt=request.question,
            context=context,
            max_tokens=settings.max_context_length
        )
        
        response_time = time.time() - start_time
        
        return AnswerResponse(
            answer=answer,
            sources=sources,
            session_id=session_id,
            response_time=response_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"问答失败: {str(e)}"
        )

@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    knowledge_manager: JSONKnowledgeManager = Depends(get_knowledge_manager)
):
    """知识库搜索接口"""
    start_time = time.time()
    
    try:
        # 搜索知识库
        items = await knowledge_manager.search(
            query=request.query,
            category=request.category,
            limit=request.limit
        )
        
        # 转换为响应格式
        search_results = []
        for item in items:
            search_results.append({
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "category": item.category,
                "tags": item.tags,
                "metadata": item.metadata,
                "created_at": item.created_at,
                "updated_at": item.updated_at
            })
        
        search_time = time.time() - start_time
        
        return KnowledgeSearchResponse(
            items=search_results,
            total_count=len(search_results),
            query=request.query,
            search_time=search_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"搜索失败: {str(e)}"
        )

@router.get("/categories")
async def get_categories(
    knowledge_manager: JSONKnowledgeManager = Depends(get_knowledge_manager)
):
    """获取知识库分类列表"""
    try:
        categories = await knowledge_manager.get_categories()
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取分类失败: {str(e)}"
        )

@router.get("/stats")
async def get_stats(
    knowledge_manager: JSONKnowledgeManager = Depends(get_knowledge_manager)
):
    """获取知识库统计信息"""
    try:
        stats = await knowledge_manager.get_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )

# ==================== 知识库管理接口 ====================

@router.post("/knowledge", response_model=KnowledgeItemResponse)
async def create_knowledge_item(
    request: KnowledgeItemRequest,
    knowledge_manager: JSONKnowledgeManager = Depends(get_knowledge_manager)
):
    """创建新的知识库条目"""
    try:
        from ..knowledge.base import KnowledgeItem
        
        # 创建知识项
        item = KnowledgeItem(
            category=request.category,
            title=request.title,
            content=request.content,
            tags=request.tags,
            metadata=request.metadata
        )
        
        # 添加到知识库
        success = await knowledge_manager.add_item(item)
        if not success:
            raise HTTPException(status_code=500, detail="创建条目失败")
        
        return KnowledgeItemResponse(
            id=item.id,
            category=item.category,
            title=item.title,
            content=item.content,
            tags=item.tags,
            metadata=item.metadata,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建知识条目失败: {str(e)}"
        )

@router.get("/knowledge/{item_id}", response_model=KnowledgeItemResponse)
async def get_knowledge_item(
    item_id: str,
    knowledge_manager: JSONKnowledgeManager = Depends(get_knowledge_manager)
):
    """根据ID获取知识库条目"""
    try:
        item = await knowledge_manager.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="条目不存在")
        
        return KnowledgeItemResponse(
            id=item.id,
            category=item.category,
            title=item.title,
            content=item.content,
            tags=item.tags,
            metadata=item.metadata,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取知识条目失败: {str(e)}"
        )

@router.put("/knowledge/{item_id}", response_model=KnowledgeItemResponse)
async def update_knowledge_item(
    item_id: str,
    request: KnowledgeItemUpdateRequest,
    knowledge_manager: JSONKnowledgeManager = Depends(get_knowledge_manager)
):
    """更新知识库条目"""
    try:
        # 获取现有条目
        item = await knowledge_manager.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="条目不存在")
        
        # 更新字段
        if request.category is not None:
            item.category = request.category
        if request.title is not None:
            item.title = request.title
        if request.content is not None:
            item.content = request.content
        if request.tags is not None:
            item.tags = request.tags
        if request.metadata is not None:
            item.metadata.update(request.metadata)
        
        # 保存更新
        success = await knowledge_manager.update_item(item)
        if not success:
            raise HTTPException(status_code=500, detail="更新条目失败")
        
        return KnowledgeItemResponse(
            id=item.id,
            category=item.category,
            title=item.title,
            content=item.content,
            tags=item.tags,
            metadata=item.metadata,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新知识条目失败: {str(e)}"
        )

@router.delete("/knowledge/{item_id}")
async def delete_knowledge_item(
    item_id: str,
    knowledge_manager: JSONKnowledgeManager = Depends(get_knowledge_manager)
):
    """删除知识库条目"""
    try:
        success = await knowledge_manager.delete_item(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="条目不存在")
        
        return {"message": "条目删除成功", "item_id": item_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除知识条目失败: {str(e)}"
        )

@router.get("/knowledge/category/{category}")
async def get_knowledge_by_category(
    category: str,
    knowledge_manager: JSONKnowledgeManager = Depends(get_knowledge_manager)
):
    """根据分类获取知识库条目"""
    try:
        items = await knowledge_manager.get_by_category(category)
        
        results = []
        for item in items:
            results.append({
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "category": item.category,
                "tags": item.tags,
                "metadata": item.metadata,
                "created_at": item.created_at,
                "updated_at": item.updated_at
            })
        
        return {
            "category": category,
            "items": results,
            "total_count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取分类条目失败: {str(e)}"
        )

@router.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 返回简单的API文档"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>医疗报销智能助手 API</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { color: #2c3e50; }
            .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { color: #27ae60; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1 class="header">🏥 医疗报销智能助手 API</h1>
        <p>版本: v1.0.0 | 状态: 运行中</p>
        
        <h2>API 接口</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/v1/health - 健康检查
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> /api/v1/ask - 智能问答
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> /api/v1/search - 知识库搜索
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/v1/categories - 获取分类
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/v1/stats - 获取统计
        </div>
        
        <h2>知识库管理</h2>
        
        <div class="endpoint">
            <span class="method">POST</span> /api/v1/knowledge - 创建知识条目
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/v1/knowledge/{id} - 获取知识条目
        </div>
        
        <div class="endpoint">
            <span class="method">PUT</span> /api/v1/knowledge/{id} - 更新知识条目
        </div>
        
        <div class="endpoint">
            <span class="method">DELETE</span> /api/v1/knowledge/{id} - 删除知识条目
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/v1/knowledge/category/{category} - 按分类获取条目
        </div>
        
        <h2>快速测试</h2>
        <p>访问 <a href="/web">/web</a> 使用Web界面</p>
        
        <h2>文档</h2>
        <p>访问 <a href="/docs">/docs</a> 查看完整API文档</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)