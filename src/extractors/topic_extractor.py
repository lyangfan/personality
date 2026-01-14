"""Topic extraction module."""

from typing import List

from .base import BaseExtractor


class TopicExtractor(BaseExtractor):
    """Extract topics/themes from text."""

    def extract(self, text: str) -> List[str]:
        """
        Extract topics from text.

        Args:
            text: Input text to analyze

        Returns:
            List of topic names
        """
        if self.llm_client:
            return self.llm_client.extract_topics(text)
        else:
            return self._heuristic_extract(text)

    def _heuristic_extract(self, text: str) -> List[str]:
        """
        Fallback heuristic extraction without LLM.

        Uses keyword matching.
        """
        # Simple keyword-based topic extraction
        topic_keywords = {
            "编程": ["代码", "编程", "开发", "程序", "软件"],
            "工作": ["工作", "职业", "公司", "团队"],
            "学习": ["学习", "研究", "课程", "知识"],
            "生活": ["生活", "日常", "家庭", "朋友"],
        }

        topics = []
        text_lower = text.lower()

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics
