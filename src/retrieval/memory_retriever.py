"""语义检索器."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from src.models import MemoryFragment
from src.storage.memory_storage import MemoryStorage


@dataclass
class RetrievalConfig:
    """检索配置"""

    top_k: int = 5  # 返回前K个最相关的记忆
    min_importance: int = 5  # 最低重要性分数
    score_threshold: Optional[float] = None  # 相似度阈值（可选）
    boost_recent: bool = True  # 是否提升近期记忆的权重
    boost_importance: bool = True  # 是否提升高分记忆的权重
    diversity_penalty: float = 0.1  # 多样性惩罚（0-1），避免返回过于相似的记忆


class MemoryRetriever:
    """
    记忆检索器 - 基于语义相似度的智能检索

    检索策略：
    1. 语义相似度检索（余弦相似度）
    2. 重要性分数过滤（min_importance）
    3. 混合排序（相似度 + 重要性 + 时间衰减）
    """

    def __init__(
        self, storage: MemoryStorage, config: Optional[RetrievalConfig] = None
    ):
        """
        初始化检索器

        Args:
            storage: 记忆存储实例
            config: 检索配置
        """
        self.storage = storage
        self.config = config or RetrievalConfig()

    def retrieve(
        self,
        user_id: str,
        session_id: str,
        query: str,
        config: Optional[RetrievalConfig] = None,
        role_id: Optional[str] = None,
    ) -> List[Tuple[MemoryFragment, float]]:
        """
        检索相关记忆

        Args:
            user_id: 用户ID
            session_id: 会话ID
            query: 查询文本
            config: 检索配置（可选，覆盖默认配置）
            role_id: 角色ID（可选，如果提供则只检索该角色的记忆）

        Returns:
            List of (MemoryFragment, relevance_score) 元组
        """
        config = config or self.config
        collection = self.storage._get_or_create_collection(user_id, session_id, role_id)

        # 1. 语义检索
        results = collection.query(
            query_texts=[query], n_results=config.top_k * 2
        )  # 多取一些，后续过滤

        if not results["ids"][0]:
            return []

        # 2. 构建候选记忆列表
        candidates = []
        for i, memory_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]

            # 过滤低重要性记忆
            importance = int(metadata.get("importance_score", 1))
            if importance < config.min_importance:
                continue

            # 转换距离为相似度（ChromaDB 默认使用 L2 距离）
            similarity = 1 / (1 + distance)

            # 应用阈值过滤
            if config.score_threshold and similarity < config.score_threshold:
                continue

            candidates.append(
                {
                    "id": memory_id,
                    "content": results["documents"][0][i],
                    "metadata": metadata,
                    "similarity": similarity,
                }
            )

        # 3. 混合排序
        ranked = self._rank_memories(candidates, query, config)

        # 4. 转换为 MemoryFragment 对象
        fragments = []
        for item in ranked[: config.top_k]:
            fragment = self._metadata_to_fragment(item)
            fragments.append((fragment, item["final_score"]))

        return fragments

    def _rank_memories(
        self, candidates: List[dict], query: str, config: RetrievalConfig
    ) -> List[dict]:
        """
        混合排序策略

        排序因子：
        1. 语义相似度（0-1）
        2. 重要性权重（importance_score / 10）
        3. 时间衰减（可选）
        """
        for item in candidates:
            similarity = item["similarity"]
            importance = int(item["metadata"].get("importance_score", 5))
            importance_weight = importance / 10.0

            # 基础分数：相似度 * 0.7 + 重要性 * 0.3
            base_score = similarity * 0.7 + importance_weight * 0.3

            # 提升重要性权重（如果启用）
            if config.boost_importance:
                base_score = similarity * 0.5 + importance_weight * 0.5

            final_score = base_score

            # 时间衰减（可选）
            if config.boost_recent:
                timestamp_str = item["metadata"].get("timestamp", "")
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    days_ago = (datetime.now() - timestamp).days
                    # 衰减因子：7天内无衰减，之后指数衰减
                    if days_ago > 7:
                        decay = 0.95 ** (days_ago - 7)
                        final_score *= decay
                except Exception:
                    pass

            item["final_score"] = final_score

        # 排序
        candidates.sort(key=lambda x: x["final_score"], reverse=True)
        return candidates

    def _metadata_to_fragment(self, item: dict) -> MemoryFragment:
        """将检索结果转换为 MemoryFragment"""
        metadata = item["metadata"]

        return MemoryFragment(
            content=item["content"],
            timestamp=datetime.fromisoformat(metadata["timestamp"]),
            speaker=metadata.get("speaker", "user"),  # ⭐ 添加 speaker 字段
            type=metadata["type"],
            entities=(
                metadata.get("entities", "").split(",")
                if metadata.get("entities")
                else []
            ),
            topics=(
                metadata.get("topics", "").split(",")
                if metadata.get("topics")
                else []
            ),
            sentiment=metadata["sentiment"],
            importance_score=int(metadata["importance_score"]),
            confidence=float(metadata.get("confidence", 0.8)),
            metadata={"retrieved": True},
        )

    def retrieve_by_type(
        self, user_id: str, session_id: str, memory_type: str, top_k: int = 5
    ) -> List[MemoryFragment]:
        """
        按类型检索记忆（元数据过滤）

        Args:
            user_id: 用户ID
            session_id: 会话ID
            memory_type: 记忆类型 (preference/event/fact/relationship)
            top_k: 返回数量

        Returns:
            匹配的记忆列表
        """
        collection = self.storage._get_or_create_collection(user_id, session_id)

        results = collection.get(where={"type": memory_type}, limit=top_k)

        fragments = []
        for i in range(len(results["ids"])):
            metadata = results["metadatas"][i]
            fragment = MemoryFragment(
                content=results["documents"][i],
                timestamp=datetime.fromisoformat(metadata["timestamp"]),
                type=metadata["type"],
                entities=(
                    metadata.get("entities", "").split(",")
                    if metadata.get("entities")
                    else []
                ),
                topics=(
                    metadata.get("topics", "").split(",")
                    if metadata.get("topics")
                    else []
                ),
                sentiment=metadata["sentiment"],
                importance_score=int(metadata["importance_score"]),
                confidence=float(metadata.get("confidence", 0.8)),
            )
            fragments.append(fragment)

        return fragments
