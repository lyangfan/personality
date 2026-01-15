"""Main memory extraction pipeline."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.extractors import EntityExtractor, SentimentAnalyzer, TopicExtractor
from src.models import MemoryFragment
from src.scorers import ImportanceScorer
from src.utils.llm_client import LLMClient


class MemoryPipeline:
    """
    Main pipeline for extracting memory fragments from conversations.

    Flow:
    1. Parse plain text conversation
    2. Extract memory fragments
    3. Enrich with entities, topics, sentiment
    4. Calculate importance_score (1-10)
    5. Filter and validate
    6. Output JSON
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        min_importance: int = 5,
        use_llm: bool = True,
    ):
        """
        Initialize memory pipeline.

        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o-mini)
            min_importance: Minimum importance score to keep (1-10)
            use_llm: Whether to use LLM for extraction (True) or heuristics (False)
        """
        self.min_importance = min_importance
        self.use_llm = use_llm

        # Initialize LLM client if needed
        if use_llm:
            self.llm_client = LLMClient(api_key=api_key, model=model)
        else:
            self.llm_client = None

        # Initialize extractors
        self.entity_extractor = EntityExtractor(llm_client=self.llm_client)
        self.topic_extractor = TopicExtractor(llm_client=self.llm_client)
        self.sentiment_analyzer = SentimentAnalyzer(llm_client=self.llm_client)

        # Initialize scorer
        self.scorer = ImportanceScorer(llm_client=self.llm_client)

    def process(self, conversation: str) -> List[MemoryFragment]:
        """
        Process conversation and extract memory fragments.

        Args:
            conversation: Plain text conversation

        Returns:
            List of MemoryFragment objects
        """
        # Step 1: Extract raw fragments
        if self.use_llm and self.llm_client:
            raw_fragments = self.llm_client.extract_memory_fragments(conversation)
        else:
            raw_fragments = self._extract_fragments_heuristic(conversation)

        # Step 2: Enrich and score each fragment
        fragments = []
        for raw_fragment in raw_fragments:
            fragment = self._enrich_fragment(raw_fragment)
            if fragment.importance_score >= self.min_importance:
                fragments.append(fragment)

        # Sort by importance (descending)
        fragments.sort(key=lambda x: x.importance_score, reverse=True)

        return fragments

    def _extract_fragments_heuristic(
        self, conversation: str
    ) -> List[Dict[str, Any]]:
        """
        Fallback: Extract fragments using heuristics (sentence splitting).

        This is a simple fallback when LLM is not available.
        """
        # Split by sentences
        sentences = [s.strip() for s in conversation.split("。") if s.strip()]

        fragments = []
        for sentence in sentences:
            fragments.append(
                {
                    "content": sentence,
                    "type": "fact",  # Default type
                    "suggested_sentiment": "neutral",
                }
            )

        return fragments

    def _enrich_fragment(self, raw_fragment: Dict[str, Any]) -> MemoryFragment:
        """
        Enrich raw fragment with entities, topics, sentiment, and score.

        Args:
            raw_fragment: Raw fragment dict with at least 'content' key

        Returns:
            Enriched MemoryFragment object
        """
        content = raw_fragment.get("content", "")
        fragment_type = raw_fragment.get("type", "fact")

        # Extract entities and topics
        entities = self.entity_extractor.extract(content)
        topics = self.topic_extractor.extract(content)

        # Analyze sentiment
        sentiment_data = self.sentiment_analyzer.extract(content)
        sentiment = sentiment_data.get("sentiment", "neutral")
        sentiment_intensity = sentiment_data.get("intensity", "medium")

        # Calculate importance score
        importance_score = self.scorer.calculate_importance_score(
            content=content,
            sentiment=sentiment,
            entities=entities,
            topics=topics,
            sentiment_intensity=sentiment_intensity,
        )

        # Create MemoryFragment
        fragment = MemoryFragment(
            content=content,
            timestamp=datetime.now(),
            type=fragment_type,
            entities=entities,
            topics=topics,
            sentiment=sentiment,
            importance_score=importance_score,
            confidence=0.8,  # Default confidence
            metadata={"source": "chat"},
        )

        return fragment

    def process_to_json(self, conversation: str, output_file: Optional[str] = None) -> str:
        """
        Process conversation and output JSON string.

        Args:
            conversation: Plain text conversation
            output_file: Optional file path to save JSON

        Returns:
            JSON string of memory fragments
        """
        fragments = self.process(conversation)

        # Convert to JSON
        json_output = json.dumps(
            [json.loads(frag.to_json()) for frag in fragments],
            ensure_ascii=False,
            indent=2,
        )

        # Save to file if specified
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_output)

        return json_output


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.pipeline.memory_pipeline <conversation_file>")
        sys.exit(1)

    conversation_file = sys.argv[1]

    # Read conversation
    with open(conversation_file, "r", encoding="utf-8") as f:
        conversation = f.read()

    # Process
    pipeline = MemoryPipeline(use_llm=True)
    json_output = pipeline.process_to_json(conversation, output_file="output.json")

    print("Extracted memory fragments:")
    print(json_output)


if __name__ == "__main__":
    main()
