"""
FastAPI 请求和响应数据模型
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== Chat 相关模型 ====================

class ChatMessage(BaseModel):
    """聊天消息"""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """对话请求"""
    user_id: str = Field(..., description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID，如果为空则创建新会话")
    message: str = Field(..., description="用户消息")

    # 可选参数
    username: Optional[str] = Field(None, description="用户名（仅新用户时需要）")
    extract_now: bool = Field(False, description="是否立即提取记忆")


class ChatResponse(BaseModel):
    """对话响应"""
    response: str = Field(..., description="AI 回复")
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")
    memory_extracted: bool = Field(False, description="是否触发了记忆提取")
    message_count: int = Field(..., description="当前会话消息数")


# ==================== 兼容 OpenAI Chat Completions 格式 ====================

class ChatCompletionMessage(BaseModel):
    """Chat completion 消息格式"""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatCompletionRequest(BaseModel):
    """兼容 OpenAI 的 chat completions 请求"""
    messages: List[ChatCompletionMessage] = Field(..., description="消息列表")
    user_id: str = Field(..., description="用户ID（自定义字段）")
    session_id: Optional[str] = Field(None, description="会话ID（自定义字段）")
    username: Optional[str] = Field(None, description="用户名（自定义字段）")
    model: Optional[str] = Field("glm-4-flash", description="模型名称")
    temperature: Optional[float] = Field(0.7, description="温度参数")
    max_tokens: Optional[int] = Field(1000, description="最大token数")
    stream: Optional[bool] = Field(False, description="是否流式输出（暂不支持）")


class ChatCompletionResponse(BaseModel):
    """兼容 OpenAI 的 chat completions 响应"""
    id: str = Field(..., description="响应ID")
    object: str = Field("chat.completion", description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="模型名称")
    choices: List[dict] = Field(..., description="选择列表")
    usage: Optional[dict] = Field(None, description="使用量统计")


# ==================== Memory 相关模型 ====================

class MemoryFragmentResponse(BaseModel):
    """记忆片段响应"""
    content: str
    timestamp: datetime
    speaker: Literal["user", "assistant"]
    type: Literal["event", "preference", "fact", "relationship"]
    entities: List[str]
    topics: List[str]
    sentiment: Literal["positive", "neutral", "negative"]
    importance_score: int
    confidence: float
    metadata: dict


class MemoriesRequest(BaseModel):
    """获取记忆请求"""
    user_id: str = Field(..., description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID，如果为空则返回所有会话的记忆")
    limit: Optional[int] = Field(50, description="返回数量限制")
    min_importance: Optional[int] = Field(None, description="最低重要性分数")
    speaker: Optional[Literal["user", "assistant"]] = Field(None, description="说话人过滤")


class MemoriesResponse(BaseModel):
    """记忆列表响应"""
    user_id: str
    session_id: Optional[str]
    total_count: int
    memories: List[MemoryFragmentResponse]


# ==================== User/Session 相关模型 ====================

class UserCreateRequest(BaseModel):
    """创建用户请求"""
    username: str
    user_id: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应"""
    user_id: str
    username: str
    created_at: datetime
    metadata: dict


class SessionCreateRequest(BaseModel):
    """创建会话请求"""
    user_id: str
    title: Optional[str] = Field("新对话", description="会话标题")
    session_id: Optional[str] = None


class SessionResponse(BaseModel):
    """会话响应"""
    session_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    is_active: bool


class UserSessionsResponse(BaseModel):
    """用户会话列表响应"""
    user_id: str
    total_sessions: int
    sessions: List[SessionResponse]


# ==================== Health Check ====================

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    embedding_model: str
    components: dict
