# 🧠 DeepMemory Streamlit MVP

记忆驱动的对话系统 - Web 界面

## ✨ 特性

- 💬 **智能对话**：基于记忆的个性化 AI 对话
- 🧠 **自动记忆提取**：每 3 轮对话自动提取重要记忆
- 🔍 **语义检索**：基于向量相似度智能检索相关记忆
- 👤 **多用户支持**：支持多个用户和会话管理
- 📊 **记忆可视化**：直观展示和管理记忆

## 🚀 快速开始

### 一键启动

```bash
./start_web.sh
```

启动后访问：**http://localhost:8501**

### 或使用 Python

```bash
streamlit run streamlit_app.py
```

## 📸 界面预览

### 对话界面
- 聊天输入框
- 实时 AI 回复
- 聊天历史显示
- 自动记忆提取提示

### 记忆界面
- 记忆统计（总数、用户记忆、AI 记忆）
- 按说话人筛选
- 按重要性筛选
- 详细记忆展示

### 设置界面
- 系统配置查看
- 使用说明
- 记忆评分标准

## 💡 使用流程

1. **登录**：在侧边栏输入昵称
2. **选择会话**：选择历史会话或创建新会话
3. **开始对话**：在聊天框输入消息
4. **查看记忆**：切换到"记忆"标签查看提取的记忆

## 🎯 记忆功能

### 自动触发
每 **3 轮**对话自动提取一次记忆

### 记忆类型
- **用户记忆**：身份、偏好、梦想、经历（≥5分）
- **AI 记忆**：承诺、建议、情感支持（≥3分）

### 记忆检索
- 基于语义相似度
- 结合重要性评分
- 时间衰减权重

## 📦 技术栈

- **前端**：Streamlit
- **后端**：FastAPI（可选，用于 API 服务）
- **AI 模型**：智谱 AI GLM-4 Flash
- **Embedding**：智谱 AI Embedding-3
- **向量数据库**：ChromaDB
- **语言**：Python 3.8+

## 🔧 配置

所有配置在 `.env` 文件中：

```bash
GLM_API_KEY=your_api_key_here
GLM_EMBEDDING_API_KEY=your_embedding_key_here
EMBEDDING_MODEL=glm
ENVIRONMENT=production
```

## 📖 详细文档

- **[完整使用指南](STREAMLIT_GUIDE.md)**：详细的功能说明和配置
- **[API 文档](FASTAPI_GUIDE.md)**：REST API 使用指南
- **[安全配置](SECURITY.md)**：API Key 配置
- **[开发文档](CLAUDE.md)**：项目架构说明

## 🛠️ 开发

### 安装依赖

```bash
pip install -r requirements.txt
```

### 项目结构

```
personality/
├── streamlit_app.py      # Streamlit 应用
├── start_web.sh          # 启动脚本
├── src/                  # 核心代码
│   ├── api/             # FastAPI 路由（可选）
│   ├── conversation/    # 对话管理
│   ├── storage/         # 数据存储
│   └── utils/           # 工具函数
└── data/                # 本地数据目录
    ├── chromadb/        # 向量数据库
    ├── users/           # 用户数据
    └── sessions/        # 会话数据
```

### 自定义配置

编辑 `streamlit_app.py` 中的参数：

```python
# 调整记忆提取频率
memory_extract_threshold=3  # 每3轮

# 调整检索策略
top_k=5                    # 返回5条记忆
min_importance=5           # 最低5分

# 调整上下文记忆数
max_context_memories=5     # 注入5条记忆
```

## 🔒 隐私

- 所有数据存储在本地
- 不会上传到云端（除了 API 调用）
- 用户可随时删除数据

## 🐛 常见问题

### Q: 如何修改端口？
A: 使用 `--server.port` 参数：
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Q: 记忆没有显示？
A: 确保已完成至少 3 轮对话，记忆才会自动提取。

### Q: 如何清除所有数据？
A: 删除 data 目录：
```bash
rm -rf ./data/
```

## 📞 反馈

如有问题或建议，欢迎反馈！

## 📄 许可

MIT License
