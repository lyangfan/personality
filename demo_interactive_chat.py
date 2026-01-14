#!/usr/bin/env python3
"""
交互式聊天演示 - 记忆增强的陪伴型 AI

功能：
- 多用户支持
- 会话管理
- 实时记忆提取和检索
- 语义相似度搜索
- 漂亮的命令行界面
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


class InteractiveChatDemo:
    """交互式聊天演示"""

    def __init__(self):
        """初始化演示系统"""
        print("🚀 初始化记忆增强聊天系统...")

        # 1. 初始化组件
        self.user_manager = UserManager()
        self.session_manager = SessionManager()
        self.memory_storage = MemoryStorage(
            embedding_model="simple"  # 使用简单 embedding（无需下载模型）
        )
        self.glm_client = GLMClient(
            api_key=os.getenv("GLM_API_KEY", "670e7d42d2c64acf9f25696e24f67227.0SN6Hp2hsMASeNeZ"),
            model="glm-4-flash",
        )

        # 2. 配置检索策略
        retrieval_config = RetrievalConfig(
            top_k=5, min_importance=6, boost_recent=True, boost_importance=True
        )

        self.conversation_manager = ConversationManager(
            user_manager=self.user_manager,
            session_manager=self.session_manager,
            memory_storage=self.memory_storage,
            glm_client=self.glm_client,
            retrieval_config=retrieval_config,
            memory_extract_threshold=3,  # 每3轮提取一次记忆
            max_context_memories=5,
        )

        # 当前用户和会话
        self.current_user = None
        self.current_session = None

        print("✅ 系统初始化完成\n")

    def show_welcome(self):
        """显示欢迎信息"""
        print("=" * 70)
        print("🤖 记忆增强的陪伴型 AI - 交互式演示")
        print("=" * 70)
        print()
        print("🎯 特色功能：")
        print("  ✓ 智能记忆提取（GLM-4 陪伴型评分）")
        print("  ✓ 语义相似度检索")
        print("  ✓ 个性化回复（基于历史记忆）")
        print("  ✓ 上下文节约（只检索最相关记忆）")
        print()
        print("📌 技术栈：")
        print("  - 记忆存储：ChromaDB 向量数据库")
        print("  - 语义检索：SentenceTransformer (中文友好)")
        print("  - 对话模型：GLM-4 Flash")
        print()
        print("=" * 70)
        print()

    def login_or_register(self):
        """用户登录/注册"""
        while True:
            username = input("请输入你的昵称（新建用户直接输入）: ").strip()
            if username:
                break

        # 获取或创建用户
        self.current_user = self.user_manager.get_or_create_user(username)

        print(f"\n👋 欢迎, {self.current_user.username}!")
        print(f"   用户ID: {self.current_user.user_id}")

        # 显示历史会话
        sessions = self.session_manager.list_user_sessions(
            self.current_user.user_id
        )
        if sessions:
            print(f"\n📚 历史会话 ({len(sessions)} 个):")
            for i, session in enumerate(sessions, 1):
                print(f"   {i}. {session.title} ({session.message_count} 条消息)")

            choice = input(
                "\n选择会话（输入数字）或创建新会话（直接回车）: "
            ).strip()

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(sessions):
                    self.current_session = sessions[idx]
                    print(f"\n✅ 已加载会话: {self.current_session.title}")
                    return

        # 创建新会话
        self.current_session = self.session_manager.create_session(
            user_id=self.current_user.user_id,
            title=f"对话-{len(sessions) + 1}",
        )
        print(f"\n✅ 已创建新会话: {self.current_session.title}")

    def show_memory_stats(self):
        """显示记忆统计"""
        memory_count = self.memory_storage.get_memory_count(
            self.current_user.user_id, self.current_session.session_id
        )

        print(f"\n📊 当前会话记忆统计:")
        print(f"   记忆总数: {memory_count} 条")
        print(f"   消息轮数: {self.current_session.message_count} 轮")

    def chat_loop(self):
        """主聊天循环"""
        print("\n" + "=" * 70)
        print("💬 开始对话（输入 '/quit' 退出，'/stats' 查看统计）")
        print("=" * 70 + "\n")

        while True:
            try:
                # 获取用户输入
                user_input = input("你: ").strip()

                # 命令处理
                if user_input == "/quit":
                    print("\n👋 再见！期待下次聊天~")
                    break
                elif user_input == "/stats":
                    self.show_memory_stats()
                    continue
                elif not user_input:
                    print("（请输入消息）")
                    continue

                # 生成回复
                print("\n🤖 AI 正在思考...")
                ai_response = self.conversation_manager.chat(
                    user_id=self.current_user.user_id,
                    session_id=self.current_session.session_id,
                    user_message=user_input,
                )

                print(f"\nAI: {ai_response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 再见！期待下次聊天~")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}\n")
                import traceback

                traceback.print_exc()

    def run(self):
        """运行演示"""
        self.show_welcome()
        self.login_or_register()
        self.chat_loop()


def main():
    """主函数"""
    demo = InteractiveChatDemo()
    demo.run()


if __name__ == "__main__":
    main()
