"""Base extractor interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseExtractor(ABC):
    """Base class for all extractors."""

    def __init__(self, llm_client=None):
        """
        Initialize extractor.

        Args:
            llm_client: Optional LLM client for advanced extraction
        """
        self.llm_client = llm_client

    @abstractmethod
    def extract(self, text: str) -> Any:
        """
        Extract information from text.

        Args:
            text: Input text to analyze

        Returns:
            Extracted information
        """
        pass
