"""
DeepMemory Streamlit MVP

记忆驱动的对话系统 - Web 界面

功能：
- 💬 聊天对话界面
- 🧠 记忆提取和检索
- 📊 记忆统计展示
- 🔄 会话管理
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd

from src.conversation.conversation_manager import ConversationManager
from src.retrieval.memory_retriever import RetrievalConfig
from src.role import RoleManager, get_role_manager
from src.storage.memory_storage import MemoryStorage
from src.storage.session_manager import SessionManager
from src.storage.user_manager import UserManager
from src.utils.glm_client import GLMClient
from src.models.memory_fragment import MemoryFragment


# ==================== 页面配置 ====================

st.set_page_config(
    page_title="DeepMemory - 记忆驱动的对话系统",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================== 初始化 ====================

@st.cache_resource
def initialize_system():
    """初始化系统组件（缓存以提高性能）"""
    # 从环境变量读取配置
    embedding_model = os.getenv("EMBEDDING_MODEL", "simple")

    # 初始化组件
    user_manager = UserManager()
    session_manager = SessionManager()
    memory_storage = MemoryStorage(
        embedding_model=embedding_model,
        embedding_api_key=os.getenv("GLM_EMBEDDING_API_KEY")
    )
    glm_client = GLMClient(
        api_key=os.getenv("GLM_API_KEY"),
        model="glm-4-flash",
    )

    # ⭐ 初始化角色管理器
    role_manager = get_role_manager(
        config_dir="config/roles",
        default_role_id="companion_warm"
    )

    # 配置检索策略
    retrieval_config = RetrievalConfig(
        top_k=5,
        min_importance=5,
        boost_recent=True,
        boost_importance=True
    )

    # 创建对话管理器（传入 role_manager）
    conversation_manager = ConversationManager(
        user_manager=user_manager,
        session_manager=session_manager,
        memory_storage=memory_storage,
        glm_client=glm_client,
        role_manager=role_manager,
        retrieval_config=retrieval_config,
        memory_extract_threshold=3,  # 每3轮提取一次记忆
        max_context_memories=5,
    )

    return {
        "conversation_manager": conversation_manager,
        "user_manager": user_manager,
        "session_manager": session_manager,
        "memory_storage": memory_storage,
        "role_manager": role_manager,
    }


# ==================== 辅助函数 ====================

def get_user_sessions(user_id: str) -> List:
    """获取用户的所有会话"""
    components = st.session_state.components
    return components["session_manager"].list_user_sessions(user_id)


def get_session_memories(user_id: str, session_id: str, limit: int = 20, role_id: Optional[str] = None) -> List[Dict]:
    """获取会话记忆"""
    components = st.session_state.components
    results = components["memory_storage"].query_memories(
        user_id=user_id,
        session_id=session_id,
        n_results=limit,
        role_id=role_id,  # ⭐ 传递 role_id 以正确检索角色的记忆
    )
    return results


def format_memory_fragment(memory: Dict) -> Dict:
    """格式化记忆片段用于显示"""
    return {
        "内容": memory.get("content", "")[:50] + "..." if len(memory.get("content", "")) > 50 else memory.get("content", ""),
        "说话人": memory.get("speaker", "user"),
        "类型": memory.get("type", ""),
        "情感": memory.get("sentiment", ""),
        "重要性": memory.get("importance_score", 0),
        "时间": memory.get("timestamp", "")[:10],
    }


# ==================== 侧边栏 ====================

def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.title("🧠 DeepMemory")
    st.sidebar.markdown("---")

    # ⭐ 角色选择（全局，在用户登录前也可选择）
    components = st.session_state.components
    role_manager = components["role_manager"]

    st.sidebar.subheader("🎭 角色选择")
    available_roles = role_manager.list_roles()

    # 创建角色选择字典
    role_options = {role["name"]: role["id"] for role in available_roles}

    # 显示当前角色
    current_role_id = st.session_state.get("current_role_id", "companion_warm")
    current_role_name = next((r["name"] for r in available_roles if r["id"] == current_role_id), "小暖")

    selected_role_name = st.sidebar.selectbox(
        "选择角色",
        options=list(role_options.keys()),
        index=list(role_options.keys()).index(current_role_name) if current_role_name in role_options else 0,
        key="role_selector"
    )

    selected_role_id = role_options[selected_role_name]

    # 角色切换确认
    if st.session_state.get("current_role_id") != selected_role_id:
        # 检测到角色切换
        if "role_change_confirmed" not in st.session_state:
            st.session_state.role_change_confirmed = False

        if not st.session_state.role_change_confirmed:
            st.sidebar.warning(f"⚠️ 切换到「{selected_role_name}」将创建独立的记忆空间")
            if st.sidebar.button("确认切换", key="confirm_role_change"):
                st.session_state.role_change_confirmed = True
                st.session_state.current_role_id = selected_role_id
                st.session_state.current_role = role_manager.get_role(selected_role_id)
                st.sidebar.success(f"✅ 已切换到 {selected_role_name}")
                st.rerun()
        else:
            st.session_state.current_role_id = selected_role_id
            st.session_state.current_role = role_manager.get_role(selected_role_id)
            st.session_state.role_change_confirmed = False
            st.rerun()

    # 显示当前角色详情
    current_role = role_manager.get_role(st.session_state.get("current_role_id", "companion_warm"))
    if current_role:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📋 角色详情")

        # 角色基本信息
        role_emoji = "🧊" if current_role.emotional_tone.value == "cold" else "🌞"
        tone_text = {
            "cold": "冷酷理性",
            "warm": "温暖陪伴",
            "neutral": "中立客观",
            "enthusiastic": "热情活力"
        }.get(current_role.emotional_tone.value, "未知")

        st.sidebar.caption(f"{role_emoji} **{current_role.name}** ({tone_text})")

        # 展开/收起角色描述
        with st.sidebar.expander("查看完整描述"):
            st.sidebar.write(current_role.description)

        # 显示对话原则
        if current_role.dialogue_principles:
            with st.sidebar.expander("对话原则"):
                for i, principle in enumerate(current_role.dialogue_principles, 1):
                    st.sidebar.write(f"{i}. {principle}")

        # 显示语言风格
        if current_role.vocabulary.get("forbidden") or current_role.vocabulary.get("high_frequency"):
            with st.sidebar.expander("语言风格"):
                if current_role.vocabulary.get("forbidden"):
                    st.sidebar.write("**禁用词**:")
                    st.sidebar.write(", ".join(current_role.vocabulary["forbidden"]))
                if current_role.vocabulary.get("high_frequency"):
                    st.sidebar.write("**高频词**:")
                    st.sidebar.write(", ".join(current_role.vocabulary["high_frequency"]))

        st.sidebar.markdown("---")

    # 用户信息
    if "current_user" not in st.session_state:
        st.sidebar.subheader("👤 用户登录")
        username = st.sidebar.text_input("昵称", placeholder="请输入你的昵称")
        if username and st.sidebar.button("登录", key="login_btn"):
            components = st.session_state.components
            user = components["user_manager"].get_or_create_user(username)
            st.session_state.current_user = user
            st.session_state.current_session = None
            st.session_state.messages = []
            st.rerun()
    else:
        user = st.session_state.current_user
        st.sidebar.subheader(f"👤 {user.username}")
        st.sidebar.caption(f"ID: {user.user_id}")

        # 会话管理
        st.sidebar.markdown("---")
        st.sidebar.subheader("💬 会话")

        sessions = get_user_sessions(user.user_id)

        # 会话选择
        session_options = {f"{s.title} ({s.message_count} 消息)": s for s in sessions}
        session_options["➕ 新建会话"] = None

        selected = st.sidebar.selectbox(
            "选择会话",
            options=list(session_options.keys()),
            key="session_selector"
        )

        if selected == "➕ 新建会话":
            components = st.session_state.components
            new_session = components["session_manager"].create_session(
                user_id=user.user_id,
                title=f"对话-{len(sessions) + 1}"
            )
            st.session_state.current_session = new_session
            st.session_state.messages = []
            st.rerun()
        elif selected and session_options[selected]:
            session = session_options[selected]
            if st.session_state.get("current_session") != session:
                st.session_state.current_session = session
                st.session_state.messages = []
                st.rerun()

        # 退出登录
        if st.sidebar.button("退出登录", key="logout_btn"):
            for key in ["current_user", "current_session", "messages"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # 系统信息
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ 系统信息")

    embedding_model = os.getenv("EMBEDDING_MODEL", "simple")
    embedding_display = "智谱 Embedding-3" if embedding_model == "glm" else "简单 Embedding"

    st.sidebar.caption(f"🧠 Embedding: {embedding_display}")
    st.sidebar.caption(f"🔧 提取阈值: 每 3 轮")
    st.sidebar.caption(f"📊 最大记忆: 5 条")
    st.sidebar.caption(f"🎭 当前角色: {selected_role_name}")


# ==================== 主聊天界面 ====================

def render_chat():
    """渲染聊天界面"""
    st.title("💬 对话")

    # 检查登录状态
    if "current_user" not in st.session_state or "current_session" not in st.session_state:
        st.info("👈 请先在侧边栏登录")
        return

    user = st.session_state.current_user
    session = st.session_state.current_session
    components = st.session_state.components

    # 显示会话和角色信息
    current_role_id = st.session_state.get("current_role_id", "companion_warm")
    current_role = components["role_manager"].get_role(current_role_id)

    if current_role:
        role_emoji = "🧊" if current_role.emotional_tone.value == "cold" else "🌞"
        st.caption(f"📁 会话: {session.title} | 💬 消息数: {session.message_count} | {role_emoji} 角色: {current_role.name}")
    else:
        st.caption(f"📁 会话: {session.title} | 💬 消息数: {session.message_count}")

    # 初始化消息历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示聊天历史
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 聊天输入
    if prompt := st.chat_input("输入你的消息..."):
        # 显示用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # ⭐ 流式生成 AI 回复（使用当前角色）
        current_role_id = st.session_state.get("current_role_id", "companion_warm")

        try:
            # 创建 AI 消息占位符
            with chat_container:
                with st.chat_message("assistant"):
                    # 使用 st.write_stream 实时显示流式输出
                    response_container = st.empty()
                    full_response = ""

                    # 逐块显示
                    for chunk in components["conversation_manager"].chat_stream(
                        user_id=user.user_id,
                        session_id=session.session_id,
                        user_message=prompt,
                        role_id=current_role_id,
                    ):
                        full_response += chunk
                        response_container.markdown(full_response + "▌")  # 添加光标效果

                    # 移除光标，显示最终回复
                    response_container.markdown(full_response)

            # 保存完整回复到历史
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # 更新会话信息
            session = components["session_manager"].get_session(session.session_id)
            st.session_state.current_session = session

            # 显示记忆提取提示
            if session.message_count % 3 == 0:
                st.success("✅ 已自动提取记忆")

        except Exception as e:
            st.error(f"❌ 发生错误: {str(e)}")


# ==================== 记忆展示界面 ====================

def render_memories():
    """渲染记忆展示界面"""
    st.title("🧠 记忆")

    # 检查登录状态
    if "current_user" not in st.session_state or "current_session" not in st.session_state:
        st.info("👈 请先在侧边栏登录并选择会话")
        return

    user = st.session_state.current_user
    session = st.session_state.current_session
    components = st.session_state.components

    # 显示会话和角色信息
    current_role_id = st.session_state.get("current_role_id", "companion_warm")
    current_role = components["role_manager"].get_role(current_role_id)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.caption(f"📁 会话: {session.title}")
    with col2:
        if current_role:
            st.caption(f"🎭 当前角色: {current_role.name}")
    with col3:
        # 添加清空记忆按钮
        if st.button("🗑️ 清空记忆", key="clear_memories_btn"):
            components["memory_storage"].delete_collection(
                user_id=user.user_id,
                session_id=session.session_id,
                role_id=current_role_id
            )
            st.success("✅ 已清空当前角色的记忆")
            st.rerun()

    # 显示角色描述
    if current_role:
        st.info(f"📖 {current_role.description}")

    st.markdown("---")

    # 获取记忆（⭐ 使用当前角色的记忆）
    with st.spinner("📊 加载记忆..."):
        memories = get_session_memories(user.user_id, session.session_id, role_id=current_role_id)

    if not memories:
        st.info("📭 当前角色的记忆为空")
        return

    # 统计信息
    col1, col2, col3, col4, col5 = st.columns(5)

    user_memories = [m for m in memories if m.get("speaker") == "user"]
    ai_memories = [m for m in memories if m.get("speaker") == "assistant"]
    high_importance = [m for m in memories if m.get("importance_score", 0) >= 7]

    with col1:
        st.metric("总记忆数", len(memories))
    with col2:
        st.metric("用户记忆", len(user_memories))
    with col3:
        st.metric("AI 记忆", len(ai_memories))
    with col4:
        st.metric("高重要性", len(high_importance))
    with col5:
        role_emoji = "🧊" if current_role and current_role.emotional_tone.value == "cold" else "🌞"
        st.metric("角色类型", role_emoji, help=f"{'冷酷理性' if current_role and current_role.emotional_tone.value == 'cold' else '温暖陪伴'}")

    st.markdown("---")

    # 记忆筛选
    col1, col2 = st.columns(2)

    with col1:
        speaker_filter = st.selectbox(
            "筛选说话人",
            options=["全部", "用户", "AI"],
            key="speaker_filter"
        )

    with col2:
        min_importance = st.slider(
            "最低重要性",
            min_value=1,
            max_value=10,
            value=5,
            key="importance_filter"
        )

    # 应用筛选
    filtered_memories = []
    for memory in memories:
        # 说话人筛选
        if speaker_filter == "用户" and memory.get("speaker") != "user":
            continue
        if speaker_filter == "AI" and memory.get("speaker") != "assistant":
            continue

        # 重要性筛选
        if memory.get("importance_score", 0) < min_importance:
            continue

        filtered_memories.append(memory)

    # 显示记忆
    if not filtered_memories:
        st.info("📭 没有符合条件的记忆")
        return

    st.subheader(f"📋 记忆列表 ({len(filtered_memories)} 条)")

    for i, memory in enumerate(filtered_memories, 1):
        with st.expander(
            f"{i}. [{memory.get('speaker', 'user').upper()}] {memory.get('content', '')[:60]}... "
            f"(重要性: {memory.get('importance_score', 0)}/10)"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**说话人:** {memory.get('speaker', 'user')}")
                st.write(f"**类型:** {memory.get('type', '')}")
                st.write(f"**情感:** {memory.get('sentiment', '')}")

            with col2:
                st.write(f"**重要性:** {memory.get('importance_score', 0)}/10")
                st.write(f"**时间:** {memory.get('timestamp', '')[:10]}")

            st.markdown("**内容:**")
            st.write(memory.get('content', ''))


# ==================== 设置界面 ====================

def render_settings():
    """渲染设置界面"""
    st.title("⚙️ 设置")

    st.subheader("📊 系统配置")

    # 显示当前配置
    embedding_model = os.getenv("EMBEDDING_MODEL", "simple")
    embedding_display = "智谱 Embedding-3" if embedding_model == "glm" else "简单 Embedding"

    st.info(f"""
    **当前配置:**
    - 🧠 Embedding 模型: {embedding_display}
    - 🔧 记忆提取阈值: 每 3 轮
    - 📊 最大上下文记忆: 5 条
    - 🎯 检索策略: 语义相似度 + 重要性提升
    """)

    st.markdown("---")

    st.subheader("📖 使用说明")

    st.markdown("""
    ### 💬 对话
    - 在侧边栏登录或创建新用户
    - 选择或创建会话
    - 开始对话，AI 会自动提取记忆

    ### 🧠 记忆
    - 每隔 3 轮对话自动提取一次记忆
    - AI 会记住用户说的话（评分 ≥ 5）
    - AI 会记住自己说的话（承诺、建议、情感支持）
    - 基于语义相似度检索相关记忆

    ### ⭐ 记忆评分标准
    - **用户记忆（5分阈值）:**
      - 身份信息（姓名、职业）→ 5分
      - 个人偏好和梦想 → 6-8分
      - 童年回忆和情感经历 → 7-9分

    - **AI 记忆（3分阈值）:**
      - 承诺和约定 → 7分
      - 具体建议 → 5分
      - 情感支持 → 6分

    ### 🔒 隐私
    - 所有数据存储在本地
    - 向量数据库: `./data/chromadb/`
    - 用户数据: `./data/users/`
    - 会话数据: `./data/sessions/`
    """)


# ==================== 主应用 ====================

def main():
    """主应用"""
    # 初始化组件
    if "components" not in st.session_state:
        with st.spinner("🚀 正在初始化系统..."):
            st.session_state.components = initialize_system()

    # 渲染侧边栏
    render_sidebar()

    # 主导航
    tab1, tab2, tab3 = st.tabs(["💬 对话", "🧠 记忆", "⚙️ 设置"])

    with tab1:
        render_chat()

    with tab2:
        render_memories()

    with tab3:
        render_settings()


if __name__ == "__main__":
    main()
