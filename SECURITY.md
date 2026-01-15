# API Key 认证配置指南

## 为什么需要 API Key？

**安全第一！** 没有 API Key 保护，任何人都可以：
- 调用你的 API 接口
- 消耗你的 GLM Token 额度
- 访问用户数据

**添加 API Key 后**：
- ✅ 只有持有正确密钥的客户端才能访问
- ✅ 防止未授权访问和滥用
- ✅ 保护你的 Token 余额

---

## 快速配置

### 1. 生成 API Key

```bash
# 方法1: 使用 OpenSSL 生成
openssl rand -hex 32

# 方法2: 使用 Python 生成
python -c "import secrets; print(secrets.token_hex(32))"

# 方法3: 在线生成器
# https://www.uuidgenerator.net/api/guid
```

生成的示例：
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# 复制模板
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用其他编辑器
```

在 `.env` 中添加：

```bash
# API 访问密钥
API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### 3. 重启服务

```bash
# 停止旧服务（如果在运行）
pkill -f "python app.py"

# 启动新服务
python app.py
```

---

## 使用 API Key

### 方法1: 环境变量（推荐）

```bash
# 设置环境变量
export API_KEY="your-api-key-here"

# 运行测试脚本
python test_api.py
```

### 方法2: 在代码中设置

编辑 `test_api.py`：

```python
# API Key（从环境变量读取，或手动设置）
API_KEY = os.getenv("API_KEY", "your-api-key-here")
```

### 方法3: 运行时传入

```bash
API_KEY="your-key" python test_api.py
```

---

## API 请求示例

### cURL

```bash
# 健康检查（不需要认证）
curl http://localhost:8000/health

# 创建用户（需要认证）
curl -X POST http://localhost:8000/v1/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"username": "张三", "user_id": "user_001"}'
```

### Python (requests)

```python
import requests

headers = {
    "X-API-Key": "your-api-key-here",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8000/v1/chat",
    headers=headers,
    json={
        "user_id": "user_001",
        "session_id": "session_001",
        "message": "你好"
    }
)

print(response.json())
```

### JavaScript (fetch)

```javascript
fetch('http://localhost:8000/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key-here'
  },
  body: JSON.stringify({
    user_id: 'user_001',
    session_id: 'session_001',
    message: '你好'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 认证错误处理

### 错误 1: API Key 缺失

```json
{
  "detail": "API Key 缺失，请在请求头中提供 X-API-Key"
}
```

**解决**：在请求头中添加 `X-API-Key`

### 错误 2: API Key 无效

```json
{
  "detail": "API Key 无效"
}
```

**解决**：检查 API Key 是否正确，与 `.env` 文件中配置的一致

### 错误 3: 生产环境未设置 API Key

服务启动时报错：
```
ValueError: 生产环境必须设置 API_KEY 环境变量！
```

**解决**：
1. 在 `.env` 文件中添加 `API_KEY=your-key`
2. 或者设置环境变量 `ENVIRONMENT=development`（仅用于开发）

---

## 开发环境配置

### 方式1: 跳过认证（仅开发）

编辑 `.env` 文件：

```bash
ENVIRONMENT=development
# 不设置 API_KEY
```

这样在开发环境中可以不使用 API Key 访问接口。

### 方式2: 开发环境也使用认证

编辑 `.env` 文件：

```bash
ENVIRONMENT=development
API_KEY=dev-key-12345  # 开发环境使用简单的 Key
```

推荐方式2，这样更接近生产环境。

---

## 生产环境配置

### 必须设置

```bash
ENVIRONMENT=production
API_KEY=your-production-key-here
```

### 安全建议

1. **使用强随机密钥**
   - 至少 32 个字符
   - 使用 OpenSSL 或 secrets 模块生成
   - 不要使用简单密码

2. **定期更换 API Key**
   ```bash
   # 每3-6个月更换一次
   openssl rand -hex 32
   ```

3. **不要提交到 Git**
   ```bash
   # .gitignore 中已包含
   .env
   ```

4. **使用环境变量**
   ```bash
   # 不要在代码中硬编码
   export API_KEY="your-key"
   ```

5. **限制访问（可选）**
   ```bash
   # 使用防火墙限制 IP
   # 使用 Nginx 反向代理添加额外保护
   ```

---

## 常见问题

### Q: 忘记 API Key 怎么办？

重新生成一个新的：
```bash
openssl rand -hex 32
```

然后更新 `.env` 文件并重启服务。

### Q: 可以同时使用多个 API Key 吗？

当前版本不支持。如果需要多用户：
- 为每个用户设置不同的 API Key（需自行实现）
- 或使用反向代理（如 Nginx）处理认证

### Q: API Key 存储在哪里最安全？

推荐顺序（从最安全到最不安全）：
1. **环境变量**（推荐）
2. **密钥管理服务**（如 AWS Secrets Manager）
3. **配置文件**（`.env`，需加入 `.gitignore`）
4. **代码中**（不推荐，有泄露风险）

### Q: 如何测试 API Key 是否生效？

```bash
# 不带 API Key（应该失败）
curl -X POST http://localhost:8000/v1/users \
  -H "Content-Type: application/json" \
  -d '{"username": "test"}'

# 带 API Key（应该成功）
curl -X POST http://localhost:8000/v1/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"username": "test"}'
```

---

## 生产部署建议

### Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 添加额外的安全头
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # 可选：在这里添加额外的认证
        # auth_basic "Restricted";
        # auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

### 使用 HTTPS（生产环境必须）

```bash
# 使用 Let's Encrypt 免费证书
certbot --nginx -d your-domain.com
```

---

## 总结

✅ **必须配置**：生产环境必须设置 API_KEY
✅ **安全第一**：保护你的 Token 余额
✅ **简单易用**：只需在请求头中添加 `X-API-Key`
✅ **灵活配置**：开发/生产环境可分别设置

**记住**：没有认证的接口 = 烧钱的接口！ 🔥
