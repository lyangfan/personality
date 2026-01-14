"""Tests for MemoryFragment Pydantic model."""

import json
from datetime import datetime

import pytest

from src.models import MemoryFragment


class TestMemoryFragment:
    """Test MemoryFragment model."""

    def test_create_valid_fragment(self):
        """Test creating a valid memory fragment."""
        fragment = MemoryFragment(
            content="用户最喜欢的编程语言是 Python",
            timestamp=datetime.now(),
            type="preference",
            entities=["Python"],
            topics=["编程语言"],
            sentiment="positive",
            importance_score=7,
        )

        assert fragment.content == "用户最喜欢的编程语言是 Python"
        assert fragment.type == "preference"
        assert fragment.importance_score == 7
        assert len(fragment.entities) == 1
        assert len(fragment.topics) == 1

    def test_importance_score_validation(self):
        """Test importance_score must be between 1-10."""
        with pytest.raises(ValueError):
            MemoryFragment(
                content="Test",
                timestamp=datetime.now(),
                type="fact",
                sentiment="neutral",
                importance_score=0,  # Invalid: too low
            )

        with pytest.raises(ValueError):
            MemoryFragment(
                content="Test",
                timestamp=datetime.now(),
                type="fact",
                sentiment="neutral",
                importance_score=11,  # Invalid: too high
            )

        with pytest.raises(ValueError):
            MemoryFragment(
                content="Test",
                timestamp=datetime.now(),
                type="fact",
                sentiment="neutral",
                importance_score=7.5,  # Invalid: not integer
            )

    def test_importance_score_boundary_values(self):
        """Test boundary values for importance_score."""
        fragment_min = MemoryFragment(
            content="Test",
            timestamp=datetime.now(),
            type="fact",
            sentiment="neutral",
            importance_score=1,
        )
        assert fragment_min.importance_score == 1

        fragment_max = MemoryFragment(
            content="Test",
            timestamp=datetime.now(),
            type="fact",
            sentiment="neutral",
            importance_score=10,
        )
        assert fragment_max.importance_score == 10

    def test_to_json(self):
        """Test JSON serialization."""
        fragment = MemoryFragment(
            content="用户最喜欢的编程语言是 Python",
            timestamp=datetime.now(),
            type="preference",
            entities=["Python"],
            topics=["编程语言"],
            sentiment="positive",
            importance_score=7,
        )

        json_str = fragment.to_json()
        data = json.loads(json_str)

        assert data["content"] == "用户最喜欢的编程语言是 Python"
        assert data["type"] == "preference"
        assert data["importance_score"] == 7
        assert isinstance(data["timestamp"], str)

    def test_from_dict(self):
        """Test creating MemoryFragment from dictionary."""
        data = {
            "content": "用户最喜欢的编程语言是 Python",
            "timestamp": datetime.now().isoformat(),
            "type": "preference",
            "entities": ["Python"],
            "topics": ["编程语言"],
            "sentiment": "positive",
            "importance_score": 7,
        }

        fragment = MemoryFragment.from_dict(data)

        assert fragment.content == "用户最喜欢的编程语言是 Python"
        assert fragment.type == "preference"
        assert fragment.importance_score == 7

    def test_confidence_validation(self):
        """Test confidence field validation."""
        with pytest.raises(ValueError):
            MemoryFragment(
                content="Test",
                timestamp=datetime.now(),
                type="fact",
                sentiment="neutral",
                importance_score=5,
                confidence=1.5,  # Invalid: > 1.0
            )

        with pytest.raises(ValueError):
            MemoryFragment(
                content="Test",
                timestamp=datetime.now(),
                type="fact",
                sentiment="neutral",
                importance_score=5,
                confidence=-0.1,  # Invalid: < 0.0
            )

    def test_default_values(self):
        """Test default field values."""
        fragment = MemoryFragment(
            content="Test",
            timestamp=datetime.now(),
            type="fact",
            sentiment="neutral",
            importance_score=5,
        )

        assert fragment.entities == []
        assert fragment.topics == []
        assert fragment.confidence == 0.8
        assert fragment.metadata == {}

    def test_sentiment_literal_validation(self):
        """Test sentiment field only accepts valid values."""
        with pytest.raises(ValueError):
            MemoryFragment(
                content="Test",
                timestamp=datetime.now(),
                type="fact",
                sentiment="invalid",  # Invalid sentiment
                importance_score=5,
            )

    def test_type_literal_validation(self):
        """Test type field only accepts valid values."""
        with pytest.raises(ValueError):
            MemoryFragment(
                content="Test",
                timestamp=datetime.now(),
                type="invalid",  # Invalid type
                sentiment="neutral",
                importance_score=5,
            )
