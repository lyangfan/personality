#!/usr/bin/env python3
"""
DeepMemory API 测试脚本

测试所有主要端点：
- POST /v1/chat
- POST /v1/chat/completions
- GET /v1/memories
- GET /health

注意：需要设置 API_KEY 环境变量或在代码中配置
"""
import requests
import json
import time
import os
from typing import Optional


# API 配置
BASE_URL = "http://localhost:8000"
USER_ID = "test_user_001"
USERNAME = "测试用户"

# API Key（从环境变量读取，或手动设置）
API_KEY = os.getenv("API_KEY", "test-api-key-12345")

# 请求头（包含 API Key）
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response: requests.Response):
    """打印响应"""
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


def test_health():
    """测试健康检查"""
    print_section("1. 健康检查 (GET /health)")

    response = requests.get(f"{BASE_URL}/health", headers=headers)
    print_response(response)

    return response.status_code == 200


def test_create_user():
    """测试创建用户"""
    print_section("2. 创建用户 (POST /v1/users)")

    payload = {
        "username": USERNAME,
        "user_id": USER_ID,
    }

    response = requests.post(
        f"{BASE_URL}/v1/users",
        json=payload,
        headers=headers
    )
    print_response(response)

    return response.status_code == 200


def test_create_session():
    """测试创建会话"""
    print_section("3. 创建会话 (POST /v1/sessions)")

    payload = {
        "user_id": USER_ID,
        "title": "测试对话",
    }

    response = requests.post(
        f"{BASE_URL}/v1/sessions",
        json=payload,
        headers=headers)

    if response.status_code == 200:
        session_id = response.json()["session_id"]
        print(f"✓ 会话创建成功: {session_id}")
        print_response(response)
        return session_id
    else:
        print("✗ 会话创建失败")
        print_response(response)
        return None


def test_chat_simple(session_id: str):
    """测试简单对话接口"""
    print_section("4. 简单对话 (POST /v1/chat)")

    payload = {
        "user_id": USER_ID,
        "session_id": session_id,
        "message": "你好，我是张三，我是一名软件工程师",
        "username": USERNAME,
    }

    response = requests.post(
        f"{BASE_URL}/v1/chat",
        json=payload,
        headers=headers)

    if response.status_code == 200:
        print("✓ 对话成功")
        print_response(response)
        return True
    else:
        print("✗ 对话失败")
        print_response(response)
        return False


def test_chat_completions(session_id: str):
    """测试 OpenAI 兼容接口"""
    print_section("5. Chat Completions (POST /v1/chat/completions)")

    payload = {
        "user_id": USER_ID,
        "session_id": session_id,
        "messages": [
            {
                "role": "user",
                "content": "我喜欢打网球和看电影，你能记住这些吗？"
            }
        ],
        "model": "glm-4-flash",
    }

    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        json=payload,
        headers=headers)

    if response.status_code == 200:
        print("✓ 对话成功")
        print_response(response)
        return True
    else:
        print("✗ 对话失败")
        print_response(response)
        return False


def test_get_memories(session_id: str):
    """测试获取记忆"""
    print_section("6. 获取记忆 (GET /v1/memories)")

    params = {
        "user_id": USER_ID,
        "session_id": session_id,
        "limit": 10,
    }

    response = requests.get(
        f"{BASE_URL}/v1/memories",
        params=params,
        headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✓ 记忆获取成功，共 {data['total_count']} 条")
        print_response(response)
        return True
    else:
        print("✗ 记忆获取失败")
        print_response(response)
        return False


def test_conversation_flow(session_id: str):
    """测试连续对话流程"""
    print_section("7. 连续对话流程测试")

    messages = [
        "我昨天去看了《阿凡达2》，太精彩了！",
        "你觉得这部电影怎么样？",
        "我特别喜欢里面的水下场景",
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n--- 第 {i} 轮对话 ---")
        print(f"用户: {message}")

        payload = {
            "user_id": USER_ID,
            "session_id": session_id,
            "message": message,
        }

        response = requests.post(
            f"{BASE_URL}/v1/chat",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            ai_response = response.json()["response"]
            print(f"AI: {ai_response}")
            time.sleep(1)  # 避免请求过快
        else:
            print(f"✗ 对话失败: {response.status_code}")
            return False

    print("\n✓ 连续对话测试完成")
    return True


def main():
    """主测试函数"""
    print("🧪 DeepMemory API 测试脚本")
    print(f"📍 API 地址: {BASE_URL}")

    try:
        # 1. 健康检查
        if not test_health():
            print("\n❌ 健康检查失败，请确保服务已启动")
            return

        # 2. 创建用户
        test_create_user()

        # 3. 创建会话
        session_id = test_create_session()
        if not session_id:
            print("\n❌ 会话创建失败")
            return

        # 4. 简单对话
        if not test_chat_simple(session_id):
            print("\n❌ 简单对话失败")
            return

        # 5. Chat Completions
        if not test_chat_completions(session_id):
            print("\n❌ Chat Completions 失败")
            return

        # 6. 连续对话
        if not test_conversation_flow(session_id):
            print("\n❌ 连续对话失败")
            return

        # 7. 获取记忆
        time.sleep(3)  # 等待后台记忆提取完成
        test_get_memories(session_id)

        print("\n" + "=" * 60)
        print("  ✅ 所有测试完成！")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败：请确保 API 服务已启动")
        print(f"   启动命令: python app.py 或 ./start.sh")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
