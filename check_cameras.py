#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动系统并监视输出
"""

import subprocess
import sys
import time

print("🚀 启动AI摄像头系统 (带监视)")
print("=" * 60)

# 启动命令
cmd = [
    sys.executable,
    "-c",
    """
import sys
sys.path.insert(0, 'D:/jsjxm/A-AI-BACKEND')

try:
    from app.main import app
    import uvicorn
    
    print('=' * 50)
    print('🤖 AI摄像头系统启动中...')
    print('=' * 50)
    
    # 启动服务器
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8001,
        reload=False,
        log_level='info'
    )
    
except Exception as e:
    print(f'启动失败: {e}')
    import traceback
    traceback.print_exc()
    input('按Enter退出...')
    """
]

try:
    print("正在启动进程...")

    # 启动子进程
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        bufsize=1,
        universal_newlines=True
    )

    print("进程已启动，监视输出...")
    print("-" * 40)

    # 读取输出
    line_count = 0
    while True:
        line = process.stdout.readline()
        if line:
            print(line, end='')
            line_count += 1

            # 检查是否成功启动
            if "Uvicorn running on" in line:
                print("\n" + "=" * 60)
                print("✅ 系统启动成功！")
                print(f"访问地址: http://localhost:8001/")
                print("=" * 60)
                break

            # 检查是否出错
            if "ERROR" in line or "Error" in line or "error" in line:
                print(f"\n⚠️  发现错误: {line}")

        # 检查进程是否结束
        if process.poll() is not None:
            print(f"\n进程已退出，返回码: {process.returncode}")
            break

        if line_count > 100:  # 防止无限循环
            print("\n⚠️  输出行数过多，可能有问题")
            break

    # 如果进程还在运行，等待用户决定
    if process.poll() is None:
        print("\n系统正在运行中...")
        print("按 Ctrl+C 停止系统")
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n用户中断，停止系统...")
            process.terminate()

except KeyboardInterrupt:
    print("\n用户中断")
except Exception as e:
    print(f"\n启动失败: {e}")

print("\n启动监视结束")
input("按Enter退出...")