# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

DeepMemory 是一个**记忆驱动的对话系统**，提供两种使用方式：

1. **FastAPI REST API 服务** ⭐ (v0.4.0 新增，推荐)
   - 开箱即用的 Web 服务
   - 异步架构，立即响应用户请求
   - 完整的 REST API 接口
   - 适合生产环境部署
   - 详细文档: [FASTAPI_GUIDE.md](FASTAPI_GUIDE.md)

2. **Python 库** (传统方式)
   - 从纯文本对话中提取结构化的记忆片段
   - 使用 LLM 驱动的提取（OpenAI API/智谱AI GLM-4）和启发式回退
   - 将对话转换为 JSON 格式的记忆并自动进行重要性评分
   - 适合集成到现有项目

### 核心特性

- 🧠 **自动记忆提取**: 从对话中自动识别并存储重要信息
- 💬 **记忆驱动对话**: 基于历史记忆生成个性化回复
- 🔄 **双向记忆**: 同时记住用户的话和 AI 的承诺
- 📊 **智能评分**: 自动评估信息重要性（1-10分）
- 🚀 **REST API**: 标准的 HTTP 接口，易于集成

### 版本历史

- **v0.4.0**: FastAPI REST API 服务（异步架构）
- **v0.3.1**: AI 承诺和回复记忆功能（speaker 字段 + AI 评分标准）
- **v0.3.0**: 记忆驱动对话系统（ChromaDB 向量存储 + 语义检索）
- **v0.2.0**: 陪伴型 AI 评分系统（GLM-4）

---

## 快速开始

### 方式一：使用 FastAPI 服务（推荐）⭐

**1. 安装依赖**
```bash
pip install -r requirements.txt
```

**2. 配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入 GLM_API_KEY
```

**3. 启动服务**
```bash
# 使用启动脚本
./start.sh

# 或直接运行
python app.py
```

**4. 访问服务**
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

**5. 测试 API**
```bash
python test_api.py
```

详细文档: [FASTAPI_GUIDE.md](FASTAPI_GUIDE.md)

### 方式二：使用 Python 库

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 运行测试
- 运行所有测试: `pytest tests/ -v`
- 运行特定测试文件:
  - `pytest tests/test_models.py -v`
  - `pytest tests/test_scorers.py -v`
  - `pytest tests/test_pipeline.py -v`

#### 快速验证
```bash
# ⭐ 记忆驱动对话系统（推荐）
python demo_interactive_chat.py

# ⭐ Speaker 功能测试
python test_speaker_feature.py

# ⭐ 真实场景完整测试
python test_real_conversation_full.py
```

### 使用示例
```bash
python -m src.pipeline.memory_pipeline examples/sample_conversation.txt
```

## 架构设计

### 核心组件

#### 记忆提取

**MemoryPipeline** (`src/pipeline/memory_pipeline.py`): 主编排器，负责:
1. 从对话中提取记忆片段（LLM 或启发式）
2. 用实体、主题和情感丰富片段
3. 计算重要性评分 (1-10)
4. 按重要性过滤和排序

#### ⭐ 记忆驱动对话系统 (v0.3.0 新增)

**ConversationManager** (`src/conversation/conversation_manager.py`): 对话编排器，负责:
1. 管理对话状态和消息历史
2. 自动提取记忆（每 N 轮对话）
3. 语义检索相关记忆
4. 将记忆注入到 Prompt
5. 生成个性化回复

**MemoryStorage** (`src/storage/memory_storage.py`): ChromaDB 向量存储层:
- 持久化存储记忆片段
- 支持多种 embedding 模型（simple/sentence-transformers/openai）
- 按用户/会话隔离数据

**MemoryRetriever** (`src/retrieval/memory_retriever.py`): 语义检索器:
- 基于向量相似度检索相关记忆
- 混合排序策略（相似度 + 重要性 + 时间衰减）
- 支持按类型/情感/重要性过滤

**UserManager** (`src/storage/user_manager.py`): 用户管理:
- 用户创建/查询/更新
- JSON 文件持久化

**SessionManager** (`src/storage/session_manager.py`): 会话管理:
- 会话创建/查询/更新
- 按用户隔离会话
- 会话历史管理

#### 评分系统

**User 评分标准** (ImportanceScorer): 多维度评分系统:
- **情感强度** (0-3 分): 情感强度 (high/medium/low/none)
- **信息密度** (0-4 分): 实体 + 主题的数量
- **任务相关性** (0-3 分): 目标导向内容评估
- 总分范围: 1-10(始终为整数)
- **过滤阈值**: 5分（低于5分的 user 记忆会被过滤）

**⭐ Assistant 评分标准** (v0.3.1 新增):
- **承诺重要性** (0-4 分): "我会一直陪着你" = 7分+, "我保证" = 高分
- **建议价值** (0-3 分): 具体步骤、解决方案 = 5分+, 推荐尝试 = 中等分
- **情感支持强度** (0-3 分): "理解你的感受" = 6分+, "支持你" = 高分
- **总分范围**: 1-10(始终为整数)
- **过滤阈值**: 3分（低于3分的 assistant 记忆会被过滤）

**混合评分模式**:
1. GLM-4 大模型给出初始评分
2. 根据推理文本和内容关键词进行校正
3. 特殊规则提升（身份信息→5分，AI承诺→7分，用户引用→7分）

#### 数据模型

**MemoryFragment** (`src/models/memory_fragment.py`): Pydantic 模型，严格验证:
- `speaker`: Literal["user", "assistant"] (⭐ v0.3.1 新增)
- `importance_score`: int, 1-10 (关键字段)
- `type`: Literal["event", "preference", "fact", "relationship"]
- `sentiment`: Literal["positive", "neutral", "negative"]
- `entities`, `topics`: List[str]
- `confidence`: float, 0.0-1.0

**User/Session/Message** (`src/models/user.py`): 用户和会话模型:
- `User`: user_id, username, created_at, metadata
- `Session`: session_id, user_id, title, message_count, is_active
- `Message`: message_id, session_id, role, content, timestamp

### 双模式运行

管道支持两种提取模式:

1. **LLM 模式** (`use_llm=True`): 使用 OpenAI API (gpt-4o-mini) 进行智能提取
   - 需要 `OPENAI_API_KEY` 环境变量
   - 提供更高质量的提取
   - 包含指数退避重试逻辑

2. **启发式模式** (`use_llm=False`): 基于规则的回退
   - 按中文句号(。)分割对话
   - 使用关键词匹配进行情感和相关性分析
   - 不需要 API key

### 记忆驱动对话流程 (v0.3.0 新增)

1. 用户输入消息
2. ConversationManager 存储消息到缓冲区
3. 检查是否需要提取记忆（每 N 轮）
4. 调用 GLM-4 提取记忆并存储到 ChromaDB
5. 语义检索相关记忆
6. 构建带记忆的 Prompt
7. 调用 GLM-4 生成个性化回复

### 模块结构

```
src/
├── models/              # Pydantic 数据模型
│   ├── memory_fragment.py  # 记忆片段模型
│   └── user.py             # ⭐ 用户、会话、消息模型
├── extractors/          # 实体、主题、情感提取
├── scorers/             # 重要性评分逻辑
├── pipeline/            # 主编排管道
├── storage/             # ⭐ 存储层
│   ├── user_manager.py      # 用户管理
│   ├── session_manager.py   # 会话管理
│   └── memory_storage.py    # ChromaDB 向量存储
├── retrieval/           # ⭐ 检索层
│   └── memory_retriever.py  # 语义检索器
├── conversation/        # ⭐ 对话层
│   └── conversation_manager.py  # 对话编排器
└── utils/
    ├── glm_client.py    # ⭐ GLM-4 客户端（陪伴型评分）
    └── llm_client.py    # OpenAI 客户端
```

所有模块通过 `__init__.py` 暴露主要类，便于导入。

## 关键设计模式

### ⭐ 记忆驱动对话系统 (v0.3.0 新增)

**ConversationManager** (`src/conversation/conversation_manager.py`): 核心编排器
- 自动记忆提取：每 N 轮对话提取一次（可配置）
- **⭐ v0.3.1**: 同时提取 user 和 assistant 的记忆（区分 speaker）
- 语义检索：基于向量相似度召回相关记忆
- 上下文管理：只注入最相关的记忆（默认 5 条）
- 个性化生成：将记忆注入到 Prompt 生成个性化回复
- **⭐ v0.3.1**: AI 能够记住自己的承诺、建议、情感支持

**工作流程**：
```
用户输入 → 缓冲消息 → 检查提取时机 → 提取记忆（区分 user/assistant） → 存储到 ChromaDB
                                                        ↓
语义检索 ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
    ↓
构建带记忆的 Prompt（区分用户和AI的话） → GLM-4 生成回复 → 返回给用户
```

**⭐ v0.3.1 新增功能**：
1. **Speaker 字段**：每个记忆标记为 user 或 assistant
2. **AI 评分标准**：承诺（7分+）、建议（5分+）、情感支持（6分+）
3. **差异化阈值**：user 5分，assistant 3分
4. **关键词检测**：自动提升包含"我会一直"、"建议"等关键词的 AI 回复
5. **用户引用检测**：当用户说"你之前说过..."时自动提升分数

**配置选项**：
- `memory_extract_threshold`: 记忆提取阈值（默认 3 轮）
- `max_context_memories`: 最大上下文记忆数（默认 5 条）
- `retrieval_config`: 检索配置（top_k, min_importance, boost_recent, boost_importance）

**使用示例**：
```python
from src.conversation.conversation_manager import ConversationManager
from src.storage import UserManager, SessionManager, MemoryStorage
from src.utils.glm_client import GLMClient

# 初始化
user_manager = UserManager()
session_manager = SessionManager()
memory_storage = MemoryStorage(embedding_model="simple")
glm_client = GLMClient(api_key="your-api-key", model="glm-4-flash")

# 创建对话管理器
conversation_manager = ConversationManager(
    user_manager=user_manager,
    session_manager=session_manager,
    memory_storage=memory_storage,
    glm_client=glm_client,
    memory_extract_threshold=3,
    max_context_memories=5
)

# 创建用户和会话
user = user_manager.create_user("张三")
session = session_manager.create_session(user_id=user.user_id)

# 对话
response = conversation_manager.chat(
    user_id=user.user_id,
    session_id=session.session_id,
    user_message="你好，我是张三"
)
```

**Embedding 模型选择**：
- `simple`: 简单字符编码（默认，无需下载）
- `sentence-transformers`: 多语言模型（需网络访问 HuggingFace）
- `openai`: OpenAI embeddings（需要 API key）

### ⭐ GLM-4 陪伴型评分 (v0.2.0)

**GLMClient** (`src/utils/glm_client.py`): GLM-4 客户端，针对陪伴型 AI 优化
- `extract_memory_with_scoring()`: 直接评分的记忆提取（单次 API 调用）
- **陪伴型四维评分**：
  - 情感强度 (0-3分): 强烈/明确/轻微/无
  - 个性化程度 (0-3分): 童年经历/明确偏好/一般信息/通用知识
  - 亲密度/关系 (0-2分): 深度信任/分享感受/无关
  - 偏好明确性 (0-2分): 明确喜好/有倾向/无偏好
- Temperature 0.1 保证稳定性
- Few-shot examples 确保评分一致性
- 本地验证和校正机制

**适用场景**：情感陪伴、个性化推荐、聊天机器人

```python
from src.utils.glm_client import GLMClient

client = GLMClient(api_key="your-glm-api-key", model="glm-4-flash")
fragments = client.extract_memory_with_scoring(conversation)
# 直接返回带评分的记忆片段
```

### Pydantic 验证
所有数据结构使用 Pydantic 进行类型安全和验证。`MemoryFragment` 模型强制执行:
- `importance_score` 始终是 1-10 之间的整数
- 正确的 ISO 格式时间戳
- `type` 和 `sentiment` 字段的有效字面量类型

### LLM 客户端模式

**OpenAI 模式**: `LLMClient` (`src/utils/llm_client.py`) 包装 OpenAI API:
- 自动重试和指数退避
- 结构化 JSON 响应
- 回退错误处理
- 可配置的模型选择

### 管道流程
1. 解析对话文本
2. 提取原始片段(LLM 或启发式)
3. 丰富每个片段:
   - 实体(人、地点、组织)
   - 主题(讨论的主题)
   - 情感(positive/neutral/negative)
4. 计算 importance_score
5. 按 min_importance 阈值过滤
6. 按重要性降序排序
7. 输出为 JSON

## 测试策略

测试按组件组织,使用 pytest:
- **test_models.py**: Pydantic 模型验证
- **test_scorers.py**: 重要性评分逻辑
- **test_pipeline.py**: 端到端管道功能

所有测试都可以在不使用 API key 的情况下运行(`use_llm=False`)。

## 测试策略

测试按组件组织,使用 pytest:
- **test_models.py**: Pydantic 模型验证
- **test_scorers.py**: 重要性评分逻辑
- **test_pipeline.py**: 端到端管道功能

所有测试都可以在不使用 API key 的情况下运行(`use_llm=False`)。

### ⭐ 陪伴型评分测试 (v0.2.0)

- 位置: `test_results/`
- 内容: 10个真实场景，62个片段
- 报告: `TESTING_SUMMARY.md`
- 运行: `python demo_companion_memory.py` 或 `python test_real_conversations.py`

关键验证结果：
- 平均分 6.05/10
- 高分片段 58.1%
- 梦想分享场景平均 7.3分
- 童年回忆场景平均 7.0分
- 日常闲聊场景平均 2.0分（成功过滤）

## 配置

### 记忆驱动对话系统配置 (v0.3.0 新增)

```python
from src.conversation.conversation_manager import ConversationManager
from src.storage import MemoryStorage
from src.retrieval import RetrievalConfig

# MemoryStorage 配置
storage = MemoryStorage(
    persist_directory="./data/chromadb",  # ChromaDB 持久化目录
    embedding_model="simple",              # embedding 模型类型
    api_key=None                           # API key（如果使用云服务）
)

# RetrievalConfig 配置
retrieval_config = RetrievalConfig(
    top_k=5,                  # 返回前 K 个最相关的记忆
    min_importance=6,         # 最低重要性分数
    score_threshold=None,     # 相似度阈值（可选）
    boost_recent=True,        # 提升近期记忆权重
    boost_importance=True,    # 提升高分记忆权重
    diversity_penalty=0.1     # 多样性惩罚
)

# ConversationManager 配置
manager = ConversationManager(
    user_manager=user_manager,
    session_manager=session_manager,
    memory_storage=storage,
    glm_client=glm_client,
    retrieval_config=retrieval_config,
    memory_extract_threshold=3,  # 每 3 轮提取一次记忆
    max_context_memories=5       # 最多注入 5 条记忆
)
```

### GLM-4 配置（推荐用于陪伴型 AI）

```python
from src.utils.glm_client import GLMClient

client = GLMClient(
    api_key="your-glm-api-key",  # 智谱AI API密钥
    model="glm-4-flash"           # 推荐使用flash模型
)

# 提取并评分
fragments = client.extract_memory_with_scoring(conversation)
```

### 管道选项（OpenAI）
```python
pipeline = MemoryPipeline(
    api_key="your-key",      # OpenAI API key (默认: OPENAI_API_KEY 环境变量)
    model="gpt-4o-mini",     # 使用的模型
    min_importance=5,        # 最小重要性评分 (1-10)
    use_llm=True             # 使用 LLM (True) 或启发式 (False)
)
```

### 环境变量
- `OPENAI_API_KEY`: OpenAI LLM 模式需要（可选）
- `GLM_API_KEY`: GLM-4 模式需要（推荐，也可代码中传入）

### 依赖说明
- `chromadb>=0.4.0`: 向量数据库（必需）
- `sentence-transformers>=2.2.0`: 语义检索（可选，支持简单 embedding）
- `pydantic>=2.0.0`: 数据验证（必需）
- `zhipuai>=2.0.0`: GLM-4 SDK（推荐）
- `openai>=1.0.0`: OpenAI API（可选）

## 重要约束

1. **importance_score 必须是整数**，范围 1-10（不是浮点数）
2. **speaker 字段**：必须是 "user" 或 "assistant"（v0.3.1 新增）
3. **启发式模式假设为中文文本**（按 。分割）
4. **LLM 客户端使用结构化输出**，要求 `{"type": "json_object"}`
5. **片段始终按重要性降序排序**
6. **所有时间戳使用带时区的 ISO 格式**
7. **ChromaDB 数据持久化在 `./data/chromadb/` 目录**（可配置）
8. **用户和会话数据以 JSON 格式存储**（分别位于 `./data/users/` 和 `./data/sessions/`）
9. **Embedding 模型默认使用 `simple` 模式**（无需下载模型，生产环境建议升级）
10. **评分阈值**：user 5分，assistant 3分（v0.3.1 新增，差异化过滤）
