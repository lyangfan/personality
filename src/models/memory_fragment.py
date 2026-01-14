"""MemoryFragment Pydantic model definition."""

from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, field_validator


class MemoryFragment(BaseModel):
    """
    Structured memory fragment extracted from conversation.

    Core Fields:
        content: The core memory text
        timestamp: When this memory occurred
        type: Memory category (event/preference/fact/relationship)
        entities: People, places, organizations mentioned
        topics: Themes or subjects discussed
        sentiment: Emotional tone (positive/neutral/negative)
        importance_score: CRITICAL - Importance rating from 1-10 (integer)
        confidence: Model confidence (0.0-1.0)
        metadata: Additional context
    """

    content: str = Field(..., description="The core memory text")
    timestamp: datetime = Field(..., description="When this memory occurred")
    type: Literal["event", "preference", "fact", "relationship"] = Field(
        ..., description="Memory category"
    )
    entities: List[str] = Field(
        default_factory=list, description="People, places, organizations mentioned"
    )
    topics: List[str] = Field(
        default_factory=list, description="Themes or subjects discussed"
    )
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        ..., description="Emotional tone"
    )
    importance_score: int = Field(
        ..., ge=1, le=10, description="Importance rating from 1-10 (integer)"
    )
    confidence: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Model confidence"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )

    @field_validator("importance_score")
    @classmethod
    def validate_importance_score(cls, v: int) -> int:
        """Ensure importance_score is an integer between 1-10."""
        if not isinstance(v, int):
            raise ValueError("importance_score must be an integer")
        if v < 1 or v > 10:
            raise ValueError("importance_score must be between 1 and 10")
        return v

    def to_json(self) -> str:
        """Serialize to JSON string with ISO format timestamps."""
        return self.model_dump_json(exclude_none=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryFragment":
        """Create MemoryFragment from dictionary."""
        # Parse timestamp if it's a string
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(
                data["timestamp"].replace("Z", "+00:00")
            )
        return cls(**data)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        schema_extra = {
            "example": {
                "content": "用户最喜欢的编程语言是 Python",
                "timestamp": "2026-01-12T10:00:00Z",
                "type": "preference",
                "entities": ["Python"],
                "topics": ["编程语言", "技术偏好"],
                "sentiment": "positive",
                "importance_score": 7,
                "confidence": 0.92,
                "metadata": {"source": "chat"},
            }
        }
