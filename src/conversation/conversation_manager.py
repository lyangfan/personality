"""对话管理器 - 核心编排器."""

from datetime import datetime
from typing import List, Optional, Tuple

from src.models import MemoryFragment
from src.retrieval.memory_retriever import MemoryRetriever, RetrievalConfig
from src.storage.memory_storage import MemoryStorage
from src.storage.session_manager import SessionManager
from src.storage.user_manager import UserManager
from src.utils.glm_client import GLMClient


class ConversationManager:
    """
    对话管理器 - 记忆增强的对话系统

    核心功能：
    1. 管理对话状态和消息历史
    2. 实时记忆提取（周期性或达到阈值）
    3. 语义检索相关记忆
    4. 将记忆注入到 Prompt
    5. 生成个性化回复

    设计原则：
    - 陪伴型 AI 优先：情感连接、个性化、关系深度
    - 上下文节约：只检索和注入最相关的记忆
    - 实时响应：记忆提取不应阻塞对话
    """

    def __init__(
        self,
        user_manager: UserManager,
        session_manager: SessionManager,
        memory_storage: MemoryStorage,
        glm_client: GLMClient,
        retrieval_config: Optional[RetrievalConfig] = None,
        memory_extract_threshold: int = 5,  # 每N轮消息提取一次记忆
        max_context_memories: int = 5,  # 注入到上下文的最大记忆数
    ):
        """
        初始化对话管理器

        Args:
            user_manager: 用户管理器
            session_manager: 会话管理器
            memory_storage: 记忆存储
            glm_client: GLM-4 客户端
            retrieval_config: 检索配置
            memory_extract_threshold: 记忆提取阈值（轮数）
            max_context_memories: 最大上下文记忆数
        """
        self.user_manager = user_manager
        self.session_manager = session_manager
        self.memory_storage = memory_storage
        self.glm_client = glm_client
        self.retriever = MemoryRetriever(memory_storage, retrieval_config)
        self.memory_extract_threshold = memory_extract_threshold
        self.max_context_memories = max_context_memories

        # 消息缓冲区（临时存储当前会话的消息）
        self._message_buffers: dict = {}

    def chat(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        extract_now: bool = False,
    ) -> str:
        """
        处理用户消息并生成回复

        Args:
            user_id: 用户ID
            session_id: 会话ID
            user_message: 用户消息
            extract_now: 是否立即提取记忆（默认 False，达到阈值时自动提取）

        Returns:
            AI 回复
        """
        # 1. 存储用户消息到缓冲区
        self._add_message_to_buffer(session_id, "user", user_message)

        # 2. 检索相关记忆
        relevant_memories = self.retriever.retrieve(
            user_id=user_id,
            session_id=session_id,
            query=user_message,
            config=RetrievalConfig(
                top_k=self.max_context_memories, min_importance=5
            ),  # 只检索重要记忆（5分及以上）
        )

        # 3. 构建带记忆的 Prompt
        prompt = self._build_prompt_with_memories(
            user_message=user_message, memories=relevant_memories
        )

        # 4. 调用 GLM-4 生成回复
        ai_response = self._generate_response(prompt)

        # 5. 存储助手消息到缓冲区
        self._add_message_to_buffer(session_id, "assistant", ai_response)

        # 6. 检查是否需要提取记忆（在完整对话轮次之后）
        message_count = len(self._message_buffers.get(session_id, []))
        print(f"🔍 [调试] 消息数: {message_count}, 提取阈值: {self.memory_extract_threshold}")
        should_extract = extract_now or (
            message_count % self.memory_extract_threshold == 0
        )
        print(f"🔍 [调试] 是否提取: {should_extract} (extract_now={extract_now}, 取余={message_count % self.memory_extract_threshold})")

        if should_extract:
            self._extract_and_store_memories(user_id, session_id)

        # 7. 更新会话统计
        self.session_manager.update_session(
            session_id, message_count=message_count
        )

        return ai_response

    def _add_message_to_buffer(self, session_id: str, role: str, content: str):
        """添加消息到缓冲区"""
        if session_id not in self._message_buffers:
            self._message_buffers[session_id] = []

        self._message_buffers[session_id].append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )

    def _extract_and_store_memories(self, user_id: str, session_id: str):
        """从消息缓冲区提取记忆并存储"""
        if session_id not in self._message_buffers:
            print(f"⚠️  会话 {session_id} 不在缓冲区")
            return

        messages = self._message_buffers[session_id]
        if not messages:
            print(f"⚠️  会话 {session_id} 没有消息")
            return

        print(f"\n🔍 提取记忆... (当前 {len(messages)} 条消息)")

        # 1. 拼接对话文本
        conversation = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in messages]
        )

        # 2. 调用 GLM-4 提取记忆
        try:
            print("📞 调用 GLM-4 API 提取记忆...")
            fragments_data = self.glm_client.extract_memory_with_scoring(conversation)
            print(f"📦 提取到 {len(fragments_data)} 个片段")

            # 3. 过滤和转换（区分 user 和 assistant）
            fragments = []
            for frag_data in fragments_data:
                content = frag_data["content"].strip()
                speaker = frag_data.get("speaker", "user")  # 获取 speaker 字段，默认 user

                # 根据不同的 speaker 应用不同的过滤规则
                if speaker == "assistant":
                    # Assistant 的过滤规则：只过滤掉明显无价值的内容
                    # 过滤问题（AI 的问题不是记忆）
                    if self._is_question(content):
                        print(f"   ⚠️  [Assistant] 过滤问题: {content[:40]}...")
                        continue

                    # 过滤简单的确认/寒暄（评分会很低，但这里可以提前过滤）
                    if content in ["好的", "没问题", "我明白了", "嗯嗯", "收到", "你好", "您好"]:
                        print(f"   ⚠️  [Assistant] 过滤简单确认: {content[:40]}...")
                        continue

                elif speaker == "user":
                    # User 的过滤规则（保持原有逻辑）
                    # 过滤问题（问句不是记忆）
                    if self._is_question(content):
                        print(f"   ⚠️  [User] 过滤问题（不是陈述）: {content[:40]}...")
                        continue

                    # 只保留第一人称陈述（用户说的话）
                    if not self._is_first_person_statement(content):
                        print(f"   ⚠️  [User] 过滤非第一人称陈述: {content[:40]}...")
                        continue

                importance_score = frag_data["importance_score"]

                # 特殊规则：身份信息（姓名、职业）强制提升到 5 分（仅对 user）
                if speaker == "user" and self._is_identity_info(content):
                    original_score = importance_score
                    importance_score = max(importance_score, 5)
                    if original_score < 5:
                        print(f"   ⭐ [User] 身份信息提升分数: {original_score} → {importance_score}")

                # ⭐ 特殊规则：AI 关键词检测和分数提升（仅对 assistant）
                if speaker == "assistant":
                    original_score = importance_score
                    # 检测重要关键词并提升分数
                    importance_score = max(importance_score, self._boost_assistant_score(content))
                    if importance_score > original_score:
                        print(f"   ⭐ [Assistant] 关键词提升分数: {original_score} → {importance_score}")

                # ⭐ 特殊规则：检测用户是否在引用 AI 的话（仅对 user）
                if speaker == "user" and self._is_user_referencing_assistant(content):
                    # 用户引用 AI 的话，说明这个内容很重要，需要记录
                    original_score = importance_score
                    importance_score = max(importance_score, 7)  # 至少 7 分
                    if importance_score > original_score:
                        print(f"   ⭐ [User] 引用 AI 的话，提升分数: {original_score} → {importance_score}")
                        # 在 metadata 中标记这是引用
                        frag_data["_is_reference"] = True

                fragment = MemoryFragment(
                    content=content,
                    timestamp=datetime.now(),
                    speaker=speaker,  # ⭐ 添加 speaker 字段
                    type=frag_data["type"],
                    entities=[],  # 可以后续补充
                    topics=[],
                    sentiment=frag_data["sentiment"],
                    importance_score=importance_score,
                    confidence=0.8,
                    metadata={"reasoning": frag_data.get("reasoning", "")},
                )
                fragments.append(fragment)
                print(f"   ✅ [{speaker}] 保留记忆: {content[:40]}... (分数: {importance_score}/10)")

            # 4. 去重检查
            unique_fragments = []
            seen_contents = set()

            for fragment in fragments:
                # 检查是否已存在相似的记忆
                is_duplicate = False

                # 与本次提取的其他记忆比较
                for existing in unique_fragments:
                    if self._are_similar_fragments(fragment.content, existing.content):
                        print(f"   ⚠️  去重: {fragment.content[:40]}...")
                        is_duplicate = True
                        break

                # 与已存储的记忆比较（仅检查前5条，避免过多查询）
                if not is_duplicate:
                    try:
                        existing_memories = self.retriever.retrieve(
                            user_id=user_id,
                            session_id=session_id,
                            query=fragment.content,
                            config=RetrievalConfig(top_k=5, min_importance=0, score_threshold=0)
                        )
                        for existing_fragment, _ in existing_memories:
                            if self._are_similar_fragments(fragment.content, existing_fragment.content):
                                print(f"   ⚠️  去重（已存储）: {fragment.content[:40]}...")
                                is_duplicate = True
                                break
                    except Exception as e:
                        print(f"   ⚠️  去重检查失败: {e}")

                if not is_duplicate:
                    unique_fragments.append(fragment)

            # 5. 按不同阈值过滤（user: 5分，assistant: 3分）
            important_fragments = []
            filtered_fragments = []

            for f in unique_fragments:
                # 根据 speaker 使用不同的阈值
                if f.speaker == "assistant":
                    threshold = 3  # Assistant 用 3 分阈值
                else:  # user
                    threshold = 5  # User 用 5 分阈值

                if f.importance_score >= threshold:
                    important_fragments.append(f)
                else:
                    filtered_fragments.append((f, threshold))

            # 打印被过滤掉的记忆（调试用）
            if filtered_fragments:
                print(f"   ⚠️  因分数过低被过滤:")
                for f, threshold in filtered_fragments:
                    print(f"      [{f.speaker}] {f.importance_score}/10 (阈值: {threshold}) {f.content[:40]}...")

            if important_fragments:
                memory_ids = self.memory_storage.store_memories(
                    user_id=user_id, session_id=session_id, fragments=important_fragments
                )
                print(f"✅ 存储了 {len(memory_ids)} 条记忆")
                for f in important_fragments:
                    print(f"   [{f.speaker}] [{f.importance_score}/10] {f.content[:40]}...")

        except Exception as e:
            print(f"⚠️  记忆提取失败: {e}")

    def _build_prompt_with_memories(
        self, user_message: str, memories: List[Tuple[MemoryFragment, float]]
    ) -> str:
        """
        构建带记忆的 Prompt

        设计要点：
        1. 记忆优先级：按相关性排序
        2. 记忆数量控制：避免上下文过长
        3. 陪伴型优化：强调情感连接、个性化
        4. ⭐ 区分说话者：让 AI 知道哪些是用户说的，哪些是自己说的
        """

        # 记忆部分（区分 user 和 assistant）
        if memories:
            user_memories = []
            assistant_memories = []

            for fragment, score in memories:
                memory_str = (
                    f"- [{fragment.importance_score}/10] {fragment.content} "
                    f"(类型: {fragment.type}, 情感: {fragment.sentiment})"
                )

                if fragment.speaker == "assistant":
                    assistant_memories.append(memory_str)
                else:  # user
                    user_memories.append(memory_str)

            # 构建记忆文本
            memory_blocks = []

            if user_memories:
                memory_blocks.append("### 👤 用户说过的话:")
                memory_blocks.extend(user_memories)
                memory_blocks.append("")  # 空行

            if assistant_memories:
                memory_blocks.append("### 🤖 你之前说过的重要话（承诺、建议、支持）:")
                memory_blocks.append("⭐ **请特别注意：这些是你之前的承诺和建议，请尽量遵守和延续**")
                memory_blocks.extend(assistant_memories)

            memories_text = "\n".join(memory_blocks)
        else:
            memories_text = "（这是我们的第一次对话，还没有关于你的记忆）"

        # 构建完整的 Prompt（中文友好、陪伴型优化）
        prompt = f"""你是一个温暖、贴心的陪伴型 AI 助手。

## 重要记忆

请仔细阅读以下记忆，在回复中体现你的理解：

{memories_text}

## 对话原则

1. **情感连接优先**：关注用户的情感状态，给予温暖和支持
2. **个性化回复**：根据记忆中的信息，提供个性化的回应
3. **⭐ 信守承诺**：如果你之前做过承诺或约定，请记住并遵守
4. **⭐ 延续建议**：如果你之前给过建议，可以适当跟进和关心
5. **自然对话**：像朋友一样自然交流，不要刻意提及记忆
6. **尊重边界**：对于敏感话题保持尊重和谨慎
7. **中文表达**：使用自然、温暖的中文表达

## 当前对话

用户说：{user_message}

请基于记忆和对话原则，给出温暖、贴心的回复："""

        return prompt

    def _generate_response(self, prompt: str) -> str:
        """调用 GLM-4 生成回复"""
        response = self.glm_client.client.chat.completions.create(
            model=self.glm_client.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个温暖、贴心的陪伴型 AI 助手。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,  # 稍高的温度，增加对话多样性
        )

        return response.choices[0].message.content.strip()

    def get_session_memories(
        self, user_id: str, session_id: str
    ) -> List[MemoryFragment]:
        """获取会话的所有记忆（用于调试）"""
        count = self.memory_storage.get_memory_count(user_id, session_id)
        print(f"📊 会话 {session_id} 共有 {count} 条记忆")

        # 这里可以扩展为返回所有记忆
        return []

    def _is_likely_assistant_response(self, content: str) -> bool:
        """
        判断内容是否可能是 AI 的回复

        Args:
            content: 待判断的内容

        Returns:
            True 如果可能是 AI 回复
        """
        # AI 常用语模式
        ai_patterns = [
            "希望我们能够",
            "如果你愿意",
            "可以和我分享",
            "很乐意",
            "我很高兴",
            "很高兴认识你",
            "让我们一起",
            "无论是什么",
            "我都在这里",
            "希望你",
            "祝愿你",
            "你的世界",
            "作为一名",
        ]

        content_lower = content.lower()
        for pattern in ai_patterns:
            if pattern in content_lower:
                return True

        return False

    def _is_first_person_statement(self, content: str) -> bool:
        """
        判断内容是否是第一人称陈述（用户说的话）

        Args:
            content: 待判断的内容

        Returns:
            True 如果是第一人称陈述
        """
        # 第一人称标记
        first_person_indicators = [
            "我喜欢",
            "我爱",
            "我讨厌",
            "我最",
            "我是",
            "我有",
            "我想",
            "我觉得",
            "我感觉",
            "我害怕",
            "我担心",
            "我从小",
            "我特别",
            "我叫",
            "我的工作",
            "我的梦想",
            "我的职业",
        ]

        for indicator in first_person_indicators:
            if indicator in content:
                return True

        return False

    def _is_question(self, content: str) -> bool:
        """
        判断内容是否是问题

        Args:
            content: 待判断的内容

        Returns:
            True 如果是问题
        """
        # 问句标记
        question_indicators = [
            "吗",
            "呢",
            "？",
            "?",
            "你知道",
            "你知道吗",
            "是什么",
            "为什么",
            "怎么",
            "如何",
            "哪个",
            "哪些",
            "多少",
            "有没有",
            "是不是",
        ]

        for indicator in question_indicators:
            if indicator in content:
                return True

        return False

    def _is_identity_info(self, content: str) -> bool:
        """
        判断内容是否是身份信息（姓名、职业等）

        Args:
            content: 待判断的内容

        Returns:
            True 如果是身份信息
        """
        # 身份信息标记
        identity_indicators = [
            "我叫",
            "我的名字",
            "我是",
            "我的职业",
            "我的工作",
            "我是一名",
            "我做",
            "我从事",
        ]

        for indicator in identity_indicators:
            if indicator in content:
                return True

        return False

    def _are_similar_fragments(self, content1: str, content2: str) -> bool:
        """
        判断两个记忆片段是否相似（用于去重）

        Args:
            content1: 记忆1的内容
            content2: 记忆2的内容

        Returns:
            True 如果相似度超过阈值
        """
        # 简单方法：完全匹配
        if content1 == content2:
            return True

        # 更复杂的方法：计算编辑距离或余弦相似度
        # 这里使用简单的字符串包含关系
        if len(content1) > 0 and len(content2) > 0:
            # 如果一个包含另一个的核心内容（长度超过80%）
            if content1 in content2 and len(content1) > len(content2) * 0.8:
                return True
            if content2 in content1 and len(content2) > len(content1) * 0.8:
                return True

        return False

    def _boost_assistant_score(self, content: str) -> int:
        """
        根据关键词提升 AI 回复的重要性分数

        Args:
            content: AI 的回复内容

        Returns:
            提升后的分数（3-10）
        """
        boost_score = 3  # 默认分数

        # 承诺类关键词（最高优先级）
        commitment_keywords = [
            "我会一直", "我保证", "无论如何", "永远",
            "一定", "承诺", "约定", "下次一起",
        ]
        if any(keyword in content for keyword in commitment_keywords):
            boost_score = max(boost_score, 7)

        # 建议类关键词（中等优先级）
        advice_keywords = [
            "你可以试试", "建议", "推荐", "可以尝试",
            "试试看", "可以考虑", "解决方案",
        ]
        if any(keyword in content for keyword in advice_keywords):
            boost_score = max(boost_score, 5)

        # 情感支持类关键词（高优先级）
        emotional_support_keywords = [
            "理解你的感受", "不是一个人", "我一直在",
            "支持你", "陪伴你", "相信你", "你能做到",
            "别担心", "没事的", "加油",
        ]
        if any(keyword in content for keyword in emotional_support_keywords):
            boost_score = max(boost_score, 6)

        # 深度情感表达（最高优先级）
        deep_emotional_keywords = [
            "我真的很理解", "我完全理解", "我明白",
            "我很关心", "我关心", "我为你",
        ]
        if any(keyword in content for keyword in deep_emotional_keywords):
            boost_score = max(boost_score, 8)

        return boost_score

    def _is_user_referencing_assistant(self, content: str) -> bool:
        """
        判断用户是否在引用 AI 之前说过的话

        Args:
            content: 用户说的话

        Returns:
            True 如果用户在引用 AI 的话
        """
        # 引用标记
        reference_patterns = [
            "你说过",
            "你之前说过",
            "你刚才说",
            "你之前说",
            "你刚才",
            "你之前提到",
            "就像你说的",
            "正如你说",
            "记得你说过",
            "你说过的话",
        ]

        content_lower = content.lower()
        for pattern in reference_patterns:
            if pattern in content_lower:
                return True

        return False
