"""Entity extraction module."""

from typing import List

from .base import BaseExtractor


class EntityExtractor(BaseExtractor):
    """Extract entities (people, places, organizations) from text."""

    def extract(self, text: str) -> List[str]:
        """
        Extract entities from text.

        Args:
            text: Input text to analyze

        Returns:
            List of entity names
        """
        if self.llm_client:
            return self.llm_client.extract_entities(text)
        else:
            return self._heuristic_extract(text)

    def _heuristic_extract(self, text: str) -> List[str]:
        """
        Fallback heuristic extraction without LLM.

        Uses simple pattern matching.
        """
        # This is a simplified placeholder
        # In production, you might use NLP libraries like spaCy
        entities = []

        # Common patterns (very basic)
        # Uppercase words might be entities
        words = text.split()
        for word in words:
            if word[0].isupper() and len(word) > 2 and word.isalpha():
                entities.append(word)

        return list(set(entities))  # Remove duplicates
