# DeepMemory FastAPI 完全使用指南

> 从零开始，手把手教你使用 DeepMemory API 服务

## 目录

1. [什么是 DeepMemory？](#什么是-deepmemory)
2. [环境准备](#环境准备)
3. [快速开始](#快速开始)
4. [API 接口详解](#api-接口详解)
5. [Python 调用示例](#python-调用示例)
6. [常见问题](#常见问题)

---

## 什么是 DeepMemory？

**DeepMemory** 是一个**记忆驱动的对话系统**，它能：

- 🧠 **记住用户说的话**：自动从对话中提取重要信息并存储
- 💬 **生成个性化回复**：基于记忆理解用户，提供更贴心的回复
- 🔄 **区分对话角色**：同时记住用户的话和 AI 的承诺
- 📊 **智能评分系统**：自动评估信息的重要性（1-10分）

**简单例子**：
```
用户: 我叫张三，喜欢打网球
AI:  你好张三！很高兴认识你...

（5轮对话后）

用户: 我之前说我叫什么名字？
AI:  你叫张三！（AI 记住了）
```

---

## 环境准备

### 第一步：安装 Python

确保你已经安装了 Python 3.8 或更高版本：

```bash
# 检查 Python 版本
python --version
# 或
python3 --version
```

如果提示找不到 Python，请先安装 Python：https://www.python.org/downloads/

### 第二步：安装 Conda（可选）

如果你使用 Conda 管理环境：

```bash
# 创建新环境
conda create -n deepmemory python=3.11

# 激活环境
conda activate deepmemory
```

### 第三步：获取 API Key

你需要一个**智谱 AI 的 API Key**：

1. 访问 https://open.bigmodel.cn/
2. 注册账号
3. 在控制台获取 API Key
4. 保存这个 Key（后面要用）

---

## 快速开始

### 1. 下载项目

```bash
# 进入项目目录
cd /path/to/personality
```

### 2. 安装依赖

```bash
# 使用阿里云镜像（推荐，速度快）
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 或使用清华镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
```

**安装什么？**
- `fastapi`：Web 框架
- `uvicorn`：服务器
- `chromadb`：向量数据库
- `zhipuai`：智谱 AI SDK
- `sentence-transformers`：文本向量化模型
- 其他依赖...

**预计时间**：3-5 分钟（首次安装会下载模型文件）

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# 复制模板
cp .env.example .env

# 编辑文件
nano .env  # 或使用 vscode、vim 等
```

在 `.env` 文件中填入你的 API Key：

```bash
# 必填：智谱 AI API Key
GLM_API_KEY=你的API_Key_填在这里

# 可选：其他配置（有默认值，可以不填）
EMBEDDING_MODEL=glm
ENVIRONMENT=production
PORT=8000
```

**保存并退出**：
- 如果用 nano：按 `Ctrl+X`，然后按 `Y`，再按 `Enter`
- 如果用 vim：按 `Esc`，输入 `:wq`，按 `Enter`

### 4. 启动服务

**方式一：使用启动脚本（推荐）**

```bash
# 给脚本执行权限
chmod +x start.sh

# 启动服务
./start.sh
```

**方式二：直接运行**

```bash
python app.py
```

**方式三：自定义参数**

```bash
# 指定端口和主机
python app.py --host 0.0.0.0 --port 8080

# 生产环境多进程
python app.py --host 0.0.0.0 --port 8000 --workers 4
```

### 5. 验证服务是否启动成功

打开浏览器，访问：
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

如果看到 API 文档页面，恭喜！服务启动成功了！

**停止服务**：
- 在终端按 `Ctrl + C`

---

## API 接口详解

### 核心概念

#### 用户 (User)
- 每个用户有唯一的 `user_id`
- 可以有多个会话

#### 会话 (Session)
- 每次对话是一个会话
- 有唯一的 `session_id`
- 归属于某个用户

#### 消息 (Message)
- 用户发送的消息
- AI 的回复
- 都会被存储和处理

### 接口 1：健康检查

**用途**：检查服务是否正常运行

**请求**：
```bash
curl http://localhost:8000/health
```

**响应**：
```json
{
  "status": "healthy",
  "version": "0.3.1",
  "embedding_model": "glm",
  "components": {
    "memory_storage": "ok",
    "embedding_model": "glm",
    "environment": "production"
  }
}
```

### 接口 2：创建用户

**用途**：创建一个新用户

**请求**：
```bash
curl -X POST http://localhost:8000/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "username": "张三"
  }'
```

**Python 代码**：
```python
import requests

response = requests.post(
    "http://localhost:8000/v1/users",
    json={
        "user_id": "user_001",
        "username": "张三"
    }
)

print(response.json())
# {'user_id': 'user_001', 'username': '张三', ...}
```

**参数说明**：
- `user_id`：用户ID（可选，不填会自动生成）
- `username`：用户名（必需）

### 接口 3：创建会话

**用途**：创建一个新的对话会话

**请求**：
```bash
curl -X POST http://localhost:8000/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "title": "我的第一次对话"
  }'
```

**响应**：
```json
{
  "session_id": "abc-123-def-456",
  "user_id": "user_001",
  "title": "我的第一次对话",
  "message_count": 0,
  "is_active": true
}
```

### 接口 4：发送消息（简单版）

**用途**：发送消息给 AI，获得回复

**请求**：
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "session_id": "abc-123-def-456",
    "message": "你好，我是张三"
  }'
```

**响应**：
```json
{
  "response": "你好张三！很高兴认识你...",
  "session_id": "abc-123-def-456",
  "user_id": "user_001",
  "memory_extracted": false,
  "message_count": 2
}
```

**字段说明**：
- `response`：AI 的回复
- `memory_extracted`：是否触发了记忆提取
- `message_count`：当前会话的消息总数

### 接口 5：发送消息（OpenAI 兼容版）

**用途**：兼容 OpenAI 格式的对话接口

**请求**：
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "session_id": "abc-123-def-456",
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "model": "glm-4-flash"
  }'
```

**响应**：
```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "glm-4-flash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！有什么我可以帮助你的吗？"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### 接口 6：查看记忆

**用途**：查看 AI 记住了哪些信息

**请求**：
```bash
curl "http://localhost:8000/v1/memories?user_id=user_001&session_id=abc-123-def-456"
```

**Python 代码**：
```python
import requests

response = requests.get(
    "http://localhost:8000/v1/memories",
    params={
        "user_id": "user_001",
        "session_id": "abc-123-def-456",
        "limit": 10
    }
)

data = response.json()
print(f"共有 {data['total_count']} 条记忆")

for memory in data['memories']:
    print(f"[{memory['speaker']}] {memory['content']}")
    print(f"   重要性: {memory['importance_score']}/10")
    print()
```

**响应**：
```json
{
  "user_id": "user_001",
  "session_id": "abc-123-def-456",
  "total_count": 5,
  "memories": [
    {
      "content": "我叫张三",
      "speaker": "user",
      "importance_score": 7,
      "type": "fact",
      "timestamp": "2024-01-15T10:30:00"
    },
    ...
  ]
}
```

**查询参数**：
- `user_id`（必需）：用户ID
- `session_id`（可选）：会话ID
- `limit`（可选）：返回数量，默认 50
- `min_importance`（可选）：最低重要性分数
- `speaker`（可选）：过滤 user 或 assistant

---

## Python 调用示例

### 完整示例：简单的对话机器人

```python
import requests
import time

class DeepMemoryClient:
    """DeepMemory API 客户端"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.user_id = None
        self.session_id = None

    def create_user(self, username, user_id=None):
        """创建用户"""
        response = requests.post(
            f"{self.base_url}/v1/users",
            json={"username": username, "user_id": user_id}
        )
        data = response.json()
        self.user_id = data["user_id"]
        print(f"✅ 用户创建成功: {self.user_id}")
        return data

    def create_session(self, title="新对话"):
        """创建会话"""
        response = requests.post(
            f"{self.base_url}/v1/sessions",
            json={"user_id": self.user_id, "title": title}
        )
        data = response.json()
        self.session_id = data["session_id"]
        print(f"✅ 会话创建成功: {self.session_id}")
        return data

    def chat(self, message):
        """发送消息"""
        response = requests.post(
            f"{self.base_url}/v1/chat",
            json={
                "user_id": self.user_id,
                "session_id": self.session_id,
                "message": message
            }
        )
        data = response.json()
        return data["response"]

    def get_memories(self, limit=10):
        """查看记忆"""
        response = requests.get(
            f"{self.base_url}/v1/memories",
            params={
                "user_id": self.user_id,
                "session_id": self.session_id,
                "limit": limit
            }
        )
        return response.json()


# 使用示例
if __name__ == "__main__":
    # 1. 创建客户端
    client = DeepMemoryClient()

    # 2. 创建用户和会话
    client.create_user("张三", "user_001")
    client.create_session("第一次对话")

    # 3. 对话
    print("\n=== 开始对话 ===\n")

    messages = [
        "你好，我叫张三，是一名软件工程师",
        "我喜欢打网球和看电影",
        "你记住我的名字了吗？",
    ]

    for msg in messages:
        print(f"👤 用户: {msg}")
        response = client.chat(msg)
        print(f"🤖 AI: {response}")
        print()
        time.sleep(1)

    # 4. 查看记忆
    print("\n=== AI 记住了什么 ===\n")
    memories = client.get_memories()
    print(f"共有 {memories['total_count']} 条记忆:\n")

    for m in memories['memories']:
        print(f"[{m['speaker']}] {m['content']}")
        print(f"   重要性: {m['importance_score']}/10 | 类型: {m['type']}")
        print()
```

**运行结果**：
```
✅ 用户创建成功: user_001
✅ 会话创建成功: abc-123-def-456

=== 开始对话 ===

👤 用户: 你好，我叫张三，是一名软件工程师
🤖 AI: 你好张三！很高兴认识你...

👤 用户: 我喜欢打网球和看电影
🤖 AI: 我记住了你喜欢打网球和看电影...

👤 用户: 你记住我的名字了吗？
🤖 AI: 当然记得！你叫张三...

=== AI 记住了什么 ===

共有 3 条记忆:

[user] 我叫张三，是一名软件工程师
   重要性: 7/10 | 类型: fact

[user] 我喜欢打网球和看电影
   重要性: 6/10 | 类型: preference

[assistant] 当然记得！你叫张三...
   重要性: 5/10 | 类型: relationship
```

### 高级示例：记忆管理

```python
import requests

API_BASE = "http://localhost:8000"

def filter_important_memories(user_id, session_id, min_score=7):
    """获取高重要性记忆"""
    response = requests.get(
        f"{API_BASE}/v1/memories",
        params={
            "user_id": user_id,
            "session_id": session_id,
            "min_importance": min_score
        }
    )

    data = response.json()
    print(f"找到 {data['total_count']} 条高重要性记忆:\n")

    for m in data['memories']:
        print(f"⭐ [{m['importance_score']}/10] {m['content']}")

def get_user_memories_only(user_id, session_id):
    """只看用户说了什么"""
    response = requests.get(
        f"{API_BASE}/v1/memories",
        params={
            "user_id": user_id,
            "session_id": session_id,
            "speaker": "user"
        }
    )

    data = response.json()
    print(f"\n用户说了 {data['total_count']} 条重要信息:\n")

    for m in data['memories']:
        print(f"• {m['content']}")

# 使用
filter_important_memories("user_001", "abc-123")
get_user_memories_only("user_001", "abc-123")
```

---

## 常见问题

### Q1: 启动时提示 "GLM_API_KEY 环境变量未设置"

**解决方法**：
1. 检查是否创建了 `.env` 文件
2. 确认 `.env` 文件中填入了正确的 API Key
3. 格式应该是：`GLM_API_KEY=your_key_here`（不要有空格）

### Q2: 安装依赖时速度很慢

**解决方法**：使用国内镜像

```bash
# 阿里云镜像
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 或使用清华镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
```

### Q3: 启动后访问 localhost:8000 显示连接失败

**检查清单**：
1. 服务是否真的启动了？（看终端有没有 "Uvicorn running"）
2. 端口是否被占用？（尝试换个端口：`python app.py --port 8080`）
3. 防火墙是否阻止了？

### Q4: AI 为什么记不住我说的话？

**原因**：
- 记忆提取默认每 **5 轮对话**触发一次
- 如果你只说了 1-2 句话，记忆可能还没提取

**解决方法**：
- 继续对话，多聊几句
- 或在请求中添加 `"extract_now": true` 强制立即提取

### Q5: 如何在代码中调用 API？

**推荐使用 `requests` 库**：

```python
import requests

# 简单对话
response = requests.post(
    "http://localhost:8000/v1/chat",
    json={
        "user_id": "user_001",
        "session_id": "session_001",
        "message": "你好"
    }
)

print(response.json()["response"])
```

### Q6: 生产环境如何部署？

**推荐方式**：

```bash
# 使用多进程（充分利用多核 CPU）
python app.py --host 0.0.0.0 --port 8000 --workers 4

# 或使用 gunicorn（更专业）
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**使用 Nginx 反向代理**：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Q7: 如何切换 Embedding 模型？

编辑 `.env` 文件：

```bash
# 使用智谱 Embedding-3（推荐，需要 API Key）
EMBEDDING_MODEL=glm

# 使用 sentence-transformers（本地运行，需要下载模型）
EMBEDDING_MODEL=sentence-transformers

# 开发环境用 simple（快速但质量低）
EMBEDDING_MODEL=simple
ENVIRONMENT=development
```

### Q8: 数据存储在哪里？

**文件存储**：
- 用户数据：`./data/users/`
- 会话数据：`./data/sessions/`
- 向量数据库：`./data/chromadb/`

**备份建议**：
```bash
# 定期备份 data 目录
tar -czf backup_$(date +%Y%m%d).tar.gz data/
```

### Q9: API 有请求频率限制吗？

**当前版本**：没有硬性限制

**建议**：
- 单机建议 `workers=4`
- 如果需要更高并发，考虑部署多台服务器 + 负载均衡

### Q10: 如何查看 API 文档？

启动服务后，在浏览器访问：
- **Swagger UI**：http://localhost:8000/docs （推荐，交互式）
- **ReDoc**：http://localhost:8000/redoc （美观，只读）

---

## 下一步

- 📖 阅读 [API.md](API.md) 了解完整 API 文档
- 🔧 查看 [CLAUDE.md](CLAUDE.md) 了解项目架构
- 💻 运行 `test_api.py` 测试所有功能
- 🚀 开始构建你的应用！

---

## 需要帮助？

- 查看 [API 文档](http://localhost:8000/docs)
- 运行测试脚本：`python test_api.py`
- 查看日志：`tail -f api_server.log`

**祝你使用愉快！** 🎉
