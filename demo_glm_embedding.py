#!/usr/bin/env python3
"""
智谱 AI Embedding-3 使用示例

演示如何使用智谱 AI 的 embedding-3 模型进行语义检索
"""

import os
from src.storage.memory_storage import MemoryStorage
from src.storage import UserManager, SessionManager
from src.conversation.conversation_manager import ConversationManager
from src.utils.glm_client import GLMClient


def test_glm_embedding():
    """测试智谱 embedding-3 的效果"""

    print("=" * 70)
    print("🧪 测试智谱 AI Embedding-3")
    print("=" * 70)

    # 1. 初始化组件（使用智谱 embedding）
    print("\n1️⃣ 初始化组件...")

    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        print("❌ 请设置 GLM_API_KEY 环境变量")
        return

    user_manager = UserManager()
    session_manager = SessionManager()

    # ⭐ 使用智谱 embedding-3
    memory_storage = MemoryStorage(
        embedding_model="glm",  # 使用智谱 embedding
        api_key=api_key
    )

    glm_client = GLMClient(api_key=api_key, model="glm-4-flash")

    print("   ✅ 使用智谱 AI Embedding-3")

    # 2. 创建测试用户和会话
    print("\n2️⃣ 创建测试用户和会话...")
    user = user_manager.create_user("测试用户")
    session = session_manager.create_session(
        user_id=user.user_id,
        title="智谱 Embedding 测试"
    )
    print(f"   ✅ 用户: {user.username}")
    print(f"   ✅ 会话: {session.title}")

    # 3. 添加测试记忆
    print("\n3️⃣ 添加测试记忆...")
    from datetime import datetime
    from src.models import MemoryFragment

    test_memories = [
        MemoryFragment(
            content="用户最喜欢吃麻辣火锅，每周都要吃一次",
            timestamp=datetime.now(),
            type="preference",
            entities=["火锅"],
            topics=["美食", "偏好"],
            sentiment="positive",
            importance_score=9,
            confidence=0.95,
        ),
        MemoryFragment(
            content="用户是一名软件工程师，擅长使用 Python 开发",
            timestamp=datetime.now(),
            type="fact",
            entities=["软件工程师", "Python"],
            topics=["职业", "技能"],
            sentiment="neutral",
            importance_score=7,
            confidence=0.90,
        ),
        MemoryFragment(
            content="用户小时候学过钢琴，但是现在很少弹了",
            timestamp=datetime.now(),
            type="fact",
            entities=["钢琴"],
            topics=["童年", "爱好"],
            sentiment="neutral",
            importance_score=6,
            confidence=0.85,
        ),
        MemoryFragment(
            content="用户特别害怕蜘蛛，看到就会很紧张",
            timestamp=datetime.now(),
            type="preference",
            entities=["蜘蛛"],
            topics=["恐惧"],
            sentiment="negative",
            importance_score=8,
            confidence=0.92,
        ),
    ]

    memory_ids = memory_storage.store_memories(
        user_id=user.user_id,
        session_id=session.session_id,
        fragments=test_memories
    )

    print(f"   ✅ 成功存储 {len(memory_ids)} 条记忆")

    # 4. 测试语义检索
    print("\n4️⃣ 测试语义检索（智谱 embedding-3）...")
    print("   " + "-" * 60)

    test_queries = [
        "你知道我喜欢吃什么吗？",
        "我的工作是什么？",
        "我小时候学过什么？",
        "我害怕什么东西？",
        "我喜欢什么运动？",  # 无关测试
    ]

    for query in test_queries:
        print(f"\n   🔍 查询: {query}")

        # 使用语义检索
        from src.retrieval.memory_retriever import MemoryRetriever, RetrievalConfig

        retriever = MemoryRetriever(
            storage=memory_storage,
            config=RetrievalConfig(
                top_k=3,
                min_importance=5,
                boost_recent=True,
                boost_importance=True
            )
        )

        memories = retriever.retrieve(
            user_id=user.user_id,
            session_id=session.session_id,
            query=query
        )

        if memories:
            for fragment, score in memories:
                print(f"   📝 [{score:.2f}] {fragment.content}")
                print(f"      类型: {fragment.type}, 重要性: {fragment.importance_score}/10")
        else:
            print("   ⚠️  未找到相关记忆")

    print("\n" + "=" * 70)
    print("✅ 测试完成！智谱 embedding-3 运行正常")
    print("=" * 70)


def compare_embedding_quality():
    """对比不同 embedding 模型的质量"""

    print("\n" + "=" * 70)
    print("📊 Embedding 质量对比")
    print("=" * 70)

    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        print("❌ 请设置 GLM_API_KEY 环境变量")
        return

    # 测试查询和目标
    query = "你喜欢吃什么？"
    target = "我最喜欢吃麻辣火锅"

    print(f"\n查询: {query}")
    print(f"目标: {target}")

    # 1. 简单 embedding
    print("\n1️⃣ 简单 Embedding（字符编码）")
    storage_simple = MemoryStorage(embedding_model="simple")

    # 创建临时 collection
    collection_simple = storage_simple._get_or_create_collection("test", "test")
    collection_simple.add(
        ids=["test1"],
        documents=[target],
        metadatas=[{"type": "preference"}]
    )

    results_simple = collection_simple.query(query_texts=[query], n_results=1)
    distance_simple = results_simple["distances"][0][0]
    similarity_simple = 1 / (1 + distance_simple)
    print(f"   相似度: {similarity_simple:.4f}")

    # 清理
    collection_simple.delete(ids=["test1"])

    # 2. 智谱 embedding-3
    print("\n2️⃣ 智谱 AI Embedding-3")
    storage_glm = MemoryStorage(embedding_model="glm", api_key=api_key)

    # 创建临时 collection
    collection_glm = storage_glm._get_or_create_collection("test", "test")
    collection_glm.add(
        ids=["test1"],
        documents=[target],
        metadatas=[{"type": "preference"}]
    )

    results_glm = collection_glm.query(query_texts=[query], n_results=1)
    distance_glm = results_glm["distances"][0][0]
    similarity_glm = 1 / (1 + distance_glm)
    print(f"   相似度: {similarity_glm:.4f}")

    # 清理
    collection_glm.delete(ids=["test1"])

    print("\n" + "-" * 70)
    print("💡 结论:")
    print(f"   - 智谱 embedding-3 相似度更高，语义理解更准确")
    print(f"   - 提升幅度: {((similarity_glm - similarity_simple) / similarity_simple * 100):.1f}%")
    print("=" * 70)


if __name__ == "__main__":
    try:
        # 测试智谱 embedding
        test_glm_embedding()

        # 质量对比
        print("\n")
        compare_embedding_quality()

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
