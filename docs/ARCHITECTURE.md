# 架构设计文档

## 1. 项目概述

**Manuskit** 是一个工业级自动化智能网页内容提取平台，基于 FastAPI、Steel SDK 和 browser-use 框架构建。平台专注于从 Reddit Answers 等网站提取结构化内容，通过 AI 驱动的浏览器自动化技术实现智能数据抓取。

### 1.1 核心特性

- **异步任务管理**：非阻塞式任务队列，支持并发控制
- **AI 驱动提取**：基于 LLM 的智能浏览器自动化
- **RESTful API**：生产级 FastAPI 接口，支持 OpenAPI 文档
- **结构化输出**：严格遵循预定义数据模式
- **高可用性**：完善的错误处理、日志记录和健康检查
- **灵活部署**：支持官方 Steel 和自托管 Steel 两种模式

### 1.2 技术栈

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| Web 框架 | FastAPI | 0.115+ | RESTful API 服务 |
| 浏览器自动化 | Steel SDK | 0.13.0 | 浏览器会话管理 |
| AI 代理 | browser-use | 0.9.5 | AI 驱动的浏览器操作 |
| 协议层 | CDP (Chrome DevTools Protocol) | 1.4.3 | 底层浏览器控制 |
| AI 模型 | OpenAI API / 兼容接口 | - | LLM 推理引擎 |
| 数据验证 | Pydantic | 2.x | 数据模型与验证 |
| 异步运行时 | asyncio | 标准库 | 异步任务执行 |
| 服务器 | Uvicorn / Gunicorn | - | ASGI 应用服务器 |

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Layer                            │
│  (HTTP Clients, API Consumers, Frontend Applications)           │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP/REST
┌───────────────────────────────▼─────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  API Endpoints (src/main.py)                               │ │
│  │  • POST /api/v1/extract        - Create async task         │ │
│  │  • POST /api/v1/extract/sync   - Sync extraction           │ │
│  │  • GET  /api/v1/tasks/{id}     - Get task status           │ │
│  │  • GET  /api/v1/tasks          - List tasks                │ │
│  │  • DELETE /api/v1/tasks/{id}   - Cancel task               │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Middleware                                                 │ │
│  │  • CORS - Cross-Origin Resource Sharing                    │ │
│  │  • Exception Handler - Global error handling               │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                      Service Layer                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Task Manager (src/services/task_manager.py)              │ │
│  │  • Task creation & lifecycle management                    │ │
│  │  • Status tracking (pending/running/completed/failed)      │ │
│  │  • Async execution with semaphore-based concurrency       │ │
│  │  • Result storage & retrieval                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Extraction Service (src/services/extraction_service.py)  │ │
│  │  • Steel client initialization                             │ │
│  │  • LLM configuration (OpenAI/custom endpoints)            │ │
│  │  • Browser session management                              │ │
│  │  • Agent task orchestration                                │ │
│  │  • Result parsing & normalization                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                   Browser Automation Layer                       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │   Steel SDK     │  │   browser-use    │  │    CDP-use     │ │
│  │                 │  │                  │  │                │ │
│  │ • Session mgmt  │→ │ • AI Agent       │→ │ • CDP control  │ │
│  │ • API client    │  │ • Action planning│  │ • Protocol I/O │ │
│  │ • CDP URL       │  │ • Vision support │  │ • State sync   │ │
│  └─────────────────┘  └──────────────────┘  └────────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │ WebSocket (CDP)
┌───────────────────────────────▼─────────────────────────────────┐
│                      Browser Infrastructure                      │
│  ┌──────────────────────┐         ┌─────────────────────────┐  │
│  │  Official Steel      │   OR    │  Self-hosted Steel      │  │
│  │  wss://steel.dev     │         │  ws://YOUR_IP:PORT      │  │
│  │                      │         │                         │  │
│  │  • Managed service   │         │  • On-premise deploy    │  │
│  │  • Auto-scaling      │         │  • Full control         │  │
│  │  • Pay-per-use       │         │  • Custom config        │  │
│  └──────────────────────┘         └─────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │          Chrome/Chromium Browser Instances                 │ │
│  │  • Headless mode                                           │ │
│  │  • JavaScript execution                                    │ │
│  │  • Page rendering & interaction                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流架构

```
Client Request
    │
    ▼
┌──────────────────────────────────────┐
│  1. API Endpoint receives request    │
│     (ExtractionRequest: question)    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  2. Task Manager creates task        │
│     • Generate UUID                  │
│     • Initialize TaskInfo            │
│     • Status: PENDING                │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  3. Submit task for async execution  │
│     • asyncio.create_task()          │
│     • Semaphore control (max 5)      │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  4. Extraction Service starts        │
│     • Create Steel client            │
│     • Initialize LLM                 │
│     • Status: RUNNING                │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  5. Steel session creation           │
│     • Official: wss://steel.dev      │
│     • Self-hosted: ws://IP:PORT      │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  6. Browser-use Agent execution      │
│     • Navigate to Reddit Answers     │
│     • Input question & submit        │
│     • Wait for page load             │
│     • Scroll to reveal content       │
│     • Extract structured data        │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  7. Result parsing & normalization   │
│     • Parse agent JSON output        │
│     • Type coercion (int→str)        │
│     • Handle None values             │
│     • Validate with Pydantic         │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  8. Task completion                  │
│     • Status: COMPLETED/FAILED       │
│     • Store ExtractionResult         │
│     • Release Steel session          │
└──────────────┬───────────────────────┘
               │
               ▼
Client polls /api/v1/tasks/{task_id}
    │
    ▼
Returns ExtractionResult
```

## 3. 模块设计

### 3.1 API 层 (src/main.py)

**职责**：
- HTTP 请求处理
- 请求验证与响应序列化
- 错误处理与异常转换
- CORS 策略控制

**关键类/函数**：
```python
app = FastAPI(title="Web Content Extraction Platform", version="1.0.0")

@app.post("/api/v1/extract")           # 异步任务创建
@app.post("/api/v1/extract/sync")      # 同步提取
@app.get("/api/v1/tasks/{task_id}")    # 任务状态查询
@app.get("/api/v1/tasks")              # 任务列表
@app.delete("/api/v1/tasks/{task_id}") # 任务取消
@app.get("/api/v1/stats")              # 统计信息
@app.get("/health")                    # 健康检查
```

**生命周期管理**：
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize task_manager
    # Yield: Application running
    # Shutdown: Cleanup resources
```

### 3.2 服务层

#### 3.2.1 任务管理器 (src/services/task_manager.py)

**职责**：
- 任务创建、存储、查询
- 异步执行调度
- 并发控制（Semaphore）
- 状态追踪与更新
- 统计数据收集

**核心数据结构**：
```python
class TaskManager:
    tasks: Dict[str, TaskInfo]              # 任务存储
    semaphore: asyncio.Semaphore            # 并发控制
    max_concurrent_tasks: int               # 最大并发数
    extraction_service: ExtractionService   # 提取服务实例
```

**任务状态机**：
```
PENDING → RUNNING → COMPLETED
                  ↘ FAILED
                  ↘ CANCELLED
```

#### 3.2.2 提取服务 (src/services/extraction_service.py)

**职责**：
- Steel 客户端配置与初始化
- LLM 模型加载与配置
- Browser-use Agent 创建与执行
- CDP 连接管理
- 结果解析与数据规范化

**Steel 配置模式**：

| 配置 | STEEL_API_KEY | STEEL_BASE_URL | CDP URL | 用途 |
|------|---------------|----------------|---------|------|
| 官方 Steel | ✅ 已配置 | ❌ 空 | `wss://connect.steel.dev?apiKey=xxx&sessionId=xxx` | 使用托管服务 |
| 自托管 Steel | ❌ 空 | ✅ 已配置 | `ws://IP:PORT` (从 base_url) | 私有化部署 |
| 本地浏览器 | ❌ 空 | ❌ 空 | 无 (Playwright 本地) | 开发测试 |

**关键方法**：
```python
class ExtractionService:
    def _create_steel_client() -> Steel
    def _create_llm() -> ChatOpenAI
    async def extract_reddit_answers(question: str) -> ExtractionResult
    def _parse_agent_result(agent_result, question) -> ExtractionResult
    def _normalize_result_data(data) -> Dict[str, Any]
```

**数据规范化逻辑**：
```python
# 处理 Agent 返回的 None 值
if post.get('url') is None: post['url'] = ""
if post.get('upvotes') is None: post['upvotes'] = 0
# 类型转换
if isinstance(post['rank'], int): post['rank'] = str(post['rank'])
```

### 3.3 数据模型层 (src/models.py)

**输入模型**：
```python
class ExtractionRequest(BaseModel):
    question: str  # 用户问题
```

**输出模型**：
```python
class ExtractionResult(BaseModel):
    url: str                           # Reddit Answers 页面 URL
    question: str                      # 原始问题
    sources: List[str]                 # 来源 subreddit URLs
    sections: List[ContentSection]     # 结构化答案章节
    relatedPosts: List[PostMetadata]   # 相关帖子元数据
    relatedTopics: List[str]           # 相关主题建议

class ContentSection(BaseModel):
    heading: str          # 章节标题
    content: List[str]    # 段落内容数组

class PostMetadata(BaseModel):
    rank: str        # 排名（字符串）
    title: str       # 帖子标题
    subreddit: str   # 所属 subreddit
    url: str         # 帖子 URL
    upvotes: int     # 点赞数
    comments: int    # 评论数
    domain: str      # 域名
    promoted: bool   # 是否推广
    score: int       # 分数
```

**任务模型**：
```python
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskInfo(BaseModel):
    task_id: str
    status: TaskStatus
    question: str
    created_at: datetime
    updated_at: datetime
    result: Optional[ExtractionResult]
    error: Optional[str]
    metadata: Dict[str, Any]
```

## 4. 核心流程

### 4.1 异步任务执行流程

```python
# 1. 客户端发起请求
POST /api/v1/extract
{
  "question": "how many planets are in our solar system?"
}

# 2. API 创建任务
task_id = task_manager.create_task(question)
task_manager.submit_task(task_id)

# 3. 异步执行
async def execute_task(task_id):
    async with semaphore:  # 并发控制
        update_status(RUNNING)
        result = await extraction_service.extract_reddit_answers(question)
        update_status(COMPLETED, result=result)

# 4. 客户端轮询
GET /api/v1/tasks/{task_id}
→ { "status": "completed", "result": {...} }
```

### 4.2 浏览器自动化流程

```python
# 1. 创建 Steel 会话
steel_client = Steel(base_url=STEEL_BASE_URL)
session = steel_client.sessions.create()

# 2. 构建 CDP URL
if has_api_key:
    cdp_url = f"wss://connect.steel.dev?apiKey={key}&sessionId={session.id}"
elif has_base_url:
    cdp_url = f"ws://{base_url}"  # 优先使用 base_url

# 3. 创建浏览器会话
browser_session = BrowserSession(cdp_url=cdp_url)

# 4. 创建 AI Agent
agent = Agent(
    task="Go to reddit.com/answers and search...",
    llm=ChatOpenAI(model="gpt-4o"),
    browser_session=browser_session
)

# 5. 执行任务
result = await agent.run()

# 6. 清理会话
steel_client.sessions.release(session.id)
```

### 4.3 错误处理流程

```python
try:
    result = await agent.run()
except ValidationError as e:
    # Pydantic 验证失败
    logger.error(f"Validation error: {e}")
    return HTTPException(400, "Invalid data format")
except ConnectionError as e:
    # Steel/浏览器连接失败
    logger.error(f"Connection error: {e}")
    return HTTPException(503, "Browser service unavailable")
except Exception as e:
    # 其他未知错误
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return HTTPException(500, "Internal server error")
finally:
    # 确保资源清理
    if session:
        steel_client.sessions.release(session.id)
```

## 5. 安全性设计

### 5.1 API 安全

- **CORS 配置**：生产环境需配置白名单
- **Rate Limiting**：建议使用 slowapi 或 Nginx 限流
- **API Key 认证**：可集成 FastAPI Security
- **HTTPS**：生产环境必须启用 TLS

### 5.2 数据安全

- **敏感信息脱敏**：日志中不记录完整 API Key
- **环境变量隔离**：`.env` 文件不提交到版本控制
- **输入验证**：Pydantic 模型强制类型检查
- **输出清理**：防止 XSS 攻击（如果返回 HTML）

### 5.3 资源安全

- **并发限制**：Semaphore 控制最大并发数
- **超时机制**：防止任务永久挂起
- **内存管理**：及时清理已完成任务数据
- **会话清理**：确保 Steel 会话正确释放

## 6. 性能优化

### 6.1 异步优化

- **非阻塞 I/O**：使用 asyncio 实现异步任务执行
- **连接池**：Steel SDK 内部管理连接复用
- **并发控制**：Semaphore 限制最大并发，避免资源耗尽

### 6.2 缓存策略

- **任务结果缓存**：可集成 Redis 缓存已完成任务
- **LLM 响应缓存**：相同问题复用结果
- **浏览器会话复用**：Steel 会话可重用（需验证）

### 6.3 资源管理

- **连接池大小**：根据服务器配置调整
- **任务队列大小**：防止内存溢出
- **日志轮转**：避免日志文件过大
- **监控指标**：集成 Prometheus 监控关键指标

## 7. 可扩展性

### 7.1 水平扩展

```
Load Balancer (Nginx)
    │
    ├─► App Instance 1 (4 workers)
    ├─► App Instance 2 (4 workers)
    └─► App Instance 3 (4 workers)
         │
         └─► Shared Redis (任务状态)
         └─► Steel Infrastructure (浏览器池)
```

### 7.2 垂直扩展

- 增加 `MAX_CONCURRENT_TASKS` 配置
- 提升 Gunicorn workers 数量
- 增加服务器 CPU/内存资源

### 7.3 功能扩展

- **多站点支持**：扩展 `extract_generic_content` 方法
- **自定义提取**：支持用户自定义提取规则
- **Webhook 通知**：任务完成后推送通知
- **批量任务**：支持批量提交多个问题

## 8. 监控与日志

### 8.1 日志级别

```python
logging.basicConfig(
    level=logging.INFO,  # 生产环境建议 INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**关键日志点**：
- 任务创建/完成/失败
- Steel 会话创建/释放
- Agent 执行步骤
- 错误堆栈跟踪

### 8.2 监控指标

**业务指标**：
- 任务成功率 (completed / total)
- 平均执行时间
- 并发任务数
- 任务队列长度

**系统指标**：
- CPU/内存使用率
- API 响应时间
- Steel 连接状态
- 错误率

### 8.3 健康检查

```python
GET /health
→ {"status": "healthy", "service": "...", "version": "1.0.0"}

GET /api/v1/stats
→ {
    "statistics": {
        "total": 150,
        "completed": 120,
        "failed": 5,
        ...
    }
}
```

## 9. 技术债务与改进方向

### 9.1 当前限制

1. **任务持久化**：任务数据仅存内存，重启丢失 → 建议集成数据库
2. **结果过期**：未实现自动清理旧任务 → 建议添加 TTL 机制
3. **重试机制**：失败任务无自动重试 → 建议集成 Celery
4. **模型支持**：DeepSeek 等模型兼容性问题 → 需适配不同模型特性

### 9.2 改进建议

**短期**：
- 集成 PostgreSQL 持久化任务数据
- 实现任务结果 TTL 自动清理
- 添加 Prometheus metrics 导出

**中期**：
- 集成 Celery + Redis 实现分布式任务队列
- 支持更多 LLM 提供商（Anthropic、Gemini）
- 实现 Webhook 回调通知

**长期**：
- 支持多站点内容提取
- 用户自定义提取规则引擎
- 实时任务执行进度推送 (WebSocket)

## 10. 附录

### 10.1 环境变量完整列表

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

### 10.2 推荐 LLM 模型

| 模型 | 提供商 | 支持状态 | 推荐场景 |
|------|--------|---------|---------|
| `gpt-4o` | OpenAI | ✅ 完全支持 | 生产环境（高准确度） |
| `gpt-4o-mini` | OpenAI | ✅ 完全支持 | 生产环境（性价比） |
| `gpt-4-turbo` | OpenAI | ✅ 完全支持 | 生产环境（快速响应） |
| `claude-3-5-sonnet` | Anthropic | ✅ 完全支持 | 生产环境（高质量） |
| `deepseek-reasoner` | DeepSeek | ⚠️ 部分支持 | 测试环境（需特殊配置） |
| `o1-mini` | OpenAI | ⚠️ 待验证 | 测试环境 |

### 10.3 参考文档

- [Steel SDK Documentation](https://docs.steel.dev)
- [browser-use Documentation](https://docs.browser-use.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Pydantic Documentation](https://docs.pydantic.dev)
