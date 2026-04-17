# encoding_env.py
# 在app/__init__.py或main.py中导入此文件设置环境变量

import os
import sys

def set_encoding_environment():
    """设置编码环境变量"""
    # 设置Python编码环境
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

    # 对于Windows，设置代码页
    if sys.platform == 'win32':
        try:
            import ctypes
            # 设置控制台代码页为UTF-8
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except:
            pass

    print("编码环境已设置: UTF-8")

# 立即执行
if __name__ != "__main__":
    set_encoding_environment()
