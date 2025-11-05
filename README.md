# Manuskit

**工业级自动化智能网页内容提取平台**

基于 FastAPI、Steel SDK 和 browser-use 框架构建的生产级内容提取服务，通过 AI 驱动的浏览器自动化技术实现智能数据抓取。

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 核心特性

- **🚀 异步任务管理** - 非阻塞式任务队列，支持并发控制
- **🤖 AI 驱动提取** - 基于 LLM 的智能浏览器自动化
- **🔌 RESTful API** - 生产级 FastAPI 接口，完整 OpenAPI 文档
- **📊 结构化输出** - 严格遵循预定义数据模式
- **⚡ 高性能** - 支持水平扩展和负载均衡
- **🔒 生产就绪** - 完善的错误处理、日志记录和监控
- **🌐 灵活部署** - 支持官方 Steel 和自托管 Steel

## 🏗️ 系统架构

```
┌─────────────────────────────────────┐
│     Client (HTTP/REST API)          │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│        FastAPI Application          │
│  ┌──────────────────────────────┐   │
│  │  API Endpoints & Middleware  │   │
│  └──────────────────────────────┘   │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│         Service Layer               │
│  ┌─────────────┬─────────────────┐  │
│  │ Task Manager│ Extraction Svc  │  │
│  └─────────────┴─────────────────┘  │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│    Browser Automation Layer         │
│  ┌──────────┬──────────┬─────────┐  │
│  │Steel SDK │browser- │CDP-use  │  │
│  │          │use      │         │  │
│  └──────────┴──────────┴─────────┘  │
└────────────────┬────────────────────┘
                 │ CDP (WebSocket)
┌────────────────▼────────────────────┐
│    Browser Infrastructure           │
│  Official Steel / Self-hosted Steel │
└─────────────────────────────────────┘
```

## 📦 快速开始

### 1. 系统要求

- Python 3.12+
- Steel Browser Service (官方或自托管)
- OpenAI API 或兼容接口

### 2. 安装

```bash
# 克隆项目
git clone <repository-url>
cd manuskit

# 创建虚拟环境
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

复制并编辑环境变量：

```bash
cp .env.example .env
```

**最小配置**（自托管 Steel）：
```bash
# Steel 配置
STEEL_BASE_URL=http://your-steel-server:3000

# LLM 配置
MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

或者**使用官方 Steel**：
```bash
STEEL_API_KEY=sk_live_your_steel_api_key
```

### 4. 运行

**开发模式**：
```bash
# 直接运行
python -m src.main

# 或使用 uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```

**生产模式**：
```bash
gunicorn src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8080 \
    --timeout 300
```

### 5. 验证

```bash
# 健康检查
curl http://localhost:8080/health

# 访问 API 文档
open http://localhost:8080/docs
```

## 🔥 使用示例

### 异步提取（推荐）

```bash
# 1. 创建任务
curl -X POST http://localhost:8080/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"question":"how many planets are in our solar system?"}'

# 响应
{
  "task_id": "a1b2c3d4-...",
  "status": "pending",
  "message": "Task created and submitted for processing"
}

# 2. 查询任务状态
curl http://localhost:8080/api/v1/tasks/a1b2c3d4-...

# 3. 获取结果（当 status 为 completed）
{
  "task_id": "a1b2c3d4-...",
  "status": "completed",
  "result": {
    "url": "https://www.reddit.com/answers/...",
    "question": "how many planets are in our solar system?",
    "sources": [...],
    "sections": [...],
    "relatedPosts": [...],
    "relatedTopics": [...]
  }
}
```

### 同步提取（简单场景）

```bash
curl -X POST http://localhost:8080/api/v1/extract/sync \
  -H "Content-Type: application/json" \
  -d '{"question":"tips to improve water pressure"}'

# 直接返回完整结果（阻塞直到完成）
```

### Python 客户端示例

```python
import requests
import time

# 创建任务
response = requests.post(
    "http://localhost:8080/api/v1/extract",
    json={"question": "how many planets are in our solar system?"}
)
task_id = response.json()["task_id"]

# 轮询任务状态
while True:
    response = requests.get(f"http://localhost:8080/api/v1/tasks/{task_id}")
    data = response.json()
    
    if data["status"] == "completed":
        print("Success!", data["result"])
        break
    elif data["status"] == "failed":
        print("Failed:", data["error"])
        break
    
    time.sleep(5)  # 等待 5 秒后重试
```

## 📚 文档

- **[架构设计文档](docs/ARCHITECTURE.md)** - 系统架构、模块设计和核心流程
- **[API 接口文档](docs/API.md)** - 完整的 RESTful API 参考
- **[部署文档](docs/DEPLOYMENT.md)** - 生产环境部署指南

### 在线文档

启动服务后访问：
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

## 🌟 API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/` | API 信息和端点列表 |
| `GET` | `/health` | 健康检查 |
| `GET` | `/docs` | 交互式 API 文档 (Swagger) |
| `GET` | `/api/v1/stats` | 平台统计信息 |
| `POST` | `/api/v1/extract` | 创建异步提取任务 |
| `POST` | `/api/v1/extract/sync` | 同步提取（阻塞） |
| `GET` | `/api/v1/tasks/{task_id}` | 查询任务状态和结果 |
| `GET` | `/api/v1/tasks` | 列出所有任务 |
| `DELETE` | `/api/v1/tasks/{task_id}` | 取消待处理任务 |

## 🛠️ 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| Web 框架 | FastAPI | 0.115+ |
| 浏览器自动化 | Steel SDK | 0.13.0 |
| AI 代理 | browser-use | 0.9.5 |
| 协议层 | CDP (Chrome DevTools) | 1.4.3 |
| AI 模型 | OpenAI API / 兼容接口 | - |
| 数据验证 | Pydantic | 2.x |
| 异步运行时 | asyncio | 标准库 |
| 服务器 | Uvicorn / Gunicorn | - |

## 🔧 环境变量

| 变量 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `STEEL_API_KEY` | string | 否* | - | Steel 官方 API Key |
| `STEEL_BASE_URL` | string | 否* | - | 自托管 Steel 地址 |
| `OPENAI_API_KEY` | string | 是 | - | OpenAI API Key |
| `OPENAI_BASE_URL` | string | 否 | `https://api.openai.com/v1` | OpenAI 兼容端点 |
| `MODEL` | string | 否 | `gpt-4o-mini` | LLM 模型名称 |
| `HOST` | string | 否 | `0.0.0.0` | 服务器监听地址 |
| `PORT` | integer | 否 | `8080` | 服务器端口 |
| `MAX_CONCURRENT_TASKS` | integer | 否 | `5` | 最大并发任务数 |

\* 至少配置 `STEEL_API_KEY` 或 `STEEL_BASE_URL` 之一

## 🚀 生产部署

### Docker Compose

```yaml
version: '3.8'

services:
  manuskit:
    build: .
    ports:
      - "8080:8080"
    environment:
      - STEEL_BASE_URL=http://steel-service:3000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL=gpt-4o-mini
      - MAX_CONCURRENT_TASKS=10
    restart: unless-stopped
```

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f k8s-deployment.yaml
```

### Systemd Service

详见 [部署文档](docs/DEPLOYMENT.md)

## 📊 监控与日志

### 健康检查

```bash
curl http://localhost:8080/health
```

### 平台统计

```bash
curl http://localhost:8080/api/v1/stats
```

### 日志位置

- **Systemd**: `/var/log/manuskit/`
- **Docker**: `docker logs manuskit`
- **标准输出**: 开发模式直接输出

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系与支持

- **文档**: 查看 `docs/` 目录
- **API 文档**: `http://localhost:8080/docs`
- **问题反馈**: GitHub Issues

## 🎯 路线图

- [ ] 支持更多提取目标站点
- [ ] 用户自定义提取规则
- [ ] Webhook 回调通知
- [ ] 结果缓存与去重
- [ ] 任务持久化（数据库）
- [ ] WebSocket 实时进度推送
- [ ] 更多 LLM 提供商支持

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐️

---

**Made with ❤️ by Manuskit Team**
