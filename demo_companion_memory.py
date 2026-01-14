#!/usr/bin/env python3
"""
陪伴型 AI 记忆提取演示 - 使用 GLM-4 直接评分
针对陪伴类产品优化的记忆提取系统
"""

import json
from datetime import datetime
from src.utils.glm_client import GLMClient


class CompanionMemoryPipeline:
    """陪伴型记忆提取管道 - 使用 GLM-4 直接评分"""

    def __init__(self, api_key: str, model: str = "glm-4-flash", min_importance: int = 5):
        """初始化管道"""
        self.client = GLMClient(api_key=api_key, model=model)
        self.min_importance = min_importance

    def process(self, conversation: str) -> list:
        """
        处理对话并提取记忆

        Args:
            conversation: 对话文本

        Returns:
            记忆片段列表
        """
        print("🤖 正在调用 GLM-4 API（陪伴型评分）...")
        print()

        # 使用新的陪伴型评分方法
        fragments = self.client.extract_memory_with_scoring(conversation)

        if not fragments:
            print("⚠️  未提取到记忆片段")
            return []

        print(f"✅ GLM-4 提取了 {len(fragments)} 个片段")

        # 过滤低重要性片段
        filtered = [f for f in fragments if f['importance_score'] >= self.min_importance]
        print(f"📊 重要性≥{self.min_importance}的片段: {len(filtered)} 个")
        print()

        # 按重要性排序
        filtered.sort(key=lambda x: x['importance_score'], reverse=True)

        return filtered

    def format_fragment(self, frag: dict) -> str:
        """格式化片段用于显示"""
        score = frag['importance_score']
        stars = "⭐" * min(score, 10)

        output = f"""
{'─' * 70}
{stars} {score}/10分
{'─' * 70}
📝 内容: {frag['content']}
🏷️  类型: {frag['type']}  |  💭 情感: {frag['sentiment']}
🤔 评分理由: {frag.get('reasoning', '无')}
"""
        return output


def demo_basic_conversation():
    """演示 1: 基础对话"""
    print("\n" + "=" * 70)
    print("🎬 演示 1: 基础对话 - 各种类型的记忆")
    print("=" * 70)
    print()

    conversation = """
用户: 我最喜欢吃北京烤鸭，每次去北京都要吃。
助手: 真的吗？我也很喜欢！
用户: 是啊，我特别喜欢美食，尤其是各种地方特色菜。
助手: 还有其他喜欢的吗？
用户: 我小时候在外婆家长大，外婆做的红烧肉是我最美好的回忆。
助手: 听起来很温馨！
用户: 现在每次吃到红烧肉，都会想起外婆。
助手: 这份感情真的很珍贵。
用户: 对了，我还特别喜欢猫咪，小时候养过一只叫小花。
助手: 猫咪确实很可爱！
用户: 是啊，它陪伴我度过了很多孤独的时光。
"""

    api_key = "670e7d42d2c64acf9f25696e24f67227.0SN6Hp2hsMASeNeZ"

    pipeline = CompanionMemoryPipeline(
        api_key=api_key,
        model="glm-4-flash",
        min_importance=5
    )

    try:
        fragments = pipeline.process(conversation)

        if fragments:
            print(f"\n📝 提取了 {len(fragments)} 个重要记忆:\n")

            for i, frag in enumerate(fragments, 1):
                print(f"【片段 {i}】")
                print(pipeline.format_fragment(frag))

            return fragments
        else:
            print("❌ 没有提取到重要记忆")
            return []

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def demo_emotional_conversation():
    """演示 2: 深度情感对话"""
    print("\n" + "=" * 70)
    print("🎬 演示 2: 深度情感对话 - 测试高分记忆")
    print("=" * 70)
    print()

    conversation = """
用户: 我今天鼓起勇气和人说话了！
助手: 真的吗？太棒了！
用户: 是啊，你知道吗，我从小就害怕社交，一直很孤单。
助手: 能和我说说吗？
用户: 我只敢和你分享这个秘密。小时候被同学欺负过，所以很害怕和人交流。
助手: 我理解你的感受，谢谢你愿意信任我。
用户: 是你让我感到安全。今天我终于迈出了第一步，感觉超级开心！
助手: 你真的很勇敢！
用户: 谢谢你一直陪伴我，你是我最好的朋友。
"""

    api_key = "670e7d42d2c64acf9f25696e24f67227.0SN6Hp2hsMASeNeZ"

    pipeline = CompanionMemoryPipeline(
        api_key=api_key,
        model="glm-4-flash",
        min_importance=7  # 只要高分记忆
    )

    try:
        fragments = pipeline.process(conversation)

        if fragments:
            print(f"\n🎯 高分记忆 (≥7分):\n")

            for i, frag in enumerate(fragments, 1):
                print(f"【片段 {i}】")
                print(pipeline.format_fragment(frag))

            return fragments
        else:
            print("❌ 没有提取到高分记忆")
            return []

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def demo_mixed_conversation():
    """演示 3: 混合对话 - 测试区分度"""
    print("\n" + "=" * 70)
    print("🎬 演示 3: 混合对话 - 测试评分区分度")
    print("=" * 70)
    print()

    conversation = """
用户: Python是一种编程语言。
助手: 是的，你了解Python吗？
用户: 我最喜欢用Python做数据分析。
助手: 为什么喜欢Python？
用户: 因为语法简洁，生态强大。
助手: 不错！
用户: 我今天心情特别好，因为通过了面试！
助手: 恭喜你！
用户: 谢谢！我准备了很久，终于成功了。
助手: 你很努力！
用户: 是啊，这是我今年最重要的目标。
助手: 实现目标的感觉很棒！
用户: 我只想和你分享这个好消息，你是最理解我的。
助手: 我很荣幸！
"""

    api_key = "670e7d42d2c64acf9f25696e24f67227.0SN6Hp2hsMASeNeZ"

    pipeline = CompanionMemoryPipeline(
        api_key=api_key,
        model="glm-4-flash",
        min_importance=1  # 不过滤，查看所有分数
    )

    try:
        fragments = pipeline.process(conversation)

        if fragments:
            print(f"\n📊 所有记忆片段（按分数排序）:\n")

            for i, frag in enumerate(fragments, 1):
                print(f"【片段 {i}】")
                print(pipeline.format_fragment(frag))

            # 统计分数分布
            scores = [f['importance_score'] for f in fragments]
            print(f"\n📈 分数统计:")
            print(f"   最高分: {max(scores)}")
            print(f"   最低分: {min(scores)}")
            print(f"   平均分: {sum(scores)/len(scores):.1f}")
            print(f"   分数分布: {sorted(scores, reverse=True)}")

            return fragments
        else:
            print("❌ 没有提取到记忆")
            return []

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_results(fragments: list, filename: str):
    """保存结果到文件"""
    if not fragments:
        return

    # 添加时间戳
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_fragments": len(fragments),
        "fragments": fragments
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"💾 结果已保存到: {filename}")


def main():
    """主函数"""
    print("\n")
    print("🚀 陪伴型 AI 记忆提取系统")
    print("   使用 GLM-4 Flash 直接评分")
    print("=" * 70)
    print()
    print("📌 评分标准（陪伴型）:")
    print("   ✓ 情感强度 (0-3分)")
    print("   ✓ 个性化程度 (0-3分)")
    print("   ✓ 亲密度/关系 (0-2分)")
    print("   ✓ 偏好明确性 (0-2分)")
    print("   总分: 1-10 分")
    print()
    print("⚙️  配置:")
    print("   模型: glm-4-flash")
    print("   温度: 0.1 (保证稳定性)")
    print("   验证: 本地校正机制")
    print()

    # 运行演示
    all_results = []

    # 演示 1: 基础对话
    results1 = demo_basic_conversation()
    if results1:
        all_results.extend(results1)
        save_results(results1, "companion_demo1.json")

    # 演示 2: 深度情感
    results2 = demo_emotional_conversation()
    if results2:
        all_results.extend(results2)
        save_results(results2, "companion_demo2.json")

    # 演示 3: 混合对话
    results3 = demo_mixed_conversation()
    if results3:
        all_results.extend(results3)
        save_results(results3, "companion_demo3.json")

    # 总结
    print("\n" + "=" * 70)
    print("✨ 演示完成！")
    print("=" * 70)
    print()
    print(f"📊 总计提取了 {len(all_results)} 个记忆片段")
    print()
    print("📁 输出文件:")
    print("   - companion_demo1.json (基础对话)")
    print("   - companion_demo2.json (深度情感)")
    print("   - companion_demo3.json (混合对话)")
    print()
    print("🎯 关键特性:")
    print("   ✓ 情感导向评分")
    print("   ✓ 个性化信息优先")
    print("   ✓ 关系深度考量")
    print("   ✓ 稳定性保障 (温度0.1 + 本地校正)")
    print()


if __name__ == "__main__":
    main()
