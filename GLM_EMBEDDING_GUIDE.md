# 智谱 AI Embedding-3 使用指南

## 简介

智谱 AI 的 **Embedding-3** 模型是专为中文语义理解优化的 embedding 模型，相比免费的简单编码方案，语义检索准确率大幅提升。

## 快速开始

### 1. 设置 API Key

```bash
export GLM_API_KEY="your-zhipu-ai-api-key"
```

### 2. 在代码中使用

#### 方式一：MemoryStorage 直接使用

```python
from src.storage.memory_storage import MemoryStorage

# 使用智谱 embedding-3
storage = MemoryStorage(
    embedding_model="glm",  # 指定为 glm
    api_key="your-api-key"  # 或从环境变量读取
)
```

#### 方式二：ConversationManager 使用

```python
from src.conversation.conversation_manager import ConversationManager
from src.storage import UserManager, SessionManager, MemoryStorage
from src.utils.glm_client import GLMClient

# 初始化
user_manager = UserManager()
session_manager = SessionManager()

# ⭐ 使用智谱 embedding-3
memory_storage = MemoryStorage(
    embedding_model="glm",
    api_key="your-api-key"
)

glm_client = GLMClient(api_key="your-api-key", model="glm-4-flash")

# 创建对话管理器
conversation_manager = ConversationManager(
    user_manager=user_manager,
    session_manager=session_manager,
    memory_storage=memory_storage,  # 使用智谱 embedding
    glm_client=glm_client
)
```

#### 方式三：GLMEmbedding 直接使用

```python
from src.utils.glm_embedding import GLMEmbedding

# 初始化
embedding = GLMEmbedding(
    api_key="your-api-key",
    model="embedding-3"
)

# 生成单个文本的 embedding
vector = embedding.embed_query("用户喜欢吃火锅")

# 批量生成
vectors = embedding.embed_documents([
    "用户喜欢吃火锅",
    "用户是软件工程师",
    "用户害怕蜘蛛"
])
```

## 运行测试

```bash
# 测试智谱 embedding-3
python demo_glm_embedding.py
```

## 性能对比

| 指标 | Simple Embedding | 智谱 Embedding-3 |
|------|-----------------|------------------|
| 语义准确性 | 中等 | ⭐⭐⭐⭐⭐ 高 |
| 中文优化 | 无 | ✅ 专为中文优化 |
| 向量维度 | 512 | 1024（或更高） |
| 响应速度 | 极快（本地） | 快（API 调用） |
| 成本 | 免费 | 按调用次数计费 |
| 网络要求 | 无 | 需要网络 |

## 示例效果

### 查询：你喜欢什么食物？

**Simple Embedding**:
```
相似度: 0.52
召回: "用户是一名软件工程师"（错误）
```

**智谱 Embedding-3**:
```
相似度: 0.89
召回: "用户最喜欢吃麻辣火锅"（正确）✅
```

## 计费说明

智谱 AI Embedding-3 按调用次数计费：
- 具体价格请查看：https://open.bigmodel.cn/pricing
- 建议：生产环境使用，开发测试可用 simple 模式

## 注意事项

1. **API 调用限制**：智谱 AI 有每分钟调用次数限制
2. **网络依赖**：需要稳定的网络连接
3. **错误处理**：系统已包含重试机制
4. **降级方案**：API 失败时会自动降级到 simple embedding

## 故障排查

### 问题 1：API 调用失败

```
错误: API key must be provided
```

**解决方案**：
```bash
export GLM_API_KEY="your-api-key"
```

### 问题 2：网络超时

```
错误: Connection timeout
```

**解决方案**：
1. 检查网络连接
2. 增加超时时间
3. 或降级到 simple 模式

### 问题 3：向量维度不匹配

如果之前使用 simple embedding 创建的数据，切换到智谱 embedding-3 后需要重新创建 collection：

```python
# 删除旧数据
import shutil
shutil.rmtree("./data/chromadb")

# 重新运行程序
python demo_glm_embedding.py
```

## 最佳实践

### 1. 开发阶段
```python
# 使用 simple 模式（快速、免费）
storage = MemoryStorage(embedding_model="simple")
```

### 2. 生产环境
```python
# 使用智谱 embedding-3（高质量）
storage = MemoryStorage(embedding_model="glm", api_key="your-key")
```

### 3. 混合模式
```python
# 先用 simple 快速开发，后期切换到 glm
embedding_model = os.getenv("EMBEDDING_MODEL", "simple")
storage = MemoryStorage(embedding_model=embedding_model)
```

## 升级指南

### 从 simple 升级到智谱 embedding-3

1. **设置 API Key**
```bash
export GLM_API_KEY="your-api-key"
```

2. **修改代码**
```python
# 原来
storage = MemoryStorage(embedding_model="simple")

# 改为
storage = MemoryStorage(embedding_model="glm", api_key=os.getenv("GLM_API_KEY"))
```

3. **清空旧数据**（可选）
```python
import shutil
shutil.rmtree("./data/chromadb")
```

4. **重新运行**
```bash
python demo_interactive_chat.py
```

## 技术细节

### 向量维度
- 智谱 embedding-3: 1024 维
- Simple embedding: 512 维

### API 端点
```
https://open.bigmodel.cn/api/paas/v4/embeddings
```

### 支持的模型
- `embedding-3`（推荐）
- `embedding-2`

## 相关链接

- [智谱 AI 官网](https://open.bigmodel.cn/)
- [API 文档](https://open.bigmodel.cn/dev/api)
- [定价说明](https://open.bigmodel.cn/pricing)
- [项目 README](README.md)
