"""
测试环境变量加载

验证 .env 文件是否正确加载
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

print("=" * 60)
print("环境变量加载测试")
print("=" * 60)

# 测试所有关键环境变量
env_vars = [
    ("GLM_API_KEY", "GLM-4 API Key"),
    ("GLM_EMBEDDING_API_KEY", "GLM Embedding API Key"),
    ("API_KEY", "API 访问密钥"),
    ("ENVIRONMENT", "运行环境"),
    ("EMBEDDING_MODEL", "Embedding 模型"),
    ("DATA_DIR", "数据目录"),
    ("MEMORY_EXTRACT_THRESHOLD", "记忆提取阈值"),
    ("MAX_CONTEXT_MEMORIES", "最大上下文记忆数"),
]

all_loaded = True
for var_name, description in env_vars:
    value = os.getenv(var_name)
    status = "✅" if value else "❌"

    # 隐藏敏感信息（只显示前8个字符）
    if value and "KEY" in var_name:
        display_value = f"{value[:8]}..." if len(value) > 8 else value
    else:
        display_value = value if value else "未设置"

    print(f"{status} {description} ({var_name}): {display_value}")

    if not value:
        all_loaded = False

print("=" * 60)

if all_loaded:
    print("✅ 所有环境变量加载成功！")
else:
    print("⚠️  部分环境变量未设置，请检查 .env 文件")

print("\n下一步:")
print("1. 编辑 .env 文件，填入你的实际 API Keys")
print("2. 运行服务: python app.py")
print("3. 访问文档: http://localhost:8000/docs")
