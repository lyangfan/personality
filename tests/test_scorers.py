"""Tests for importance scorer."""

import pytest

from src.scorers import ImportanceScorer, calculate_importance_score


class TestImportanceScorer:
    """Test ImportanceScorer logic."""

    def setup_method(self):
        """Setup test fixtures."""
        self.scorer = ImportanceScorer(llm_client=None)

    def test_high_importance_positive_high_intensity(self):
        """Test high importance: positive sentiment, high intensity, many entities."""
        score = self.scorer.calculate_importance_score(
            content="我超级喜欢 Python 编程!",
            sentiment="positive",
            entities=["Python", "编程", "开发"],
            topics=["技术", "工作"],
            sentiment_intensity="high",
        )

        assert score >= 7  # Should be high importance
        assert 1 <= score <= 10

    def test_low_importance_neutral_no_entities(self):
        """Test low importance: neutral sentiment, no entities/topics."""
        score = self.scorer.calculate_importance_score(
            content="今天天气不错",
            sentiment="neutral",
            entities=[],
            topics=[],
            sentiment_intensity="none",
        )

        assert score <= 4  # Should be low importance
        assert 1 <= score <= 10

    def test_importance_score_bounds(self):
        """Test importance_score always stays within 1-10."""
        # Even with maximum factors
        score = self.scorer.calculate_importance_score(
            content="非常重要!",
            sentiment="positive",
            entities=["A", "B", "C", "D", "E"],
            topics=["X", "Y", "Z"],
            sentiment_intensity="high",
        )

        assert 1 <= score <= 10

    def test_sentiment_intensity_scoring(self):
        """Test different sentiment intensities produce different scores."""
        high_score = self.scorer.calculate_importance_score(
            content="Test",
            sentiment="positive",
            entities=[],
            topics=[],
            sentiment_intensity="high",
        )

        low_score = self.scorer.calculate_importance_score(
            content="Test",
            sentiment="positive",
            entities=[],
            topics=[],
            sentiment_intensity="low",
        )

        assert high_score > low_score

    def test_information_density_scoring(self):
        """Test more entities/topics increase score."""
        low_density = self.scorer.calculate_importance_score(
            content="Test",
            sentiment="neutral",
            entities=[],
            topics=[],
            sentiment_intensity="none",
        )

        high_density = self.scorer.calculate_importance_score(
            content="Test",
            sentiment="neutral",
            entities=["Python", "OpenAI", "Google"],
            topics=["编程", "AI", "技术"],
            sentiment_intensity="none",
        )

        assert high_density > low_density

    def test_negative_sentiment_scoring(self):
        """Test negative sentiment also scores high."""
        score = self.scorer.calculate_importance_score(
            content="我非常讨厌这个!",
            sentiment="negative",
            entities=[],
            topics=[],
            sentiment_intensity="high",
        )

        # High intensity negative should also get points
        assert score >= 3

    def test_heuristic_relevance(self):
        """Test heuristic relevance detection."""
        # High relevance keywords
        high_relevance = self.scorer._heuristic_relevance("这是我必须完成的任务")
        assert high_relevance >= 1

        # No relevance keywords
        low_relevance = self.scorer._heuristic_relevance("今天天气不错")
        assert low_relevance == 0

    def test_sentiment_intensity_analysis(self):
        """Test sentiment intensity analysis."""
        # High intensity
        intensity = self.scorer.analyze_sentiment_intensity("positive", "我超级喜欢!")
        assert intensity == "high"

        # Low intensity
        intensity = self.scorer.analyze_sentiment_intensity("positive", "还行吧")
        assert intensity == "low"

        # Neutral
        intensity = self.scorer.analyze_sentiment_intensity("neutral", "一般")
        assert intensity == "none"


class TestCalculateImportanceScore:
    """Test convenience function."""

    def test_convenience_function(self):
        """Test the calculate_importance_score helper function."""
        score = calculate_importance_score(
            content="Test",
            sentiment="positive",
            entities=["Python"],
            topics=["编程"],
            sentiment_intensity="medium",
        )

        assert isinstance(score, int)
        assert 1 <= score <= 10

    def test_convenience_function_with_defaults(self):
        """Test convenience function with default parameters."""
        score = calculate_importance_score(
            content="Test", sentiment="neutral", entities=[], topics=[]
        )

        assert isinstance(score, int)
        assert 1 <= score <= 10
