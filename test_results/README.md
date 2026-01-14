# 测试结果目录

本目录包含陪伴型记忆提取系统的完整测试结果。

## 📁 文件说明

### 1. TESTING_SUMMARY.md (5.4KB)
**测试总结文档** - 人类可读的测试分析报告
- 核心指标统计
- 10个场景的详细分析
- 高分片段展示
- 陪伴型评分验证结果

### 2. real_conversation_test_results.json (28KB)
**完整测试数据** - 包含所有62个记忆片段的详细信息
- 10个真实聊天场景
- 每个片段的：内容、类型、情感、重要性评分、理由
- JSON格式，便于程序读取和分析

### 3. test_report.txt (3.9KB)
**测试报告** - 简洁版测试结果
- 总体统计
- 各场景摘要
- 亮点片段TOP 5

## 🎯 快速查看

### 查看测试总结
```bash
cat TESTING_SUMMARY.md
```

### 查看完整数据
```bash
cat real_conversation_test_results.json | jq '.scenarios[0].fragments'
```

### 查看简洁报告
```bash
cat test_report.txt
```

## 📊 核心发现

- **总片段数**: 62个
- **平均分**: 6.05/10
- **高分占比**: 58.1% (7-10分)
- **评分范围**: 1-8分

### 最高分片段（8分）
- "你是我最好的倾诉对象" (情感倾诉)
- "他每年春天都陪我放，还给我做了个最大的风筝" (童年回忆)
- "去年我生病在家，它一直守在床边" (宠物情缘)

## 📈 场景排名

| 排名 | 场景 | 平均分 | 高分占比 |
|------|------|--------|---------|
| 1 | 梦想分享 | 7.3 | 100% |
| 2 | 童年回忆 | 7.0 | 83% |
| 3 | 宠物情缘 | 6.8 | 67% |
| 4 | 旅行经历 | 6.6 | 75% |
| 5 | 情感倾诉 | 6.6 | 80% |

## 🔧 如何使用

### 重新运行测试
```bash
# 完整测试（10个场景）
python test_real_conversations.py

# 演示版（3个精选场景）
python demo_companion_memory.py
```

### 分析特定场景
```python
import json

with open("test_results/real_conversation_test_results.json", "r") as f:
    data = json.load(f)

# 查看场景1的所有片段
scenario1 = data['scenarios'][0]
for frag in scenario1['fragments']:
    print(f"{frag['importance_score']}/10 - {frag['content']}")
```

## ⚠️ 注意事项

- 测试使用 GLM-4 Flash 模型
- API 调用需要有效的 API Key
- 测试结果生成于 2026-01-14

## 📚 相关文档

- 项目根目录: `USER_GUIDE_CN.md` - 完整使用手册
- 项目根目录: `README.md` - 项目说明
