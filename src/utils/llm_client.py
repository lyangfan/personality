"""OpenAI API client wrapper for LLM operations."""

import json
import os
import time
from typing import Any, Dict, List, Optional

import openai
from openai import OpenAI


class LLMClient:
    """
    Wrapper for OpenAI API with retry logic and structured outputs.

    Uses gpt-4o-mini for cost efficiency.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize LLM client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name to use (default: gpt-4o-mini)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided or set in OPENAI_API_KEY environment variable"
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds

    def call_with_retry(
        self,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Any:
        """
        Call OpenAI API with exponential backoff retry logic.

        Args:
            messages: Chat messages for the API
            response_format: Optional response format (e.g., {"type": "json_object"})
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            API response content
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content

            except openai.RateLimitError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2**attempt)
                    print(f"Rate limit hit, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Max retries exceeded: {e}")

            except openai.APIError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2**attempt)
                    print(f"API error, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Max retries exceeded: {e}")

            except Exception as e:
                raise Exception(f"Unexpected error calling OpenAI API: {e}")

    def extract_entities(self, text: str) -> List[str]:
        """
        Extract entities (people, places, organizations) from text.

        Args:
            text: Input text to analyze

        Returns:
            List of entity names
        """
        prompt = f"""
Extract all important entities from the following text.
Entities include: people, places, organizations, products, etc.

Text: {text}

Return ONLY a JSON array of entity names (strings).
Example: ["Python", "Google", "Alice"]
"""

        response = self.call_with_retry(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        try:
            data = json.loads(response)
            return data.get("entities", [])
        except json.JSONDecodeError:
            # Fallback: try to parse as list directly
            try:
                return json.loads(response)
            except:
                return []

    def extract_topics(self, text: str) -> List[str]:
        """
        Extract topics/themes from text.

        Args:
            text: Input text to analyze

        Returns:
            List of topic names
        """
        prompt = f"""
Extract the main topics or themes discussed in the following text.

Text: {text}

Return ONLY a JSON array of topic names (strings).
Example: ["编程", "技术", "职业发展"]
"""

        response = self.call_with_retry(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        try:
            data = json.loads(response)
            return data.get("topics", [])
        except json.JSONDecodeError:
            try:
                return json.loads(response)
            except:
                return []

    def analyze_sentiment(self, text: str) -> Dict[str, str]:
        """
        Analyze sentiment of text.

        Args:
            text: Input text to analyze

        Returns:
            Dict with 'sentiment' and 'intensity' keys
        """
        prompt = f"""
Analyze the sentiment of the following text.

Text: {text}

Return a JSON object with:
- sentiment: "positive", "neutral", or "negative"
- intensity: "high", "medium", "low", or "none"

Example: {{"sentiment": "positive", "intensity": "medium"}}
"""

        response = self.call_with_retry(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"sentiment": "neutral", "intensity": "none"}

    def extract_memory_fragments(self, conversation: str) -> List[Dict[str, Any]]:
        """
        Extract memory fragments from conversation.

        Args:
            conversation: Plain text conversation

        Returns:
            List of memory fragment dictionaries
        """
        prompt = f"""
Extract important memory fragments from this conversation.
Focus on: user preferences, important events, facts mentioned, relationships.

Conversation:
{conversation}

Return a JSON array of memory fragments. Each fragment should have:
- content: the core memory text (summary)
- type: "preference", "event", "fact", or "relationship"
- suggested_sentiment: "positive", "neutral", or "negative"

Example:
[
  {{
    "content": "用户最喜欢的编程语言是 Python",
    "type": "preference",
    "suggested_sentiment": "positive"
  }}
]
"""

        response = self.call_with_retry(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.5,
        )

        try:
            data = json.loads(response)
            return data.get("fragments", [])
        except json.JSONDecodeError:
            try:
                return json.loads(response)
            except:
                return []

    def assess_task_relevance(self, content: str) -> float:
        """
        Assess if content is related to user goals/tasks (0.0-1.0).

        Args:
            content: Memory content text

        Returns:
            Relevance score between 0.0 and 1.0
        """
        prompt = f"""
Rate how relevant this content is to the user's goals, tasks, or important plans.

Content: {content}

Return a JSON object with:
- relevance: a float from 0.0 to 1.0
- reasoning: brief explanation

Example: {{"relevance": 0.8, "reasoning": "Expresses a clear goal"}}
"""

        response = self.call_with_retry(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        try:
            data = json.loads(response)
            return float(data.get("relevance", 0.5))
        except (json.JSONDecodeError, ValueError):
            return 0.5
