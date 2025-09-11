# 🏥 医疗报销智能助手

基于RAG技术的智能医疗报销问答系统，为北京交通大学威海校区师生提供7x24小时专业咨询服务。

## ✨ 核心特性

- 🧠 **智能问答**: 基于通义千问大语言模型，深度理解用户意图
- 📚 **知识驱动**: 基于真实政策文档，确保信息准确性
- 🔄 **实时响应**: 毫秒级检索 + 秒级AI生成
- 🌐 **Web界面**: 现代化响应式设计，支持PC和移动端
- 🔌 **API接口**: RESTful API，支持第三方集成
- 🛡️ **安全可靠**: 会话隔离，无状态设计

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- 通义千问API密钥

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 设置通义千问API密钥
export DASHSCOPE_API_KEY=your_api_key_here

# 或创建.env文件
cp .env.example .env
# 编辑.env文件，填入API密钥
```

### 4. 启动应用

```bash
# 方式1: 使用启动脚本
python start.py

# 方式2: 直接启动
python main.py
```

### 5. 访问应用

- **Web界面**: http://localhost:8080/web
- **API文档**: http://localhost:8080/docs
- **健康检查**: http://localhost:8080/api/v1/health

## 📖 使用指南

### Web界面使用

1. 打开浏览器访问 https://www.bjtuai.cn/web
2. 在输入框中输入问题，如"感冒药能报销吗？"
3. 点击发送或按回车键
4. 查看AI回答和相关信息来源

### API接口使用

```bash
# 健康检查
curl http://localhost:8080/api/v1/health

# 智能问答
curl -X POST http://localhost:8080/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "感冒药能报销吗？"}'

# 知识库搜索
curl -X POST http://localhost:8080/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "报销材料", "limit": 5}'
```

## 🏗️ 项目结构

```
mediAi/
├── src/                    # 源代码
│   ├── core/              # 核心业务逻辑
│   │   ├── rag/          # RAG引擎
│   │   ├── knowledge/    # 知识库管理
│   │   └── api/          # API接口
│   ├── web/              # Web界面
│   └── config/           # 配置管理
├── data/                 # 数据文件
├── tests/                # 测试文件
├── docs/                 # 文档
├── main.py              # 主应用入口
├── start.py             # 启动脚本
└── requirements.txt     # 依赖列表
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | 通义千问API密钥 | 必须设置 |
| `DEBUG` | 调试模式 | false |
| `HOST` | 服务主机 | 0.0.0.0 |
| `PORT` | 服务端口 | 8080 |
| `LOG_LEVEL` | 日志级别 | INFO |

### 知识库配置

知识库数据存储在 `data/knowledge_base.json` 文件中，包含：

- **报销政策**: 比例、时间窗口、排除项目
- **材料要求**: 不同场景的详细材料清单
- **联系人信息**: 负责老师和保险合作方
- **医院信息**: 地址、电话、挂号方式
- **常见问题**: 预设问答对

## 🧪 测试

```bash
# 运行测试
pytest tests/

# 健康检查测试
curl http://localhost:8080/api/v1/health

# 功能测试
python -m pytest tests/test_api.py -v
```

## 📊 性能指标

- **响应时间**: < 3秒
- **并发支持**: 50+ 用户
- **准确率**: > 90%
- **可用性**: > 99%

## 🔮 扩展规划

### 短期优化
- [ ] 向量数据库集成
- [ ] 多模态交互支持
- [ ] 用户会话管理
- [ ] 数据分析面板

### 长期规划
- [ ] 微服务架构
- [ ] 移动端APP
- [ ] 多校扩展
- [ ] 智能推荐系统

## 🛠️ 开发指南

### 添加新的RAG引擎

```python
from src.core.rag.base import RAGEngine

class CustomRAGEngine(RAGEngine):
    async def search(self, query: str, top_k: int = 5):
        # 实现自定义搜索逻辑
        pass
```

### 添加新的知识库源

```python
from src.core.knowledge.base import KnowledgeBase

class CustomKnowledgeBase(KnowledgeBase):
    async def load(self):
        # 实现自定义加载逻辑
        pass
```

## 📞 技术支持

- **项目负责人**: 曹益波
- **技术栈**: Python + FastAPI + 通义千问 + RAG
- **问题反馈**: 通过Web界面或API接口

## 📄 许可证

MIT License

---

**🎯 产品使命**: 让医疗报销咨询变得简单、准确、高效

*Built with ❤️ using 阿里通义千问 RAG技术*
