# 记忆驱动对话系统使用指南

## 简介

记忆驱动对话系统是 DeepMemory v0.3.0 的核心功能，它能够：

1. **自动提取记忆**：从对话中自动提取重要信息并持久化存储
2. **智能检索记忆**：基于语义相似度召回相关历史记忆
3. **个性化回复**：将检索到的记忆注入到对话中，生成个性化回复
4. **上下文节约**：只检索最相关的记忆，避免上下文过长

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动交互式聊天

```bash
python demo_interactive_chat.py
```

### 3. 编程方式使用

```python
from src.conversation.conversation_manager import ConversationManager
from src.storage import UserManager, SessionManager, MemoryStorage
from src.utils.glm_client import GLMClient
import os

# 初始化组件
user_manager = UserManager()
session_manager = SessionManager()
memory_storage = MemoryStorage(embedding_model="simple")
glm_client = GLMClient(
    api_key=os.getenv("GLM_API_KEY"),
    model="glm-4-flash"
)

# 创建对话管理器
conversation_manager = ConversationManager(
    user_manager=user_manager,
    session_manager=session_manager,
    memory_storage=memory_storage,
    glm_client=glm_client,
    memory_extract_threshold=3,  # 每3轮提取一次记忆
    max_context_memories=5       # 最多注入5条记忆
)

# 创建用户和会话
user = user_manager.create_user("张三")
session = session_manager.create_session(
    user_id=user.user_id,
    title="第一次对话"
)

# 开始对话
response = conversation_manager.chat(
    user_id=user.user_id,
    session_id=session.session_id,
    user_message="你好，我是张三"
)
print(response)

# 继续对话
response = conversation_manager.chat(
    user_id=user.user_id,
    session_id=session.session_id,
    user_message="我最喜欢吃火锅，特别是麻辣锅底"
)
# 系统会自动提取这个偏好

# 下次对话时，AI 会记得这个偏好
response = conversation_manager.chat(
    user_id=user.user_id,
    session_id=session.session_id,
    user_message="你知道我喜欢吃什么吗？"
)
print(response)
# 预期回复：火锅（系统成功召回记忆）
```

## 核心组件

### 1. MemoryStorage（记忆存储）

负责将记忆存储到 ChromaDB 向量数据库。

```python
from src.storage.memory_storage import MemoryStorage

# 使用简单 embedding（无需下载模型）
storage = MemoryStorage(embedding_model="simple")

# 或使用 sentence-transformers（需要网络）
storage = MemoryStorage(embedding_model="sentence-transformers")

# 或使用 OpenAI embedding（需要 API key）
storage = MemoryStorage(
    embedding_model="openai",
    api_key="your-openai-key"
)
```

### 2. MemoryRetriever（记忆检索）

基于语义相似度检索相关记忆。

```python
from src.retrieval.memory_retriever import MemoryRetriever, RetrievalConfig

# 创建检索器
retriever = MemoryRetriever(
    storage=storage,
    config=RetrievalConfig(
        top_k=5,               # 返回前5个最相关的记忆
        min_importance=6,      # 最低重要性分数
        boost_recent=True,     # 提升近期记忆权重
        boost_importance=True  # 提升高分记忆权重
    )
)

# 检索记忆
memories = retriever.retrieve(
    user_id="user-id",
    session_id="session-id",
    query="用户喜欢吃什么？"
)

for fragment, score in memories:
    print(f"[{score:.2f}] {fragment.content}")
```

### 3. ConversationManager（对话管理）

核心编排器，负责：
- 管理对话状态
- 自动提取记忆
- 检索相关记忆
- 生成个性化回复

```python
from src.conversation.conversation_manager import ConversationManager

manager = ConversationManager(
    user_manager=user_manager,
    session_manager=session_manager,
    memory_storage=storage,
    glm_client=glm_client,
    memory_extract_threshold=3,  # 每3轮提取一次记忆
    max_context_memories=5       # 最多注入5条记忆
)

# 处理用户消息
response = manager.chat(
    user_id="user-id",
    session_id="session-id",
    user_message="用户消息"
)
```

## 工作流程

```
用户输入
    ↓
ConversationManager.chat()
    ↓
1. 存储消息到缓冲区
2. 检查是否需要提取记忆（每 N 轮）
    ↓
3. 语义检索相关记忆
    ↓
4. 构建带记忆的 Prompt
    ↓
5. 调用 GLM-4 生成回复
    ↓
返回 AI 回复
```

## 记忆提取时机

系统默认每 3 轮对话提取一次记忆，可通过配置调整：

```python
manager = ConversationManager(
    ...,
    memory_extract_threshold=5  # 每5轮提取一次
)
```

也可以强制立即提取：

```python
response = manager.chat(
    user_id="user-id",
    session_id="session-id",
    user_message="用户消息",
    extract_now=True  # 立即提取记忆
)
```

## 检索策略

### 相似度 + 重要性混合排序

```
最终分数 = 相似度 × 0.7 + 重要性权重 × 0.3
```

其中：
- **相似度**：基于向量检索的余弦相似度（0-1）
- **重要性权重**：importance_score / 10（0-1）

### 时间衰减

近期记忆的权重会更高：

```
7天内：无衰减
7天后：指数衰减（0.95^(days-7)）
```

## 配置选项

### MemoryStorage

```python
storage = MemoryStorage(
    persist_directory="./data/chromadb",  # 数据持久化目录
    embedding_model="simple",              # embedding 模型类型
    api_key=None                           # API key（如果使用云服务）
)
```

### MemoryRetriever

```python
config = RetrievalConfig(
    top_k=5,                  # 返回前 K 个最相关的记忆
    min_importance=5,         # 最低重要性分数
    score_threshold=None,     # 相似度阈值（可选）
    boost_recent=True,        # 是否提升近期记忆权重
    boost_importance=True,    # 是否提升高分记忆权重
    diversity_penalty=0.1     # 多样性惩罚（0-1）
)
```

### ConversationManager

```python
manager = ConversationManager(
    user_manager=user_manager,
    session_manager=session_manager,
    memory_storage=storage,
    glm_client=glm_client,
    retrieval_config=None,           # 检索配置（可选）
    memory_extract_threshold=3,      # 记忆提取阈值（轮数）
    max_context_memories=5           # 最大上下文记忆数
)
```

## 数据持久化

### 用户数据

存储在 `./data/users/` 目录下，每个用户一个 JSON 文件：

```json
{
  "user_id": "uuid",
  "username": "张三",
  "created_at": "2026-01-14T10:00:00",
  "metadata": {}
}
```

### 会话数据

存储在 `./data/sessions/` 目录下，每个会话一个 JSON 文件：

```json
{
  "session_id": "uuid",
  "user_id": "uuid",
  "title": "第一次对话",
  "created_at": "2026-01-14T10:00:00",
  "updated_at": "2026-01-14T11:00:00",
  "message_count": 10,
  "is_active": true,
  "metadata": {}
}
```

### 向量数据库

存储在 `./data/chromadb/` 目录下，使用 ChromaDB 持久化存储。

## 测试

运行测试脚本验证系统功能：

```bash
python test_memory_system.py
```

测试内容包括：
1. 组件初始化
2. 用户和会话创建
3. 记忆存储
4. 语义检索
5. 记忆统计

## 常见问题

### Q: 如何更换 embedding 模型？

A: 修改 `embedding_model` 参数：

```python
# 简单 embedding（默认，无需下载）
storage = MemoryStorage(embedding_model="simple")

# sentence-transformers（需要网络）
storage = MemoryStorage(embedding_model="sentence-transformers")

# OpenAI（需要 API key）
storage = MemoryStorage(embedding_model="openai", api_key="your-key")
```

### Q: 如何调整记忆提取频率？

A: 修改 `memory_extract_threshold` 参数：

```python
manager = ConversationManager(
    ...,
    memory_extract_threshold=5  # 每5轮提取一次
)
```

### Q: 如何限制注入的记忆数量？

A: 修改 `max_context_memories` 参数：

```python
manager = ConversationManager(
    ...,
    max_context_memories=3  # 最多注入3条记忆
)
```

### Q: 如何查看用户的记忆统计？

A: 使用 `/stats` 命令（交互式聊天）或调用 API：

```python
count = storage.get_memory_count(user_id, session_id)
print(f"总记忆数: {count} 条")
```

## 下一步

- 升级到更高质量的 embedding 模型（如智谱AI embedding-2）
- 添加 Web 界面（使用 Streamlit 或 Gradio）
- 实现异步记忆提取（不阻塞对话）
- 添加记忆可视化功能

## 相关文档

- [README.md](README.md) - 项目总览
- [USER_GUIDE_CN.md](USER_GUIDE_CN.md) - 用户指南
- [CLAUDE.md](CLAUDE.md) - AI 助手项目指南
