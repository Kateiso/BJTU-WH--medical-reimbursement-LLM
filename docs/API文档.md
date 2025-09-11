# 📄 API文档

## 📋 API概述

**API版本**: v1.0  
**基础URL**: https://www.bjtuai.cn  
**协议**: HTTP/HTTPS + WebSocket  
**认证**: 无需认证 (公开API)  

---

## 🔗 端点列表

### HTTP端点
- `GET /` - 根路径 (重定向到Web界面)
- `GET /web` - Web界面
- `GET /health` - 健康检查
- `GET /stats` - 访问统计
- `GET /docs` - API文档 (Swagger UI)

### WebSocket端点
- `WebSocket /ws` - 实时问答服务

---

## 📊 HTTP API

### 1. 根路径

#### `GET /`
**描述**: 根路径，自动重定向到Web界面  
**响应**: 302重定向到 `/web`

```bash
curl -I https://www.bjtuai.cn/
# HTTP/1.1 302 Found
# Location: /web
```

### 2. Web界面

#### `GET /web`
**描述**: 返回Web界面HTML页面  
**响应**: HTML页面

```bash
curl https://www.bjtuai.cn/web
# 返回完整的HTML页面
```

### 3. 健康检查

#### `GET /health`
**描述**: 检查应用健康状态  
**响应**: JSON格式的健康状态信息

```bash
curl https://www.bjtuai.cn/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-09-11T10:00:00Z",
  "components": {
    "qwen_api": {
      "status": "healthy",
      "model": "qwen-plus",
      "response_time": 0.246
    },
    "knowledge_base": {
      "status": "healthy",
      "items_count": 33
    }
  }
}
```

**状态码**:
- `200` - 健康
- `503` - 服务不可用

### 4. 访问统计

#### `GET /stats`
**描述**: 获取访问统计信息  
**响应**: JSON格式的统计数据

```bash
curl https://www.bjtuai.cn/stats
```

**响应示例**:
```json
{
  "total_visits": 1000,
  "unique_visitors": 500,
  "today_visits": 50,
  "yesterday_visits": 45,
  "week_visits": 300,
  "most_active_hour": "14:00-15:00",
  "most_popular_endpoint": "/web",
  "endpoint_stats": {
    "/web": 800,
    "/health": 100,
    "/stats": 50
  },
  "daily_visits_last_7_days": {
    "2025-09-11": 50,
    "2025-09-10": 45
  },
  "hourly_distribution": {
    "14": 20,
    "15": 15
  },
  "top_user_agents": {
    "Mozilla/5.0": 400,
    "curl/8.7.1": 100
  },
  "last_updated": "2025-09-11T10:00:00Z"
}
```

---

## 🔌 WebSocket API

### 实时问答服务

#### `WebSocket /ws`
**描述**: 提供实时问答服务，支持流式响应  
**协议**: WebSocket  
**认证**: 无需认证  

#### 连接建立
```javascript
const ws = new WebSocket('wss://www.bjtuai.cn/ws');

ws.onopen = function(event) {
    console.log('WebSocket连接已建立');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
};

ws.onclose = function(event) {
    console.log('WebSocket连接已关闭');
};

ws.onerror = function(error) {
    console.error('WebSocket错误:', error);
};
```

#### 发送消息
**消息格式**: JSON字符串

```json
{
  "question": "感冒药能报销吗？"
}
```

**发送示例**:
```javascript
const message = {
    question: "感冒药能报销吗？"
};
ws.send(JSON.stringify(message));
```

#### 接收消息
**消息类型**:

1. **开始标记** (`type: "start"`)
```json
{
  "type": "start",
  "question": "感冒药能报销吗？"
}
```

2. **流式内容** (`type: "chunk"`)
```json
{
  "type": "chunk",
  "content": "根据北京交通大学威海校区的报销政策..."
}
```

3. **信息来源** (`type: "sources"`)
```json
{
  "type": "sources",
  "content": [
    {
      "id": "policy_001",
      "title": "学生门诊报销比例",
      "category": "政策",
      "score": 0.95
    }
  ]
}
```

4. **结束标记** (`type: "end"`)
```json
{
  "type": "end",
  "total_time": 2.5
}
```

5. **错误消息** (`type: "error"`)
```json
{
  "type": "error",
  "message": "问题不能为空"
}
```

#### 完整示例
```javascript
// 发送问题
ws.send(JSON.stringify({
    question: "感冒药能报销吗？"
}));

// 处理响应
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'start':
            console.log('开始处理问题:', data.question);
            break;
            
        case 'chunk':
            console.log('收到内容片段:', data.content);
            // 实时显示内容
            break;
            
        case 'sources':
            console.log('信息来源:', data.content);
            break;
            
        case 'end':
            console.log('回答完成，总耗时:', data.total_time);
            break;
            
        case 'error':
            console.error('错误:', data.message);
            break;
    }
};
```

---

## 🛡️ 安全限制

### 访问频率限制
- **每分钟**: 最多60次请求
- **每小时**: 最多1000次请求
- **IP白名单**: 本地IP不受限制

### 输入验证
- **问题长度**: 1-500字符
- **恶意脚本**: 自动过滤危险内容
- **空输入**: 拒绝空问题

### 错误处理
```json
{
  "type": "error",
  "message": "问题长度不能超过500字符"
}
```

---

## 📊 状态码

### HTTP状态码
- `200` - 成功
- `302` - 重定向
- `400` - 请求错误
- `404` - 未找到
- `429` - 请求过于频繁
- `500` - 服务器错误
- `503` - 服务不可用

### WebSocket状态码
- `1000` - 正常关闭
- `1008` - 访问频率过高
- `1011` - 服务器错误

---

## 🧪 测试示例

### 健康检查测试
```bash
# 测试健康检查
curl -X GET https://www.bjtuai.cn/health

# 预期响应
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 访问统计测试
```bash
# 测试访问统计
curl -X GET https://www.bjtuai.cn/stats

# 预期响应
{
  "total_visits": 1000,
  "unique_visitors": 500
}
```

### WebSocket测试
```javascript
// 测试WebSocket连接
const ws = new WebSocket('wss://www.bjtuai.cn/ws');

ws.onopen = () => {
    // 发送测试问题
    ws.send(JSON.stringify({
        question: "测试问题"
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到响应:', data);
};
```

---

## 📈 性能指标

### 响应时间
- **健康检查**: < 100ms
- **访问统计**: < 200ms
- **WebSocket连接**: < 500ms
- **AI问答**: < 3s

### 并发支持
- **HTTP请求**: 50+ 并发
- **WebSocket连接**: 20+ 并发
- **AI处理**: 10+ 并发

### 可用性
- **目标可用性**: > 99%
- **平均响应时间**: < 2s
- **错误率**: < 1%

---

## 🔧 集成示例

### Python集成
```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"收到消息: {data}")

def on_error(ws, error):
    print(f"错误: {error}")

def on_close(ws, close_status_code, close_msg):
    print("连接已关闭")

def on_open(ws):
    # 发送问题
    question = {"question": "感冒药能报销吗？"}
    ws.send(json.dumps(question))

# 建立连接
ws = websocket.WebSocketApp(
    "wss://www.bjtuai.cn/ws",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
```

### JavaScript集成
```javascript
class CampusAI {
    constructor() {
        this.ws = null;
        this.onMessage = null;
    }
    
    connect() {
        this.ws = new WebSocket('wss://www.bjtuai.cn/ws');
        
        this.ws.onopen = () => {
            console.log('连接已建立');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (this.onMessage) {
                this.onMessage(data);
            }
        };
        
        this.ws.onclose = () => {
            console.log('连接已关闭');
        };
    }
    
    ask(question) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ question }));
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// 使用示例
const ai = new CampusAI();
ai.onMessage = (data) => {
    console.log('收到响应:', data);
};

ai.connect();
ai.ask("感冒药能报销吗？");
```

---

## 📞 技术支持

**API负责人**: 曹益波  
**邮箱**: C.yibo2@gmail.com  
**电话**: 19862294890  

**API问题反馈**: 通过GitHub Issues或邮件联系

---

*最后更新: 2025-09-11*
*版本: v1.0*
