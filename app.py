"""
DeepMemory FastAPI 应用

记忆驱动的对话系统 REST API 服务

特性：
- 异步架构：立即响应用户请求，记忆提取在后台执行
- 依赖注入：单例模式管理核心组件
- 生产模式：强制使用 GLM embedding-3
- OpenAI 兼容：支持标准 chat completions 格式
"""
import os
from dotenv import load_dotenv

# ⭐ 加载 .env 文件（必须在其他导入之前）
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.api.routes import router
from src.api.dependencies import get_app_config, reset_singletons


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动时：初始化单例组件
    关闭时：清理资源
    """
    # 启动时预加载所有单例
    print("🚀 启动 DeepMemory API 服务...")
    config = get_app_config()
    print(f"📊 环境: {config.environment}")
    print(f"🧠 Embedding 模型: {config.embedding_model}")
    print(f"💾 数据目录: {config.data_dir}")
    print(f"⚙️ 记忆提取阈值: 每 {config.memory_extract_threshold} 轮")
    print(f"💬 最大上下文记忆: {config.max_context_memories} 条")

    yield

    # 关闭时清理
    print("🛑 关闭 DeepMemory API 服务...")


# 创建 FastAPI 应用
app = FastAPI(
    title="DeepMemory API",
    description="记忆驱动的对话系统 REST API 服务",
    version="0.3.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": str(request.url),
        },
    )


# 注册路由
app.include_router(router)


# 根路径
@app.get("/")
async def root():
    """根路径欢迎信息"""
    return {
        "name": "DeepMemory API",
        "version": "0.3.1",
        "description": "记忆驱动的对话系统 REST API 服务",
        "endpoints": {
            "chat": "/v1/chat",
            "chat_completions": "/v1/chat/completions",
            "memories": "/v1/memories",
            "health": "/health",
            "docs": "/docs",
        },
    }


# ==================== 启动脚本 ====================

def main(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
):
    """
    启动 FastAPI 服务

    Args:
        host: 监听地址
        port: 监听端口
        reload: 是否自动重载（开发模式）
        workers: 工作进程数（生产环境建议使用多进程）
    """
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DeepMemory API 服务")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8000, help="监听端口")
    parser.add_argument("--reload", action="store_true", help="自动重载（开发模式）")
    parser.add_argument("--workers", type=int, default=1, help="工作进程数")

    args = parser.parse_args()

    main(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
    )
