#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试摄像头API
"""

import sys
import os

sys.path.insert(0, r"D:\jsjxm\A-AI-BACKEND")

print("🔧 调试摄像头API")
print("=" * 60)

try:
    # 导入摄像头API模块
    from app.api.endpoints import cameras

    print("✅ 摄像头API模块导入成功")

    # 检查router
    print(f"Router: {cameras.router}")

except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)

# 尝试直接调用API
try:
    import requests

    print("\n直接测试API端点:")

    # 测试不同的端点
    endpoints = [
        "/api/v1/cameras",
        "/api/v1/cameras/with-filters",
    ]

    for endpoint in endpoints:
        url = f"http://localhost:8001{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            print(f"\n{endpoint}:")
            print(f"  状态码: {response.status_code}")

            if response.status_code == 500:
                print(f"  错误详情: {response.text[:500]}")
        except Exception as e:
            print(f"\n{endpoint}: ❌ {e}")

except Exception as e:
    print(f"API测试失败: {e}")

input("\n按Enter键退出...")