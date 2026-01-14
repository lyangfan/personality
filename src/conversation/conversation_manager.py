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

        # 2. 检查是否需要提取记忆
        message_count = len(self._message_buffers.get(session_id, []))
        should_extract = extract_now or (
            message_count % self.memory_extract_threshold == 0
        )

        if should_extract:
            self._extract_and_store_memories(user_id, session_id)

        # 3. 检索相关记忆
        relevant_memories = self.retriever.retrieve(
            user_id=user_id,
            session_id=session_id,
            query=user_message,
            config=RetrievalConfig(
                top_k=self.max_context_memories, min_importance=6
            ),  # 只检索重要记忆
        )

        # 4. 构建带记忆的 Prompt
        prompt = self._build_prompt_with_memories(
            user_message=user_message, memories=relevant_memories
        )

        # 5. 调用 GLM-4 生成回复
        ai_response = self._generate_response(prompt)

        # 6. 存储助手消息到缓冲区
        self._add_message_to_buffer(session_id, "assistant", ai_response)

        # 7. 更新会话统计
        self.session_manager.update_session(
            session_id, message_count=message_count + 2
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
            return

        messages = self._message_buffers[session_id]
        if not messages:
            return

        # 1. 拼接对话文本
        conversation = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in messages]
        )

        # 2. 调用 GLM-4 提取记忆
        try:
            fragments_data = self.glm_client.extract_memory_with_scoring(conversation)

            # 3. 转换为 MemoryFragment 对象
            fragments = []
            for frag_data in fragments_data:
                fragment = MemoryFragment(
                    content=frag_data["content"],
                    timestamp=datetime.now(),
                    type=frag_data["type"],
                    entities=[],  # 可以后续补充
                    topics=[],
                    sentiment=frag_data["sentiment"],
                    importance_score=frag_data["importance_score"],
                    confidence=0.8,
                    metadata={"reasoning": frag_data.get("reasoning", "")},
                )
                fragments.append(fragment)

            # 4. 过滤并存储
            important_fragments = [f for f in fragments if f.importance_score >= 5]
            if important_fragments:
                memory_ids = self.memory_storage.store_memories(
                    user_id=user_id, session_id=session_id, fragments=important_fragments
                )
                print(f"✅ 存储了 {len(memory_ids)} 条记忆")

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
        """

        # 记忆部分
        if memories:
            memory_blocks = []
            for fragment, score in memories:
                memory_blocks.append(
                    f"- {fragment.content} (重要性: {fragment.importance_score}/10, "
                    f"类型: {fragment.type}, 情感: {fragment.sentiment})"
                )

            memories_text = "\n".join(memory_blocks)
        else:
            memories_text = "（这是我们的第一次对话，还没有关于你的记忆）"

        # 构建完整的 Prompt（中文友好、陪伴型优化）
        prompt = f"""你是一个温暖、贴心的陪伴型 AI 助手。

## 关于用户的重要记忆

请仔细阅读以下关于用户的重要记忆，在回复中体现你的理解：

{memories_text}

## 对话原则

1. **情感连接优先**：关注用户的情感状态，给予温暖和支持
2. **个性化回复**：根据记忆中的信息，提供个性化的回应
3. **自然对话**：像朋友一样自然交流，不要刻意提及记忆
4. **尊重边界**：对于敏感话题保持尊重和谨慎
5. **中文表达**：使用自然、温暖的中文表达

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
