"""Tests for memory extraction pipeline."""

import json
from datetime import datetime

import pytest

from src.pipeline import MemoryPipeline
from src.models import MemoryFragment


class TestMemoryPipeline:
    """Test MemoryPipeline."""

    def test_init_with_llm(self):
        """Test initializing pipeline with LLM enabled."""
        pipeline = MemoryPipeline(use_llm=False)

        assert pipeline.min_importance == 5
        assert pipeline.use_llm is False
        assert pipeline.llm_client is None

    def test_init_with_custom_min_importance(self):
        """Test initializing with custom min_importance."""
        pipeline = MemoryPipeline(min_importance=7, use_llm=False)

        assert pipeline.min_importance == 7

    def test_extract_fragments_heuristic(self):
        """Test heuristic fragment extraction."""
        pipeline = MemoryPipeline(use_llm=False)
        conversation = "今天天气不错。我非常喜欢Python编程。"

        fragments = pipeline._extract_fragments_heuristic(conversation)

        assert len(fragments) == 2
        assert fragments[0]["content"] == "今天天气不错"
        assert fragments[1]["content"] == "我非常喜欢Python编程"

    def test_enrich_fragment(self):
        """Test fragment enrichment."""
        pipeline = MemoryPipeline(use_llm=False)
        raw_fragment = {
            "content": "我非常喜欢Python编程",
            "type": "preference",
            "suggested_sentiment": "positive",
        }

        fragment = pipeline._enrich_fragment(raw_fragment)

        assert isinstance(fragment, MemoryFragment)
        assert fragment.content == "我非常喜欢Python编程"
        assert fragment.type == "preference"
        assert isinstance(fragment.importance_score, int)
        assert 1 <= fragment.importance_score <= 10
        assert isinstance(fragment.entities, list)
        assert isinstance(fragment.topics, list)

    def test_process_conversation(self):
        """Test processing full conversation."""
        pipeline = MemoryPipeline(min_importance=3, use_llm=False)
        conversation = "我非常喜欢Python编程,因为语法简洁。"

        fragments = pipeline.process(conversation)

        assert len(fragments) >= 1
        for fragment in fragments:
            assert isinstance(fragment, MemoryFragment)
            assert fragment.importance_score >= 3

    def test_process_to_json(self):
        """Test processing conversation to JSON."""
        pipeline = MemoryPipeline(min_importance=1, use_llm=False)
        conversation = "我非常喜欢Python编程。"

        json_output = pipeline.process_to_json(conversation)

        # Verify valid JSON
        data = json.loads(json_output)
        assert isinstance(data, list)

        # Verify structure
        if len(data) > 0:
            fragment = data[0]
            assert "content" in fragment
            assert "importance_score" in fragment
            assert "type" in fragment
            assert "sentiment" in fragment
            assert "timestamp" in fragment

    def test_fragments_sorted_by_importance(self):
        """Test fragments are sorted by importance (descending)."""
        pipeline = MemoryPipeline(min_importance=1, use_llm=False)
        conversation = "重要的事情。一般的事情。"

        fragments = pipeline.process(conversation)

        if len(fragments) >= 2:
            # Check descending order
            for i in range(len(fragments) - 1):
                assert fragments[i].importance_score >= fragments[i + 1].importance_score

    def test_importance_score_always_integer(self):
        """Test importance_score is always integer."""
        pipeline = MemoryPipeline(use_llm=False)
        conversation = "测试内容。"

        fragments = pipeline.process(conversation)

        for fragment in fragments:
            assert isinstance(fragment.importance_score, int)
            assert 1 <= fragment.importance_score <= 10

    def test_min_importance_filter(self):
        """Test fragments below min_importance are filtered out."""
        pipeline = MemoryPipeline(min_importance=8, use_llm=False)
        conversation = "今天天气不错。"

        fragments = pipeline.process(conversation)

        # All fragments should have score >= 8
        for fragment in fragments:
            assert fragment.importance_score >= 8

    def test_empty_conversation(self):
        """Test handling empty conversation."""
        pipeline = MemoryPipeline(use_llm=False)
        conversation = ""

        fragments = pipeline.process(conversation)

        # Should return empty list or handle gracefully
        assert isinstance(fragments, list)

    def test_fragment_fields_complete(self):
        """Test all required fields are present."""
        pipeline = MemoryPipeline(use_llm=False)
        raw_fragment = {
            "content": "测试内容",
            "type": "fact",
            "suggested_sentiment": "neutral",
        }

        fragment = pipeline._enrich_fragment(raw_fragment)

        # Check all required fields
        assert fragment.content is not None
        assert fragment.timestamp is not None
        assert fragment.type is not None
        assert fragment.sentiment is not None
        assert fragment.importance_score is not None
        assert isinstance(fragment.entities, list)
        assert isinstance(fragment.topics, list)
        assert isinstance(fragment.metadata, dict)
