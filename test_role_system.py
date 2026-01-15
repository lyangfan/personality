"""
测试角色系统

验证：
1. RoleManager 可以正确加载角色配置
2. 角色可以正确生成 system prompt
3. 角色切换功能正常
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.role import get_role_manager
from src.models.personality import PersonalityProfile


def test_role_manager():
    """测试 RoleManager"""
    print("=" * 60)
    print("测试 1: RoleManager 初始化和角色加载")
    print("=" * 60)

    # 初始化 RoleManager
    role_manager = get_role_manager(config_dir="config/roles", default_role_id="companion_warm")

    # 列出所有可用角色
    roles = role_manager.list_roles()
    print(f"\n✓ 成功加载 {len(roles)} 个角色:")
    for role in roles:
        print(f"  - {role['name']} ({role['id']})")
        print(f"    描述: {role['description']}")
        print(f"    基调: {role['tone']}, 风格: {role['style']}")
        print()

    # 测试获取角色
    print("\n" + "=" * 60)
    print("测试 2: 获取特定角色")
    print("=" * 60)

    # 测试获取 INTJ 角色
    intj_role = role_manager.get_role("intj_prometheus")
    if intj_role:
        print("\n✓ 成功获取 INTJ Prometheus 角色:")
        print(f"  名称: {intj_role.name}")
        print(f"  描述: {intj_role.description}")
        print(f"  核心身份: {intj_role.core_identity[:100]}...")
        print(f"  情感基调: {intj_role.emotional_tone.value}")
        print(f"  回复风格: {intj_role.response_style.value}")
    else:
        print("\n✗ 无法获取 INTJ Prometheus 角色")
        return False

    # 测试获取默认角色
    default_role = role_manager.get_default_role()
    if default_role:
        print(f"\n✓ 成功获取默认角色: {default_role.name}")
    else:
        print("\n✗ 无法获取默认角色")
        return False

    # 测试生成 system prompt
    print("\n" + "=" * 60)
    print("测试 3: 生成 System Prompt")
    print("=" * 60)

    system_prompt = intj_role.build_system_prompt()
    print(f"\n✓ 成功生成 INTJ System Prompt (长度: {len(system_prompt)} 字符)")
    print("\n--- System Prompt 预览 (前 500 字符) ---")
    print(system_prompt[:500])
    print("...\n")

    # 测试温暖型角色的 system prompt
    warm_role = role_manager.get_role("companion_warm")
    if warm_role:
        warm_prompt = warm_role.build_system_prompt()
        print(f"✓ 成功生成温暖型 System Prompt (长度: {len(warm_prompt)} 字符)")
        print("\n--- System Prompt 预览 (前 500 字符) ---")
        print(warm_prompt[:500])
        print("...\n")

    # 测试角色选择器字典
    print("\n" + "=" * 60)
    print("测试 4: 角色选择器")
    print("=" * 60)

    role_choices = role_manager.get_role_choices()
    print("\n✓ 角色选择器字典:")
    for name, id in role_choices.items():
        print(f"  {name} -> {id}")

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = test_role_manager()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
