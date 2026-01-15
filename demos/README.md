# Demos 目录

此目录包含 DeepMemory 的演示脚本。

## 演示列表

### 1. demo_interactive_chat.py ⭐ 推荐
交互式聊天演示，展示记忆驱动的对话系统。

```bash
cd ..
python demos/demo_interactive_chat.py
```

**功能**：
- 创建用户和会话
- 实时对话
- 自动记忆提取
- 语义检索相关记忆

### 2. demo_companion_memory.py
陪伴型 AI 演示，展示情感支持和记忆评分。

```bash
python demos/demo_companion_memory.py
```

**功能**：
- GLM-4 陪伴型评分
- 情感支持对话
- 记忆提取和评分

### 3. demo_glm_embedding.py
GLM Embedding-3 演示，展示向量化和语义检索。

```bash
python demos/demo_glm_embedding.py
```

**功能**：
- GLM Embedding-3 向量化
- ChromaDB 存储
- 语义相似度检索

---

**注意**：运行演示前，请确保已设置 `GLM_API_KEY` 环境变量。
