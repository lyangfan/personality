# DeepMemory FastAPI 服务

记忆驱动的对话系统 REST API 服务

## 特性

- **异步架构**: 立即响应用户请求，记忆提取在后台异步执行
- **依赖注入**: 单例模式管理核心组件，确保高效资源利用
- **生产就绪**: 强制使用 GLM Embedding-3 或 sentence-transformers，严禁 simple embedding
- **OpenAI 兼容**: 支持标准 chat completions 格式

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 GLM_API_KEY
```

### 3. 启动服务

```bash
# 方式1：使用启动脚本
./start.sh

# 方式2：直接运行
python app.py

# 方式3：指定参数
python app.py --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 1. 健康检查

```
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "version": "0.3.1",
  "embedding_model": "glm",
  "components": {
    "memory_storage": "ok",
    "embedding_model": "glm",
    "environment": "production"
  }
}
```

### 2. 简单对话接口

```
POST /v1/chat
```

**请求体**:
```json
{
  "user_id": "user_001",
  "session_id": "session_001",
  "message": "你好，我是张三",
  "username": "张三",
  "extract_now": false
}
```

**响应**:
```json
{
  "response": "你好张三！很高兴认识你...",
  "session_id": "session_001",
  "user_id": "user_001",
  "memory_extracted": false,
  "message_count": 1
}
```

### 3. OpenAI 兼容接口

```
POST /v1/chat/completions
```

**请求体**:
```json
{
  "user_id": "user_001",
  "session_id": "session_001",
  "messages": [
    {
      "role": "user",
      "content": "我喜欢打网球"
    }
  ],
  "model": "glm-4-flash"
}
```

**响应**:
```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "glm-4-flash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "我记住了你喜欢打网球！"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### 4. 获取记忆

```
GET /v1/memories?user_id={user_id}&session_id={session_id}
```

**查询参数**:
- `user_id` (必需): 用户ID
- `session_id` (可选): 会话ID
- `limit` (可选): 返回数量限制，默认 50
- `min_importance` (可选): 最低重要性分数
- `speaker` (可选): 说话人过滤 (user/assistant)

**响应**:
```json
{
  "user_id": "user_001",
  "session_id": "session_001",
  "total_count": 5,
  "memories": [
    {
      "content": "用户叫张三",
      "timestamp": "2024-01-15T10:30:00Z",
      "speaker": "user",
      "type": "fact",
      "entities": ["张三"],
      "topics": ["自我介绍"],
      "sentiment": "neutral",
      "importance_score": 7,
      "confidence": 0.9,
      "metadata": {}
    }
  ]
}
```

### 5. 用户管理

**创建用户**:
```
POST /v1/users
```

**获取用户**:
```
GET /v1/users/{user_id}
```

### 6. 会话管理

**创建会话**:
```
POST /v1/sessions
```

**获取会话**:
```
GET /v1/sessions/{session_id}
```

**获取用户的所有会话**:
```
GET /v1/users/{user_id}/sessions
```

## 架构设计

### 异步处理流程

```
用户请求 → 立即生成 AI 回复 → 返回给用户
                ↓
         后台异步任务
                ↓
         提取并存储记忆
```

关键特性：
- 记忆提取不阻塞主线程
- 立即响应用户请求
- 后台任务使用 BackgroundTasks

### 依赖注入

所有核心组件使用单例模式：
- `ConversationManager`: 对话编排器
- `UserManager`: 用户管理器
- `SessionManager`: 会话管理器
- `MemoryStorage`: ChromaDB 向量存储
- `GLMClient`: GLM-4 客户端
- `MemoryRetriever`: 语义检索器

### Embedding 模型

**生产环境** (ENVIRONMENT=production):
- 默认: `glm` (智谱 Embedding-3)
- 可选: `sentence-transformers`
- 严禁: `simple`

**开发环境** (ENVIRONMENT=development):
- 默认: `simple`
- 可选: `glm`, `sentence-transformers`

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `GLM_API_KEY` | 智谱AI API密钥 | 必需 |
| `ENVIRONMENT` | 运行环境 | production |
| `EMBEDDING_MODEL` | Embedding模型 | glm |
| `DATA_DIR` | 数据目录 | ./data |
| `MEMORY_EXTRACT_THRESHOLD` | 记忆提取阈值（轮） | 5 |
| `MAX_CONTEXT_MEMORIES` | 最大上下文记忆数 | 5 |
| `HOST` | 监听地址 | 0.0.0.0 |
| `PORT` | 监听端口 | 8000 |
| `WORKERS` | 工作进程数 | 1 |
| `RELOAD` | 自动重载 | false |

### 生产环境部署

```bash
# 设置环境变量
export ENVIRONMENT=production
export EMBEDDING_MODEL=glm
export WORKERS=4

# 启动服务
python app.py --host 0.0.0.0 --port 8000 --workers 4
```

## 测试

运行测试脚本：

```bash
python test_api.py
```

测试内容包括：
1. 健康检查
2. 创建用户
3. 创建会话
4. 简单对话
5. Chat Completions
6. 连续对话
7. 获取记忆

## 项目结构

```
.
├── app.py                      # FastAPI 主应用
├── start.sh                    # 启动脚本
├── test_api.py                 # API 测试脚本
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
└── src/
    ├── api/
    │   ├── __init__.py
    │   ├── models.py           # API 数据模型
    │   ├── routes.py           # API 路由
    │   └── dependencies.py     # 依赖注入
    ├── conversation/
    │   └── conversation_manager.py
    ├── storage/
    │   ├── user_manager.py
    │   ├── session_manager.py
    │   └── memory_storage.py
    └── utils/
        └── glm_client.py
```

## 常见问题

### 1. 如何切换 Embedding 模型？

编辑 `.env` 文件：
```bash
# 使用智谱 Embedding-3（推荐）
EMBEDDING_MODEL=glm

# 使用 sentence-transformers
EMBEDDING_MODEL=sentence-transformers
```

### 2. 生产环境可以不使用多进程吗？

可以，但不推荐。多进程可以充分利用多核 CPU：
```bash
# 单进程（开发模式）
python app.py

# 多进程（生产模式）
python app.py --workers 4
```

### 3. 如何查看记忆提取日志？

后台记忆提取失败会打印到标准输出：
```
后台记忆提取失败: ...
```

### 4. 为什么我的对话没有触发记忆提取？

记忆提取默认每 5 轮对话触发一次。可以调整阈值：
```bash
# .env 文件
MEMORY_EXTRACT_THRESHOLD=3  # 每 3 轮提取一次
```

或在请求中强制立即提取：
```json
{
  "extract_now": true
}
```

## 性能优化建议

1. **使用多进程**: 生产环境建议 4+ 工作进程
2. **调整记忆提取阈值**: 降低阈值减少内存占用，但会影响记忆质量
3. **选择合适的 Embedding**: `glm` 质量高但需要 API 调用，`sentence-transformers` 本地运行但需要下载模型
4. **限制上下文记忆数**: 减少 `MAX_CONTEXT_MEMORIES` 可以加快响应速度

## License

MIT
