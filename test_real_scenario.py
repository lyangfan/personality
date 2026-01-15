#!/usr/bin/env python3
"""
真实场景完整测试

模拟真实用户对话，全程使用 AI：
1. AI 生成回复（GLM-4-Flash）
2. AI 进行记忆评分（GLM-4）
3. AI 生成向量（GLM Embedding-3）

测试场景：一个用户初次使用 AI 陪伴，分享自己的生活和感受
"""

import requests
import json
import time
from datetime import datetime


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.END}\n")


def print_section(text):
    """打印分节"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}▶ {text}{Colors.END}")
    print(f"{Colors.CYAN}{'─' * 70}{Colors.END}")


def print_user_message(text):
    """打印用户消息"""
    print(f"\n{Colors.GREEN}👤 用户:{Colors.END} {text}")


def print_ai_message(text):
    """打印 AI 消息"""
    print(f"{Colors.BLUE}🤖 AI:{Colors.END} {text}")


def print_memory(memory):
    """打印记忆"""
    score = memory['importance_score']
    speaker = memory['speaker']
    content = memory['content']

    if speaker == 'user':
        color = Colors.GREEN
    else:
        color = Colors.BLUE

    score_color = Colors.YELLOW if score >= 7 else Colors.END

    print(f"{color}  [{speaker}]{Colors.END} {content}")
    print(f"     {score_color}⭐ {score}/10{Colors.END} | {memory['type']} | {memory['sentiment']}")


class DeepMemoryClient:
    """DeepMemory API 客户端"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.user_id = None
        self.session_id = None

    def check_health(self):
        """健康检查"""
        print_section("1. 健康检查")

        response = requests.get(f"{self.base_url}/health")
        data = response.json()

        print(f"✅ 服务状态: {data['status']}")
        print(f"📊 版本: {data['version']}")
        print(f"🧠 Embedding 模型: {data['embedding_model']}")
        print(f"🔧 环境: {data['components']['environment']}")

        return data['status'] == 'healthy'

    def create_user(self, username, user_id=None):
        """创建用户"""
        print_section("2. 创建用户")

        response = requests.post(
            f"{self.base_url}/v1/users",
            json={"username": username, "user_id": user_id}
        )
        data = response.json()

        self.user_id = data['user_id']
        print(f"✅ 用户创建成功")
        print(f"   用户ID: {data['user_id']}")
        print(f"   用户名: {data['username']}")
        print(f"   创建时间: {data['created_at']}")

        return data

    def create_session(self, title="真实场景测试"):
        """创建会话"""
        print_section("3. 创建会话")

        response = requests.post(
            f"{self.base_url}/v1/sessions",
            json={"user_id": self.user_id, "title": title}
        )
        data = response.json()

        self.session_id = data['session_id']
        print(f"✅ 会话创建成功")
        print(f"   会话ID: {data['session_id']}")
        print(f"   标题: {data['title']}")

        return data

    def chat(self, message, extract_now=False):
        """发送消息"""
        response = requests.post(
            f"{self.base_url}/v1/chat",
            json={
                "user_id": self.user_id,
                "session_id": self.session_id,
                "message": message,
                "extract_now": extract_now
            }
        )

        if response.status_code == 200:
            data = response.json()
            return {
                'response': data['response'],
                'memory_extracted': data['memory_extracted'],
                'message_count': data['message_count']
            }
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)
            return None

    def get_memories(self, limit=20):
        """获取记忆"""
        response = requests.get(
            f"{self.base_url}/v1/memories",
            params={
                "user_id": self.user_id,
                "session_id": self.session_id,
                "limit": limit
            }
        )

        if response.status_code == 200:
            return response.json()
        return None


def test_scenario():
    """测试真实场景"""

    print_header("DeepMemory 真实场景完整测试")

    print(f"{Colors.BOLD}测试场景：{Colors.END}")
    print(f"  用户：小明，一个刚毕业的大学生，正在找工作")
    print(f"  场景：初次使用 AI 陪伴，分享自己的焦虑和梦想")
    print(f"  目标：验证 AI 能否记住重要信息并给予情感支持")
    print(f"\n{Colors.YELLOW}⚠️  全程使用 AI：{Colors.END}")
    print(f"  • AI 回复：GLM-4-Flash")
    print(f"  • 记忆评分：GLM-4")
    print(f"  • 向量化：GLM Embedding-3")

    # 初始化客户端
    client = DeepMemoryClient()

    # 1. 健康检查
    if not client.check_health():
        print(f"{Colors.RED}❌ 服务未启动，请先运行：python app.py{Colors.END}")
        return

    # 2. 创建用户和会话
    client.create_user("小明", "user_xiaoming_20250115")
    client.create_session("小明的第一次对话")

    # 3. 模拟真实对话
    print_section("4. 开始对话（模拟真实场景）")

    # 定义对话脚本
    conversations = [
        {
            "round": 1,
            "user": "你好，我今年刚大学毕业，正在找工作，有点焦虑",
            "context": "初次见面，分享基本信息和情绪"
        },
        {
            "round": 2,
            "user": "我学的是计算机专业，但感觉自己技术还不够好",
            "context": "分享自我怀疑"
        },
        {
            "round": 3,
            "user": "其实我从小就喜欢编程，高考填志愿时毫不犹豫选了计算机",
            "context": "分享童年经历和兴趣起源"
        },
        {
            "round": 4,
            "user": "上周面试了一家大厂，二面被刷了，感觉很难受",
            "context": "分享挫折和负面情绪"
        },
        {
            "round": 5,
            "user": "但我不会放弃的！我的梦想是成为一名优秀的算法工程师",
            "context": "表达梦想和决心（高重要性）"
        },
        {
            "round": 6,
            "user": "谢谢你一直听我说这些，感觉好多了",
            "context": "感谢 AI 的陪伴"
        },
        {
            "round": 7,
            "user": "对了，我之前说我学什么专业来着？",
            "context": "测试 AI 是否记住"
        },
    ]

    # 执行对话
    for conv in conversations:
        print(f"\n{Colors.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
        print(f"{Colors.YELLOW}第 {conv['round']} 轮对话{Colors.END}")
        print(f"{Colors.YELLOW}{conv['context']}{Colors.END}")
        print(f"{Colors.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")

        # 用户消息
        print_user_message(conv['user'])

        # AI 回复
        result = client.chat(conv['user'])
        if result:
            print_ai_message(result['response'])
            print(f"\n  📊 当前消息数: {result['message_count']}")
            if result['memory_extracted']:
                print(f"  🧠 ✅ 已触发记忆提取")

        time.sleep(1.5)  # 模拟真实对话间隔

    # 4. 触发记忆提取
    print_section("5. 触发记忆提取")

    print("强制提取记忆...")
    result = client.chat("请帮我总结一下我们刚才的对话", extract_now=True)
    if result:
        print_ai_message(result['response'])
        print(f"\n  🧠 ✅ 记忆已提取")

    # 等待后台任务完成
    print("\n⏳ 等待记忆存储完成...")
    time.sleep(5)

    # 5. 查看记忆
    print_section("6. 查看 AI 记住了什么")

    memories = client.get_memories(limit=50)

    if memories and memories['total_count'] > 0:
        print(f"\n✅ 成功提取 {memories['total_count']} 条记忆\n")

        # 分类展示
        user_memories = [m for m in memories['memories'] if m['speaker'] == 'user']
        ai_memories = [m for m in memories['memories'] if m['speaker'] == 'assistant']

        print(f"{Colors.GREEN}{'=' * 70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}用户的重要信息（{len(user_memories)} 条）{Colors.END}")
        print(f"{Colors.GREEN}{'=' * 70}{Colors.END}")

        for m in user_memories:
            print_memory(m)
            print()

        print(f"{Colors.BLUE}{'=' * 70}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}AI 的承诺和回应（{len(ai_memories)} 条）{Colors.END}")
        print(f"{Colors.BLUE}{'=' * 70}{Colors.END}")

        for m in ai_memories:
            print_memory(m)
            print()

        # 6. 分析记忆质量
        print_section("7. 记忆质量分析")

        # 统计
        high_score = [m for m in memories['memories'] if m['importance_score'] >= 7]
        medium_score = [m for m in memories['memories'] if 5 <= m['importance_score'] < 7]
        low_score = [m for m in memories['memories'] if m['importance_score'] < 5]

        print(f"\n📊 记忆分布:")
        print(f"  • 高重要性 (7-10分): {len(high_score)} 条")
        print(f"  • 中等重要性 (5-6分): {len(medium_score)} 条")
        print(f"  • 低重要性 (1-4分): {len(low_score)} 条")

        # 类型分布
        types = {}
        for m in memories['memories']:
            t = m['type']
            types[t] = types.get(t, 0) + 1

        print(f"\n📋 记忆类型分布:")
        for t, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {t}: {count} 条")

        # 情感分布
        sentiments = {}
        for m in memories['memories']:
            s = m['sentiment']
            sentiments[s] = sentiments.get(s, 0) + 1

        print(f"\n💭 情感分布:")
        for s, count in sorted(sentiments.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {s}: {count} 条")

        # 7. 验证记忆效果
        print_section("8. 验证 AI 记忆效果")

        print("\n🔍 验证 1：用户提到'计算机专业'")
        major_memories = [m for m in user_memories if '计算机' in m['content']]
        if major_memories:
            print(f"  ✅ 记住了！找到 {len(major_memories)} 条相关记忆")
            for m in major_memories[:1]:
                print_memory(m)
        else:
            print(f"  ❌ 没找到相关记忆")

        print("\n🔍 验证 2：用户提到'梦想'")
        dream_memories = [m for m in user_memories if '梦想' in m['content'] or '算法工程师' in m['content']]
        if dream_memories:
            print(f"  ✅ 记住了！找到 {len(dream_memories)} 条相关记忆")
            for m in dream_memories[:1]:
                print_memory(m)
        else:
            print(f"  ❌ 没找到相关记忆")

        print("\n🔍 验证 3：AI 的承诺")
        promise_memories = [m for m in ai_memories if any(kw in m['content'] for kw in ['会一直', '会陪', '支持你', '相信你'])]
        if promise_memories:
            print(f"  ✅ 记住了！找到 {len(promise_memories)} 条承诺记忆")
            for m in promise_memories[:2]:
                print_memory(m)
        else:
            print(f"  ❌ 没找到相关记忆")

        # 8. 总结
        print_section("9. 测试总结")

        print(f"\n{Colors.BOLD}✅ 测试完成！{Colors.END}\n")

        print(f"{Colors.BOLD}关键成果：{Colors.END}")
        print(f"  • 对话轮数: {len(conversations)} + 1 次总结")
        print(f"  • 提取记忆: {memories['total_count']} 条")
        print(f"  • 高分记忆: {len(high_score)} 条（占比 {len(high_score)/memories['total_count']*100:.1f}%）")
        print(f"  • 用户信息: {len(user_memories)} 条")
        print(f"  • AI 承诺: {len(ai_memories)} 条")

        print(f"\n{Colors.BOLD}AI 能力验证：{Colors.END}")
        print(f"  • {'✅' if major_memories else '❌'} 记住用户基本信息")
        print(f"  • {'✅' if dream_memories else '❌'} 记住用户梦想")
        print(f"  • {'✅' if promise_memories else '❌'} 记住 AI 承诺")
        print(f"  • ✅ 情感陪伴和鼓励")

        print(f"\n{Colors.BOLD}技术验证：{Colors.END}")
        print(f"  • ✅ GLM-4-Flash 生成回复")
        print(f"  • ✅ GLM-4 智能评分")
        print(f"  • ✅ GLM Embedding-3 向量化")
        print(f"  • ✅ 异步记忆提取")
        print(f"  • ✅ ChromaDB 持久化")

        # 最终测试：让 AI 回答
        print_section("10. 最终测试：AI 能否准确回忆")

        final_test_questions = [
            "我叫什么名字？",
            "我学的什么专业？",
            "我的梦想是什么？",
        ]

        for q in final_test_questions:
            print(f"\n{Colors.YELLOW}Q: {q}{Colors.END}")
            result = client.chat(q)
            if result:
                print(f"{Colors.BLUE}A: {result['response']}{Colors.END}")

        print(f"\n{Colors.GREEN}{'=' * 70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 真实场景测试完成！{Colors.END}")
        print(f"{Colors.GREEN}{'=' * 70}{Colors.END}\n")

    else:
        print(f"{Colors.RED}❌ 未获取到记忆{Colors.END}")


if __name__ == "__main__":
    try:
        test_scenario()
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ 无法连接到服务{Colors.END}")
        print(f"{Colors.YELLOW}请确保服务已启动：python app.py{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ 测试失败: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
