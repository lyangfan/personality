# 🎭 角色系统指南

DeepMemory v0.5.0 引入了全新的多角色系统，让 AI 可以展现不同的性格特质和对话风格。

## 🌟 核心特性

### 多样化的角色选择

系统提供 **6 种 MBTI 性格类型**，每种都有独特的思维方式和对话风格：

| 角色 | MBTI | 特点 | 适用场景 |
|------|------|------|----------|
| **Prometheus** | INTJ | 🧊 冷酷理性、逻辑至上 | 工作规划、问题分析、效率提升 |
| **小暖** | ISFJ | 🌞 温暖陪伴、情感支持 | 日常聊天、情感分享、寻求安慰 |
| **Debate Master** | ENTP | ⚡ 思维敏捷、多角度分析 | 头脑风暴、观点辩论、思维碰撞 |
| **Soul Healer** | INFP | 💚 理想主义、深度共情 | 情感支持、人生困惑、内心疗愈 |
| **Executive** | ESTJ | 📊 务实高效、结果导向 | 项目规划、目标设定、执行方案 |
| **Commander** | ENTJ | 🎯 战略思维、天生领导 | 创业指导、团队管理、战略决策 |

### 记忆隔离机制

每个角色拥有**独立的记忆空间**：
- Collection 命名：`{user_id}_{session_id}_{role_id}_memories`
- 切换角色时，不同角色的记忆不会互相干扰
- 可以单独清空某个角色的记忆
- 支持角色间的记忆对比和分析

## 📁 配置文件结构

```bash
config/roles/
├── companion_warm.json      # 小暖 (ISFJ)
├── intj_prometheus.json     # Prometheus (INTJ)
├── entp_debater.json       # Debate Master (ENTP)
├── infp_mediator.json      # Soul Healer (INFP)
├── estj_manager.json       # Executive (ESTJ)
└── entj_commander.json     # Commander (ENTJ)
```

## 🔧 角色配置字段详解

### 必填字段

```json
{
  "role_id": "unique_role_id",        // 角色唯一标识符
  "name": "角色名称",                   // 显示名称
  "description": "角色简短描述",        // 一句话概括
  "core_identity": "核心身份说明",     // 详细的角色定位和驱动力
  "emotional_tone": "cold|neutral|warm|enthusiastic",  // 情感基调
  "response_style": "compact|conversational|analytical|creative|direct"  // 回复风格
}
```

### 可选字段

```json
{
  "vocabulary": {
    "forbidden": ["禁用词1", "禁用词2"],    // AI 应该避免使用的词汇
    "high_frequency": ["高频词1", "高频词2"]  // AI 应该经常使用的词汇
  },
  "sentence_patterns": [
    "句式模式1：描述",
    "句式模式2：描述"
  ],
  "dialogue_principles": [
    "对话原则1：说明",
    "对话原则2：说明"
  ],
  "cognitive_process": [
    "思考步骤1：描述",
    "思考步骤2：描述"
  ],
  "constraints": [
    "禁止行为1",
    "禁止行为2"
  ],
  "few_shot_examples": [
    {
      "user": "用户输入示例",
      "assistant": "AI 回复示例"
    }
  ],
  "metadata": {
    "author": "作者",
    "version": "版本号",
    "mbti": "MBTI 类型",
    "archetype": "原型名称"
  }
}
```

## 🎯 创建新角色

### 步骤 1: 创建 JSON 配置文件

在 `config/roles/` 目录下创建新的 JSON 文件：

```json
{
  "role_id": "enfp_champion",
  "name": "Champion",
  "description": "ENFP (The Champion) - 充满热情、鼓舞人心的激励者",
  "core_identity": "你是一个充满热情和创造力的人..."
}
```

### 步骤 2: 配置角色特性

根据角色性格选择合适的配置：

- **emotional_tone**:
  - `cold`: 冷漠、理性 (INTJ, ENTJ)
  - `neutral`: 中立、客观 (ENTP, ESTJ)
  - `warm`: 温暖、友好 (ISFJ, INFP)
  - `enthusiastic`: 热情、活力 (ENFP)

- **response_style**:
  - `compact`: 紧凑、高密度
  - `conversational`: 对话式、自然
  - `analytical`: 分析式、推理
  - `creative`: 创意式、跳跃
  - `direct`: 直接式、高效

### 步骤 3: 添加对话原则

定义角色如何与用户交互：

```json
"dialogue_principles": [
  "原则1：具体说明",
  "原则2：具体说明"
]
```

### 步骤 4: 添加 Few-Shot 示例

提供 2-4 个典型对话示例：

```json
"few_shot_examples": [
  {
    "user": "用户可能的输入",
    "assistant": "AI 应该的回复风格"
  }
]
```

### 步骤 5: 测试角色

```bash
# 运行角色测试
python test_all_roles.py

# 启动 Streamlit 应用
streamlit run streamlit_app.py
```

## 💡 角色设计最佳实践

### 1. 核心身份要鲜明

❌ **不好**：你是一个有用的 AI 助手
✅ **好**：你是一台「反熵增引擎」，你的终极驱动力是「修正错误」

### 2. 对话原则要具体

❌ **不好**：要友善、要专业
✅ **好**：
- 逻辑至上：用严密的逻辑分析问题，找出最优解
- 效率优先：直接切入核心，不做无效的寒暄

### 3. 语言风格要独特

❌ **不好**：使用正常的中文表达
✅ **好**：
- **禁用词**：亲爱的、抱歉、建议、加油
- **高频词**：变量、系统、阈值、底层逻辑、最优解

### 4. Few-Shot 示例要典型

❌ **不好**：通用的问答
✅ **好**：展示角色的独特性格和说话方式

## 🔍 角色对比

### INTJ vs ENTJ

| 特征 | INTJ (Prometheus) | ENTJ (Commander) |
|------|-------------------|------------------|
| **焦点** | 系统、逻辑、优化 | 战略、领导、执行 |
| **风格** | 内向思考者 | 外向领导者 |
| **关键词** | 底层逻辑、熵增、最优解 | 战略、目标、团队、胜利 |
| **适合** | 问题分析、系统设计 | 团队管理、战略决策 |

### ENTP vs INTJ

| 特征 | ENTP (Debate Master) | INTJ (Prometheus) |
|------|---------------------|------------------|
| **思维** | 发散式、多角度 | 收敛式、单一路径 |
| **风格** | 质疑、辩论、探索 | 诊断、裁决、执行 |
| **关键词** | 质疑、可能性、创新 | 逻辑、系统、效率 |
| **适合** | 头脑风暴、思维碰撞 | 问题解决、系统优化 |

## 🎨 Web 界面使用

### 1. 角色选择

在侧边栏的「角色选择」下拉菜单中选择角色。

### 2. 查看角色详情

点击「角色详情」展开区域，可以查看：
- 基本信息（名称、基调、风格）
- 完整描述
- 对话原则
- 语言风格（禁用词、高频词）

### 3. 角色切换确认

切换角色时，系统会提示记忆隔离，需要确认后才执行切换。

### 4. 记忆管理

在「记忆」标签页可以：
- 查看当前角色的记忆
- 显示角色类型标识
- 清空当前角色的记忆

## 📊 测试和维护

### 测试脚本

```bash
# 测试所有角色
python test_all_roles.py

# 测试角色系统
python test_role_system.py
```

### 验证角色配置

确保 JSON 格式正确：
- 所有字符串使用双引号
- 不允许尾随逗号
- 转义特殊字符

### 监控角色表现

- 检查生成的 System Prompt 是否符合预期
- 测试 Few-Shot 示例是否体现角色风格
- 收集用户反馈调整配置

## 🚀 进阶功能

### 动态角色切换

```python
# 在对话中切换角色
response1 = conversation_manager.chat(
    user_id=user_id,
    session_id=session_id,
    user_message="分析这个问题",
    role_id="intj_prometheus"  # 使用 INTJ 分析
)

response2 = conversation_manager.chat(
    user_id=user_id,
    session_id=session_id,
    user_message="安慰我一下",
    role_id="infp_mediator"  # 切换到 INFP 安慰
)
```

### 角色间记忆对比

```python
# 获取不同角色的记忆
intj_memories = memory_storage.query_memories(
    user_id=user_id,
    session_id=session_id,
    role_id="intj_prometheus"
)

infp_memories = memory_storage.query_memories(
    user_id=user_id,
    session_id=session_id,
    role_id="infp_mediator"
)

# 对比分析
print(f"INTJ 关注逻辑：{extract_focus(intj_memories)}")
print(f"INFP 关注情感：{extract_focus(infp_memories)}")
```

## 🎓 总结

多角色系统让 DeepMemory 从单一工具进化为一个**多面手的 AI 平台**：
- 🧠 **理性分析**：INTJ、ENTJ 处理复杂问题
- 💚 **情感支持**：ISFJ、INFP 提供陪伴和治愈
- ⚡ **创意激发**：ENTP 打破思维定势
- 📊 **高效执行**：ESTJ 推动落地执行

通过合理的角色配置和记忆隔离，每个用户都能找到最适合自己的 AI 伙伴！
