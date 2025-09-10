"""
通义千问RAG引擎实现
"""
import time
import json
from typing import List, Dict, Any, Optional
from dashscope import Generation
from dashscope.api_entities.dashscope_response import GenerationResponse

from .base import RAGEngine, Document, SearchResult, LLMProvider
from ...config.settings import settings

class QwenLLMProvider(LLMProvider):
    """通义千问大语言模型提供者"""
    
    def __init__(self, api_key: str, model: str = "qwen-plus"):
        self.api_key = api_key
        self.model = model
    
    async def generate(
        self, 
        prompt: str, 
        context: str = "", 
        max_tokens: int = 1000
    ) -> str:
        """生成回答"""
        try:
            # 构建完整提示词
            full_prompt = self._build_prompt(prompt, context)
            
            # 调用通义千问API
            response = Generation.call(
                model=self.model,
                prompt=full_prompt,
                max_tokens=max_tokens,
                api_key=self.api_key
            )
            
            if response.status_code == 200:
                return response.output.text
            else:
                raise Exception(f"API调用失败: {response.message}")
                
        except Exception as e:
            raise Exception(f"生成回答失败: {str(e)}")
    
    def _build_prompt(self, query: str, context: str) -> str:
        """构建提示词"""
        system_prompt = """你是北京交通大学威海校区的医疗报销智能助手。请基于提供的政策文档，为用户提供准确、专业的医疗报销咨询服务。

要求：
1. 回答要准确、专业、友好
2. 如果信息不完整，请说明
3. 提供具体的操作建议
4. 引用相关政策和规定"""
        
        if context:
            prompt = f"""{system_prompt}

相关政策信息：
{context}

用户问题：{query}

请基于以上信息回答用户问题："""
        else:
            prompt = f"""{system_prompt}

用户问题：{query}

请回答用户问题："""
        
        return prompt
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            response = Generation.call(
                model=self.model,
                prompt="测试",
                max_tokens=10,
                api_key=self.api_key
            )
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "model": self.model,
                "response_time": 0.1
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": self.model
            }

class QwenRAGEngine(RAGEngine):
    """通义千问RAG引擎"""
    
    def __init__(self, api_key: str, model: str = "qwen-plus"):
        self.llm_provider = QwenLLMProvider(api_key, model)
        self.documents: Dict[str, Document] = {}
        self.embedding_model = None  # 预留向量化模型
    
    async def search(self, query: str, top_k: int = 5) -> SearchResult:
        """搜索相关文档"""
        start_time = time.time()
        
        try:
            # 简单的关键词匹配搜索 (MVP版本)
            # 后续可扩展为向量搜索
            relevant_docs = self._simple_search(query, top_k)
            
            search_time = time.time() - start_time
            
            return SearchResult(
                documents=relevant_docs,
                query=query,
                total_count=len(relevant_docs),
                search_time=search_time
            )
            
        except Exception as e:
            raise Exception(f"搜索失败: {str(e)}")
    
    def _simple_search(self, query: str, top_k: int) -> List[Document]:
        """简单关键词搜索 (MVP版本)"""
        query_lower = query.lower()
        scored_docs = []
        
        for doc in self.documents.values():
            score = 0
            
            # 标题匹配
            if query_lower in doc.title.lower():
                score += 3
            
            # 内容匹配
            content_lower = doc.content.lower()
            if query_lower in content_lower:
                score += 1
            
            # 关键词匹配
            keywords = query_lower.split()
            for keyword in keywords:
                if keyword in content_lower:
                    score += 0.5
            
            if score > 0:
                doc.score = score
                scored_docs.append(doc)
        
        # 按分数排序
        scored_docs.sort(key=lambda x: x.score, reverse=True)
        
        return scored_docs[:top_k]
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """添加文档到知识库"""
        try:
            for doc in documents:
                self.documents[doc.id] = doc
            return True
        except Exception as e:
            raise Exception(f"添加文档失败: {str(e)}")
    
    async def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        try:
            if doc_id in self.documents:
                del self.documents[doc_id]
                return True
            return False
        except Exception as e:
            raise Exception(f"删除文档失败: {str(e)}")
    
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """获取单个文档"""
        return self.documents.get(doc_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        llm_health = await self.llm_provider.health_check()
        
        return {
            "rag_engine": "qwen",
            "document_count": len(self.documents),
            "llm_provider": llm_health,
            "status": "healthy" if llm_health["status"] == "healthy" else "unhealthy"
        }