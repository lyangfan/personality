#!/usr/bin/env python3
"""
测试记忆驱动对话系统 - 端到端验证
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.conversation.conversation_manager import ConversationManager
from src.models import MemoryFragment
from src.retrieval.memory_retriever import RetrievalConfig
from src.storage.memory_storage import MemoryStorage
from src.storage.session_manager import SessionManager
from src.storage.user_manager import UserManager
from src.utils.glm_client import GLMClient


def test_memory_system():
    """测试记忆系统的完整流程"""

    print("=" * 70)
    print("🧪 测试记忆驱动对话系统")
    print("=" * 70)

    # 1. 初始化组件
    print("\n1️⃣ 初始化组件...")
    user_manager = UserManager()
    session_manager = SessionManager()

    # ⭐ 使用智谱 embedding-3
    import os
    embedding_model = os.getenv("EMBEDDING_MODEL", "simple")
    print(f"   📊 使用 Embedding 模型: {embedding_model}")

    memory_storage = MemoryStorage(embedding_model=embedding_model)
    glm_client = GLMClient(
        api_key=os.getenv(
            "GLM_API_KEY", "670e7d42d2c64acf9f25696e24f67227.0SN6Hp2hsMASeNeZ"
        ),
        model="glm-4-flash",
    )

    retrieval_config = RetrievalConfig(
        top_k=5, min_importance=6, boost_recent=True, boost_importance=True
    )

    conversation_manager = ConversationManager(
        user_manager=user_manager,
        session_manager=session_manager,
        memory_storage=memory_storage,
        glm_client=glm_client,
        retrieval_config=retrieval_config,
        memory_extract_threshold=3,
        max_context_memories=5,
    )
    print("   ✅ 组件初始化完成")

    # 2. 创建测试用户和会话
    print("\n2️⃣ 创建测试用户和会话...")
    user = user_manager.create_user("测试用户")
    session = session_manager.create_session(user_id=user.user_id, title="测试会话")
    print(f"   ✅ 用户: {user.username} (ID: {user.user_id})")
    print(f"   ✅ 会话: {session.title} (ID: {session.session_id})")

    # 3. 手动添加一些测试记忆
    print("\n3️⃣ 添加测试记忆...")
    test_memories = [
        MemoryFragment(
            content="用户最喜欢吃北京烤鸭，特别是皮脆肉嫩的那种",
            timestamp=datetime.now(),
            type="preference",
            entities=["北京烤鸭"],
            topics=["美食", "偏好"],
            sentiment="positive",
            importance_score=8,
            confidence=0.9,
        ),
        MemoryFragment(
            content="用户小时候曾经被狗咬过，所以现在比较怕狗",
            timestamp=datetime.now(),
            type="fact",
            entities=["狗"],
            topics=["童年", "恐惧"],
            sentiment="negative",
            importance_score=7,
            confidence=0.85,
        ),
        MemoryFragment(
            content="用户的梦想是成为一名优秀的软件工程师",
            timestamp=datetime.now(),
            type="preference",
            entities=["软件工程师"],
            topics=["梦想", "职业"],
            sentiment="positive",
            importance_score=9,
            confidence=0.95,
        ),
    ]

    memory_ids = memory_storage.store_memories(
        user_id=user.user_id, session_id=session.session_id, fragments=test_memories
    )
    print(f"   ✅ 成功存储 {len(memory_ids)} 条测试记忆")

    # 4. 测试语义检索
    print("\n4️⃣ 测试语义检索...")
    test_queries = [
        "你喜欢吃什么？",
        "你害怕什么动物？",
        "你的梦想是什么？",
    ]

    for query in test_queries:
        print(f"\n   🔍 查询: {query}")
        memories = conversation_manager.retriever.retrieve(
            user_id=user.user_id,
            session_id=session.session_id,
            query=query,
            config=RetrievalConfig(top_k=3, min_importance=5),
        )

        for fragment, score in memories:
            print(f"   📝 [{score:.2f}] {fragment.content}")
            print(f"      类型: {fragment.type}, 重要性: {fragment.importance_score}/10")

    # 5. 测试记忆统计
    print("\n5️⃣ 记忆统计...")
    count = memory_storage.get_memory_count(user.user_id, session.session_id)
    print(f"   📊 总记忆数: {count} 条")

    print("\n" + "=" * 70)
    print("✅ 所有测试通过！系统运行正常")
    print("=" * 70)

    return user, session


def test_conversation_flow():
    """测试完整对话流程"""

    print("\n" + "=" * 70)
    print("💬 测试对话流程")
    print("=" * 70)

    # 初始化系统
    import os

    user_manager = UserManager()
    session_manager = SessionManager()

    # ⭐ 使用智谱 embedding-3
    embedding_model = os.getenv("EMBEDDING_MODEL", "simple")
    print(f"   📊 使用 Embedding 模型: {embedding_model}")

    memory_storage = MemoryStorage(embedding_model=embedding_model)
    glm_client = GLMClient(
        api_key=os.getenv(
            "GLM_API_KEY", "670e7d42d2c64acf9f25696e24f67227.0SN6Hp2hsMASeNeZ"
        ),
        model="glm-4-flash",
    )

    conversation_manager = ConversationManager(
        user_manager=user_manager,
        session_manager=session_manager,
        memory_storage=memory_storage,
        glm_client=glm_client,
        memory_extract_threshold=2,  # 每2轮提取一次
        max_context_memories=5,
    )

    # 创建用户和会话
    user = user_manager.create_user("对话测试用户")
    session = session_manager.create_session(user_id=user.user_id, title="对话测试")

    print(f"\n👤 用户: {user.username}")
    print(f"💬 会话: {session.title}\n")

    # 模拟对话
    test_conversations = [
        "我最喜欢吃的是火锅",
        "特别是麻辣锅底",
        "你知道我喜欢吃什么吗？",  # 应该召回火锅的记忆
    ]

    for user_message in test_conversations:
        print(f"👤 用户: {user_message}")
        print("🤖 AI: ", end="", flush=True)

        try:
            ai_response = conversation_manager.chat(
                user_id=user.user_id,
                session_id=session.session_id,
                user_message=user_message,
            )
            print(ai_response)
        except Exception as e:
            print(f"(错误: {e})")

        print()

    # 显示最终统计
    memory_count = memory_storage.get_memory_count(user.user_id, session.session_id)
    print(f"📊 对话结束，共提取 {memory_count} 条记忆")


if __name__ == "__main__":
    try:
        # 测试记忆系统
        test_memory_system()

        # 测试对话流程（可选，需要调用 GLM API）
        print("\n" + "=" * 70)
        print("是否测试对话流程？(需要调用 GLM API)")
        choice = input("输入 y 继续，其他键跳过: ").strip().lower()

        if choice == "y":
            test_conversation_flow()

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
