#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
干净启动器 - 修复Windows多进程问题
"""

import sys
import os

# 设置项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置环境变量
os.environ['PYTHONUTF8'] = '1'

print("🚀 启动AI摄像头系统...")
print("=" * 60)

try:
    # 直接导入app并运行uvicorn
    import uvicorn
    from app.core.config import settings

    host = getattr(settings, 'host', '0.0.0.0')
    port = getattr(settings, 'port', 8000)
    debug = getattr(settings, 'debug', True)

    print(f"服务器地址: {host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")
    print(f"健康检查: http://{host}:{port}/health")
    print("=" * 60)

    # 在Windows上禁用reload，避免多进程问题
    if debug and sys.platform == "win32":
        print("⚠️  Windows系统，禁用自动重载(reload)功能")
        debug = False

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,  # Windows上设为False
        log_level="info"
    )

except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback

    traceback.print_exc()
    input("按Enter键退出...")