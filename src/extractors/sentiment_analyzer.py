"""Sentiment analysis module."""

from typing import Dict, Literal

from .base import BaseExtractor


class SentimentAnalyzer(BaseExtractor):
    """Analyze sentiment of text."""

    def extract(self, text: str) -> Dict[str, str]:
        """
        Analyze sentiment of text.

        Args:
            text: Input text to analyze

        Returns:
            Dict with 'sentiment' and 'intensity' keys
        """
        if self.llm_client:
            return self.llm_client.analyze_sentiment(text)
        else:
            return self._heuristic_analyze(text)

    def _heuristic_analyze(self, text: str) -> Dict[str, str]:
        """
        Fallback heuristic analysis without LLM.

        Uses keyword matching for simple sentiment detection.
        """
        positive_words = [
            "喜欢",
            "爱",
            "好",
            "棒",
            "优秀",
            "开心",
            "高兴",
            "满意",
            "喜欢",
        ]
        negative_words = [
            "讨厌",
            "恨",
            "坏",
            "差",
            "糟",
            "难过",
            "伤心",
            "不满",
            "愤怒",
        ]

        text_lower = text.lower()

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            sentiment: Literal["positive", "neutral", "negative"] = "positive"
            # Check for intensity keywords
            if any(word in text_lower for word in ["非常", "特别", "超级"]):
                intensity = "high"
            elif any(word in text_lower for word in ["有点", "还算"]):
                intensity = "low"
            else:
                intensity = "medium"
        elif negative_count > positive_count:
            sentiment = "negative"
            if any(word in text_lower for word in ["非常", "特别", "超级"]):
                intensity = "high"
            elif any(word in text_lower for word in ["有点", "还算"]):
                intensity = "low"
            else:
                intensity = "medium"
        else:
            sentiment = "neutral"
            intensity = "none"

        return {"sentiment": sentiment, "intensity": intensity}
