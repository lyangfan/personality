# Streamlit MVP 使用指南

## 🚀 快速开始

### 方法 1：使用启动脚本（推荐）

```bash
./run_streamlit.sh
```

### 方法 2：手动启动

```bash
# 确保已加载环境变量
source .env  # Linux/Mac
# 或
# Windows: 在 PowerShell 中运行 Get-Content .env | ForEach-Object { $var = $_.Split('='); [System.Environment]::SetEnvironmentVariable($var[0], $var[1]) }

# 启动 Streamlit
streamlit run streamlit_app.py
```

启动后访问：**http://localhost:8501**

## ✨ 功能特性

### 1. 💬 对话界面
- 实时聊天对话
- 自动记忆提取（每 3 轮）
- 基于记忆的个性化回复
- 聊天历史记录

### 2. 🧠 记忆管理
- 查看所有提取的记忆
- 按说话人筛选（用户/AI）
- 按重要性筛选
- 记忆统计信息

### 3. 👤 用户管理
- 创建新用户
- 多会话管理
- 会话切换
- 历史记录

### 4. ⚙️ 系统配置
- 查看当前配置
- 使用说明
- 记忆评分标准

## 📖 使用流程

### 第一步：登录
1. 在侧边栏输入昵称
2. 点击"登录"按钮
3. 系统自动创建用户

### 第二步：选择或创建会话
1. 在侧边栏选择历史会话
2. 或点击"新建会话"创建新对话

### 第三步：开始对话
1. 在聊天输入框输入消息
2. AI 会基于历史记忆生成个性化回复
3. 每隔 3 轮自动提取记忆

### 第四步：查看记忆
1. 切换到"记忆"标签
2. 查看所有提取的记忆
3. 使用筛选器查找特定记忆

## 🎨 界面预览

### 侧边栏
```
🧠 DeepMemory
---
👤 张三
   ID: user_xxx
---
💬 会话
   [选择会话]
   ➕ 新建会话
   [退出登录]
---
⚙️ 系统信息
   🧠 Embedding: 智谱 Embedding-3
   🔧 提取阈值: 每 3 轮
   📊 最大记忆: 5 条
```

### 主界面
- **💬 对话**：聊天对话区域
- **🧠 记忆**：记忆展示和筛选
- **⚙️ 设置**：系统配置和说明

## 🔧 技术架构

### 前端
- **Streamlit**：Python Web 框架
- **Chat Interface**：对话组件
- **Data Display**：记忆展示

### 后端
- **ConversationManager**：对话管理
- **MemoryStorage**：向量存储（ChromaDB）
- **GLMClient**：AI 对话和记忆提取

### 数据流
```
用户输入 → ConversationManager → GLM-4 生成回复
                          ↓
                    记忆提取（每3轮）
                          ↓
                    ChromaDB 存储
                          ↓
                    语义检索 → 下次对话
```

## 📊 记忆评分标准

### 用户记忆（阈值：5分）
- **5分**：身份信息（姓名、职业）
- **6-7分**：个人偏好和兴趣
- **7-8分**：梦想和目标
- **8-9分**：童年回忆和重要经历
- **9-10分**：深度情感分享

### AI 记忆（阈值：3分）
- **3-4分**：一般回复
- **5分**：具体建议和解决方案
- **6分**：情感支持和鼓励
- **7分**：承诺和约定
- **8-10分**：深度情感理解

## 🎯 MVP 特性

### ✅ 已实现
- [x] 基础对话功能
- [x] 记忆自动提取
- [x] 记忆语义检索
- [x] 用户和会话管理
- [x] 记忆展示和筛选
- [x] 个性化回复

### 🚀 未来扩展
- [ ] 记忆搜索功能
- [ ] 记忆编辑和删除
- [ ] 数据导出功能
- [ ] 多语言支持
- [ ] 主题切换
- [ ] 移动端优化

## 🛠️ 开发说明

### 添加新功能
编辑 `streamlit_app.py`：

```python
# 添加新的页面
def render_new_page():
    st.title("新页面")
    # 你的代码

# 在主应用中注册
tab1, tab2, tab3, tab4 = st.tabs(["💬 对话", "🧠 记忆", "⚙️ 设置", "🆕 新页面"])

with tab4:
    render_new_page()
```

### 自定义样式
修改 `run_streamlit.sh` 中的主题参数：

```bash
--theme.primaryColor "#FF6B6B"  # 主色调
--theme.backgroundColor "#FFFFFF"  # 背景色
--theme.secondaryBackgroundColor "#F0F2F6"  # 次级背景色
```

### 调整系统参数
编辑 `streamlit_app.py` 中的配置：

```python
retrieval_config = RetrievalConfig(
    top_k=5,              # 返回记忆数量
    min_importance=5,     # 最低重要性
    boost_recent=True,    # 时间衰减
    boost_importance=True # 重要性提升
)

conversation_manager = ConversationManager(
    memory_extract_threshold=3,  # 提取频率
    max_context_memories=5,      # 上下文记忆数
)
```

## 📦 依赖安装

```bash
pip install streamlit pandas
```

或使用项目依赖：

```bash
pip install -r requirements.txt
```

## 🔒 隐私和数据

### 数据存储位置
- **向量数据库**：`./data/chromadb/`
- **用户数据**：`./data/users/`
- **会话数据**：`./data/sessions/`

### 数据安全
- 所有数据存储在本地
- 不会上传到云端（除了 API 调用）
- 用户可以随时删除数据目录

### 清除数据
```bash
# 删除所有数据
rm -rf ./data/

# 或只删除特定用户/会话
rm ./data/users/{user_id}.json
rm ./data/sessions/{session_id}.json
```

## 🐛 故障排除

### 问题 1：环境变量未加载
**症状**：API Key 错误
**解决方案**：
```bash
# 检查 .env 文件
cat .env

# 手动加载环境变量
export $(cat .env | grep -v '^#' | xargs)
```

### 问题 2：端口被占用
**症状**：Address already in use
**解决方案**：
```bash
# 使用其他端口
streamlit run streamlit_app.py --server.port 8502
```

### 问题 3：记忆未显示
**症状**：记忆页面为空
**解决方案**：
- 确保已完成至少 3 轮对话
- 检查日志是否有错误
- 尝试降低重要性筛选阈值

## 📞 支持

如有问题，请查看：
- 项目 README
- CLAUDE.md（开发文档）
- FASTAPI_GUIDE.md（API 指南）
- SECURITY.md（安全配置）

## 🎉 享受使用！

这是一个 MVP 版本，功能将持续完善。欢迎反馈建议！
