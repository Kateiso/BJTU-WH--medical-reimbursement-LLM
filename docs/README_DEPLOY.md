# 医疗报销智能助手 - 云端部署指南

## 🚀 快速部署

### 方案一：Railway（推荐）
1. **准备代码仓库**
   - 将代码推送到 GitHub/GitLab
   - 确保包含所有必要文件：`Dockerfile`, `requirements.txt`, `railway.json`

2. **Railway 部署**
   - 访问 [railway.app](https://railway.app)
   - 登录并创建新项目
   - 选择 "Deploy from GitHub repo"
   - 连接你的代码仓库

3. **配置环境变量**
   - 在 Railway 项目设置中添加：
     ```
     DASHSCOPE_API_KEY=sk-your-api-key-here
     ```
   - Railway 会自动设置 `PORT` 环境变量

4. **部署完成**
   - Railway 会自动构建并部署
   - 获得公网 URL，如：`https://your-app.railway.app`

### 方案二：Render
1. **连接仓库**
   - 访问 [render.com](https://render.com)
   - 创建新 Web Service
   - 连接 GitHub 仓库

2. **配置服务**
   - Build Command: `docker build -t app .`
   - Start Command: `python qwen_stream_app.py`
   - 添加环境变量：`DASHSCOPE_API_KEY`

### 方案三：Fly.io
1. **安装 Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **部署**
   ```bash
   fly launch
   fly secrets set DASHSCOPE_API_KEY=sk-your-key
   fly deploy
   ```

## 🐳 本地 Docker 测试

```bash
# 构建镜像
docker build -t mediai .

# 运行容器
docker run --rm -it \
  -e DASHSCOPE_API_KEY=sk-your-api-key \
  -p 8081:8081 \
  mediai

# 访问应用
open http://localhost:8081/web
```

## 📁 部署文件说明

- `Dockerfile`: 容器化配置
- `requirements.txt`: Python 依赖
- `railway.json`: Railway 部署配置
- `env.example`: 环境变量模板

## 🔧 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `DASHSCOPE_API_KEY` | 通义千问 API 密钥 | ✅ |
| `PORT` | 服务端口（PaaS 自动设置） | ❌ |

## 🌐 访问地址

部署完成后，可通过以下地址访问：
- **Web 界面**: `https://your-domain.com/web`
- **API 文档**: `https://your-domain.com/docs`
- **健康检查**: `https://your-domain.com/health`

## 💡 注意事项

1. **API 密钥安全**: 不要在代码中硬编码 API 密钥
2. **WebSocket 支持**: 确保选择的 PaaS 支持 WebSocket
3. **资源限制**: 注意免费额度的使用限制
4. **域名绑定**: 可绑定自定义域名提升用户体验

## 🆘 故障排除

### 常见问题
1. **构建失败**: 检查 `requirements.txt` 依赖版本
2. **启动失败**: 确认环境变量配置正确
3. **WebSocket 连接失败**: 检查 PaaS 的 WebSocket 支持

### 日志查看
```bash
# Railway
railway logs

# Render
在 Dashboard 查看 Build/Deploy 日志

# Fly.io
fly logs
```
