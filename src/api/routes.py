"""
FastAPI 路由定义

实现异步架构：
- /chat 立即响应用户请求
- 记忆提取作为后台任务执行，不阻塞主线程
"""
import time
import asyncio
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from src.api.models import (
    ChatRequest,
    ChatResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    MemoriesRequest,
    MemoriesResponse,
    MemoryFragmentResponse,
    UserCreateRequest,
    UserResponse,
    SessionCreateRequest,
    SessionResponse,
    UserSessionsResponse,
    HealthResponse,
)
from src.api.dependencies import (
    get_conversation_manager,
    get_user_manager,
    get_session_manager,
    get_memory_storage,
    get_app_config,
    AppConfig,
)
from src.conversation.conversation_manager import ConversationManager
from src.storage.user_manager import UserManager
from src.storage.session_manager import SessionManager
from src.storage.memory_storage import MemoryStorage
from src.models.user import User, Session
from src.models.memory_fragment import MemoryFragment


# 创建路由器
router = APIRouter()


# ==================== 辅助函数 ====================

async def extract_memories_background(
    conversation_manager: ConversationManager,
    user_id: str,
    session_id: str,
):
    """
    后台任务：异步提取记忆

    在后台线程中执行记忆提取，不阻塞主线程的响应
    """
    try:
        # 在线程池中执行同步的记忆提取操作
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: conversation_manager._extract_and_store_memories(
                user_id=user_id,
                session_id=session_id,
            )
        )
    except Exception as e:
        # 记忆提取失败不应影响主流程
        print(f"后台记忆提取失败: {e}")


# ==================== Chat 端点 ====================

@router.post("/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    user_manager: UserManager = Depends(get_user_manager),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """
    对话接口（简化版）

    异步架构：
    1. 立即生成 AI 回复
    2. 在后台异步提取记忆（不阻塞响应）
    """
    try:
        # 确保用户存在
        user = user_manager.get_or_create_user(
            username=request.username or f"user_{request.user_id}",
            user_id=request.user_id,
        )

        # 确保会话存在
        session = None
        if request.session_id:
            session = session_manager.get_session(request.session_id)

        if not session:
            session = session_manager.create_session(
                user_id=user.user_id,
                title="新对话",
            )

        # 立即生成回复（同步操作）
        response = conversation_manager.chat(
            user_id=user.user_id,
            session_id=session.session_id,
            user_message=request.message,
            extract_now=request.extract_now,
        )

        # 在后台异步提取记忆（不阻塞响应）
        if not request.extract_now:
            background_tasks.add_task(
                extract_memories_background,
                conversation_manager,
                user.user_id,
                session.session_id,
            )

        # 获取更新后的会话信息
        session = session_manager.get_session(session.session_id)

        return ChatResponse(
            response=response,
            session_id=session.session_id,
            user_id=user.user_id,
            memory_extracted=request.extract_now,
            message_count=session.message_count,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对话处理失败: {str(e)}",
        )


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse, tags=["Chat"])
async def chat_completions(
    request: ChatCompletionRequest,
    background_tasks: BackgroundTasks,
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    user_manager: UserManager = Depends(get_user_manager),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """
    兼容 OpenAI 的对话接口

    异步架构：
    1. 立即生成 AI 回复
    2. 在后台异步提取记忆（不阻塞响应）
    """
    try:
        # 提取最后一条用户消息
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break

        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未找到用户消息",
            )

        # 确保用户存在
        user = user_manager.get_or_create_user(
            username=request.username or f"user_{request.user_id}",
            user_id=request.user_id,
        )

        # 确保会话存在
        session = None
        if request.session_id:
            session = session_manager.get_session(request.session_id)

        if not session:
            session = session_manager.create_session(
                user_id=user.user_id,
                title="新对话",
            )

        # 立即生成回复
        response_text = conversation_manager.chat(
            user_id=user.user_id,
            session_id=session.session_id,
            user_message=user_message,
            extract_now=False,
        )

        # 在后台异步提取记忆（不阻塞响应）
        background_tasks.add_task(
            extract_memories_background,
            conversation_manager,
            user.user_id,
            session.session_id,
        )

        # 获取更新后的会话信息
        session = session_manager.get_session(session.session_id)

        # 构造兼容 OpenAI 格式的响应
        completion_id = f"chatcmpl-{int(time.time())}"
        created_timestamp = int(time.time())

        return ChatCompletionResponse(
            id=completion_id,
            object="chat.completion",
            created=created_timestamp,
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text,
                },
                "finish_reason": "stop",
            }],
            usage={
                "prompt_tokens": len(user_message),
                "completion_tokens": len(response_text),
                "total_tokens": len(user_message) + len(response_text),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对话处理失败: {str(e)}",
        )


# ==================== Memory 端点 ====================

@router.get("/v1/memories", response_model=MemoriesResponse, tags=["Memory"])
async def get_memories(
    user_id: str,
    session_id: Optional[str] = None,
    limit: int = 50,
    min_importance: Optional[int] = None,
    speaker: Optional[str] = None,
    memory_storage: MemoryStorage = Depends(get_memory_storage),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """
    获取用户记忆（用于调试）

    支持按会话、重要性、说话人过滤
    """
    try:
        # 验证用户和会话
        if session_id:
            session = session_manager.get_session(session_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"会话 {session_id} 不存在",
                )
            if session.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问其他用户的会话",
                )

        # 从 ChromaDB 查询记忆
        results = memory_storage.query_memories(
            user_id=user_id,
            session_id=session_id,
            n_results=limit,
        )

        # 过滤和转换
        fragments = []
        for result in results:
            fragment = MemoryFragment(**result)

            # 应用过滤条件
            if min_importance and fragment.importance_score < min_importance:
                continue
            if speaker and fragment.speaker != speaker:
                continue

            fragments.append(fragment)

        # 转换为响应模型
        memory_responses = [
            MemoryFragmentResponse(**fragment.model_dump())
            for fragment in fragments
        ]

        return MemoriesResponse(
            user_id=user_id,
            session_id=session_id,
            total_count=len(memory_responses),
            memories=memory_responses,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取记忆失败: {str(e)}",
        )


# ==================== User 端点 ====================

@router.post("/v1/users", response_model=UserResponse, tags=["User"])
async def create_user(
    request: UserCreateRequest,
    user_manager: UserManager = Depends(get_user_manager),
):
    """创建新用户"""
    try:
        user = user_manager.create_user(
            username=request.username,
            user_id=request.user_id,
        )
        return UserResponse(**user.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}",
        )


@router.get("/v1/users/{user_id}", response_model=UserResponse, tags=["User"])
async def get_user(
    user_id: str,
    user_manager: UserManager = Depends(get_user_manager),
):
    """获取用户信息"""
    user = user_manager.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {user_id} 不存在",
        )
    return UserResponse(**user.model_dump())


# ==================== Session 端点 ====================

@router.post("/v1/sessions", response_model=SessionResponse, tags=["Session"])
async def create_session(
    request: SessionCreateRequest,
    user_manager: UserManager = Depends(get_user_manager),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """创建新会话"""
    try:
        # 验证用户存在
        user = user_manager.get_user(request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户 {request.user_id} 不存在",
            )

        session = session_manager.create_session(
            user_id=request.user_id,
            title=request.title,
            session_id=request.session_id,
        )
        return SessionResponse(**session.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}",
        )


@router.get("/v1/sessions/{session_id}", response_model=SessionResponse, tags=["Session"])
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager),
):
    """获取会话信息"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会话 {session_id} 不存在",
        )
    return SessionResponse(**session.model_dump())


@router.get("/v1/users/{user_id}/sessions", response_model=UserSessionsResponse, tags=["Session"])
async def list_user_sessions(
    user_id: str,
    user_manager: UserManager = Depends(get_user_manager),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """获取用户的所有会话"""
    # 验证用户存在
    user = user_manager.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {user_id} 不存在",
        )

    sessions = session_manager.list_user_sessions(user_id)
    session_responses = [
        SessionResponse(**session.model_dump())
        for session in sessions
    ]

    return UserSessionsResponse(
        user_id=user_id,
        total_sessions=len(session_responses),
        sessions=session_responses,
    )


# ==================== Health Check ====================

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check(
    config: AppConfig = Depends(get_app_config),
    memory_storage: MemoryStorage = Depends(get_memory_storage),
):
    """健康检查"""
    # 检查组件状态
    components = {
        "memory_storage": "ok" if memory_storage else "not_initialized",
        "embedding_model": config.embedding_model,
        "environment": config.environment,
    }

    return HealthResponse(
        status="healthy",
        version="0.3.1",
        embedding_model=config.embedding_model,
        components=components,
    )
