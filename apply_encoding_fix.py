# apply_encoding_fix.py
# 在main.py中导入此文件以修复编码问题

import sys
import os
import json
import codecs


def apply_comprehensive_encoding_fix():
    """应用全面的编码修复"""

    print("🔧 应用编码修复...")

    # 1. 修复系统编码设置
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass

    # 2. 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'

    # 3. 修复JSON模块
    fix_json_module()

    # 4. 修复可能的文件读取问题
    patch_builtin_open()

    print("✅ 编码修复已应用")


def fix_json_module():
    """修复JSON模块的编码问题"""

    # 保存原始函数
    original_json_load = json.load
    original_json_loads = json.loads

    def patched_json_load(fp, **kwargs):
        """修复的json.load函数"""
        # 确保使用utf-8编码
        if 'encoding' not in kwargs:
            kwargs['encoding'] = 'utf-8'

        # 如果是文件路径
        if isinstance(fp, str):
            # 尝试多种方式读取
            try:
                # 方式1: 使用原始方法
                return original_json_load(fp, **kwargs)
            except UnicodeDecodeError as e:
                print(f"⚠️  JSON加载遇到编码问题: {e}")
                print(f"    文件: {fp}")

                # 方式2: 读取字节然后尝试多种编码
                with open(fp, 'rb') as f:
                    content_bytes = f.read()

                # 尝试常见编码
                encodings_to_try = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1', 'cp1252']

                for encoding in encodings_to_try:
                    try:
                        content_str = content_bytes.decode(encoding)
                        # 清理可能的BOM
                        if encoding == 'utf-8-sig':
                            content_str = content_str.lstrip('\ufeff')
                        return json.loads(content_str)
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue

                # 如果都失败，抛出原始异常
                raise e

        # 如果不是文件路径，使用原始方法
        return original_json_load(fp, **kwargs)

    def patched_json_loads(s, **kwargs):
        """修复的json.loads函数"""
        # 如果是字节串，先解码
        if isinstance(s, bytes):
            encodings_to_try = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1']
            for encoding in encodings_to_try:
                try:
                    decoded = s.decode(encoding)
                    return original_json_loads(decoded, **kwargs)
                except UnicodeDecodeError:
                    continue

        return original_json_loads(s, **kwargs)

    # 替换函数
    json.load = patched_json_load
    json.loads = patched_json_loads

    print("   ✅ JSON模块修复完成")


def patch_builtin_open():
    """修补内置open函数以处理编码问题"""

    original_open = open

    def patched_open(file, mode='r', encoding=None, errors=None, **kwargs):
        """修复的open函数"""
        # 如果是读取文本文件且未指定编码，默认使用utf-8
        if 'r' in mode and 'b' not in mode and encoding is None:
            encoding = 'utf-8'

        # 如果是写文本文件且未指定编码，默认使用utf-8
        if ('w' in mode or 'a' in mode) and 'b' not in mode and encoding is None:
            encoding = 'utf-8'

        return original_open(file, mode=mode, encoding=encoding, errors=errors, **kwargs)

    # 替换内置open
    builtins = __import__('builtins')
    builtins.open = patched_open

    print("   ✅ 内置open函数修复完成")


# 立即应用修复
if __name__ != "__main__":
    apply_comprehensive_encoding_fix()