# 项目结构

```
personality/
├── app.py                      # FastAPI 主应用 ⭐
├── start.sh                    # 启动脚本
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
│
├── 📖 文档/
│   ├── README.md               # 项目概览
│   ├── FASTAPI_GUIDE.md        # FastAPI 使用指南（小白必读）⭐
│   ├── API.md                  # API 完整文档
│   ├── CLAUDE.md               # 开发者指南
│   └── TEST_RESULTS.md         # 真实场景测试报告
│
├── 🧪 测试/
│   ├── test_api.py             # FastAPI API 测试 ⭐
│   ├── test_real_scenario.py   # 真实场景测试 ⭐
│   └── tests/                  # 单元测试
│       ├── test_models.py
│       ├── test_scorers.py
│       ├── test_pipeline.py
│       └── ...
│
├── 🎭 演示/
│   └── demos/                  # 演示脚本
│       ├── demo_interactive_chat.py     # 交互式聊天 ⭐
│       ├── demo_companion_memory.py     # 陪伴型 AI
│       └── demo_glm_embedding.py        # Embedding 演示
│
├── 💻 源代码/
│   └── src/
│       ├── api/                # FastAPI API 模块 ⭐
│       │   ├── models.py
│       │   ├── routes.py
│       │   └── dependencies.py
│       ├── models/             # 数据模型
│       ├── storage/            # 存储层
│       ├── retrieval/          # 检索层
│       ├── conversation/       # 对话层
│       └── utils/              # 工具类
│
└── 💾 数据/
    ├── data/users/             # 用户数据
    ├── data/sessions/          # 会话数据
    └── data/chromadb/          # 向量数据库
```

---

## 快速开始

### 1. 使用 FastAPI 服务（推荐）⭐

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env 文件

# 启动服务
python app.py

# 访问 API 文档
# http://localhost:8000/docs
```

详细教程: [FASTAPI_GUIDE.md](FASTAPI_GUIDE.md)

### 2. 运行演示

```bash
# 交互式聊天演示
python demos/demo_interactive_chat.py

# 陪伴型 AI 演示
python demos/demo_companion_memory.py
```

### 3. 运行测试

```bash
# API 测试
python test_api.py

# 真实场景测试
python test_real_scenario.py

# 单元测试
pytest tests/ -v
```

---

## 核心文件说明

| 文件 | 说明 | 重要性 |
|------|------|--------|
| `app.py` | FastAPI 主应用 | ⭐⭐⭐ |
| `test_api.py` | API 接口测试 | ⭐⭐⭐ |
| `test_real_scenario.py` | 真实场景测试 | ⭐⭐⭐ |
| `demos/demo_interactive_chat.py` | 交互式演示 | ⭐⭐⭐ |
| `FASTAPI_GUIDE.md` | 使用指南 | ⭐⭐⭐ |

---

## 推荐阅读顺序

1. **新手**：README.md → FASTAPI_GUIDE.md → 运行 test_api.py
2. **开发者**：CLAUDE.md → API.md → 查看源码
3. **测试**：TEST_RESULTS.md → test_real_scenario.py
