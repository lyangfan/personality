"""记忆存储层 - ChromaDB 向量数据库."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from src.models import MemoryFragment


class MemoryStorage:
    """
    记忆存储层 - 基于 ChromaDB 的向量数据库

    设计要点：
    1. Collection 结构：{user_id}_{session_id}_memories
    2. Embedding 策略：使用中文友好的 embedding 模型
    3. 元数据设计：包含 importance_score, type, sentiment 等
    4. 支持按用户/会话隔离
    """

    def __init__(
        self,
        persist_directory: str = "./data/chromadb",
        embedding_model: str = "sentence-transformers",  # 或 "openai", "glm"
        api_key: Optional[str] = None,
    ):
        """
        初始化记忆存储

        Args:
            persist_directory: ChromaDB 持久化目录
            embedding_model: embedding 模型类型
            api_key: API key (如果使用 OpenAI/GLM embeddings)
        """
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # 初始化 ChromaDB 客户端
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # 选择 embedding 函数
        self.embedding_func = self._get_embedding_function(
            embedding_model, api_key
        )

        # Collection 缓存
        self._collections_cache: Dict[str, chromadb.Collection] = {}

    def _get_embedding_function(self, model_type: str, api_key: Optional[str]):
        """获取 embedding 函数"""
        if model_type == "simple":
            # 使用简单的词频统计作为 fallback（不需要下载模型）
            return self._create_simple_embedding_function()
        elif model_type == "sentence-transformers":
            # 推荐使用：免费、本地、中文友好
            try:
                return embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="paraphrase-multilingual-MiniLM-L12-v2", device="cpu"
                )
            except Exception as e:
                print(f"⚠️  无法加载 sentence-transformers，使用简单 embedding: {e}")
                return self._create_simple_embedding_function()
        elif model_type == "openai":
            import os

            key = api_key or os.getenv("OPENAI_API_KEY")
            return embedding_functions.OpenAIEmbeddingFunction(
                api_key=key, model_name="text-embedding-3-small"
            )
        else:
            raise ValueError(f"不支持的 embedding 模型: {model_type}")

    def _create_simple_embedding_function(self):
        """创建简单的 embedding 函数（基于词频）"""

        class SimpleEmbeddingFunction:
            def __init__(self):
                import numpy as np

                self.np = np

            def __call__(self, input):
                # 简单的字符统计作为 embedding（仅用于演示）
                return self._embed_documents(input)

            def _embed_documents(self, texts):
                embeddings = []
                for text in texts:
                    # 使用字符频率统计生成固定长度向量
                    vec = self.np.zeros(512)
                    for i, char in enumerate(text[:512]):
                        vec[i] = ord(char) / 65536.0
                    embeddings.append(vec.tolist())
                return embeddings

            def embed_documents(self, texts):
                return self._embed_documents(texts)

            def embed_query(self, input):
                # input 是一个列表，返回一个 embeddings 列表
                return self._embed_documents(input)

        return SimpleEmbeddingFunction()

    def _get_collection_name(self, user_id: str, session_id: str) -> str:
        """生成 collection 名称"""
        return f"{user_id}_{session_id}_memories"

    def _get_or_create_collection(
        self, user_id: str, session_id: str
    ) -> chromadb.Collection:
        """获取或创建 collection"""
        collection_name = self._get_collection_name(user_id, session_id)

        if collection_name not in self._collections_cache:
            # 检查 collection 是否已存在
            try:
                collection = self.client.get_collection(
                    name=collection_name, embedding_function=self.embedding_func
                )
            except Exception:
                # 不存在则创建
                collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_func,
                    metadata={"user_id": user_id, "session_id": session_id},
                )

            self._collections_cache[collection_name] = collection

        return self._collections_cache[collection_name]

    def store_memory(
        self, user_id: str, session_id: str, fragment: MemoryFragment
    ) -> str:
        """
        存储单个记忆片段

        Args:
            user_id: 用户ID
            session_id: 会话ID
            fragment: 记忆片段

        Returns:
            记忆ID
        """
        collection = self._get_or_create_collection(user_id, session_id)

        # 生成记忆ID
        memory_id = str(uuid.uuid4())

        # 准备元数据
        metadata = {
            "importance_score": fragment.importance_score,
            "type": fragment.type,
            "sentiment": fragment.sentiment,
            "timestamp": fragment.timestamp.isoformat(),
            "confidence": fragment.confidence,
            "entities": ",".join(fragment.entities),
            "topics": ",".join(fragment.topics),
        }

        # 存入 ChromaDB
        collection.add(
            ids=[memory_id], documents=[fragment.content], metadatas=[metadata]
        )

        return memory_id

    def store_memories(
        self, user_id: str, session_id: str, fragments: List[MemoryFragment]
    ) -> List[str]:
        """批量存储记忆片段"""
        collection = self._get_or_create_collection(user_id, session_id)

        memory_ids = [str(uuid.uuid4()) for _ in fragments]

        documents = [f.content for f in fragments]
        metadatas = [
            {
                "importance_score": f.importance_score,
                "type": f.type,
                "sentiment": f.sentiment,
                "timestamp": f.timestamp.isoformat(),
                "confidence": f.confidence,
                "entities": ",".join(f.entities),
                "topics": ",".join(f.topics),
            }
            for f in fragments
        ]

        collection.add(ids=memory_ids, documents=documents, metadatas=metadatas)

        return memory_ids

    def get_memory_count(self, user_id: str, session_id: str) -> int:
        """获取记忆数量"""
        collection = self._get_or_create_collection(user_id, session_id)
        return collection.count()

    def delete_collection(self, user_id: str, session_id: str):
        """删除会话的所有记忆"""
        collection_name = self._get_collection_name(user_id, session_id)
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self._collections_cache:
                del self._collections_cache[collection_name]
        except Exception:
            pass
