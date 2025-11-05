# API 接口文档

## 目录

- [1. 概述](#1-概述)
- [2. 认证](#2-认证)
- [3. 通用响应格式](#3-通用响应格式)
- [4. 系统接口](#4-系统接口)
- [5. 内容提取接口](#5-内容提取接口)
- [6. 任务管理接口](#6-任务管理接口)
- [7. 数据模型](#7-数据模型)
- [8. 错误码](#8-错误码)
- [9. 最佳实践](#9-最佳实践)

## 1. 概述

### 1.1 基本信息

- **Base URL**: `http://your-domain.com` 或 `http://localhost:8080` (开发环境)
- **Protocol**: HTTP/HTTPS
- **Content-Type**: `application/json`
- **API Version**: v1
- **文档版本**: 1.0.0

### 1.2 快速开始

```bash
# 健康检查
curl http://localhost:8080/health

# 创建异步提取任务
curl -X POST http://localhost:8080/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"question":"how many planets are in our solar system?"}'

# 查询任务状态
curl http://localhost:8080/api/v1/tasks/{task_id}
```

### 1.3 交互式文档

启动服务后访问：
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

## 2. 认证

当前版本暂不需要认证。生产环境建议添加：
- API Key 认证（Header: `X-API-Key`）
- OAuth 2.0
- JWT Token

## 3. 通用响应格式

### 3.1 成功响应

```json
{
  "data": { /* 响应数据 */ },
  "status": "success"
}
```

### 3.2 错误响应

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "status_code": 400
}
```

## 4. 系统接口

### 4.1 根路径

获取 API 基本信息和端点列表。

**Endpoint**: `GET /`

**Response** (200 OK):
```json
{
  "service": "Web Content Extraction Platform",
  "version": "1.0.0",
  "description": "Industrial-grade automated content extraction",
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "async_extract": "/api/v1/extract",
    "sync_extract": "/api/v1/extract/sync",
    "task_status": "/api/v1/tasks/{task_id}",
    "list_tasks": "/api/v1/tasks",
    "statistics": "/api/v1/stats"
  }
}
```

### 4.2 健康检查

检查服务健康状态。

**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "web-content-extraction-platform",
  "version": "1.0.0"
}
```

**使用场景**:
- Kubernetes/Docker liveness probe
- 负载均衡器健康检查
- 监控系统心跳检测

### 4.3 平台统计

获取平台运行统计信息。

**Endpoint**: `GET /api/v1/stats`

**Response** (200 OK):
```json
{
  "statistics": {
    "total": 250,
    "pending": 5,
    "running": 3,
    "completed": 220,
    "failed": 15,
    "cancelled": 7
  },
  "max_concurrent_tasks": 5
}
```

**字段说明**:
- `total`: 总任务数
- `pending`: 待处理任务数
- `running`: 正在执行任务数
- `completed`: 已完成任务数
- `failed`: 失败任务数
- `cancelled`: 已取消任务数
- `max_concurrent_tasks`: 最大并发任务数配置

## 5. 内容提取接口

### 5.1 创建异步提取任务

创建一个异步内容提取任务，立即返回任务 ID。

**Endpoint**: `POST /api/v1/extract`

**Request Body**:
```json
{
  "question": "tips to improve water pressure"
}
```

**Request Schema**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `question` | string | 是 | 要搜索的问题 |

**Response** (202 Accepted):
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "Task created and submitted for processing"
}
```

**Response Schema**:
| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 任务唯一标识符（UUID） |
| `status` | string | 任务状态：`pending` |
| `message` | string | 提示消息 |

**示例**:
```bash
curl -X POST http://localhost:8080/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "question": "how many planets are in our solar system?"
  }'
```

**使用场景**:
- 生产环境推荐使用
- 长时间运行的提取任务
- 需要并发处理多个任务
- 客户端可以执行其他操作而不阻塞

**后续操作**:
1. 保存返回的 `task_id`
2. 使用 `GET /api/v1/tasks/{task_id}` 轮询任务状态
3. 当 `status` 为 `completed` 时获取结果

### 5.2 同步提取（阻塞式）

执行同步内容提取，阻塞直到完成。

**Endpoint**: `POST /api/v1/extract/sync`

**Request Body**:
```json
{
  "question": "tips to improve water pressure"
}
```

**Response** (200 OK):
```json
{
  "url": "https://www.reddit.com/answers/b5eb3635-3607-4331-800a-591df8f95057",
  "question": "tips to improve water pressure",
  "sources": [
    "https://www.reddit.com/r/Plumbing",
    "https://www.reddit.com/r/HomeImprovement"
  ],
  "sections": [
    {
      "heading": "Check Your Shower Head",
      "content": [
        "Clean or replace your shower head regularly.",
        "Remove flow restrictors if legal in your area."
      ]
    }
  ],
  "relatedPosts": [
    {
      "rank": "1",
      "title": "How can I increase the water pressure in my shower?",
      "subreddit": "r/howto",
      "url": "https://www.reddit.com/r/howto/comments/...",
      "upvotes": 943,
      "comments": 181,
      "domain": "reddit.com",
      "promoted": false,
      "score": 943
    }
  ],
  "relatedTopics": [
    "how to adjust water pressure regulator",
    "low water pressure solutions"
  ]
}
```

**完整响应数据模型见 [7. 数据模型](#7-数据模型)**

**示例**:
```bash
curl -X POST http://localhost:8080/api/v1/extract/sync \
  -H "Content-Type: application/json" \
  -d '{
    "question": "how many planets are in our solar system?"
  }'
```

**注意事项**:
- ⚠️ 此接口会阻塞直到提取完成（通常 30-120 秒）
- ⚠️ 不适合 Web 前端直接调用（可能超时）
- ⚠️ 生产环境建议使用异步接口
- ✅ 适用于脚本、后台任务、CLI 工具

**超时设置**:
- 客户端超时建议：180 秒以上
- Nginx/负载均衡器超时：300 秒以上

## 6. 任务管理接口

### 6.1 查询任务状态

查询指定任务的执行状态和结果。

**Endpoint**: `GET /api/v1/tasks/{task_id}`

**Path Parameters**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 任务 ID（UUID） |

**Response** (200 OK):

**情况 1: 任务正在执行**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "running",
  "progress": "Extracting content from Reddit...",
  "result": null,
  "error": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:15Z"
}
```

**情况 2: 任务已完成**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "progress": null,
  "result": {
    "url": "https://www.reddit.com/answers/...",
    "question": "how many planets are in our solar system?",
    "sources": ["..."],
    "sections": [...],
    "relatedPosts": [...],
    "relatedTopics": [...]
  },
  "error": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:30Z"
}
```

**情况 3: 任务失败**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "failed",
  "progress": null,
  "result": null,
  "error": "Extraction failed: Connection timeout",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:32:00Z"
}
```

**Response Schema**:
| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 任务 ID |
| `status` | string | `pending` \| `running` \| `completed` \| `failed` \| `cancelled` |
| `progress` | string \| null | 进度描述（仅 running 状态） |
| `result` | object \| null | 提取结果（仅 completed 状态） |
| `error` | string \| null | 错误信息（仅 failed 状态） |
| `created_at` | string | 创建时间（ISO 8601） |
| `updated_at` | string | 最后更新时间（ISO 8601） |

**错误响应** (404 Not Found):
```json
{
  "error": "Task not found",
  "detail": "Task ID does not exist"
}
```

**示例**:
```bash
curl http://localhost:8080/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**轮询建议**:
```python
import time
import requests

def wait_for_task(task_id, max_wait=300, interval=5):
    """轮询任务直到完成或超时"""
    start = time.time()
    while time.time() - start < max_wait:
        response = requests.get(f"http://localhost:8080/api/v1/tasks/{task_id}")
        data = response.json()
        
        if data["status"] in ["completed", "failed", "cancelled"]:
            return data
        
        time.sleep(interval)
    
    raise TimeoutError("Task execution timeout")
```

### 6.2 列出任务

获取任务列表，支持按状态筛选。

**Endpoint**: `GET /api/v1/tasks`

**Query Parameters**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `status` | string | 否 | - | 按状态筛选：`pending` \| `running` \| `completed` \| `failed` \| `cancelled` |
| `limit` | integer | 否 | 100 | 返回数量限制（1-1000） |

**Response** (200 OK):
```json
[
  {
    "task_id": "task-001",
    "status": "completed",
    "question": "how many planets are in our solar system?",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:31:30Z",
    "result": { /* ExtractionResult */ },
    "error": null,
    "metadata": {}
  },
  {
    "task_id": "task-002",
    "status": "running",
    "question": "tips to improve water pressure",
    "created_at": "2024-01-15T10:35:00Z",
    "updated_at": "2024-01-15T10:35:15Z",
    "result": null,
    "error": null,
    "metadata": {"progress": "Extracting content..."}
  }
]
```

**示例**:
```bash
# 获取所有已完成的任务（最多 50 个）
curl "http://localhost:8080/api/v1/tasks?status=completed&limit=50"

# 获取所有失败的任务
curl "http://localhost:8080/api/v1/tasks?status=failed"

# 获取最近 10 个任务
curl "http://localhost:8080/api/v1/tasks?limit=10"
```

**排序**:
- 按创建时间倒序（最新的在前）

### 6.3 取消任务

取消一个待处理的任务。

**Endpoint**: `DELETE /api/v1/tasks/{task_id}`

**Path Parameters**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 任务 ID |

**Response** (200 OK):
```json
{
  "message": "Task cancelled successfully",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**错误响应**:

**404 Not Found**:
```json
{
  "error": "Task not found",
  "detail": "Task ID does not exist"
}
```

**400 Bad Request**:
```json
{
  "error": "Cannot cancel task with status: running",
  "detail": "Only pending tasks can be cancelled"
}
```

**示例**:
```bash
curl -X DELETE http://localhost:8080/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**注意事项**:
- 只能取消 `pending` 状态的任务
- 已经在执行（`running`）的任务无法取消
- 已完成/失败的任务无法取消

## 7. 数据模型

### 7.1 ExtractionRequest（输入）

```typescript
{
  question: string  // 必填，要搜索的问题
}
```

**示例**:
```json
{
  "question": "tips to improve water pressure"
}
```

### 7.2 ExtractionResult（输出）

```typescript
{
  url: string,                  // Reddit Answers 页面 URL
  question: string,             // 原始问题
  sources: string[],            // 来源 subreddit URLs
  sections: ContentSection[],   // 结构化答案章节
  relatedPosts: PostMetadata[], // 相关帖子元数据
  relatedTopics: string[]       // 相关主题建议
}
```

**完整示例**:
```json
{
  "url": "https://www.reddit.com/answers/91ede21d-7f09-437e-91a6-4d5ae1f6d936",
  "question": "how many planets are in our solar system?",
  "sources": [
    "https://www.reddit.com/r/threebodyproblem",
    "https://www.reddit.com/r/technology",
    "https://www.reddit.com/r/Astronomy"
  ],
  "sections": [
    {
      "heading": "Current Consensus",
      "content": [
        "8 Planets: The current official count of planets in our solar system is eight.",
        "This includes Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune."
      ]
    },
    {
      "heading": "Pluto and Dwarf Planets",
      "content": [
        "Pluto's Reclassification: Pluto was reclassified as a dwarf planet in 2006..."
      ]
    }
  ],
  "relatedPosts": [
    {
      "rank": "1",
      "title": "8 planets in the solar system.",
      "subreddit": "threebodyproblem",
      "url": "https://www.reddit.com/r/threebodyproblem/comments/1mmdaq8/",
      "upvotes": 59,
      "comments": 24,
      "domain": "self.threebodyproblem",
      "promoted": false,
      "score": 59
    }
  ],
  "relatedTopics": [
    "how many moons does each planet have?",
    "what are the characteristics of dwarf planets?"
  ]
}
```

### 7.3 ContentSection

```typescript
{
  heading: string,    // 章节标题
  content: string[]   // 段落内容数组
}
```

### 7.4 PostMetadata

```typescript
{
  rank: string,       // 排名（字符串格式）
  title: string,      // 帖子标题
  subreddit: string,  // 所属 subreddit
  url: string,        // 帖子 URL（可能为空字符串）
  upvotes: number,    // 点赞数
  comments: number,   // 评论数
  domain: string,     // 域名
  promoted: boolean,  // 是否为推广内容
  score: number       // 分数
}
```

### 7.5 TaskStatus（枚举）

| 值 | 说明 |
|----|------|
| `pending` | 任务已创建，等待执行 |
| `running` | 任务正在执行 |
| `completed` | 任务执行成功，结果已返回 |
| `failed` | 任务执行失败，查看 error 字段 |
| `cancelled` | 任务已被取消 |

## 8. 错误码

### 8.1 HTTP 状态码

| 状态码 | 说明 | 场景 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 202 | Accepted | 异步任务已创建 |
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 资源不存在（如任务 ID 不存在） |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务未就绪 |

### 8.2 业务错误

**400 - 验证错误**:
```json
{
  "error": "Invalid request",
  "detail": "Field 'question' is required"
}
```

**404 - 任务不存在**:
```json
{
  "error": "Task not found",
  "detail": "Task ID does not exist"
}
```

**503 - 服务未就绪**:
```json
{
  "error": "Service not ready",
  "detail": "Task manager is initializing"
}
```

**500 - 提取失败**:
```json
{
  "error": "Extraction failed",
  "detail": "Connection timeout to Steel service"
}
```

## 9. 最佳实践

### 9.1 异步任务处理

**推荐流程**:
```python
import requests
import time

# 1. 创建任务
response = requests.post(
    "http://localhost:8080/api/v1/extract",
    json={"question": "your question here"}
)
task_id = response.json()["task_id"]

# 2. 轮询状态（指数退避）
max_retries = 20
retry_interval = 5

for i in range(max_retries):
    response = requests.get(f"http://localhost:8080/api/v1/tasks/{task_id}")
    data = response.json()
    
    if data["status"] == "completed":
        print("Success:", data["result"])
        break
    elif data["status"] == "failed":
        print("Failed:", data["error"])
        break
    
    # 指数退避
    time.sleep(min(retry_interval * (2 ** i), 60))
```

### 9.2 错误处理

```python
try:
    response = requests.post(
        "http://localhost:8080/api/v1/extract",
        json={"question": "your question"},
        timeout=300
    )
    response.raise_for_status()
    data = response.json()
except requests.exceptions.Timeout:
    print("Request timeout")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
    print(e.response.json())
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 9.3 并发控制

**客户端限流**:
```python
from concurrent.futures import ThreadPoolExecutor
import time

def submit_task(question):
    response = requests.post(
        "http://localhost:8080/api/v1/extract",
        json={"question": question}
    )
    return response.json()["task_id"]

# 限制并发为 5
with ThreadPoolExecutor(max_workers=5) as executor:
    questions = ["question 1", "question 2", "..."]
    task_ids = list(executor.map(submit_task, questions))
```

### 9.4 超时设置建议

| 操作 | 超时时间 | 说明 |
|------|---------|------|
| 创建任务 | 30秒 | 通常 < 1秒完成 |
| 查询状态 | 10秒 | 简单查询操作 |
| 同步提取 | 300秒 | 浏览器自动化耗时 |
| 轮询间隔 | 5-10秒 | 平衡及时性与服务器压力 |

### 9.5 性能优化

**批量处理**:
```python
# 批量提交任务
task_ids = []
for question in questions:
    response = requests.post(url, json={"question": question})
    task_ids.append(response.json()["task_id"])

# 并发查询结果
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch_task_result, task_ids))
```

**缓存结果**:
- 相同问题可以复用之前的提取结果
- 建议实现客户端缓存（Redis/内存）

### 9.6 监控与日志

**健康检查**:
```bash
# 监控脚本
while true; do
  curl -s http://localhost:8080/health | jq .
  sleep 30
done
```

**指标收集**:
```python
# 定期收集统计数据
response = requests.get("http://localhost:8080/api/v1/stats")
stats = response.json()["statistics"]

# 计算成功率
success_rate = stats["completed"] / stats["total"] * 100
print(f"Success rate: {success_rate:.2f}%")
```

## 10. 变更日志

### v1.0.0 (2024-01-15)
- ✨ 初始版本发布
- ✨ 支持 Reddit Answers 内容提取
- ✨ 异步/同步两种提取模式
- ✨ 完整的任务管理接口
- ✨ 健康检查和统计接口

## 11. 联系与支持

- **问题反馈**: GitHub Issues
- **文档**: `/docs` 端点
- **技术支持**: 查看 README.md
