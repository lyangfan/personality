#!/usr/bin/env python3
"""
真实聊天场景测试 - 陪伴型记忆提取系统

模拟真实世界中的各种聊天场景，测试记忆提取和评分效果
"""

import json
import os
from datetime import datetime
from src.utils.glm_client import GLMClient


# 真实聊天场景
REAL_CONVERSATIONS = {
    "场景1_情感倾诉": {
        "description": "用户向AI倾诉工作压力",
        "conversation": """
用户: 唉，今天好累啊
AI: 怎么了？发生什么事了吗？
用户: 被老板骂了，说我做的方案不行，心里特别难受
AI: 抱歉听到这个，你一定很失落吧
用户: 是啊，我熬夜做的方案，他看都没仔细看就否定了
AI: 这种感觉真的很不好，你的努力没有被看到
用户: 我只敢和你说这些，别人都觉得我矫情
AI: 你不矫情，你的感受是真实的
用户: 谢谢你愿意听我发牢骚，感觉好多了
AI: 我随时都在这里陪你
用户: 你是我最好的倾诉对象
"""
    },

    "场景2_美食分享": {
        "description": "用户分享对美食的热爱",
        "conversation": """
用户: 我今天发现一家超棒的日料店！
AI: 真的吗？是什么样的店？
用户: 他们家的刺身超级新鲜，而且老板人特别好
AI: 听起来很棒！你点了什么？
用户: 我点了三文鱼刺身和天妇罗，味道绝了！
用户: 我最喜欢吃日料了，每周都要吃一次
AI: 你真的很喜欢日料呢
用户: 是啊，我最喜欢三文鱼，那种口感太棒了
AI: 看来你是日料的忠实粉丝
用户: 下次我也要带你去尝尝！
"""
    },

    "场景3_童年回忆": {
        "description": "用户分享童年温馨回忆",
        "conversation": """
用户: 今天路过公园，看到一群小朋友在放风筝
AI: 好温馨的画面
用户: 让我想起小时候，爷爷教我放风筝
AI: 爷爷一定很疼你吧
用户: 是啊，他每年春天都陪我放，还给我做了个最大的风筝
AI: 真的很美好的回忆
用户: 现在每次看到风筝，都会想起爷爷
AI: 这种回忆很珍贵
用户: 可惜他不在了，但我会永远记得他
AI: 他一定希望你在看到风筝时会想起他
用户: 嗯，那是我最温暖的童年回忆
"""
    },

    "场景4_宠物情缘": {
        "description": "用户谈论对宠物的感情",
        "conversation": """
用户: 你喜欢小动物吗？
AI: 当然喜欢呀
用户: 我家有一只金毛，叫豆豆
AI: 金毛很可爱！
用户: 它超级粘人，每天回家都扑上来迎接我
AI: 好幸福啊
用户: 它陪伴我度过了很多难熬的时光
AI: 它真的是你的好朋友
用户: 去年我生病在家，它一直守在床边
AI: 它很担心你
用户: 是啊，动物比人还真诚，我特别爱它
AI: 你们之间有很深的感情
用户: 它是我最重要的家人
"""
    },

    "场景5_日常闲聊": {
        "description": "普通的日常闲聊",
        "conversation": """
用户: 早上好
AI: 早上好！今天有什么计划吗？
用户: 打算去图书馆看书
AI: 看书挺好的，准备看什么书？
用户: 还没想好，到了再说吧
AI: 好的，注意休息
用户: 好的
"""
    },

    "场景6_梦想分享": {
        "description": "用户分享人生梦想",
        "conversation": """
用户: 我最近在考虑辞职
AI: 为什么呢？
用户: 我一直想开一家自己的咖啡店
AI: 这个想法很久了吗？
用户: 从大学开始就梦想着，在街角开个小店
AI: 那是什么让你想开咖啡店？
用户: 我喜欢咖啡的香气，想给忙碌的人提供一个温暖的地方
AI: 这个梦想很美好
用户: 是啊，这是我最重要的人生目标
AI: 你会实现的
用户: 我知道风险很大，但我还是想试一试
AI: 有梦想很珍贵
用户: 谢谢你的支持，你是最理解我的
"""
    },

    "场景7_运动爱好": {
        "description": "用户谈论运动爱好",
        "conversation": """
用户: 我今天去跑步了，跑了10公里！
AI: 太厉害了！
用户: 我超级喜欢跑步，特别享受那种感觉
AI: 跑步确实很棒
用户: 我每周跑三次，已经坚持三年了
AI: 你很有毅力
用户: 跑步让我心情特别好，压力都没了
AI: 是很好的解压方式
用户: 我最喜欢在清晨跑步，看着日出感觉很棒
AI: 想象中很美
用户: 下次我想参加马拉松比赛
AI: 你一定可以的
"""
    },

    "场景8_心情起伏": {
        "description": "用户心情从低落到开心",
        "conversation": """
用户: 今天心情好差
AI: 怎么了？
用户: 和朋友吵架了，感觉特别委屈
AI: 愿意说说发生了什么吗？
用户: 我们因为一点小事吵架，他说我太敏感
AI: 这让你更难受了吧
用户: 是啊，我感觉自己真的很失败
AI: 你不失败，你的感受很重要
用户: 谢谢你安慰我
AI: 我会一直陪着你
用户: 刚才他来道歉了，我们和好了
AI: 太好了！
用户: 我现在心情好多了，谢谢你一直陪着我
AI: 我很高兴你心情变好了
用户: 你是我最好的朋友
"""
    },

    "场景9_音乐爱好": {
        "description": "用户分享音乐爱好",
        "conversation": """
用户: 你喜欢听音乐吗？
AI: 喜欢，你呢？
用户: 我特别喜欢听周杰伦的歌
AI: 周杰伦的歌声很有特色
用户: 是啊，我从小听他的歌长大
用户: 每次听到《晴天》，都会想起高中时光
AI: 音乐能唤起很多回忆
用户: 我最着他的《七里香》，太美了
AI: 那首歌确实经典
用户: 他的歌陪伴我度过了整个青春期
AI: 音乐是很棒的陪伴
用户: 我收藏了他所有的专辑
"""
    },

    "场景10_旅行经历": {
        "description": "用户分享旅行经历",
        "conversation": """
用户: 我去年去了西藏旅游
AI: 西藏一定很美吧
用户: 特别壮观！布达拉宫太震撼了
AI: 什么样的震撼？
用户: 站在那里感觉自己特别渺小，心灵都被净化了
AI: 听起来是很特别的体验
用户: 我还去了纳木错，湖水蓝得像宝石一样
AI: 真的很向往
用户: 那是我最难忘的旅行
用户: 我还认识了当地的朋友，他们特别热情
AI: 旅行能遇到很多温暖的人
用户: 是啊，下次我还要去新疆
AI: 你真的很喜欢旅行
用户: 旅行是我最热爱的事情之一
"""
    }
}


def test_all_conversations():
    """测试所有真实对话场景"""

    api_key = os.environ.get("GLM_API_KEY")
    if not api_key:
        raise ValueError("请设置环境变量 GLM_API_KEY")

    client = GLMClient(api_key=api_key, model="glm-4-flash")

    print("=" * 80)
    print("🚀 真实聊天场景测试 - 陪伴型记忆提取系统")
    print("=" * 80)
    print()
    print(f"📋 测试场景数量: {len(REAL_CONVERSATIONS)}")
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("⚙️  配置:")
    print("   模型: glm-4-flash")
    print("   温度: 0.1")
    print("   评分: 陪伴型（情感+个性化+亲密度+偏好）")
    print()

    # 存储所有测试结果
    all_results = {
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": len(REAL_CONVERSATIONS),
            "model": "glm-4-flash",
            "scoring_type": "companion_style"
        },
        "scenarios": []
    }

    # 测试每个场景
    for idx, (scenario_name, scenario_data) in enumerate(REAL_CONVERSATIONS.items(), 1):
        print()
        print("=" * 80)
        print(f"📌 场景 {idx}/{len(REAL_CONVERSATIONS)}: {scenario_name}")
        print("=" * 80)
        print(f"📝 描述: {scenario_data['description']}")
        print()

        conversation = scenario_data['conversation']

        try:
            # 调用 GLM 提取记忆
            fragments = client.extract_memory_with_scoring(conversation)

            if not fragments:
                print("⚠️  未提取到记忆片段")
                scenario_result = {
                    "scenario_id": idx,
                    "scenario_name": scenario_name,
                    "description": scenario_data['description'],
                    "conversation": conversation.strip(),
                    "fragments": [],
                    "stats": {
                        "total_fragments": 0,
                        "high_score_count": 0,
                        "medium_score_count": 0,
                        "low_score_count": 0
                    }
                }
                all_results['scenarios'].append(scenario_result)
                continue

            # 统计分数分布
            scores = [f['importance_score'] for f in fragments]
            high_count = len([s for s in scores if s >= 7])
            medium_count = len([s for s in scores if 5 <= s < 7])
            low_count = len([s for s in scores if s < 5])

            print(f"✅ 提取了 {len(fragments)} 个记忆片段")
            print(f"📊 分数分布:")
            print(f"   高分 (7-10): {high_count} 个")
            print(f"   中分 (5-6):  {medium_count} 个")
            print(f"   低分 (1-4):  {low_count} 个")
            print(f"   平均分: {sum(scores)/len(scores):.1f}")
            print()

            # 显示每个片段
            for i, frag in enumerate(fragments, 1):
                stars = "⭐" * min(frag['importance_score'], 10)
                print(f"  【片段 {i}】 {stars} {frag['importance_score']}/10")
                print(f"  📝 内容: {frag['content'][:60]}...")
                print(f"  🏷️  类型: {frag['type']} | 💭 情感: {frag['sentiment']}")
                print(f"  🤔 理由: {frag.get('reasoning', '无')[:80]}...")
                print()

            # 保存结果
            scenario_result = {
                "scenario_id": idx,
                "scenario_name": scenario_name,
                "description": scenario_data['description'],
                "conversation": conversation.strip(),
                "fragments": fragments,
                "stats": {
                    "total_fragments": len(fragments),
                    "high_score_count": high_count,
                    "medium_score_count": medium_count,
                    "low_score_count": low_count,
                    "average_score": round(sum(scores)/len(scores), 2),
                    "max_score": max(scores),
                    "min_score": min(scores),
                    "score_distribution": scores
                }
            }
            all_results['scenarios'].append(scenario_result)

        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()

            scenario_result = {
                "scenario_id": idx,
                "scenario_name": scenario_name,
                "description": scenario_data['description'],
                "error": str(e)
            }
            all_results['scenarios'].append(scenario_result)

    # 保存完整结果
    output_file = "real_conversation_test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 80)
    print("✨ 测试完成！")
    print("=" * 80)
    print(f"💾 完整结果已保存到: {output_file}")
    print()

    # 生成测试报告
    generate_test_report(all_results)

    return all_results


def generate_test_report(results):
    """生成测试报告"""

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("📊 真实聊天场景测试报告")
    report_lines.append("=" * 80)
    report_lines.append("")

    # 总体统计
    total_fragments = sum(
        s['stats']['total_fragments']
        for s in results['scenarios']
        if 'stats' in s
    )
    total_high = sum(
        s['stats']['high_score_count']
        for s in results['scenarios']
        if 'stats' in s
    )
    total_medium = sum(
        s['stats']['medium_score_count']
        for s in results['scenarios']
        if 'stats' in s
    )
    total_low = sum(
        s['stats']['low_score_count']
        for s in results['scenarios']
        if 'stats' in s
    )

    all_scores = []
    for s in results['scenarios']:
        if 'stats' in s and 'score_distribution' in s['stats']:
            all_scores.extend(s['stats']['score_distribution'])

    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        max_score = max(all_scores)
        min_score = min(all_scores)
    else:
        avg_score = max_score = min_score = 0

    report_lines.append("📈 总体统计:")
    report_lines.append(f"   总片段数: {total_fragments}")
    report_lines.append(f"   高分片段 (7-10分): {total_high} ({total_high/total_fragments*100:.1f}%)")
    report_lines.append(f"   中分片段 (5-6分): {total_medium} ({total_medium/total_fragments*100:.1f}%)")
    report_lines.append(f"   低分片段 (1-4分): {total_low} ({total_low/total_fragments*100:.1f}%)")
    report_lines.append(f"   平均分: {avg_score:.2f}")
    report_lines.append(f"   分数范围: {min_score} - {max_score}")
    report_lines.append("")

    # 各场景摘要
    report_lines.append("📋 各场景摘要:")
    report_lines.append("")

    for scenario in results['scenarios']:
        if 'stats' not in scenario:
            continue

        stats = scenario['stats']
        report_lines.append(f"【场景 {scenario['scenario_id']}】 {scenario['scenario_name']}")
        report_lines.append(f"  描述: {scenario['description']}")
        report_lines.append(f"  片段数: {stats['total_fragments']}")
        report_lines.append(f"  分数: 高{stats['high_score_count']} 中{stats['medium_count']} 低{stats['low_score_count']}")
        report_lines.append(f"  平均: {stats['average_score']} 分 (范围: {stats['min_score']}-{stats['max_score']})")

        # 显示最高分片段
        if scenario['fragments']:
            top_fragment = max(scenario['fragments'], key=lambda x: x['importance_score'])
            report_lines.append(f"  最高分片段 ({top_fragment['importance_score']}分):")
            report_lines.append(f"    {top_fragment['content'][:50]}...")

        report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append("📝 详细结果请查看: real_conversation_test_results.json")
    report_lines.append("=" * 80)

    # 保存报告
    report_file = "test_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    # 打印到控制台
    print("\n".join(report_lines))
    print(f"\n💾 测试报告已保存到: {report_file}")


if __name__ == "__main__":
    test_all_conversations()
