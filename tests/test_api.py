"""
API接口测试
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app

client = TestClient(app)

class TestHealthAPI:
    """健康检查API测试"""
    
    def test_health_check(self):
        """测试健康检查接口"""
        with patch('src.core.api.router.get_rag_engine') as mock_rag, \
             patch('src.core.api.router.get_knowledge_manager') as mock_knowledge:
            
            # 模拟健康检查响应
            mock_rag.return_value.health_check = AsyncMock(return_value={
                "status": "healthy",
                "document_count": 10
            })
            mock_knowledge.return_value.get_stats = AsyncMock(return_value={
                "total_items": 10,
                "categories": ["policy", "material"]
            })
            
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] in ["healthy", "degraded"]
            assert "version" in data
            assert "components" in data

class TestAskAPI:
    """问答API测试"""
    
    def test_ask_question_success(self):
        """测试成功问答"""
        with patch('src.core.api.router.get_rag_engine') as mock_rag, \
             patch('src.core.api.router.get_knowledge_manager') as mock_knowledge:
            
            # 模拟知识库搜索
            mock_knowledge.return_value.search = AsyncMock(return_value=[])
            
            # 模拟RAG引擎
            mock_rag.return_value.add_documents = AsyncMock(return_value=True)
            mock_rag.return_value.search = AsyncMock(return_value=type('obj', (object,), {
                'documents': [],
                'query': 'test',
                'total_count': 0,
                'search_time': 0.1
            })())
            mock_rag.return_value.llm_provider.generate = AsyncMock(return_value="测试回答")
            
            response = client.post("/api/v1/ask", json={
                "question": "测试问题"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "session_id" in data
            assert "response_time" in data
    
    def test_ask_question_missing_question(self):
        """测试缺少问题参数"""
        response = client.post("/api/v1/ask", json={})
        assert response.status_code == 422  # 验证错误
    
    def test_ask_question_empty_question(self):
        """测试空问题"""
        response = client.post("/api/v1/ask", json={
            "question": ""
        })
        assert response.status_code == 422  # 验证错误

class TestSearchAPI:
    """知识库搜索API测试"""
    
    def test_search_knowledge_success(self):
        """测试成功搜索"""
        with patch('src.core.api.router.get_knowledge_manager') as mock_knowledge:
            mock_knowledge.return_value.search = AsyncMock(return_value=[])
            
            response = client.post("/api/v1/search", json={
                "query": "测试查询"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total_count" in data
            assert "query" in data
            assert "search_time" in data
    
    def test_search_knowledge_with_category(self):
        """测试带分类的搜索"""
        with patch('src.core.api.router.get_knowledge_manager') as mock_knowledge:
            mock_knowledge.return_value.search = AsyncMock(return_value=[])
            
            response = client.post("/api/v1/search", json={
                "query": "测试查询",
                "category": "policy",
                "limit": 5
            })
            
            assert response.status_code == 200

class TestCategoriesAPI:
    """分类API测试"""
    
    def test_get_categories(self):
        """测试获取分类列表"""
        with patch('src.core.api.router.get_knowledge_manager') as mock_knowledge:
            mock_knowledge.return_value.get_categories = AsyncMock(return_value=[
                "policy", "material", "contact"
            ])
            
            response = client.get("/api/v1/categories")
            assert response.status_code == 200
            
            data = response.json()
            assert "categories" in data
            assert isinstance(data["categories"], list)

class TestStatsAPI:
    """统计API测试"""
    
    def test_get_stats(self):
        """测试获取统计信息"""
        with patch('src.core.api.router.get_knowledge_manager') as mock_knowledge:
            mock_knowledge.return_value.get_stats = AsyncMock(return_value={
                "total_items": 10,
                "categories": {"policy": 5, "material": 3, "contact": 2}
            })
            
            response = client.get("/api/v1/stats")
            assert response.status_code == 200
            
            data = response.json()
            assert "total_items" in data
            assert "categories" in data

class TestWebInterface:
    """Web界面测试"""
    
    def test_web_interface(self):
        """测试Web界面"""
        response = client.get("/web")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_root_redirect(self):
        """测试根路径重定向"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])