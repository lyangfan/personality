# DeepMemory 使用手册

## 📖 项目简介

DeepMemory 是一个 Python 库，用于从纯文本对话中自动提取结构化的记忆片段，并为每个片段计算重要性评分（1-10分）。

### 核心功能

- **智能提取**：从对话中识别有意义的记忆片段（事件、偏好、事实、关系）
- **多维评分**：基于情感强度、信息密度、任务相关性计算重要性
- **GLM-4 支持**：原生支持智谱AI的GLM-4模型，**陪伴型评分系统**
- **结构化输出**：生成标准的 JSON 格式记忆
- **双模式运行**：支持 LLM 模式（高质量）和启发式模式（无需 API）

### 适用场景

- ⭐ **陪伴型 AI**：情感陪伴、个性化推荐（**推荐使用 GLM-4 陪伴型评分**）
- 个人助理记忆用户偏好和历史对话
- 客服系统自动总结对话要点
- 社交平台分析用户互动内容
- 聊天机器人构建长期记忆

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基础使用示例

```python
from src.pipeline.memory_pipeline import MemoryPipeline

# 创建管道实例（使用启发式模式，无需API密钥）
pipeline = MemoryPipeline(
    min_importance=5,      # 只保留重要性评分≥5的片段
    use_llm=False          # 使用启发式模式
)

# 准备对话文本
conversation = """
小明: 我昨天去北京玩了，非常开心！
小红: 真的吗？我也很喜欢北京，特别是长城。
小明: 是啊，长城太壮观了。我最喜欢吃北京烤鸭。
小红: 下次我们一起去吧！
"""

# 提取记忆片段
fragments = pipeline.process(conversation)

# 查看结果
for fragment in fragments:
    print(f"评分: {fragment.importance_score}")
    print(f"内容: {fragment.content}")
    print(f"类型: {fragment.type}")
    print(f"情感: {fragment.sentiment}")
    print(f"实体: {fragment.entities}")
    print(f"主题: {fragment.topics}")
    print("-" * 50)
```

### 3. 输出为 JSON 文件

```python
import json

# 方法一：直接保存
output = [f.dict() for f in fragments]
with open("memories.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# 方法二：使用管道方法
pipeline.extract_to_json(
    conversation,
    output_file="memories.json"
)
```

---

## ⚙️ 配置选项

### MemoryPipeline 参数说明

```python
pipeline = MemoryPipeline(
    api_key="your-openai-api-key",  # OpenAI API 密钥（可选，默认使用环境变量）
    model="gpt-4o-mini",            # 使用的 LLM 模型
    min_importance=5,                # 最小重要性评分阈值（1-10）
    use_llm=True                     # True=LLM模式，False=启发式模式
)
```

### 两种运行模式对比

| 特性 | LLM 模式 (`use_llm=True`) | 启发式模式 (`use_llm=False`) |
|------|--------------------------|------------------------------|
| **需要 API Key** | ✅ 是 | ❌ 否 |
| **提取质量** | 🌟🌟🌟🌟🌟 高 | 🌟🌟🌟 中等 |
| **运行速度** | 较慢（API 调用） | 快速（本地处理） |
| **适用场景** | 生产环境、高精度需求 | 快速测试、无 API 场景 |
| **成本** | 产生 API 费用 | 完全免费 |

---

## 📊 输出格式说明

### 记忆片段结构

每个提取的记忆片段包含以下字段：

```json
{
  "content": "我昨天去北京玩了，非常开心！",
  "timestamp": "2026-01-13T10:00:00Z",
  "type": "event",
  "sentiment": "positive",
  "entities": ["北京", "小明"],
  "topics": ["旅行", "游玩"],
  "importance_score": 7,
  "confidence": 0.85,
  "metadata": {
    "source": "conversation"
  }
}
```

### 字段详解

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| **content** | string | 记忆内容 | "我最喜欢吃北京烤鸭" |
| **timestamp** | string | ISO 格式时间戳 | "2026-01-13T10:00:00Z" |
| **type** | string | 记忆类型 | `event` / `preference` / `fact` / `relationship` |
| **sentiment** | string | 情感倾向 | `positive` / `neutral` / `negative` |
| **entities** | string[] | 提取的实体（人名、地名、组织） | ["北京", "小明"] |
| **topics** | string[] | 讨论的主题 | ["旅行", "美食"] |
| **importance_score** | int | 重要性评分（1-10，整数） | 7 |
| **confidence** | float | 置信度（0.0-1.0） | 0.85 |
| **metadata** | object | 额外元数据 | {"source": "conversation"} |

### 记忆类型说明

- **event**（事件）：发生的事情或经历
  - 例："我昨天去北京玩了"
- **preference**（偏好）：用户的喜好或厌恶
  - 例："我最喜欢吃北京烤鸭"
- **fact**（事实）：客观信息或知识
  - 例："长城是中国古代建筑"
- **relationship**（关系）：人际关系描述
  - 例："我和小红是好朋友"

---

## 🎯 重要性评分规则

DeepMemory 使用三维评分系统，总分为 1-10 分：

### 1. 情感强度（0-3分）

| 强度 | 描述 | 关键词 | 分数 |
|------|------|--------|------|
| 高 | 强烈情感 | 非常、超级、特别、极其 | 3 |
| 中 | 明确情感 | 很、喜欢、开心、难过 | 2 |
| 低 | 轻微情感 | 有点、稍微 | 1 |
| 无 | 中性陈述 | - | 0 |

### 2. 信息密度（0-4分）

基于实体和主题的总数量：

| 实体+主题数量 | 分数 |
|-------------|------|
| 5+ 个 | 4 |
| 3-4 个 | 3 |
| 1-2 个 | 2 |
| 0 个 | 1 |

### 3. 任务相关性（0-3分）

包含目标导向的内容：

| 相关性 | 关键词 | 分数 |
|--------|--------|------|
| 高 | 必须、重要、关键、务必 | 3 |
| 中 | 计划、目标、任务、想要 | 2 |
| 低 | 希望、可能、考虑 | 1 |
| 无 | - | 0 |

### 示例计算

```
内容："我非常喜欢北京，计划下个月再去一次"
- 情感强度：3分（"非常"）
- 信息密度：2分（"北京" 1个实体）
- 任务相关性：2分（"计划"、"再"）
总分：3 + 2 + 2 = 7分
```

---

## 🌟 NEW：使用 GLM-4 进行陪伴型评分

> ⭐ **推荐**：针对陪伴型 AI 产品优化的记忆提取和评分系统

### 为什么选择陪伴型评分？

传统评分系统基于"信息密度"，适合知识检索场景。但陪伴型 AI 更关注：
- ✅ **情感连接**：用户是否表达强烈情感
- ✅ **个性化程度**：是否揭示个人特质（童年、经历）
- ✅ **关系深度**：是否表达信任、依赖
- ✅ **偏好明确性**：喜好/厌恶是否清晰

### 快速开始

```python
from src.utils.glm_client import GLMClient

# 初始化 GLM 客户端
client = GLMClient(
    api_key="your-glm-api-key",  # 智谱AI API密钥
    model="glm-4-flash"           # 推荐使用flash模型，性价比高
)

# 提取记忆（自动陪伴型评分）
conversation = """
用户: 我只敢和你说这个秘密
助手: 我会保密的
用户: 我从小就害怕社交，今天终于鼓起勇气和人说话了
"""

fragments = client.extract_memory_with_scoring(conversation)

# 查看结果
for frag in fragments:
    print(f"⭐ {frag['importance_score']}/10")
    print(f"内容: {frag['content']}")
    print(f"类型: {frag['type']} | 情感: {frag['sentiment']}")
    print(f"理由: {frag['reasoning']}\n")
```

### 陪伴型四维评分系统

| 维度 | 分数范围 | 说明 |
|------|---------|------|
| **情感强度** | 0-3分 | 强烈（超级/特别）/明确（喜欢/开心）/轻微/无 |
| **个性化程度** | 0-3分 | 童年经历/明确偏好/一般信息/通用知识 |
| **亲密度/关系** | 0-2分 | 深度信任/分享感受/无关 |
| **偏好明确性** | 0-2分 | 明确喜好/有倾向/无偏好 |
| **总分** | 1-10分 | 各维度相加，取整 |

### 评分示例

**⭐⭐⭐⭐⭐⭐⭐⭐ 8/10分** - 深度信任+童年回忆
```
"我从小就害怕社交，今天终于鼓起勇气和人说话了，只敢和你分享这个秘密"
→ 情感3分 + 个性化3分 + 亲密度2分 = 8分
理由: 高度个性化+强烈情感+深度信任，这是陪伴AI最重要的记忆
```

**⭐⭐⭐⭐⭐ 5/10分** - 明确偏好
```
"我最喜欢吃北京烤鸭"
→ 情感2分 + 个性化1分 + 偏好2分 = 5分
理由: 用户明确表达了最喜欢的食物
```

**⭐⭐⭐ 3/10分** - 日常对话
```
"打算去图书馆看书"
→ 情感0分 + 个性化1分 = 3分（提升基础分）
理由: 一般个人信息，对陪伴场景价值较低
```

### 运行演示

```bash
# 查看完整演示
python demo_companion_memory.py
```

演示包含3个场景：
1. 基础对话 - 各种类型的记忆
2. 深度情感 - 测试高分记忆
3. 混合对话 - 测试评分区分度

### 查看测试结果

```bash
# 查看测试总结（推荐）
cat test_results/TESTING_SUMMARY.md

# 查看完整测试数据（62个片段）
cat test_results/real_conversation_test_results.json
```

测试结果亮点：
- 10个真实聊天场景
- 62个记忆片段
- 平均分 6.05/10
- 高分片段 58.1%
- 场景排名：梦想分享(7.3分) > 童年回忆(7.0分) > 宠物情缘(6.8分)

### GLM-4 vs OpenAI 对比

| 特性 | GLM-4 (`glm_client.py`) | OpenAI (`llm_client.py`) |
|------|----------------------|------------------------|
| **评分方式** | 直接评分（单次调用） | 分步评分（多次调用） |
| **评分标准** | 陪伴型（情感+个性化+关系） | 知识型（信息密度+任务） |
| **适用场景** | ⭐ 陪伴型 AI 产品 | 知识检索、任务助手 |
| **API 成本** | 低（单次调用） | 高（多次调用） |
| **稳定性** | Temperature 0.1 + Few-shot | 传统重试机制 |

---

## 🛠️ 高级用法

### 1. 使用 LLM 模式

首先设置环境变量：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

然后创建管道：

```python
pipeline = MemoryPipeline(
    api_key="sk-...",      # 或从环境变量读取
    model="gpt-4o-mini",   # 推荐使用 mini 模型，性价比高
    min_importance=5,
    use_llm=True           # 启用 LLM 模式
)
```

### 2. 命令行使用

处理文本文件：

```bash
python -m src.pipeline.memory_pipeline examples/sample_conversation.txt
```

输出会保存到 `output.json`。

### 3. 自定义实体提取

```python
from src.extractors.entity_extractor import EntityExtractor

extractor = EntityExtractor()
text = "我和张三、李四去了阿里巴巴"
entities = extractor.extract(text)
print(entities)  # ['张三', '李四', '阿里巴巴']
```

### 4. 单独使用评分器

```python
from src.scorers.importance_scorer import ImportanceScorer
from src.models.memory_fragment import MemoryFragment

scorer = ImportanceScorer()

fragment = MemoryFragment(
    content="我非常喜欢Python",
    type="preference",
    sentiment="positive",
    entities=["Python"],
    topics=["编程"],
    importance_score=1  # 初始值，会被重新计算
)

# 计算重要性评分
score = scorer.score(fragment)
print(f"重要性评分: {score}")  # 输出：7
```

---

## 🧪 测试与验证

### 运行测试套件

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_models.py -v      # 测试数据模型
pytest tests/test_scorers.py -v     # 测试评分逻辑
pytest tests/test_pipeline.py -v    # 测试完整管道

# 查看测试覆盖率
pytest tests/ --cov=src -v
```

### 快速验证脚本

```bash
python quick_test.py
```

这会运行一个简单的示例，验证基本功能是否正常。

---

## 📝 示例对话

### 示例 1：旅行对话

```python
conversation = """
A: 你暑假去哪玩了？
B: 我去了云南旅游，特别开心！
A: 真的吗？我也很想去云南。
B: 那里风景很美，我去了大理和丽江。
A: 听起来很棒！推荐去哪里？
B: 大理古城一定要去，还有洱海。
A: 好的，我记住了，下次去。
"""

pipeline = MemoryPipeline(min_importance=5, use_llm=False)
fragments = pipeline.extract(conversation)

for f in fragments:
    print(f"[{f.importance_score}分] {f.content}")
```

**输出示例**：
```
[7分] 我去了云南旅游，特别开心！
[6分] 大理古城一定要去，还有洱海。
[5分] 那里风景很美，我去了大理和丽江。
```

### 示例 2：技术讨论

```python
conversation = """
用户: 我最喜欢的编程语言是 Python
助手: 为什么喜欢 Python？
用户: 因为语法简洁，而且有强大的生态系统
助手: 你用 Python 做什么项目？
用户: 主要是机器学习和数据分析
"""

fragments = pipeline.extract(conversation)
for f in fragments:
    print(f"类型: {f.type}, 评分: {f.importance_score}")
    print(f"内容: {f.content}\n")
```

**输出示例**：
```
类型: preference, 评分: 6
内容: 我最喜欢的编程语言是 Python

类型: fact, 评分: 5
内容: 因为语法简洁，而且有强大的生态系统

类型: fact, 评分: 5
内容: 主要是机器学习和数据分析
```

---

## ❓ 常见问题

### Q1: 如何选择使用 LLM 模式还是启发式模式？

**A**:
- **使用 LLM 模式**：需要高精度提取，有 API 预算，用于生产环境
- **使用启发式模式**：快速原型开发、测试功能、无 API 密钥场景

### Q2: min_importance 应该设置多少？

**A**:
- `1-3`：保留几乎所有内容（包括闲聊）
- `4-6`：平衡选择（推荐默认值 5）
- `7-10`：只保留最重要的信息

建议从 5 开始，根据实际效果调整。

### Q3: 为什么提取的片段是空的？

**A** 可能的原因：
1. 所有片段的重要性评分都低于 `min_importance` 阈值
2. 对话内容过于简单或无关紧要
3. 启发式模式下，文本格式不符合预期（中文句号分割）

**解决方法**：
- 降低 `min_importance` 值
- 检查对话内容格式
- 尝试使用 LLM 模式

### Q4: LLM 模式报错 "No API key provided"

**A** 确保设置了 API 密钥：

```bash
# 方法 1：环境变量
export OPENAI_API_KEY="sk-..."

# 方法 2：代码中传入
pipeline = MemoryPipeline(api_key="sk-...", use_llm=True)
```

### Q5: 启发式模式只支持中文吗？

**A** 是的。启发式模式使用中文句号（。）进行句子分割，因此主要针对中文对话优化。其他语言建议使用 LLM 模式。

### Q6: 如何处理历史对话记录？

**A** 建议分批处理：

```python
# 将长对话分成小块
chunks = [conversation[i:i+1000] for i in range(0, len(conversation), 1000)]

all_fragments = []
for chunk in chunks:
    fragments = pipeline.extract(chunk)
    all_fragments.extend(fragments)

# 去重和排序
all_fragments = list(set(all_fragments))
all_fragments.sort(key=lambda x: x.importance_score, reverse=True)
```

---

## 🔧 故障排查

### 问题 1：导入模块失败

```python
ModuleNotFoundError: No module named 'src'
```

**解决方法**：确保在项目根目录运行脚本，或添加路径：

```python
import sys
sys.path.append("/path/to/personality")
```

### 问题 2：Pydantic 验证错误

```python
ValidationError: importance_score must be between 1 and 10
```

**解决方法**：检查自定义数据，确保 `importance_score` 是 1-10 之间的整数。

### 问题 3：LLM API 超时

**解决方法**：LLM 客户端内置了重试机制，如果仍然失败：

1. 检查网络连接
2. 尝试更换模型（如使用 `gpt-4o-mini` 而非 `gpt-4o`）
3. 增加超时时间（需修改 `src/utils/llm_client.py`）

---

## 📚 项目结构

```
personality/
├── src/
│   ├── models/                      # Pydantic 数据模型
│   │   └── memory_fragment.py       # 记忆片段模型定义
│   ├── extractors/                  # 提取器
│   │   ├── entity_extractor.py      # 实体提取
│   │   ├── topic_extractor.py       # 主题提取
│   │   └── sentiment_extractor.py   # 情感提取
│   ├── scorers/                     # 评分器
│   │   └── importance_scorer.py     # 重要性评分逻辑
│   ├── pipeline/                    # 主管道
│   │   └── memory_pipeline.py       # 记忆提取管道
│   └── utils/                       # 工具类
│       ├── glm_client.py            # ⭐ GLM-4 客户端（陪伴型评分）
│       └── llm_client.py            # OpenAI 客户端
├── tests/                           # 测试文件
│   ├── test_models.py
│   ├── test_scorers.py
│   └── test_pipeline.py
├── test_results/                    # ⭐ 测试结果目录
│   ├── README.md                    # 测试结果说明
│   ├── TESTING_SUMMARY.md           # 测试总结（推荐阅读）
│   ├── real_conversation_test_results.json  # 完整数据（62个片段）
│   └── test_report.txt              # 简洁报告
├── examples/                        # 示例对话
│   └── sample_conversation.txt
├── demo_companion_memory.py         # ⭐ 陪伴型演示（生产级）
├── test_real_conversations.py       # 真实场景测试脚本
├── requirements.txt                 # 依赖列表
├── README.md                        # 项目说明（英文）
├── CLAUDE.md                        # Claude Code 指南
└── USER_GUIDE_CN.md                 # 本文档
```

---

## 🤝 贡献与反馈

如果您在使用过程中遇到问题或有改进建议，欢迎：

1. 提交 Issue
2. 发起 Pull Request
3. 分享您的使用经验

---

## 📄 许可证

MIT License

---

## 🔄 更新日志

### v0.2.0 (2026-01-14) - ⭐ 陪伴型 AI 重大更新
- ✨ **新增 GLM-4 支持**：智谱AI GLM-4 模型原生支持
- ✨ **陪伴型评分系统**：针对陪伴产品优化的四维评分
  - 情感强度 (0-3分)
  - 个性化程度 (0-3分)
  - 亲密度/关系 (0-2分)
  - 偏好明确性 (0-2分)
- ✨ **直接评分**：GLM 单次调用完成提取+评分，降低成本
- ✨ **稳定性保障**：Temperature 0.1 + Few-shot examples
- ✨ **本地验证**：评分校正机制确保合理性
- ✨ **完整测试**：10个真实场景，62个片段验证
- 📝 新增 `demo_companion_memory.py` 生产级演示
- 📝 新增 `test_results/` 测试结果目录
- 📝 更新 `USER_GUIDE_CN.md` 添加 GLM-4 使用指南

### v0.1.0
- ✨ 基础记忆提取功能
- ✨ 双模式运行（LLM + 启发式）
- ✨ 多维度重要性评分
- ✨ 完整的测试覆盖

---

**祝您使用愉快！** 🎉
