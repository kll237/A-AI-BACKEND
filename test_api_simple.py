#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试端口8001的API
"""

import requests
import json


def test_api():
    base_url = "http://localhost:8001"  # 注意是8001端口！

    print("🔍 测试端口8001的API")
    print("=" * 60)

    endpoints = [
        ("/", "根路径"),
        ("/health", "健康检查"),
        ("/api/v1/cameras", "摄像头列表"),
        ("/api/v1/contextual/cameras", "上下文摄像头"),
    ]

    for endpoint, description in endpoints:
        url = base_url + endpoint
        try:
            print(f"\n📡 {description}:")
            print(f"   URL: {url}")

            response = requests.get(url, timeout=5)
            print(f"   状态码: {response.status_code}")

            if response.status_code == 200:
                print("   ✅ 成功")
                try:
                    data = response.json()
                    print(f"   返回数据: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                except:
                    print(f"   返回内容: {response.text[:100]}...")
            elif response.status_code == 500:
                print("   ❌ 服务器错误 (500)")
                error_text = response.text
                print(f"   错误信息: {error_text[:300]}")
            else:
                print(f"   ⚠️  状态码: {response.status_code}")
                print(f"   响应: {response.text[:100]}")

        except requests.exceptions.ConnectionError:
            print(f"   ❌ 连接失败 - 服务可能未启动")
            print(f"   请确认系统正在端口8001运行")
            break
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")


if __name__ == "__main__":
    test_api()