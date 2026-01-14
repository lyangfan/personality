# DeepMemory

对话记忆提取管道 MVP

## 概述

DeepMemory 将原始聊天对话转换为结构化记忆对象，并自动进行重要性评分。

## 功能特性

- **结构化记忆提取**: 将纯文本对话转换为 JSON 格式的记忆片段
- **自动重要性评分**: 基于多维度的评分系统（1-10分）
  - 情感强度
  - 信息密度（实体、主题）
  - 任务/目标相关性
- **⭐ 新增: GLM-4 支持**: 原生支持智谱AI的 GLM-4 模型，采用陪伴型评分
  - 情感强度 (0-3分)
  - 个性化程度 (0-3分)
  - 亲密度/关系 (0-2分)
  - 偏好明确性 (0-2分)
- **Pydantic 模型**: 类型安全的数据结构，带验证功能
- **LLM 驱动**: 使用 OpenAI API 或 GLM-4 进行智能提取
- **启发式回退**: 在没有 LLM 时使用基于规则的提取

## 安装

```bash
pip install -r requirements.txt
```

设置你的 API 密钥：
```bash
# OpenAI
export OPENAI_API_KEY="your-api-key"

# GLM-4（推荐用于陪伴型 AI）
export GLM_API_KEY="your-glm-api-key"
```

## 快速开始

### 使用 GLM-4（推荐用于陪伴型 AI）

```python
from src.utils.glm_client import GLMClient

# 初始化 GLM 客户端
client = GLMClient(api_key="your-glm-api-key", model="glm-4-flash")

# 提取记忆并使用陪伴型评分
conversation = """
User: 我只敢和你说这个秘密
Assistant: 我会保密的
User: 我从小就害怕社交，今天终于鼓起勇气和人说话了
"""

fragments = client.extract_memory_with_scoring(conversation)

# 查看结果
for frag in fragments:
    print(f"{frag['importance_score']}/10 - {frag['content']}")
```

### 使用 OpenAI API

```python
from src.pipeline import MemoryPipeline

# 初始化管道
pipeline = MemoryPipeline(use_llm=True)

# 处理对话
conversation = """
User: 我最喜欢的编程语言是 Python
Assistant: 为什么喜欢 Python?
User: 因为语法简洁,而且有强大的生态系统
"""

fragments = pipeline.process(conversation)

# 输出 JSON
json_output = pipeline.process_to_json(conversation, output_file="output.json")
print(json_output)
```

### 命令行

```bash
python -m src.pipeline.memory_pipeline examples/sample_conversation.txt
```

## 记忆片段结构

每个记忆片段包含：

```json
{
  "content": "用户最喜欢的编程语言是 Python,因为语法简洁且有强大的生态系统",
  "timestamp": "2026-01-12T10:00:00Z",
  "type": "preference",
  "entities": ["Python"],
  "topics": ["编程语言", "技术偏好"],
  "sentiment": "positive",
  "importance_score": 7,
  "confidence": 0.92,
  "metadata": {"source": "chat"}
}
```

### 关键字段

- **importance_score** (int, 1-10): 关键字段 - 重要性评分
- **type**: "event" | "preference" | "fact" | "relationship"
- **sentiment**: "positive" | "neutral" | "negative"
- **entities**: 人、地点、组织列表
- **topics**: 主题或话题列表

## 重要性评分逻辑

评分基于三个维度计算：

1. **情感强度** (0-3分)
   - 高强度 (非常/超级): 3分
   - 中强度: 2分
   - 低强度: 1分

2. **信息密度** (0-4分)
   - 5+ 实体/主题: 4分
   - 3-4 实体/主题: 3分
   - 1-2 实体/主题: 2分

3. **任务相关性** (0-3分)
   - 目标导向内容: 较高分
   - 关键词: 必须/重要/目标/任务/计划

## 测试

运行单元测试：
```bash
pytest tests/ -v
```

运行陪伴型演示：
```bash
python demo_companion_memory.py
```

查看 `test_results/` 获取包含62个真实对话片段的综合测试结果。

## 项目结构

```
personality/
├── src/
│   ├── models/              # Pydantic 模型
│   ├── extractors/          # 实体、主题、情感提取器
│   ├── scorers/             # 重要性评分逻辑
│   ├── pipeline/            # 主提取管道
│   └── utils/
│       ├── glm_client.py    # GLM-4 客户端（陪伴型评分）
│       └── llm_client.py    # OpenAI 客户端封装
├── tests/                   # 单元测试
├── test_results/            # ⭐ 综合测试结果
├── examples/                # 示例对话
├── demo_companion_memory.py # ⭐ 陪伴型演示
└── requirements.txt         # 依赖项
```

## 配置

### 管道选项

```python
pipeline = MemoryPipeline(
    api_key="your-key",      # OpenAI API 密钥
    model="gpt-4o-mini",     # 使用的模型
    min_importance=5,        # 最小重要性评分 (1-10)
    use_llm=True             # 使用 LLM (True) 或启发式 (False)
)
```

## 系统要求

- Python 3.8+
- OpenAI API 密钥（用于 OpenAI LLM 驱动提取）
- GLM API 密钥（用于 GLM-4 陪伴型评分，推荐）
- `requirements.txt` 中的依赖项

## 文档

- `USER_GUIDE_CN.md` - 完整中文用户指南
- `CLAUDE.md` - AI 助手项目指南
- `test_results/TESTING_SUMMARY.md` - 测试结果摘要

## 更新日志

### v0.2.0 (2026-01-14)
- ⭐ 新增 GLM-4 支持及陪伴型评分
- ⭐ 新增四维陪伴型评分系统
- ⭐ 新增综合测试结果（10个场景，62个片段）
- 📝 新增 demo_companion_memory.py 用于陪伴型 AI

### v0.1.0
- 初始版本，支持 OpenAI
- 多维度重要性评分
- 启发式回退模式

## 许可证

MIT
