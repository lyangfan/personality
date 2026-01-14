"""Importance scoring logic for memory fragments.

Implements multi-dimensional scoring:
1. Sentiment Intensity (0-3 points)
2. Information Density (0-4 points)
3. Task/Goal Relevance (0-3 points)
Total: 0-10 points
"""

from typing import List, Literal


class ImportanceScorer:
    """
    Calculate importance score (1-10) for memory fragments.

    Uses three dimensions:
    1. Sentiment Intensity: Strong emotions = higher score
    2. Information Density: More entities/topics = higher score
    3. Task Relevance: Goal-oriented content = higher score
    """

    def __init__(self, llm_client=None):
        """Initialize scorer with optional LLM client for advanced analysis."""
        self.llm_client = llm_client

    def calculate_importance_score(
        self,
        content: str,
        sentiment: str,
        entities: List[str],
        topics: List[str],
        sentiment_intensity: str = "medium",
    ) -> int:
        """
        Calculate importance score (1-10) based on multiple dimensions.

        Args:
            content: The memory content text
            sentiment: "positive", "neutral", or "negative"
            entities: List of entities mentioned
            topics: List of topics discussed
            sentiment_intensity: "high", "medium", "low", or "none"

        Returns:
            Integer score between 1 and 10
        """
        score = 0

        # Dimension 1: Sentiment Intensity (0-3 points)
        # Strong emotions (very positive/negative) = higher score
        if sentiment in ["positive", "negative"]:
            if sentiment_intensity == "high":
                score += 3
            elif sentiment_intensity == "medium":
                score += 2
            else:  # low
                score += 1
        # neutral sentiment gets 0 points

        # Dimension 2: Information Density (0-4 points)
        # Count entities and topics mentioned
        entity_count = len(entities)
        topic_count = len(topics)
        total_density = entity_count + topic_count

        if total_density >= 5:
            score += 4
        elif total_density >= 3:
            score += 3
        elif total_density >= 1:
            score += 2

        # Dimension 3: Task/Goal Relevance (0-3 points)
        # Use LLM to assess if related to user goals/tasks
        if self.llm_client:
            relevance = self._assess_task_relevance(content)
            score += int(relevance * 3)  # 0-3 points
        else:
            # Fallback: heuristic based on keywords
            score += self._heuristic_relevance(content)

        # Ensure score is between 1-10
        return min(max(score, 1), 10)

    def _assess_task_relevance(self, content: str) -> float:
        """
        Use LLM to assess task/goal relevance (0.0-1.0).

        This is a placeholder for LLM-based assessment.
        In production, you would call OpenAI API here.
        """
        # TODO: Implement actual LLM call
        # For now, return a default mid-range relevance
        return 0.5

    def _heuristic_relevance(self, content: str) -> int:
        """
        Fallback heuristic for task relevance without LLM.

        Returns 0-2 points based on keyword matching.
        """
        # Keywords that suggest high relevance
        high_relevance_keywords = [
            "必须",
            "重要",
            "关键",
            "目标",
            "任务",
            "计划",
            "需要",
            "一定要",
        ]
        medium_relevance_keywords = ["想要", "希望", "应该", "可以"]

        content_lower = content.lower()

        # Check for high relevance keywords
        for keyword in high_relevance_keywords:
            if keyword in content_lower:
                return 2

        # Check for medium relevance keywords
        for keyword in medium_relevance_keywords:
            if keyword in content_lower:
                return 1

        return 0

    def analyze_sentiment_intensity(
        self, sentiment: str, content: str
    ) -> Literal["high", "medium", "low", "none"]:
        """
        Analyze sentiment intensity from content.

        Returns estimated intensity level.
        """
        # TODO: This could use LLM for more accurate analysis
        # For now, use simple heuristics

        if sentiment == "neutral":
            return "none"

        # Keywords indicating high intensity
        high_intensity_words = [
            "非常",
            "极其",
            "特别",
            "超级",
            "最爱",
            "讨厌",
            "愤怒",
            "!!",
            "!!!",
        ]

        # Keywords indicating low intensity
        low_intensity_words = ["还行", "不错", "可以", "一般"]

        content_lower = content.lower()

        for word in high_intensity_words:
            if word in content_lower:
                return "high"

        for word in low_intensity_words:
            if word in content_lower:
                return "low"

        return "medium"


def calculate_importance_score(
    content: str,
    sentiment: str,
    entities: List[str],
    topics: List[str],
    sentiment_intensity: str = "medium",
    llm_client=None,
) -> int:
    """
    Convenience function to calculate importance score.

    Args:
        content: The memory content text
        sentiment: "positive", "neutral", or "negative"
        entities: List of entities mentioned
        topics: List of topics discussed
        sentiment_intensity: "high", "medium", "low", or "none"
        llm_client: Optional LLM client for advanced analysis

    Returns:
        Integer score between 1 and 10
    """
    scorer = ImportanceScorer(llm_client=llm_client)
    return scorer.calculate_importance_score(
        content=content,
        sentiment=sentiment,
        entities=entities,
        topics=topics,
        sentiment_intensity=sentiment_intensity,
    )
