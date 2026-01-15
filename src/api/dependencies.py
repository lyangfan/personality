"""
FastAPI 依赖注入系统

实现单例模式的管理器，确保：
1. ConversationManager、UserManager 等核心组件全局唯一
2. 生产模式强制使用 glm 或 sentence-transformers embedding，严禁 simple
3. 正确的生命周期管理
4. API Key 认证保护所有接口
"""
import os
from typing import Optional
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from src.storage.user_manager import UserManager
from src.storage.session_manager import SessionManager
from src.storage.memory_storage import MemoryStorage
from src.utils.glm_client import GLMClient
from src.retrieval.memory_retriever import MemoryRetriever, RetrievalConfig
from src.conversation.conversation_manager import ConversationManager


# ==================== API Key 认证 ====================

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


class AppConfig:
    """应用配置类"""

    def __init__(
        self,
        data_dir: str = "./data",
        chromadb_dir: Optional[str] = None,
        glm_api_key: Optional[str] = None,
        embedding_model: Optional[str] = None,
        memory_extract_threshold: int = 5,
        max_context_memories: int = 5,
        environment: str = "production",
        api_key: Optional[str] = None,
    ):
        # 数据目录
        self.data_dir = data_dir
        self.users_dir = f"{data_dir}/users"
        self.sessions_dir = f"{data_dir}/sessions"
        self.chromadb_dir = chromadb_dir or f"{data_dir}/chromadb"

        # API 配置
        self.glm_api_key = glm_api_key or os.getenv("GLM_API_KEY")

        # API Key 认证配置
        self.api_key = api_key or os.getenv("API_KEY")
        # 生产环境必须设置 API Key
        if environment == "production" and not self.api_key:
            raise ValueError(
                "生产环境必须设置 API_KEY 环境变量！"
                "请在 .env 文件中设置: API_KEY=your-secret-api-key"
            )

        # Embedding 模型配置
        # 生产环境强制使用 glm 或 sentence-transformers，严禁 simple
        if embedding_model:
            self.embedding_model = embedding_model
        else:
            env_embedding = os.getenv("EMBEDDING_MODEL")
            if env_embedding:
                self.embedding_model = env_embedding
            else:
                # 默认使用 glm（智谱 Embedding-3）
                if environment == "production":
                    self.embedding_model = "glm"
                else:
                    self.embedding_model = "simple"

        # 对话配置
        self.memory_extract_threshold = memory_extract_threshold
        self.max_context_memories = max_context_memories

        # 环境
        self.environment = environment


@lru_cache()
def get_app_config() -> AppConfig:
    """
    获取应用配置（单例）

    使用 lru_cache 确保全局唯一实例
    """
    environment = os.getenv("ENVIRONMENT", "production")

    return AppConfig(
        data_dir=os.getenv("DATA_DIR", "./data"),
        glm_api_key=os.getenv("GLM_API_KEY"),
        embedding_model=os.getenv("EMBEDDING_MODEL"),
        memory_extract_threshold=int(os.getenv("MEMORY_EXTRACT_THRESHOLD", "5")),
        max_context_memories=int(os.getenv("MAX_CONTEXT_MEMORIES", "5")),
        environment=environment,
        api_key=os.getenv("API_KEY"),
    )


async def verify_api_key(
    api_key_header: str = Depends(api_key_header),
    config: AppConfig = Depends(get_app_config),
) -> bool:
    """
    验证 API Key

    Args:
        api_key_header: 从请求头 X-API-Key 中获取的 API Key
        config: 应用配置

    Returns:
        bool: 验证成功返回 True

    Raises:
        HTTPException: 验证失败返回 401 Unauthorized
    """
    # 开发环境可以跳过认证（如果未设置 API_KEY）
    if config.environment == "development" and not config.api_key:
        return True

    # 验证 API Key
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key 缺失，请在请求头中提供 X-API-Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if api_key_header != config.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key 无效",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return True


@lru_cache()
def get_user_manager(
    config: AppConfig = Depends(get_app_config),
) -> UserManager:
    """
    获取 UserManager（单例）

    使用 lru_cache 确保全局唯一实例
    """
    return UserManager(data_dir=config.users_dir)


@lru_cache()
def get_session_manager(
    config: AppConfig = Depends(get_app_config),
) -> SessionManager:
    """
    获取 SessionManager（单例）

    使用 lru_cache 确保全局唯一实例
    """
    return SessionManager(data_dir=config.sessions_dir)


@lru_cache()
def get_memory_storage(
    config: AppConfig = Depends(get_app_config),
) -> MemoryStorage:
    """
    获取 MemoryStorage（单例）

    使用 lru_cache 确保全局唯一实例
    生产模式强制使用 glm 或 sentence-transformers，严禁 simple embedding
    """
    # 验证 embedding 模型配置
    if config.environment == "production" and config.embedding_model == "simple":
        raise ValueError(
            "生产环境严禁使用 simple embedding 模型！"
            "请设置 EMBEDDING_MODEL=glm 或 sentence-transformers，"
            "或使用环境变量 ENVIRONMENT=development"
        )

    return MemoryStorage(
        persist_directory=config.chromadb_dir,
        embedding_model=config.embedding_model,
        api_key=config.glm_api_key,
    )


@lru_cache()
def get_glm_client(
    config: AppConfig = Depends(get_app_config),
) -> GLMClient:
    """
    获取 GLMClient（单例）

    使用 lru_cache 确保全局唯一实例
    """
    if not config.glm_api_key:
        raise ValueError(
            "GLM_API_KEY 环境变量未设置！"
            "请设置 GLM_API_KEY 或在配置中提供 api_key"
        )

    return GLMClient(
        api_key=config.glm_api_key,
        model="glm-4-flash",
    )


@lru_cache()
def get_memory_retriever(
    storage: MemoryStorage = Depends(get_memory_storage),
    config: AppConfig = Depends(get_app_config),
) -> MemoryRetriever:
    """
    获取 MemoryRetriever（单例）

    使用 lru_cache 确保全局唯一实例
    """
    retrieval_config = RetrievalConfig(
        top_k=config.max_context_memories,
        min_importance=5,
        boost_recent=True,
        boost_importance=True,
        diversity_penalty=0.1,
    )

    return MemoryRetriever(
        storage=storage,
        config=retrieval_config,
    )


@lru_cache()
def get_conversation_manager(
    user_manager: UserManager = Depends(get_user_manager),
    session_manager: SessionManager = Depends(get_session_manager),
    memory_storage: MemoryStorage = Depends(get_memory_storage),
    glm_client: GLMClient = Depends(get_glm_client),
    retriever: MemoryRetriever = Depends(get_memory_retriever),
    config: AppConfig = Depends(get_app_config),
) -> ConversationManager:
    """
    获取 ConversationManager（单例）

    使用 lru_cache 确保全局唯一实例
    这是整个应用的核心组件，协调所有其他组件
    """
    return ConversationManager(
        user_manager=user_manager,
        session_manager=session_manager,
        memory_storage=memory_storage,
        glm_client=glm_client,
        retrieval_config=retriever.config,
        memory_extract_threshold=config.memory_extract_threshold,
        max_context_memories=config.max_context_memories,
    )


# ==================== 辅助函数 ====================

def reset_singletons():
    """
    重置所有单例（主要用于测试）

    警告：生产环境不应调用此函数
    """
    get_app_config.cache_clear()
    get_user_manager.cache_clear()
    get_session_manager.cache_clear()
    get_memory_storage.cache_clear()
    get_glm_client.cache_clear()
    get_memory_retriever.cache_clear()
    get_conversation_manager.cache_clear()
