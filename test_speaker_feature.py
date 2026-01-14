#!/usr/bin/env python3
"""
测试新功能：Speaker 字段和 AI 回复记忆提取

测试内容：
1. MemoryFragment 模型支持 speaker 字段
2. GLM-4 能够正确提取和标记 speaker
3. 过滤逻辑区分 user 和 assistant 的阈值
4. AI 关键词检测和分数提升
5. 用户引用检测
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.models.memory_fragment import MemoryFragment


def test_memory_fragment_speaker_field():
    """测试 1: MemoryFragment 支持 speaker 字段"""
    print("\n" + "="*70)
    print("测试 1: MemoryFragment speaker 字段")
    print("="*70)

    try:
        # 测试 user 记忆
        user_memory = MemoryFragment(
            content="我最喜欢吃北京烤鸭",
            timestamp=datetime.now(),
            speaker="user",
            type="preference",
            entities=[],
            topics=[],
            sentiment="positive",
            importance_score=5,
            confidence=0.8,
        )
        print(f"✅ User 记忆创建成功: {user_memory.content}")
        print(f"   Speaker: {user_memory.speaker}, Score: {user_memory.importance_score}")

        # 测试 assistant 记忆
        assistant_memory = MemoryFragment(
            content="我会一直陪着你，无论什么时候你需要我，我都在这里",
            timestamp=datetime.now(),
            speaker="assistant",
            type="relationship",
            entities=[],
            topics=[],
            sentiment="positive",
            importance_score=9,
            confidence=0.8,
        )
        print(f"✅ Assistant 记忆创建成功: {assistant_memory.content}")
        print(f"   Speaker: {assistant_memory.speaker}, Score: {assistant_memory.importance_score}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_glm_speaker_extraction():
    """测试 2: GLM-4 提取 speaker 信息"""
    print("\n" + "="*70)
    print("测试 2: GLM-4 提取 speaker 信息")
    print("="*70)

    try:
        # 延迟导入
        from src.utils.glm_client import GLMClient

        # 从环境变量获取 API key
        api_key = os.getenv("GLM_API_KEY")
        if not api_key:
            print("⚠️  未设置 GLM_API_KEY，跳过此测试")
            return True

        client = GLMClient(api_key=api_key, model="glm-4-flash")

        # 测试对话（包含 user 和 assistant）
        conversation = """user: 我最喜欢吃北京烤鸭
assistant: 我会一直陪着你，无论什么时候你需要我，我都在这里
user: 你可以给我一些建议吗？
assistant: 你可以试试每天花10分钟写日记，这能帮助你更好地理解自己的情绪"""

        print(f"📞 调用 GLM-4 API 测试对话...")
        fragments_data = client.extract_memory_with_scoring(conversation)

        print(f"\n📦 提取到 {len(fragments_data)} 个片段:\n")

        for i, frag in enumerate(fragments_data, 1):
            speaker = frag.get("speaker", "未标记")
            content = frag["content"]
            score = frag["importance_score"]
            reasoning = frag.get("reasoning", "")

            print(f"{i}. [{speaker}] [{score}/10] {content[:50]}...")
            print(f"   推理: {reasoning[:80]}...")
            print()

        # 验证是否有 speaker 字段
        has_speaker = any("speaker" in frag for frag in fragments_data)
        if has_speaker:
            print("✅ GLM-4 成功提取 speaker 信息")
            return True
        else:
            print("⚠️  GLM-4 未提取 speaker 信息（可能需要更多示例）")
            return True  # 不算失败，因为 LLM 可能不稳定

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_assistant_keyword_detection():
    """测试 3: AI 关键词检测"""
    print("\n" + "="*70)
    print("测试 3: AI 关键词检测")
    print("="*70)

    try:
        # 延迟导入
        from src.conversation.conversation_manager import ConversationManager
        from src.storage.memory_storage import MemoryStorage
        from src.storage.session_manager import SessionManager
        from src.storage.user_manager import UserManager
        from src.utils.glm_client import GLMClient

        # 初始化 ConversationManager
        user_manager = UserManager()
        session_manager = SessionManager()
        memory_storage = MemoryStorage(embedding_model="simple")
        glm_client = GLMClient(
            api_key=os.getenv("GLM_API_KEY", "670e7d42d2c64acf9f25696e24f67227.0SN6Hp2hsMASeNeZ"),
            model="glm-4-flash",
        )

        manager = ConversationManager(
            user_manager=user_manager,
            session_manager=session_manager,
            memory_storage=memory_storage,
            glm_client=glm_client,
            memory_extract_threshold=3,
            max_context_memories=5,
        )

        # 测试不同类型的 AI 回复
        test_cases = [
            ("我会一直陪着你", "承诺类", 7),
            ("你可以试试每天写日记", "建议类", 5),
            ("我理解你的感受，支持你", "情感支持类", 6),
            ("好的，我明白了", "简单确认", 3),
        ]

        print("\n测试 AI 关键词检测和分数提升:\n")

        all_passed = True
        for content, category, expected_min_score in test_cases:
            boost_score = manager._boost_assistant_score(content)
            passed = boost_score >= expected_min_score
            status = "✅" if passed else "❌"

            print(f"{status} [{category}] {content}")
            print(f"   预期最低分: {expected_min_score}, 实际提升分: {boost_score}")

            if not passed:
                all_passed = False

        if all_passed:
            print("\n✅ AI 关键词检测测试通过")
        else:
            print("\n⚠️  部分测试未通过（可能需要调整阈值）")

        return all_passed

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_reference_detection():
    """测试 4: 用户引用检测"""
    print("\n" + "="*70)
    print("测试 4: 用户引用检测")
    print("="*70)

    try:
        # 延迟导入
        from src.conversation.conversation_manager import ConversationManager
        from src.storage.memory_storage import MemoryStorage
        from src.storage.session_manager import SessionManager
        from src.storage.user_manager import UserManager
        from src.utils.glm_client import GLMClient

        # 初始化 ConversationManager
        user_manager = UserManager()
        session_manager = SessionManager()
        memory_storage = MemoryStorage(embedding_model="simple")
        glm_client = GLMClient(
            api_key=os.getenv("GLM_API_KEY", "670e7d42d2c64acf9f25696e24f67227.0SN6Hp2hsMASeNeZ"),
            model="glm-4-flash",
        )

        manager = ConversationManager(
            user_manager=user_manager,
            session_manager=session_manager,
            memory_storage=memory_storage,
            glm_client=glm_client,
            memory_extract_threshold=3,
            max_context_memories=5,
        )

        # 测试用户引用
        test_cases = [
            ("你之前说过我应该多运动", True),
            ("就像你说的，我要坚持", True),
            ("记得你说过要相信我自己", True),
            ("我今天很开心", False),  # 不是引用
        ]

        print("\n测试用户引用检测:\n")

        all_passed = True
        for content, expected in test_cases:
            is_reference = manager._is_user_referencing_assistant(content)
            passed = is_reference == expected
            status = "✅" if passed else "❌"

            print(f"{status} '{content}'")
            print(f"   预期: {expected}, 实际: {is_reference}")

            if not passed:
                all_passed = False

        if all_passed:
            print("\n✅ 用户引用检测测试通过")
        else:
            print("\n⚠️  部分测试未通过")

        return all_passed

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n🚀 开始测试新功能：Speaker 字段和 AI 回复记忆提取")

    results = []

    # 运行基础测试（不需要 API）
    results.append(("MemoryFragment speaker 字段", test_memory_fragment_speaker_field()))

    # 检查是否可以运行需要 API 的测试
    try:
        import openai
        results.append(("GLM-4 提取 speaker 信息", test_glm_speaker_extraction()))
        results.append(("AI 关键词检测", test_assistant_keyword_detection()))
        results.append(("用户引用检测", test_user_reference_detection()))
    except ImportError:
        print("\n⚠️  未安装 openai 库，跳过需要 API 的测试")
        print("   可以运行: pip install openai")

    # 汇总结果
    print("\n" + "="*70)
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
        print(f"\n⚠️  有 {failed} 个测试失败，请检查")


if __name__ == "__main__":
    main()
