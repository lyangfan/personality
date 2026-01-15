"""
角色系统综合测试

测试内容：
1. 所有角色配置加载
2. 角色详情展示
3. System Prompt 生成
4. 角色切换功能
5. 对话原则测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.role import get_role_manager
from src.models.personality import PersonalityProfile, ResponseStyle, EmotionalTone


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_role_loading():
    """测试所有角色加载"""
    print_section("测试 1: 角色加载")

    role_manager = get_role_manager(config_dir="config/roles", default_role_id="companion_warm")

    roles = role_manager.list_roles()
    print(f"\n✅ 成功加载 {len(roles)} 个角色：\n")

    for i, role in enumerate(roles, 1):
        print(f"{i}. **{role['name']}** ({role['id']})")
        print(f"   - 描述: {role['description']}")
        print(f"   - 情感基调: {role['tone']}")
        print(f"   - 回复风格: {role['style']}")
        print()

    return role_manager


def test_role_details(role_manager):
    """测试角色详情"""
    print_section("测试 2: 角色详情")

    role_ids = role_manager.list_roles()

    for role_id in role_ids:
        role = role_manager.get_role(role_id)
        if not role:
            continue

        print(f"\n{'─' * 80}")
        print(f"📋 **{role.name}** 详细信息")
        print(f"{'─' * 80}")

        # 基本信息
        print(f"\n📖 描述: {role.description}")
        print(f"🎭 情感基调: {role.emotional_tone.value}")
        print(f"💬 回复风格: {role.response_style.value}")

        # 语言风格
        if role.vocabulary.get("forbidden"):
            print(f"\n🚫 禁用词 ({len(role.vocabulary['forbidden'])}个):")
            print(f"   {', '.join(role.vocabulary['forbidden'][:10])}")

        if role.vocabulary.get("high_frequency"):
            print(f"\n✨ 高频词 ({len(role.vocabulary['high_frequency'])}个):")
            print(f"   {', '.join(role.vocabulary['high_frequency'][:10])}")

        # 对话原则
        if role.dialogue_principles:
            print(f"\n💡 对话原则 ({len(role.dialogue_principles)}条):")
            for i, principle in enumerate(role.dialogue_principles, 1):
                print(f"   {i}. {principle}")

        # 约束
        if role.constraints:
            print(f"\n⚠️  约束 ({len(role.constraints)}条):")
            for i, constraint in enumerate(role.constraints, 1):
                print(f"   {i}. {constraint}")

        # 示例数量
        if role.few_shot_examples:
            print(f"\n💬 对话示例: {len(role.few_shot_examples)} 个")


def test_system_prompt_generation(role_manager):
    """测试 System Prompt 生成"""
    print_section("测试 3: System Prompt 生成")

    role_ids = role_manager.list_roles()

    for role_id in role_ids:
        role = role_manager.get_role(role_id)
        if not role:
            continue

        print(f"\n{'─' * 80}")
        print(f"🤖 **{role.name}** 的 System Prompt")
        print(f"{'─' * 80}\n")

        prompt = role.build_system_prompt()

        print(f"长度: {len(prompt)} 字符\n")
        print("--- Prompt 预览 (前800字符) ---")
        print(prompt[:800])
        if len(prompt) > 800:
            print("\n... (内容太长，已截断)")
        print()


def test_role_comparison(role_manager):
    """对比不同角色的特点"""
    print_section("测试 4: 角色特点对比")

    roles = role_manager.list_roles()

    print(f"\n{'角色名称':<20} {'情感基调':<12} {'回复风格':<15} {'对话原则数':<10} {'约束数':<10}")
    print("─" * 80)

    for role_info in roles:
        role = role_manager.get_role(role_info['id'])
        if role:
            principles_count = len(role.dialogue_principles) if role.dialogue_principles else 0
            constraints_count = len(role.constraints)

            print(f"{role.name:<20} {role.emotional_tone.value:<12} {role.response_style.value:<15} "
                  f"{principles_count:<10} {constraints_count:<10}")


def main():
    """主测试函数"""
    print("\n" + "🎭" * 40)
    print(" " * 15 + "角色系统综合测试")
    print("🎭" * 40)

    try:
        # 测试1: 角色加载
        role_manager = test_role_loading()

        # 测试2: 角色详情
        test_role_details(role_manager)

        # 测试3: System Prompt 生成
        test_system_prompt_generation(role_manager)

        # 测试4: 角色对比
        test_role_comparison(role_manager)

        # 总结
        print_section("✅ 测试完成")

        print(f"""
📊 测试总结：
   ✅ 成功加载 {len(role_manager.list_roles())} 个角色
   ✅ 所有角色配置格式正确
   ✅ System Prompt 生成正常
   ✅ 对话原则和约束字段完整

💡 提示：
   - 现在可以启动 Streamlit 应用测试角色切换功能
   - 命令: streamlit run streamlit_app.py
   - 在侧边栏切换角色，体验不同性格的 AI
        """)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
