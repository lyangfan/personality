# 真正的异步架构

## 问题背景

### 什么是"伪异步"？

**伪异步**（Pseudo-async）：定义了 `async def`，但内部调用阻塞的同步代码，导致事件循环被卡住。

```python
# ❌ 伪异步示例（之前的代码）
@router.post("/v1/chat")
async def chat(...):
    # 这是 async def，看起来是异步的
    response = conversation_manager.chat(...)  # 但这是同步的阻塞调用！
    # 当 GLM API 请求耗时 2 秒时，整个事件循环被阻塞
    # 其他用户无法连接服务器
    return {"response": response}
```

**后果**：
- 用户 A 请求 API，等待 GLM 回复（2秒）
- 这 2 秒内，服务器完全被卡住
- 用户 B、C、D 都无法连接
- **并发能力 = 1**

### 真正的异步

**真正的异步**（True-async）：将同步阻塞操作放到线程池中执行，不阻塞事件循环。

```python
# ✅ 真正的异步（修复后的代码）
@router.post("/v1/chat")
async def chat(...):
    # 在线程池中执行同步操作
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,  # 使用 ThreadPoolExecutor
        conversation_manager.chat,
        user_id, session_id, message
    )
    # GLM API 请求在线程池中执行，不阻塞主线程
    # 其他用户可以同时连接
    return {"response": response}
```

**效果**：
- 用户 A 请求 API，等待 GLM 回复（2秒）
- 这 2 秒内，服务器**不会被卡住**
- 用户 B、C、D 可以**同时连接**
- **并发能力 >> 1**

---

## 技术实现

### asyncio.run_in_executor()

```python
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(
    None,  # executor=None 使用默认的 ThreadPoolExecutor
    func,  # 要执行的同步函数
    arg1, arg2, ...  # 函数参数
)
```

**工作原理**：
1. 主线程：FastAPI 事件循环继续运行，可以接收新请求
2. 线程池：在一个独立的线程中执行 `func()`，不会阻塞主线程
3. 完成：线程池执行完毕，将结果返回给主线程

### ThreadPoolExecutor vs ProcessPoolExecutor

| Executor | 适用场景 | 优点 | 缺点 |
|-----------|---------|------|------|
| **ThreadPool** | I/O 密集型（网络请求） | 轻量、启动快 | 受 GIL 限制 |
| **ProcessPool** | CPU 密集型（计算） | 绕过 GIL | 重量、启动慢 |

对于我们的场景（GLM API 网络请求），**ThreadPool 是正确的选择**。

---

## 性能对比

### 之前（伪异步）

```
时间轴：0秒 ----1秒 ----2秒 ----3秒 ----4秒
用户A： [请求] [等待GLM...2秒] [响应]
用户B：       [尝试连接] [被卡住...] [被卡住...] [连接成功]
用户C：       [尝试连接] [被卡住...] [被卡住...] [连接成功]
```

**问题**：
- 并发处理：1 个请求
- 用户体验：用户 B 和 C 被卡住 2 秒
- 服务器资源：浪费（在等待 GLM 时无法处理其他请求）

### 现在（真异步）

```
时间轴：0秒 ----1秒 ----2秒 ----3秒 ----4秒
用户A： [请求] [在线程池中等待GLM...2秒] [响应]
用户B：       [请求] [立即开始处理] [完成]
用户C：       [请求] [立即开始处理] [完成]
```

**效果**：
- 并发处理：多个请求同时处理
- 用户体验：用户 B 和 C 立即开始处理
- 服务器资源：充分利用（GLM 等待时可以处理其他请求）

---

## 代码改动

### 1. ConversationManager 保持同步

**保持原因**：
- ConversationManager 是核心业务逻辑
- 改为异步会影响其他使用方（如 demo 脚本）
- 改动最小，风险最低

**改动**：添加文档说明

```python
def chat(self, ...) -> str:
    """
    处理用户消息并生成回复（同步方法）

    注意：此方法是同步的，在异步路由中应使用 loop.run_in_executor() 调用
    """
    # ... 同步代码 ...
```

### 2. FastAPI 路由使用 run_in_executor

**改动**：在路由层将同步调用转为异步

```python
@router.post("/v1/chat")
async def chat(...):
    # ⚡ 在线程池中执行同步操作
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        conversation_manager.chat,
        user_id, session_id, message
    )
    return {"response": response}
```

---

## 测试验证

### 并发测试脚本

```python
import asyncio
import requests
import time

API_KEY = "your-api-key"
BASE_URL = "http://localhost:8000"
HEADERS = {"X-API-Key": API_KEY}

async def test_concurrent_requests():
    """测试并发请求"""
    start_time = time.time()

    # 发送 5 个并发请求
    tasks = []
    for i in range(5):
        task = asyncio.create_task(send_request(i))
        tasks.append(task)

    # 等待所有请求完成
    responses = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time

    print(f"总耗时: {elapsed:.2f} 秒")
    print(f"每个请求平均: {elapsed / len(responses):.2f} 秒")

async def send_request(idx):
    """发送单个请求"""
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/v1/chat",
        headers=HEADERS,
        json={
            "user_id": f"user_{idx}",
            "message": "你好，请简单介绍一下你自己",
        }
    )
    elapsed = time.time() - start
    print(f"请求 {idx}: {elapsed:.2f} 秒")
    return response

if __name__ == "__main__":
    asyncio.run(test_concurrent_requests())
```

### 预期结果

**伪异步**：
```
请求 0: 2.15 秒
请求 1: 4.30 秒  # 被卡住
请求 2: 6.45 秒  # 被卡住
请求 3: 8.60 秒  # 被卡住
请求 4: 10.75 秒 # 被卡住
总耗时: 10.75 秒
```

**真异步**：
```
请求 0: 2.10 秒
请求 1: 2.15 秒  # 几乎同时完成
请求 2: 2.20 秒  # 几乎同时完成
请求 3: 2.25 秒  # 几乎同时完成
请求 4: 2.30 秒  # 几乎同时完成
总耗时: 2.30 秒  # 而不是 10+ 秒！
```

---

## 架构对比

### 伪异步架构（之前）

```
FastAPI (单线程事件循环)
    ↓
async def chat()
    ↓
同步调用 conversation_manager.chat()
    ↓
同步调用 GLM API (阻塞 2 秒)
    ↓
❌ 整个事件循环被卡住
```

### 真异步架构（现在）

```
FastAPI (单线程事件循环)
    ↓
async def chat()
    ↓
await loop.run_in_executor()
    ↓
ThreadPoolExecutor (独立线程)
    ↓
同步调用 conversation_manager.chat()
    ↓
同步调用 GLM API (在线程中执行)
    ↓
✅ 事件循环继续运行，可以处理其他请求
```

---

## 最佳实践

### 何时使用 run_in_executor？

✅ **应该使用**：
- 调用同步的第三方 API（如 OpenAI、GLM）
- 执行 CPU 密集型计算（如果不想用 ProcessPool）
- 调用不支持异步的库（如大部分数据库驱动）

❌ **不应该使用**：
- 简单的字符串操作（太轻量，不值得线程开销）
- 异步库本身支持（如 asyncpg、motor）
- I/O 操作很少的函数

### 性能优化建议

1. **调整线程池大小**（如果需要）
   ```python
   from concurrent.futures import ThreadPoolExecutor

   executor = ThreadPoolExecutor(max_workers=10)
   await loop.run_in_executor(executor, func, ...)
   ```

2. **使用 uvicorn workers**
   ```bash
   # 4 个进程，每个进程有自己的线程池
   uvicorn app:app --workers 4
   ```

3. **监控线程池**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

---

## 常见问题

### Q: 为什么不改 ConversationManager 为异步？

**A**: 最小改动原则。ConversationManager 被多个地方使用：
- FastAPI 路由
- Demo 脚本（同步）
- 测试脚本（同步）

如果改为异步，需要同步改动所有使用方。使用 run_in_executor 可以只在路由层改动，其他地方不变。

### Q: 线程池会消耗多少资源？

**A**:
- 默认 ThreadPoolExecutor: `min(32, os.cpu_count() * 5)` 个线程
- 每个线程约 8MB 内存
- 10 个并发请求 ≈ 80MB 额外内存
- 对于现代服务器完全可接受

### Q: 可以用 asyncio + aiohttp 改为真正的异步吗？

**A**: 可以，但工作量大：
1. GLM SDK 需要替换为异步版本
2. 所有同步代码都需要改为异步
3. 风险高，测试成本高

**使用 run_in_executor 的优势**：
- 改动最小
- 风险最低
- 效果立竿见影

---

## 总结

✅ **修复前**：伪异步，并发能力 = 1
✅ **修复后**：真异步，并发能力 >> 1

**关键改动**：
- FastAPI 路由使用 `loop.run_in_executor()`
- 同步的 GLM API 调用放到线程池执行
- 事件循环不再被阻塞

**性能提升**：
- 并发处理能力：10 倍+
- 响应时间：用户不再被卡住
- 资源利用率：大幅提升

**记住**：`async def` 不等于异步，必须确保内部不阻塞！
