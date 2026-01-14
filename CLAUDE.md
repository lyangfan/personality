# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

DeepMemory 是一个 Python 库,用于从纯文本对话中提取结构化的记忆片段。它使用 LLM 驱动的提取(OpenAI API/智谱AI GLM-4)和启发式回退,将对话转换为 JSON 格式的记忆并自动进行重要性评分。

**⭐ v0.2.0 新增**: 陪伴型 AI 评分系统（GLM-4）

## 开发命令

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行测试
- 运行所有测试: `pytest tests/ -v`
- 运行特定测试文件:
  - `pytest tests/test_models.py -v`
  - `pytest tests/test_scorers.py -v`
  - `pytest tests/test_pipeline.py -v`
- 运行测试并查看覆盖率: `pytest tests/ --cov=src -v`

### 快速验证
```bash
# 陪伴型演示（推荐）
python demo_companion_memory.py

# 或使用真实场景测试
python test_real_conversations.py
```

### 使用示例
```bash
python -m src.pipeline.memory_pipeline examples/sample_conversation.txt
```

## 架构设计

### 核心组件

**MemoryPipeline** (`src/pipeline/memory_pipeline.py`): 主编排器,负责:
1. 从对话中提取记忆片段(LLM 或启发式)
2. 用实体、主题和情感丰富片段
3. 计算重要性评分 (1-10)
4. 按重要性过滤和排序

**ImportanceScorer** (`src/scorers/importance_scorer.py`): 多维度评分系统:
- **情感强度** (0-3 分): 情感强度 (high/medium/low/none)
- **信息密度** (0-4 分): 实体 + 主题的数量
- **任务相关性** (0-3 分): 目标导向内容评估
- 总分范围: 1-10(始终为整数)

**MemoryFragment** (`src/models/memory_fragment.py`): Pydantic 模型,严格验证:
- `importance_score`: int, 1-10 (关键字段)
- `type`: Literal["event", "preference", "fact", "relationship"]
- `sentiment`: Literal["positive", "neutral", "negative"]
- `entities`, `topics`: List[str]
- `confidence`: float, 0.0-1.0

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

### 模块结构

```
src/
├── models/              # Pydantic 数据模型
├── extractors/          # 实体、主题、情感提取
├── scorers/             # 重要性评分逻辑
├── pipeline/            # 主编排管道
└── utils/
    ├── glm_client.py    # ⭐ GLM-4 客户端（陪伴型评分）
    └── llm_client.py    # OpenAI 客户端
```

所有模块通过 `__init__.py` 暴露主要类,便于导入。

## 关键设计模式

### ⭐ GLM-4 陪伴型评分 (v0.2.0 新增)

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
- `OPENAI_API_KEY`: OpenAI LLM 模式需要
- `GLM_API_KEY`: GLM-4 模式需要（可选，代码中传入也可）

## 重要约束

1. **importance_score 必须是整数**,范围 1-10(不是浮点数)
2. **启发式模式假设为中文文本**(按 。分割)
3. **LLM 客户端使用结构化输出**,要求 `{"type": "json_object"}`
4. **片段始终按重要性降序排序**
5. **所有时间戳使用带时区的 ISO 格式**
