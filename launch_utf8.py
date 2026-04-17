#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UTF-8编码启动器
解决Windows中文编码问题
"""

import sys
import os
import locale

# ========== 编码修复 ==========
print("🔧 应用编码修复...")

# 1. 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# 2. 设置区域编码
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    except:
        pass

# 3. 修复标准输出
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 4. 修复JSON模块 - 正确版本
import json


def fix_json_module():
    """修复JSON模块编码问题 - 正确版本"""
    original_load = json.load
    original_loads = json.loads

    def safe_load(fp, **kwargs):
        """安全的json.load - 处理编码问题"""
        # json.load() 不接受 encoding 参数，所以我们需要特殊处理
        # 如果是文件路径，直接读取字节然后解码
        if isinstance(fp, str):
            try:
                # 先尝试使用原始方法
                return original_load(fp, **kwargs)
            except (UnicodeDecodeError, TypeError):
                # 读取文件字节
                with open(fp, 'rb') as f:
                    content = f.read()

                # 尝试多种编码
                encodings_to_try = ['utf-8', 'utf-8-sig', 'gbk', 'latin-1', 'cp1252']
                for encoding in encodings_to_try:
                    try:
                        decoded = content.decode(encoding)
                        # 清理BOM
                        if encoding == 'utf-8-sig':
                            decoded = decoded.lstrip('\ufeff')
                        return json.loads(decoded, **kwargs)
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue

                # 所有编码都失败，重新抛出异常
                raise
        else:
            # 如果是文件对象，使用原始方法
            return original_load(fp, **kwargs)

    def safe_loads(s, **kwargs):
        """安全的json.loads"""
        # 如果是字节串，先解码
        if isinstance(s, bytes):
            for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'latin-1']:
                try:
                    decoded = s.decode(encoding)
                    # 清理BOM
                    if encoding == 'utf-8-sig':
                        decoded = decoded.lstrip('\ufeff')
                    return original_loads(decoded, **kwargs)
                except UnicodeDecodeError:
                    continue

        # 否则使用原始方法
        return original_loads(s, **kwargs)

    # 替换函数
    json.load = safe_load
    json.loads = safe_loads


fix_json_module()
print("✅ 编码修复完成")

# ========== 导入主应用 ==========
try:
    # 导入主应用
    from app.main import app

    import uvicorn

    print("\n🚀 启动AI摄像头系统...")
    print("=" * 60)

    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保在项目根目录运行此脚本")
    input("按Enter键退出...")

except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback

    traceback.print_exc()
    input("按Enter键退出...")