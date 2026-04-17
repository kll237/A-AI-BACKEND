#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终API测试
"""

import requests
import json
import time


def test_all_apis():
    base_url = "http://localhost:8001"

    print("🎯 最终API测试报告")
    print("=" * 60)

    # 等待系统响应
    print("检查系统状态...")
    for i in range(10):
        try:
            r = requests.get(f"{base_url}/health", timeout=2)
            if r.status_code == 200:
                print(f"✅ 系统已就绪")
                break
        except:
            if i < 9:
                print(f"⏳ 等待系统... ({i + 1}/10)")
                time.sleep(1)
            else:
                print("❌ 系统无响应")
                return

    print("\n测试API端点:")
    print("-" * 60)

    endpoints = [
        ("/", "系统主页"),
        ("/health", "健康检查"),
        ("/api/v1/cameras", "摄像头列表"),
        ("/api/v1/contextual/cameras", "上下文摄像头"),
        ("/docs", "API文档")
    ]

    results = []

    for endpoint, name in endpoints:
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=5)
            status = response.status_code

            if status == 200:
                print(f"✅ {name}: 正常 (状态码: {status})")

                if endpoint == "/api/v1/cameras":
                    data = response.json()
                    print(f"   返回 {len(data)} 个摄像头")
                    if data:
                        print(f"   示例: {json.dumps(data[0], ensure_ascii=False)[:80]}...")

                elif endpoint == "/api/v1/contextual/cameras":
                    data = response.json()
                    print(f"   返回 {len(data)} 个上下文摄像头")

                results.append(True)

            elif status == 500:
                error_text = response.text[:300]
                print(f"❌ {name}: 服务器错误 (状态码: {status})")
                print(f"   错误: {error_text}")
                results.append(False)

            else:
                print(f"⚠️  {name}: 状态码 {status}")
                print(f"   响应: {response.text[:100]}")
                results.append(False)

        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: 连接失败")
            results.append(False)
        except Exception as e:
            print(f"❌ {name}: 错误 - {e}")
            results.append(False)

    # 总结
    print("\n" + "=" * 60)
    success = sum(results)
    total = len(results)

    print(f"📊 测试结果: {success}/{total} 通过")

    if success == total:
        print("\n🎉 🎉 🎉 所有API测试通过！ 🎉 🎉 🎉")
        print("\n✅ 前端可以正常连接以下API:")
        print("   1. http://localhost:8001/          - 系统主页")
        print("   2. http://localhost:8001/health    - 健康检查")
        print("   3. http://localhost:8001/api/v1/cameras - 摄像头列表")
        print("   4. http://localhost:8001/api/v1/contextual/cameras - 上下文摄像头")
        print("   5. http://localhost:8001/docs      - API文档")
        print("\n🚀 系统完全正常运行！")
    else:
        print(f"\n⚠️  有 {total - success} 个API需要检查")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_all_apis()
    input("\n按Enter键退出...")