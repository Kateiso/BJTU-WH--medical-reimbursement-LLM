# 🏥 医疗报销智能助手 → 🎓 校园智能助手

基于RAG技术的智能问答系统，从医疗报销垂直领域起步，逐步扩展为全方位的校园生活智能助手。

## 🎯 项目愿景

**阶段1**: 医疗报销专业助手 ✅  
**阶段2**: 校园办事流程助手 🚧  
**阶段3**: 课程学习指南助手 📋  
**阶段4**: 通用校园生活助手 🌟

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

## 🚀 战略发展规划

### 阶段1: 医疗报销助手 ✅ (已完成)
- ✅ 报销政策问答
- ✅ 材料要求查询
- ✅ 流程指导
- ✅ 联系人信息

### 阶段2: 校园办事助手 🚧 (进行中)
- [ ] 学籍管理流程
- [ ] 宿舍申请指导
- [ ] 成绩查询帮助
- [ ] 证明开具流程

### 阶段3: 课程学习助手 📋 (规划中)
- [ ] 选课指导系统
- [ ] 考试安排查询
- [ ] 课程评价分析
- [ ] 学习资源推荐

### 阶段4: 通用校园助手 🌟 (愿景)
- [ ] 校园生活百科
- [ ] 就业指导服务
- [ ] 社团活动推荐
- [ ] 综合智能助手

## 🔧 技术架构升级

### 当前架构
- ✅ FastAPI + 通义千问 + JSON知识库
- ✅ WebSocket实时通信
- ✅ 访问统计分析

### 计划升级
- [x] **安全加固**: API密钥管理、输入验证、访问控制 ✅
- [ ] **数据管理**: 新知识库API系统、批量导入工具
- [ ] **备案合规**: 工信部备案、内容审核机制
- [ ] **性能优化**: 向量数据库、缓存系统、负载均衡
- [ ] **服务器迁移**: 从Railway迁移到国内云服务商

## 📋 当前任务清单

### 🔥 高优先级
- [x] **安全改进**: 移除硬编码API密钥，添加环境变量管理 ✅
- [ ] **备案申请**: 向工信部提交网站备案申请
- [ ] **项目重命名**: 从"医疗AI"升级为"校园智能助手"
- [ ] **域名规划**: 考虑更通用的域名方案
- [ ] **服务器迁移**: 准备迁移到国内云服务商

### 📊 中优先级
- [ ] **知识库扩展**: 添加学籍、宿舍、成绩等新领域数据
- [ ] **API完善**: 实现完整的CRUD知识库管理接口
- [ ] **用户系统**: 添加用户认证和权限管理
- [ ] **数据分析**: 扩展访问统计和用户行为分析

### 🎯 低优先级
- [ ] **移动端**: 开发微信小程序或APP
- [ ] **多校扩展**: 支持其他高校的定制化需求
- [ ] **AI升级**: 集成更多大语言模型
- [ ] **国际化**: 支持多语言界面

## 🛠️ 开发指南

### 新知识库管理系统

项目已集成完整的知识库管理API，支持程序化添加和管理：

```python
# 1. API方式添加知识条目
import requests

url = "http://localhost:8080/api/v1/knowledge"
data = {
    "category": "policy",
    "title": "新政策标题",
    "content": "政策详细内容...",
    "tags": ["标签1", "标签2"],
    "metadata": {"priority": "high"}
}
response = requests.post(url, json=data)
```

```bash
# 2. 命令行方式管理
python scripts/manage_knowledge.py add --category policy --title "新政策"
python scripts/manage_knowledge.py list --category policy
python scripts/manage_knowledge.py search "关键词"
```

### 扩展新领域知识

```python
# 添加学籍管理知识
from src.core.knowledge.json_manager import JSONKnowledgeManager

manager = JSONKnowledgeManager()
await manager.load()

# 添加学籍相关条目
new_item = KnowledgeItem(
    category="academic",  # 新分类
    title="学籍证明开具流程",
    content="详细流程说明...",
    tags=["学籍", "证明", "流程"]
)
await manager.add_item(new_item)
```

### 添加新的RAG引擎

```python
from src.core.rag.base import RAGEngine

class CustomRAGEngine(RAGEngine):
    async def search(self, query: str, top_k: int = 5):
        # 实现自定义搜索逻辑
        pass
```

## 📊 项目状态

### 当前版本: v1.0.0
- ✅ **核心功能**: 医疗报销智能问答
- ✅ **部署状态**: Railway云端部署
- ✅ **访问统计**: 实时用户访问分析
- ✅ **知识库**: 33条专业报销知识
- ✅ **安全加固**: 访问控制、输入验证、环境变量管理

### 访问地址
- **生产环境**: https://www.bjtuai.cn
- **备用地址**: https://bjtu-wh-medical-reimbursement-llm-production.up.railway.app
- **统计面板**: https://www.bjtuai.cn/stats

## 🚀 服务器迁移和备案策略

### 当前部署 (Railway)
- **服务器**: Railway (海外)
- **优势**: 免费、部署简单、自动CI/CD
- **劣势**: 无法备案、国内访问可能受限
- **状态**: 开发测试阶段

### 目标部署 (阿里云)
- **服务器**: 阿里云ECS + RDS
- **优势**: 国内服务器、支持备案、扩展性强
- **成本**: 新用户1年免费
- **状态**: 准备迁移

### 备案策略: 先开发后备案 ⭐

#### 阶段1: 继续开发 (当前-1个月)
```
服务器: Railway (海外)
域名: www.bjtuai.cn
状态: 开发测试，收集用户反馈
目标: 验证产品价值，完善功能
```

#### 阶段2: 准备迁移 (1-2个月)
```
服务器: 阿里云免费ECS
备案: 个人备案申请
状态: 准备材料，申请备案
目标: 完成备案，准备迁移
```

#### 阶段3: 正式上线 (2-3个月)
```
服务器: 阿里云 (已备案)
域名: www.bjtuai.cn (已备案)
状态: 正式运营，开始收费
目标: 商业化运营
```

### 备案方案: 个人备案
- **备案主体**: 个人
- **优势**: 流程简单、材料要求少、审核快
- **材料**: 身份证、个人承诺书、域名证书、服务器合同
- **时间**: 1-2个月

## 📞 技术支持

- **项目负责人**: 曹益波
- **技术栈**: Python + FastAPI + 通义千问 + RAG
- **问题反馈**: 通过Web界面或API接口
- **开发文档**: 详见 `docs/` 目录

## 📄 许可证

MIT License

---

**🎯 产品使命**: 从医疗报销起步，打造全方位的校园智能助手

**🌟 发展愿景**: 让校园生活咨询变得简单、准确、高效

*Built with ❤️ using 阿里通义千问 RAG技术*
