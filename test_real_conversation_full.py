#!/usr/bin/env python3
"""
真实场景测试 - 完整对话流程

模拟真实对话场景：
1. 用户输入真实消息
2. AI 由 GLM-4 生成回复（不是硬编码）
3. 每 3 轮自动提取记忆（区分 user 和 assistant）
4. 测试记忆检索和个性化回复
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.conversation.conversation_manager import ConversationManager
from src.retrieval.memory_retriever import RetrievalConfig
from src.storage.memory_storage import MemoryStorage
from src.storage.session_manager import SessionManager
from src.storage.user_manager import UserManager
from src.utils.glm_client import GLMClient


def test_real_conversation_scenario():
    """测试真实对话场景"""
    print("\n" + "="*70)
    print("🎭 真实场景测试 - 完整对话流程")
    print("="*70)

    try:
        # 初始化组件
        print("\n📦 初始化系统组件...")
        user_manager = UserManager()
        session_manager = SessionManager()
        memory_storage = MemoryStorage(embedding_model="simple")

        # 使用 GLM API（从环境变量或默认）
        api_key = os.getenv("GLM_API_KEY", "670e7d42d2c64acf9f25696e24f67227.0SN6Hp2hsMASeNeZ")
        glm_client = GLMClient(api_key=api_key, model="glm-4-flash")

        # 配置检索策略
        retrieval_config = RetrievalConfig(
            top_k=5,
            min_importance=5,  # 检索5分以上的记忆
            boost_recent=True,
            boost_importance=True
        )

        conversation_manager = ConversationManager(
            user_manager=user_manager,
            session_manager=session_manager,
            memory_storage=memory_storage,
            glm_client=glm_client,
            retrieval_config=retrieval_config,
            memory_extract_threshold=3,  # 每3轮提取一次
            max_context_memories=5,
        )

        print("✅ 系统初始化完成\n")

        # 创建测试用户和会话
        user = user_manager.create_user("测试用户小王")
        session = session_manager.create_session(
            user_id=user.user_id,
            title="真实场景测试对话"
        )

        print(f"👤 用户: {user.username} (ID: {user.user_id})")
        print(f"💬 会话: {session.title} (ID: {session.session_id})\n")

        # 模拟真实对话（6轮，会触发2次记忆提取）
        test_conversations = [
            "我叫小王，是一名软件工程师",
            "我最近工作压力很大，经常加班到很晚",
            "我从小就很怕孤独，现在一个人在北京打拼",
            # 第3轮后会触发记忆提取
            "你之前说过要一直陪着我对吧？",  # 测试用户引用
            "我有时候会怀疑自己的能力，不知道该怎么办",
            "我特别喜欢猫咪，小时候家里养过一只",
            # 第6轮后会触发记忆提取
        ]

        print("="*70)
        print("🎬 开始对话（每3轮提取一次记忆）")
        print("="*70 + "\n")

        for i, user_message in enumerate(test_conversations, 1):
            print(f"\n{'='*70}")
            print(f"第 {i} 轮对话")
            print(f"{'='*70}")

            # 用户说话
            print(f"\n👤 用户: {user_message}")

            # AI 生成回复（使用 GLM-4）
            print("\n🤖 AI 正在思考...")
            ai_response = conversation_manager.chat(
                user_id=user.user_id,
                session_id=session.session_id,
                user_message=user_message
            )

            print(f"\n🤖 AI: {ai_response}")

            # 检查是否刚刚进行了记忆提取
            if i % 3 == 0:
                print(f"\n📊 [第 {i} 轮] 已触发记忆提取")

        # 显示最终记忆统计
        print("\n" + "="*70)
        print("📊 对话结束 - 记忆统计")
        print("="*70)

        memory_count = memory_storage.get_memory_count(
            user_id=user.user_id,
            session_id=session.session_id
        )

        print(f"\n总记忆数: {memory_count} 条")
        print(f"总对话轮数: {len(test_conversations)} 轮\n")

        # 检索所有记忆查看详情
        print("="*70)
        print("📋 所有记忆详情")
        print("="*70 + "\n")

        # 注意：这里我们无法直接获取所有记忆，但可以通过检索显示
        # 让我们检索一些相关记忆
        test_queries = [
            "用户身份",
            "用户的压力",
            "AI 的承诺",
            "用户的童年",
            "用户的偏好"
        ]

        for query in test_queries:
            print(f"\n🔍 查询: '{query}'")
            print("-" * 70)

            memories = conversation_manager.retriever.retrieve(
                user_id=user.user_id,
                session_id=session.session_id,
                query=query,
                config=RetrievalConfig(top_k=3, min_importance=0, score_threshold=0)
            )

            if memories:
                for fragment, score in memories:
                    speaker_icon = "👤" if fragment.speaker == "user" else "🤖"
                    print(f"  {speaker_icon} [{fragment.importance_score}/10] {fragment.content}")
                    print(f"      类型: {fragment.type}, 情感: {fragment.speaker}, 相似度: {score:.2f}")
            else:
                print("  （未找到相关记忆）")

        print("\n" + "="*70)
        print("✅ 测试完成")
        print("="*70)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_personalized_response():
    """测试个性化回复（基于记忆）"""
    print("\n" + "="*70)
    print("🎯 测试个性化回复")
    print("="*70)

    try:
        # 初始化组件
        print("\n📦 初始化系统...")
        user_manager = UserManager()
        session_manager = SessionManager()
        memory_storage = MemoryStorage(embedding_model="simple")

        api_key = os.getenv("GLM_API_KEY", "670e7d42d2c64acf9f25696e24f67227.0SN6Hp2hsMASeNeZ")
        glm_client = GLMClient(api_key=api_key, model="glm-4-flash")

        retrieval_config = RetrievalConfig(
            top_k=5,
            min_importance=5,
            boost_recent=True,
            boost_importance=True
        )

        conversation_manager = ConversationManager(
            user_manager=user_manager,
            session_manager=session_manager,
            memory_storage=memory_storage,
            glm_client=glm_client,
            retrieval_config=retrieval_config,
            memory_extract_threshold=2,  # 每2轮提取，加快测试
            max_context_memories=5,
        )

        # 创建用户和会话
        user = user_manager.create_user("测试用户小李")
        session = session_manager.create_session(user_id=user.user_id)

        print(f"✅ 用户: {user.username}\n")

        # 第一阶段：建立记忆
        print("="*70)
        print("📝 第一阶段：建立记忆")
        print("="*70 + "\n")

        initial_memories = [
            "我叫小李，是一名设计师",
            "我最近压力很大，因为项目deadline快到了",
        ]

        for msg in initial_memories:
            print(f"\n👤 用户: {msg}")
            ai_response = conversation_manager.chat(
                user_id=user.user_id,
                session_id=session.session_id,
                user_message=msg
            )
            print(f"🤖 AI: {ai_response}")

        # 触发记忆提取
        print("\n📞 触发记忆提取...")
        conversation_manager._extract_and_store_memories(
            user_id=user.user_id,
            session_id=session.session_id
        )

        # 第二阶段：测试个性化回复
        print("\n" + "="*70)
        print("🎯 第二阶段：测试个性化回复（基于记忆）")
        print("="*70 + "\n")

        test_queries = [
            "我还是很焦虑",
            "你是谁",
            "我该怎么办",  # 测试 AI 是否记得之前的承诺/建议
        ]

        for query in test_queries:
            print(f"\n👤 用户: {query}")
            print(f"\n🤖 AI 正在思考...")

            ai_response = conversation_manager.chat(
                user_id=user.user_id,
                session_id=session.session_id,
                user_message=query
            )

            print(f"\n🤖 AI: {ai_response}\n")

        print("="*70)
        print("✅ 个性化回复测试完成")
        print("="*70)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有真实场景测试"""
    print("\n🚀 开始真实场景测试")

    import openai

    results = []

    # 测试 1: 完整对话流程
    print("\n" + "📍"*35)
    print("测试 1: 完整对话流程")
    print("📍"*35)
    results.append(("完整对话流程", test_real_conversation_scenario()))

    # 测试 2: 个性化回复
    print("\n\n" + "📍"*35)
    print("测试 2: 个性化回复")
    print("📍"*35)
    results.append(("个性化回复", test_personalized_response()))

    # 汇总结果
    print("\n\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n总计: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")


if __name__ == "__main__":
    main()
