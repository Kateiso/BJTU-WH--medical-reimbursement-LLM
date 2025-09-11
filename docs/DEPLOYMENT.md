# 🚀 部署指南 - 医疗报销智能助手

## 📋 部署方案总览

| 方案 | 成本 | 难度 | 适用场景 | 访问方式 |
|------|------|------|----------|----------|
| **本地运行** | 免费 | ⭐ | 个人测试 | localhost:8080 |
| **ngrok公网** | 免费 | ⭐⭐ | 临时分享 | 动态域名 |
| **Vercel部署** | 免费 | ⭐⭐⭐ | 正式发布 | 固定域名 |
| **云服务器** | 10-100元/月 | ⭐⭐⭐⭐ | 商业使用 | 自定义域名 |

---

## 🎯 快速开始

### 方案1：一键部署（推荐新手）

```bash
# 运行一键部署脚本
python3 one_click_deploy.py
```

选择部署方式：
- `1` - 本地运行
- `2` - ngrok公网访问  
- `3` - 生成Vercel部署包

### 方案2：快速部署脚本

```bash
# 运行快速部署脚本
bash quick_deploy.sh
```

### 方案3：简化启动

```bash
# 直接启动（需要先安装依赖）
python3 simple_start.py
```

---

## 🌐 详细部署方案

### 1. 本地运行

**适用场景**: 个人测试、开发调试

```bash
# 安装依赖
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi uvicorn dashscope

# 启动服务
python3 simple_start.py
```

**访问地址**:
- 主页: http://localhost:8080
- Web界面: http://localhost:8080/web
- API文档: http://localhost:8080/docs

---

### 2. ngrok公网访问

**适用场景**: 临时分享、快速测试

#### 安装ngrok
```bash
# macOS
brew install ngrok/ngrok/ngrok

# Linux
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Windows
# 下载: https://ngrok.com/download
```

#### 注册ngrok账号
1. 访问: https://ngrok.com
2. 注册账号获取token
3. 配置token: `ngrok config add-authtoken YOUR_TOKEN`

#### 启动公网访问
```bash
# 使用专用脚本
bash ngrok_deploy.sh

# 或手动启动
python3 main.py &
ngrok http 8080
```

**特点**:
- ✅ 完全免费
- ✅ 5分钟搞定
- ❌ 地址会变化
- ❌ 免费版有连接限制

---

### 3. Vercel部署（推荐）

**适用场景**: 正式发布、长期使用

#### 部署步骤

1. **注册Vercel账号**
   - 访问: https://vercel.com
   - 使用GitHub账号注册

2. **安装Vercel CLI**
   ```bash
   npm install -g vercel
   ```

3. **生成部署包**
   ```bash
   python3 one_click_deploy.py
   # 选择选项 3
   ```

4. **部署到Vercel**
   ```bash
   cd vercel_deploy
   vercel login
   vercel --prod
   ```

5. **获得公网地址**
   - 类似: `https://mediAi-abc123.vercel.app`

**特点**:
- ✅ 完全免费
- ✅ 固定域名
- ✅ 自动部署
- ✅ 全球CDN
- ❌ 有使用限制

---

### 4. 云服务器部署

**适用场景**: 商业使用、高并发

#### 学生优惠服务器
- **阿里云学生机**: 9.9元/月
- **腾讯云学生机**: 10元/月
- **华为云学生机**: 9.9元/月

#### 海外VPS
- **Vultr**: $2.5/月（约18元）
- **DigitalOcean**: $4/月（约28元）

#### 部署脚本
```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/your-repo/deploy.sh
chmod +x deploy.sh

# 运行部署
bash deploy.sh your-domain.com
```

---

## 🔧 环境配置

### 环境变量
```bash
# 必需配置
DASHSCOPE_API_KEY=sk-2ea7b3f8fb7742828ff836eed6050f19

# 可选配置
DEBUG=false
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO
```

### 依赖安装
```bash
# 核心依赖
pip install fastapi uvicorn pydantic python-multipart dashscope python-dotenv

# 使用国内镜像（推荐）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi uvicorn dashscope
```

---

## 🧪 测试部署

### 功能测试
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
  -d '{"query": "报销材料"}'
```

### 性能测试
```bash
# 安装测试工具
pip install locust

# 运行压力测试
locust -f tests/locustfile.py --host=http://localhost:8080
```

---

## 🚨 常见问题

### Q1: 依赖安装失败
```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name

# 或使用conda
conda install package_name
```

### Q2: 端口被占用
```bash
# 查看端口占用
lsof -i :8080

# 杀死进程
kill -9 PID

# 或修改端口
export PORT=8081
```

### Q3: ngrok连接失败
```bash
# 检查token配置
ngrok config check

# 重新配置token
ngrok config add-authtoken YOUR_TOKEN
```

### Q4: Vercel部署失败
```bash
# 检查vercel.json配置
cat vercel.json

# 查看部署日志
vercel logs
```

---

## 📞 技术支持

- **项目地址**: https://github.com/your-repo/mediAi
- **问题反馈**: 通过GitHub Issues
- **技术交流**: 微信群/QQ群

---

## 🎯 推荐部署流程

### 新手用户
1. 运行 `python3 one_click_deploy.py`
2. 选择 `1` 本地运行测试
3. 测试成功后选择 `2` ngrok公网访问
4. 长期使用选择 `3` Vercel部署

### 开发者
1. 本地开发: `python3 simple_start.py`
2. 测试分享: `bash ngrok_deploy.sh`
3. 正式发布: Vercel部署
4. 商业使用: 云服务器部署

**🎉 现在就开始部署吧！选择最适合你的方案！**

