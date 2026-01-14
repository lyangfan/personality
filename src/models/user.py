"""用户和会话数据模型."""

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """用户模型."""

    user_id: str = Field(..., description="用户唯一标识")
    username: str = Field(..., description="用户昵称")
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, str] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Session(BaseModel):
    """会话模型."""

    session_id: str = Field(..., description="会话唯一标识")
    user_id: str = Field(..., description="所属用户ID")
    title: str = Field(default="新对话", description="会话标题")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    message_count: int = Field(default=0, description="消息数量")
    is_active: bool = Field(default=True)
    metadata: Dict[str, str] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Message(BaseModel):
    """消息模型."""

    message_id: str = Field(..., description="消息唯一标识")
    session_id: str = Field(..., description="所属会话ID")
    role: str = Field(..., description="role: user/assistant")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now)
    memory_extracted: bool = Field(default=False, description="是否已提取记忆")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
