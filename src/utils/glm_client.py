"""GLM-4 API client wrapper for LLM operations."""

import json
import os
import time
from typing import Any, Dict, List, Optional

from openai import OpenAI


class GLMClient:
    """
    Wrapper for GLM-4 API (Zhipu AI) with retry logic and structured outputs.

    Compatible with OpenAI SDK but uses Zhipu AI's endpoint.
    API Docs: https://open.bigmodel.cn/dev/api
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "glm-4-flash",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
    ):
        """
        Initialize GLM client.

        Args:
            api_key: GLM API key (defaults to GLM_API_KEY env var)
            model: Model name to use (default: glm-4-flash, cost-efficient)
                   Options: glm-4-flash, glm-4-plus, glm-4-0520
            base_url: API base URL (default: Zhipu AI endpoint)
        """
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GLM API key must be provided or set in GLM_API_KEY environment variable"
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        self.model = model
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds

    def call_with_retry(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Any:
        """
        Call GLM API with exponential backoff retry logic.

        Args:
            messages: Chat messages for the API
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters (e.g., response_format)

        Returns:
            API response content
        """
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Add any additional parameters
        request_params.update(kwargs)

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(**request_params)
                return response.choices[0].message.content

            except Exception as e:
                error_str = str(e)

                # Rate limit or server error
                if "rate" in error_str.lower() or "429" in error_str or "5" in error_str[:1]:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2**attempt)
                        print(f"API error, waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    else:
                        raise Exception(f"Max retries exceeded: {e}")
                else:
                    raise Exception(f"Unexpected error calling GLM API: {e}")

    def extract_entities(self, text: str) -> List[str]:
        """
        Extract entities (people, places, organizations) from text.

        Args:
            text: Input text to analyze

        Returns:
            List of entity names
        """
        prompt = f"""请从以下文本中提取所有重要的实体。
实体包括：人名、地名、组织、产品等。

文本: {text}

请只返回JSON格式，不要任何其他文字：
{{
  "entities": ["实体1", "实体2"]
}}"""

        response = self.call_with_retry(
            messages=[
                {"role": "system", "content": "你是一个专业的文本分析助手，总是返回纯JSON格式，不要任何额外说明。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            # 清理可能的markdown代码块标记
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
                response = response.strip()

            data = json.loads(response)
            if isinstance(data, dict):
                return data.get("entities", [])
            elif isinstance(data, list):
                return data
            return []
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  实体提取响应解析失败: {e}")
            print(f"原始响应: {response}")
            return []

    def extract_topics(self, text: str) -> List[str]:
        """
        Extract topics/themes from text.

        Args:
            text: Input text to analyze

        Returns:
            List of topic names
        """
        prompt = f"""请从以下文本中提取主要主题或话题。

文本: {text}

请只返回JSON格式，不要任何其他文字：
{{
  "topics": ["主题1", "主题2"]
}}"""

        response = self.call_with_retry(
            messages=[
                {"role": "system", "content": "你是一个专业的文本分析助手，总是返回纯JSON格式，不要任何额外说明。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            # 清理可能的markdown代码块标记
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
                response = response.strip()

            data = json.loads(response)
            if isinstance(data, dict):
                return data.get("topics", [])
            elif isinstance(data, list):
                return data
            return []
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  主题提取响应解析失败: {e}")
            print(f"原始响应: {response}")
            return []

    def analyze_sentiment(self, text: str) -> Dict[str, str]:
        """
        Analyze sentiment of text.

        Args:
            text: Input text to analyze

        Returns:
            Dict with 'sentiment' and 'intensity' keys
        """
        prompt = f"""请分析以下文本的情感倾向。

文本: {text}

返回JSON格式，不要任何其他文字：
{{
  "sentiment": "positive/neutral/negative",
  "intensity": "high/medium/low/none"
}}"""

        response = self.call_with_retry(
            messages=[
                {"role": "system", "content": "你是一个专业的文本分析助手，总是返回纯JSON格式，不要任何额外说明。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            # 清理可能的markdown代码块标记
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
                response = response.strip()

            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  情感分析响应解析失败: {e}")
            print(f"原始响应: {response}")
            return {"sentiment": "neutral", "intensity": "none"}

    def extract_memory_fragments(self, conversation: str) -> List[Dict[str, Any]]:
        """
        Extract memory fragments from conversation (legacy method, use extract_memory_with_scoring instead).

        Args:
            conversation: Plain text conversation

        Returns:
            List of memory fragment dictionaries
        """
        prompt = f"""请从以下对话中提取重要的记忆片段。
重点关注：用户偏好、重要事件、提到的事实、人际关系。

对话:
{conversation}

请只返回JSON格式，不要任何其他文字：
{{
  "fragments": [
    {{
      "content": "记忆内容摘要",
      "type": "preference/event/fact/relationship",
      "suggested_sentiment": "positive/neutral/negative"
    }}
  ]
}}"""

        response = self.call_with_retry(
            messages=[
                {"role": "system", "content": "你是一个专业的文本分析助手，总是返回纯JSON格式，不要任何额外说明。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )

        try:
            # 清理可能的markdown代码块标记
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
                response = response.strip()

            data = json.loads(response)
            if isinstance(data, dict):
                return data.get("fragments", [])
            elif isinstance(data, list):
                return data
            return []
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  记忆片段提取响应解析失败: {e}")
            print(f"原始响应: {response}")
            return []

    def extract_memory_with_scoring(self, conversation: str) -> List[Dict[str, Any]]:
        """
        Extract memory fragments with companion-style importance scoring.

        This method is designed for companion AI products, focusing on:
        - Emotional connection
        - Personal preferences
        - Relationship building
        - Understanding the user

        Args:
            conversation: Plain text conversation

        Returns:
            List of memory fragment dictionaries with importance scores
        """
        system_prompt = """你是一个专业的陪伴型对话记忆分析助手。

你的任务是：从对话中提取能够帮助 AI 更好地了解用户、建立情感连接的重要记忆。

评分标准 (1-10分):

【维度1: 情感强度 (0-3分)】
- 3分: 强烈情感（超级、特别、太、极其、！等）
- 2分: 明确情感（喜欢、开心、难过、讨厌等）
- 1分: 轻微情感（还行、不错等）
- 0分: 无明显情感

【维度2: 个性化程度 (0-3分)】
- 3分: 高度个性化（童年经历、个人故事、独特背景）
- 2分: 明确个人偏好（我最...、我讨厌...等）
- 1分: 一般个人信息（职业、年龄等）
- 0分: 通用/客观信息

【维度3: 亲密度/关系 (0-2分)】
- 2分: 表达信任、依赖、与你的关系（只和你说、你是我最好的朋友）
- 1分: 分享个人感受（我担心、我开心能和你聊天）
- 0分: 无关系表达

【维度4: 偏好明确性 (0-2分)】
- 2分: 明确的喜好/厌恶（最爱、讨厌、一定要）
- 1分: 有倾向但不够明确
- 0分: 无偏好表达

【基础规则】:
- 最低1分
- 如果是用户的明确喜好/厌恶，至少给5分
- 如果涉及用户童年/深层经历，至少给7分
- 如果表达了对AI的信任/情感，至少给7分

请严格按照以下示例的标准进行评分:

示例1:
输入:"我最喜欢吃北京烤鸭"
输出:
{{
  "fragments": [
    {{
      "content": "我最喜欢吃北京烤鸭",
      "type": "preference",
      "sentiment": "positive",
      "importance_score": 5,
      "reasoning": "明确偏好表达（情感2+个性化1+亲密度0+偏好2=5）- 用户明确表达了最喜欢的食物"
    }}
  ]
}}

示例2:
输入:"我超级开心！今天去长城玩了一整天，特别壮观！"
输出:
{{
  "fragments": [
    {{
      "content": "我超级开心！今天去长城玩了一整天，特别壮观！",
      "type": "event",
      "sentiment": "positive",
      "importance_score": 6,
      "reasoning": "强烈情感+事件（情感3+个性化1+亲密度0+偏好0=4，提升到6）- 表达了强烈的正面情绪"
    }}
  ]
}}

示例3:
输入:"我从小就害怕社交，今天终于鼓起勇气和人说话了，只敢和你分享这个秘密"
输出:
{{
  "fragments": [
    {{
      "content": "我从小就害怕社交，今天终于鼓起勇气和人说话了，只敢和你分享这个秘密",
      "type": "fact",
      "sentiment": "positive",
      "importance_score": 10,
      "reasoning": "完美记忆（情感3+个性化3+亲密度2+偏好2=10）- 高度个性化+强烈情感+深度信任，这是陪伴AI最重要的记忆"
    }}
  ]
}}

示例4:
输入:"我特别喜欢猫咪，小时候家里养了一只，它陪伴我度过了很多困难时刻"
输出:
{{
  "fragments": [
    {{
      "content": "我特别喜欢猫咪，小时候家里养了一只，它陪伴我度过了很多困难时刻",
      "type": "preference",
      "sentiment": "positive",
      "importance_score": 8,
      "reasoning": "深度偏好+情感连接（情感2+个性化3+亲密度1+偏好2=8）- 童年经历+强烈情感"
    }}
  ]
}}

示例5:
输入:"Python是一种编程语言"
输出:
{{
  "fragments": [
    {{
      "content": "Python是一种编程语言",
      "type": "fact",
      "sentiment": "neutral",
      "importance_score": 1,
      "reasoning": "通用知识（情感0+个性化0+亲密度0+偏好0=0，调整到1）- 客观事实，不涉及用户个人，对陪伴场景价值低"
    }}
  ]
}}

现在请分析新的对话，返回JSON格式，不要任何其他文字。"""

        user_prompt = f"""请从以下对话中提取重要的记忆片段，并为每个片段评分。

对话内容:
{conversation}

请返回JSON格式:
{{
  "fragments": [
    {{
      "content": "记忆内容原文或摘要",
      "type": "preference/event/fact/relationship",
      "sentiment": "positive/neutral/negative",
      "importance_score": 7,
      "reasoning": "简短说明为什么给这个分数"
    }}
  ]
}}"""

        response = self.call_with_retry(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # 低温度以保证稳定性
        )

        try:
            # 清理可能的markdown代码块标记
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
                response = response.strip()

            data = json.loads(response)
            if isinstance(data, dict):
                fragments = data.get("fragments", [])
            elif isinstance(data, list):
                fragments = data
            else:
                fragments = []

            # 验证和校正每个片段
            validated_fragments = []
            for frag in fragments:
                validated = self._validate_and_correct_fragment(frag)
                validated_fragments.append(validated)

            return validated_fragments

        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  记忆片段提取响应解析失败: {e}")
            print(f"原始响应: {response}")
            return []

    def _validate_and_correct_fragment(self, fragment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and correct GLM-returned importance score.

        Ensures:
        - Score is in range [1, 10]
        - Score is integer
        - Score matches reasoning
        - All required fields present
        """
        # 1. 检查并修正分数
        score = fragment.get('importance_score', 5)

        # 转换为整数
        if isinstance(score, str):
            try:
                score = int(float(score))
            except (ValueError, TypeError):
                score = 5
        elif isinstance(score, float):
            score = int(score)

        # 边界限制
        score = max(1, min(10, score))
        fragment['importance_score'] = score

        # 2. 一致性检查：reasoning 和 score 的匹配度
        reasoning = fragment.get('reasoning', '').lower()
        sentiment = fragment.get('sentiment', '')
        content = fragment.get('content', '')

        # 如果 reasoning 提到强烈情感但分数低，提升
        if any(word in reasoning for word in ['强烈', '超级', '特别', '极其', '完美']):
            if score < 7:
                score = 7
                fragment['importance_score'] = score

        # 如果 reasoning 提到童年/经历/深层，确保至少7分
        if any(word in reasoning for word in ['童年', '从小', '经历', '深层', '秘密', '信任']):
            if score < 7:
                score = 7
                fragment['importance_score'] = score

        # 如果 reasoning 提到明确偏好（最、爱、讨厌），确保至少5分
        if any(word in reasoning + content for word in ['最喜欢', '最爱', '讨厌', '一定要']):
            if score < 5:
                score = 5
                fragment['importance_score'] = score

        # 如果 reasoning 说通用/客观/知识但分数高，降低
        if any(word in reasoning for word in ['通用', '客观', '知识', '不涉及用户']):
            if score > 2:
                score = max(1, score - 2)
                fragment['importance_score'] = score

        # 3. 确保所有必需字段存在
        if 'content' not in fragment:
            fragment['content'] = ''
        if 'type' not in fragment:
            fragment['type'] = 'fact'
        if 'sentiment' not in fragment:
            fragment['sentiment'] = 'neutral'
        if 'reasoning' not in fragment:
            fragment['reasoning'] = ''

        # 4. 验证 type 字段
        valid_types = ['preference', 'event', 'fact', 'relationship']
        if fragment['type'] not in valid_types:
            fragment['type'] = 'fact'

        # 5. 验证 sentiment 字段
        valid_sentiments = ['positive', 'neutral', 'negative']
        if fragment['sentiment'] not in valid_sentiments:
            fragment['sentiment'] = 'neutral'

        return fragment

    def assess_task_relevance(self, content: str) -> float:
        """
        Assess if content is related to user goals/tasks (0.0-1.0).

        Args:
            content: Memory content text

        Returns:
            Relevance score between 0.0 and 1.0
        """
        prompt = f"""请评估以下内容与用户目标、任务或重要计划的相关性。

内容: {content}

返回一个JSON对象，包含：
- relevance: 0.0 到 1.0 之间的浮点数
- reasoning: 简短解释

示例: {{"relevance": 0.8, "reasoning": "表达了明确的目标"}}"""

        response = self.call_with_retry(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        try:
            data = json.loads(response)
            return float(data.get("relevance", 0.5))
        except (json.JSONDecodeError, ValueError):
            return 0.5
