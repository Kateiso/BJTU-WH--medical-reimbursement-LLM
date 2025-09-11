# 🎓 校园智能助手

> 基于RAG技术的智能问答系统，从医疗报销起步，逐步扩展为全方位校园生活助手

[![项目状态](https://img.shields.io/badge/状态-开发中-green)](https://github.com/Kateiso/BJTU-WH--medical-reimbursement-LLM)
[![版本](https://img.shields.io/badge/版本-v1.0.0-blue)](https://github.com/Kateiso/BJTU-WH--medical-reimbursement-LLM)
[![部署](https://img.shields.io/badge/部署-Railway-orange)](https://www.bjtuai.cn)
[![安全](https://img.shields.io/badge/安全-已加固-green)](https://www.bjtuai.cn/stats)

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
- 🛡️ **安全可靠**: 访问控制、输入验证、环境变量管理

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 通义千问API密钥

### 安装运行
```bash
# 1. 克隆项目
git clone https://github.com/Kateiso/BJTU-WH--medical-reimbursement-LLM.git
cd mediAi

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
export DASHSCOPE_API_KEY=your_api_key_here

# 4. 启动应用
python qwen_stream_app.py
```

### 访问应用
- **Web界面**: http://localhost:8081/web
- **API文档**: http://localhost:8081/docs
- **健康检查**: http://localhost:8081/health
- **访问统计**: http://localhost:8081/stats

## 🌐 在线体验

- **生产环境**: https://www.bjtuai.cn
- **备用地址**: https://bjtu-wh-medical-reimbursement-llm-production.up.railway.app
- **统计面板**: https://www.bjtuai.cn/stats

## 📊 项目状态

### 当前版本: v1.0.0
- ✅ **核心功能**: 医疗报销智能问答
- ✅ **部署状态**: Railway云端部署
- ✅ **安全加固**: 访问控制、输入验证、环境变量管理
- ✅ **知识库**: 33条专业报销知识
- ✅ **访问统计**: 实时用户访问分析

### 技术栈
- **后端**: Python + FastAPI + 通义千问
- **前端**: HTML + JavaScript + WebSocket
- **部署**: Railway + Docker
- **数据库**: JSON文件存储

## 📚 文档导航

| 文档 | 描述 | 受众 |
|------|------|------|
| [📋 产品需求文档](PRD.md) | 产品设计、用户需求、功能规格 | 产品经理、开发者 |
| [📝 开发任务清单](task.md) | 详细任务分解、优先级、进度跟踪 | 开发者、项目经理 |
| [🏗️ 技术架构](docs/技术架构.md) | 系统架构、技术选型、设计决策 | 开发者、架构师 |
| [🚀 部署指南](docs/部署指南.md) | 部署流程、环境配置、运维管理 | 运维、开发者 |
| [📄 API文档](docs/API文档.md) | 接口规范、使用示例、错误码 | 开发者、集成方 |
| [📋 备案指南](docs/备案申请指南.md) | 备案流程、材料准备、合规要求 | 合规、法务 |

## 🛠️ 开发指南

### 项目结构
```
mediAi/
├── qwen_stream_app.py          # 主应用
├── src/                        # 源代码
│   ├── core/                   # 核心业务逻辑
│   ├── config/                 # 配置管理
│   └── web/                    # Web界面
├── data/                       # 数据文件
├── docs/                       # 文档
├── tests/                      # 测试
└── requirements.txt            # 依赖
```

### 贡献指南
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系我们

- **项目负责人**: 曹益波
- **技术栈**: Python + FastAPI + 通义千问 + RAG
- **问题反馈**: 通过GitHub Issues或Web界面
- **邮箱**: C.yibo2@gmail.com

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

**🎯 产品使命**: 从医疗报销起步，打造全方位的校园智能助手

**🌟 发展愿景**: 让校园生活咨询变得简单、准确、高效

*Built with ❤️ using 阿里通义千问 RAG技术*
