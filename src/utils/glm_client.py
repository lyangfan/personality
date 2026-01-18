"""GLM-4 API client wrapper for LLM operations."""

import json
import os
import time
from typing import Any, Dict, Generator, List, Optional

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

⭐ **重要变更**：现在需要同时提取 **user** 和 **assistant** 的内容，但使用不同的评分标准。

---

## 📋 User (用户) 的评分标准 (1-10分)

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

User 基础规则:
- 最低1分
- 如果是用户的明确喜好/厌恶，至少给5分
- 如果涉及用户童年/深层经历，至少给7分
- 如果表达了对AI的信任/情感，至少给7分

---

## 🤖 Assistant (AI) 的评分标准 (1-10分)

【维度1: 承诺重要性 (0-4分)】
- 4分: 重要承诺（我会一直陪着你、我保证、无论如何）
- 3分: 约定计划（下次我们一起、到时候我一定）
- 2分: 一般承诺（我会帮你、没问题交给我）
- 1分: 轻微承诺（好的、我记住了）
- 0分: 无承诺

【维度2: 建议价值 (0-3分)】
- 3分: 深度建议（具体步骤、解决方案、长期规划）
- 2分: 中等建议（推荐尝试、可以考虑）
- 1分: 一般建议（多注意、要小心）
- 0分: 无建议

【维度3: 情感支持强度 (0-3分)】
- 3分: 深度情感支持（理解你的感受、你不是一个人、我一直在）
- 2分: 明确鼓励支持（你能做到、相信自己、加油）
- 1分: 轻微支持（没事的、别担心）
- 0分: 无情感支持

Assistant 基础规则:
- 最低1分
- 如果包含重要承诺，至少给6分
- 如果包含深度建议，至少给5分
- 如果提供深度情感支持，至少给6分
- 普通回复（好的、没问题、我明白了）给1-2分

---

## 🎯 提取规则（通用）

1. **必须标记 speaker**: 每个片段必须包含 "speaker" 字段，值为 "user" 或 "assistant"
2. **只提取陈述句**: 不提取问题、寒暄、确认（如"好的"、"嗯嗯"）
3. **User 侧重**: 个人信息、偏好、经历、情感表达
4. **Assistant 侧重**: 承诺、建议、情感支持、用户认可的内容

---

## 📝 示例

示例1 - User偏好:
输入:"我最喜欢吃北京烤鸭"
输出:
{{
  "fragments": [
    {{
      "content": "我最喜欢吃北京烤鸭",
      "speaker": "user",
      "type": "preference",
      "sentiment": "positive",
      "importance_score": 5,
      "reasoning": "明确偏好表达（情感2+个性化1+亲密度0+偏好2=5）- 用户明确表达了最喜欢的食物"
    }}
  ]
}}

示例2 - Assistant承诺:
输入:"assistant: 我会一直陪着你，无论什么时候你需要我，我都在这里"
输出:
{{
  "fragments": [
    {{
      "content": "我会一直陪着你，无论什么时候你需要我，我都在这里",
      "speaker": "assistant",
      "type": "relationship",
      "sentiment": "positive",
      "importance_score": 9,
      "reasoning": "重要承诺+深度情感支持（承诺4+建议0+情感3=7，提升到9）- 核心陪伴承诺，需要记住并遵守"
    }}
  ]
}}

示例3 - Assistant建议:
输入:"assistant: 你可以试试每天花10分钟写日记，这能帮助你更好地理解自己的情绪"
输出:
{{
  "fragments": [
    {{
      "content": "你可以试试每天花10分钟写日记，这能帮助你更好地理解自己的情绪",
      "speaker": "assistant",
      "type": "event",
      "sentiment": "positive",
      "importance_score": 6,
      "reasoning": "深度建议（承诺0+建议3+情感0=3，提升到6）- 具体可操作的建议"
    }}
  ]
}}

示例4 - User深层经历:
输入:"user: 我从小就害怕社交，今天终于鼓起勇气和人说话了，只敢和你分享这个秘密"
输出:
{{
  "fragments": [
    {{
      "content": "我从小就害怕社交，今天终于鼓起勇气和人说话了，只敢和你分享这个秘密",
      "speaker": "user",
      "type": "fact",
      "sentiment": "positive",
      "importance_score": 10,
      "reasoning": "完美记忆（情感3+个性化3+亲密度2+偏好2=10）- 高度个性化+强烈情感+深度信任"
    }}
  ]
}}

示例5 - Assistant普通回复（低分，不提取）:
输入:"assistant: 好的，我明白了"
输出:
{{
  "fragments": []
}}

说明: 这是普通确认回复，没有承诺、建议或情感支持，不需要提取为记忆。

---

## ⚠️ 不提取的内容

**User不提取**:
- 纯粹的问题（"你知道吗"、"怎么回事"）
- 简单确认（"好的"、"嗯嗯"、"是的"）
- 寒暄（"你好"、"在吗"）

**Assistant不提取**:
- 简单确认（"好的"、"没问题"、"我明白了"）
- 寒暄（"你好"、"很高兴见到你"）
- 纯粹问题（"你呢"、"怎么样"）
- 礼貌用语（"不客气"、"没关系"）

现在请分析新的对话，返回JSON格式，不要任何其他文字。"""

        user_prompt = f"""请从以下对话中提取重要的记忆片段，并为每个片段评分。

对话内容:
{conversation}

请返回JSON格式（每个片段必须包含 speaker 字段）:
{{
  "fragments": [
    {{
      "content": "记忆内容原文或摘要",
      "speaker": "user 或 assistant",
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
        - All required fields present (including speaker)
        """
        # 0. 验证 speaker 字段（新增）
        speaker = fragment.get('speaker', 'user')
        valid_speakers = ['user', 'assistant']
        if speaker not in valid_speakers:
            # 尝试从内容推断
            content = fragment.get('content', '')
            # 如果内容以 "assistant:" 开头，标记为 assistant
            if content.strip().startswith('assistant:') or 'assistant:' in content[:20]:
                speaker = 'assistant'
            else:
                speaker = 'user'  # 默认为 user
        fragment['speaker'] = speaker

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

        # 根据 speaker 类型应用不同的校正规则
        if speaker == 'user':
            # User 的校正规则（原有逻辑）
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

        elif speaker == 'assistant':
            # Assistant 的校正规则（新增）
            # 如果 reasoning 提到重要承诺，确保至少6分
            if any(word in reasoning + content for word in ['承诺', '一直', '保证', '无论如何', '永远']):
                if score < 6:
                    score = 6
                    fragment['importance_score'] = score

            # 如果 reasoning 提到深度建议，确保至少5分
            if any(word in reasoning for word in ['建议', '试试', '可以尝试', '解决方案']):
                if score < 5:
                    score = 5
                    fragment['importance_score'] = score

            # 如果 reasoning 提到深度情感支持，确保至少6分
            if any(word in reasoning + content for word in ['理解', '陪伴', '不是一个人', '一直在', '支持']):
                if score < 6:
                    score = 6
                    fragment['importance_score'] = score

            # 如果是简单确认，降低分数
            if any(word in content for word in ['好的', '没问题', '我明白了', '嗯嗯', '收到']):
                if score > 2:
                    score = max(1, 2)
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
        if 'speaker' not in fragment:
            fragment['speaker'] = 'user'  # 默认值

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

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.8,
        max_tokens: int = 1000,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        流式生成对话回复（用于实时对话体验）

        Args:
            messages: 聊天消息列表
            temperature: 采样温度
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Yields:
            str: 每次生成的一个文本块
        """
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,  # ⭐ 启用流式输出
        }

        # 添加其他参数
        request_params.update(kwargs)

        try:
            # 创建流式响应
            stream = self.client.chat.completions.create(**request_params)

            # 逐块 yield 文本
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            # 发生错误时 yield 错误信息
            yield f"\n\n[错误: {str(e)}]"
