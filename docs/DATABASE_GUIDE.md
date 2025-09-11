# 数据库管理指南

## 概述

本项目使用 **JSON 文件数据库** 存储知识库数据，这是一种轻量级、易维护的 NoSQL 方案。

## 数据库结构

### 文件位置
```
/data/knowledge_base.json
```

### 数据结构
```json
{
  "knowledge_base": [
    {
      "category": "policy",           // 分类
      "title": "学生门诊报销比例",     // 标题
      "content": "具体内容...",       // 内容
      "tags": ["门诊", "报销比例"],   // 标签
      "metadata": {...}              // 元数据
    }
  ]
}
```

## 分类体系

| 分类 | 用途 | 示例 |
|------|------|------|
| `policy` | 报销政策 | 门诊/住院报销比例 |
| `materials` | 材料要求 | 发票、病历等 |
| `procedure` | 流程步骤 | 申请、审核流程 |
| `contacts` | 联系人 | 老师、医院联系方式 |
| `hospitals` | 医院信息 | 地址、电话、预约方式 |
| `common_questions` | 常见问题 | FAQ 问答 |
| `special_cases` | 特殊情况 | 急诊、异地就医 |
| `greetings` | 问候语 | 聊天回复模板 |

## API 接口

### 1. 创建知识条目
```http
POST /api/v1/knowledge
Content-Type: application/json

{
  "category": "policy",
  "title": "新政策标题",
  "content": "政策详细内容...",
  "tags": ["标签1", "标签2"],
  "metadata": {"priority": "high"}
}
```

### 2. 获取知识条目
```http
GET /api/v1/knowledge/{item_id}
```

### 3. 更新知识条目
```http
PUT /api/v1/knowledge/{item_id}
Content-Type: application/json

{
  "title": "更新后的标题",
  "content": "更新后的内容"
}
```

### 4. 删除知识条目
```http
DELETE /api/v1/knowledge/{item_id}
```

### 5. 按分类获取条目
```http
GET /api/v1/knowledge/category/{category}
```

### 6. 搜索知识库
```http
POST /api/v1/search
Content-Type: application/json

{
  "query": "门诊报销",
  "category": "policy",
  "limit": 10
}
```

## 操作方法

### Python 代码示例

```python
from src.core.knowledge.json_manager import JSONKnowledgeManager
from src.core.knowledge.base import KnowledgeItem

# 初始化管理器
manager = JSONKnowledgeManager()
await manager.load()

# 创建新条目
new_item = KnowledgeItem(
    category="policy",
    title="新政策",
    content="政策内容",
    tags=["标签1", "标签2"],
    metadata={"priority": "high"}
)
await manager.add_item(new_item)

# 搜索条目
results = await manager.search("门诊报销", limit=5)

# 更新条目
item = await manager.get_by_id("item_id")
item.title = "新标题"
await manager.update_item(item)

# 删除条目
await manager.delete_item("item_id")
```

## 添加新条目的步骤

### 方法一：通过 API 接口

1. **启动服务**
```bash
python start.py
```

2. **使用 curl 添加条目**
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "policy",
    "title": "新政策标题",
    "content": "政策详细内容...",
    "tags": ["标签1", "标签2"],
    "metadata": {"priority": "high"}
  }'
```

3. **使用 Python requests**
```python
import requests

url = "http://localhost:8000/api/v1/knowledge"
data = {
    "category": "policy",
    "title": "新政策标题",
    "content": "政策详细内容...",
    "tags": ["标签1", "标签2"],
    "metadata": {"priority": "high"}
}

response = requests.post(url, json=data)
print(response.json())
```

### 方法二：直接编辑 JSON 文件

1. **打开文件**
```bash
nano /data/knowledge_base.json
```

2. **添加新条目**
```json
{
  "knowledge_base": [
    // ... 现有条目 ...
    {
      "category": "policy",
      "title": "新政策标题",
      "content": "政策详细内容...",
      "tags": ["标签1", "标签2"]
    }
  ]
}
```

3. **保存文件** (Ctrl+X, Y, Enter)

### 方法三：使用 Python 脚本

```python
#!/usr/bin/env python3
"""
添加知识库条目的脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.knowledge.json_manager import JSONKnowledgeManager
from src.core.knowledge.base import KnowledgeItem

async def add_knowledge_item():
    """添加知识库条目"""
    manager = JSONKnowledgeManager()
    await manager.load()
    
    # 创建新条目
    new_item = KnowledgeItem(
        category="policy",
        title="新政策标题",
        content="政策详细内容...",
        tags=["标签1", "标签2"],
        metadata={"priority": "high"}
    )
    
    success = await manager.add_item(new_item)
    if success:
        print(f"✅ 成功添加条目: {new_item.id}")
        print(f"标题: {new_item.title}")
        print(f"分类: {new_item.category}")
    else:
        print("❌ 添加条目失败")

if __name__ == "__main__":
    asyncio.run(add_knowledge_item())
```

## 最佳实践

### 1. 数据质量
- **标题简洁明确**：便于搜索和识别
- **内容完整准确**：包含所有必要信息
- **标签合理**：便于分类和检索
- **分类正确**：确保数据组织清晰

### 2. 备份策略
```bash
# 备份知识库
cp data/knowledge_base.json data/knowledge_base_backup_$(date +%Y%m%d).json

# 恢复备份
cp data/knowledge_base_backup_20240101.json data/knowledge_base.json
```

### 3. 数据验证
```python
# 验证 JSON 格式
import json

with open('data/knowledge_base.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print("✅ JSON 格式正确")
```

### 4. 批量操作
```python
# 批量添加条目
items_to_add = [
    {
        "category": "policy",
        "title": "政策1",
        "content": "内容1",
        "tags": ["标签1"]
    },
    {
        "category": "policy", 
        "title": "政策2",
        "content": "内容2",
        "tags": ["标签2"]
    }
]

for item_data in items_to_add:
    item = KnowledgeItem(**item_data)
    await manager.add_item(item)
```

## 故障排除

### 常见问题

1. **JSON 格式错误**
   - 检查括号、引号是否匹配
   - 使用 JSON 验证工具

2. **文件权限问题**
   - 确保有读写权限
   - 检查文件路径是否正确

3. **编码问题**
   - 确保使用 UTF-8 编码
   - 检查中文字符显示

### 调试方法

```python
# 检查知识库状态
stats = await manager.get_stats()
print(f"总条目数: {stats['total_items']}")
print(f"分类: {stats['categories']}")

# 搜索测试
results = await manager.search("测试", limit=5)
print(f"搜索结果: {len(results)} 条")
```

## 扩展建议

### 1. 数据迁移
- 考虑迁移到 SQLite 或 PostgreSQL
- 实现数据导入导出功能

### 2. 版本控制
- 集成 Git 进行版本管理
- 实现数据变更历史记录

### 3. 数据验证
- 添加数据格式验证
- 实现必填字段检查

### 4. 性能优化
- 实现数据索引
- 添加缓存机制

---

**Better phrasing**: "数据管理工具箱，JSON 让知识库更灵活"
