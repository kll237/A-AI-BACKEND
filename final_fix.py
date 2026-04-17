#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终修复脚本：解决所有编码问题
"""

import os
import sys
import json
import shutil


def fix_all_encoding():
    """修复所有编码问题"""
    print("🚀 开始最终修复...")
    print("=" * 70)

    project_root = "D:/jsjxm/A-AI-BACKEND"
    os.chdir(project_root)

    # 1. 备份原始数据
    print("\n1. 📦 备份数据文件...")
    if os.path.exists("data"):
        if os.path.exists("data_backup_final"):
            shutil.rmtree("data_backup_final")
        shutil.copytree("data", "data_backup_final")
        print("   ✅ 数据已备份到: data_backup_final")

    # 2. 修复cameras.json
    print("\n2. 🔧 修复cameras.json...")
    cameras_path = "data/cameras.json"

    if os.path.exists(cameras_path):
        # 读取文件
        try:
            with open(cameras_path, 'rb') as f:
                content_bytes = f.read()

            # 尝试多种编码
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'latin-1']:
                try:
                    content = content_bytes.decode(encoding)
                    print(f"   ✅ 使用 {encoding} 编码成功读取")
                    break
                except UnicodeDecodeError:
                    continue

            if content:
                # 解析JSON
                data = json.loads(content)

                # 创建简化版本
                simplified_data = {}
                for cam_id, cam_info in data.items():
                    # 确保必要字段存在
                    simplified_data[cam_id] = {
                        "id": cam_info.get("id", cam_id),
                        "name": cam_info.get("name", f"Camera {cam_id}"),
                        "rtsp_url": cam_info.get("rtsp_url", ""),
                        "created_at": cam_info.get("created_at", "2025-12-10T00:00:00.000000"),
                        "updated_at": cam_info.get("updated_at", "2025-12-10T00:00:00.000000"),
                        "filters": cam_info.get("filters", []),
                        "is_active": cam_info.get("is_active", False),
                        "stream_status": cam_info.get("stream_status", False),
                        "validation_result": cam_info.get("validation_result", {
                            "is_valid": False,
                            "frames_read": 0,
                            "validation_time": 0
                        })
                    }

                # 写入UTF-8
                with open(cameras_path, 'w', encoding='utf-8', newline='\n') as f:
                    json.dump(simplified_data, f, ensure_ascii=False, indent=2)

                print(f"   ✅ cameras.json 修复完成，保留 {len(simplified_data)} 个摄像头")
            else:
                print("   ❌ 无法读取文件，创建新文件")
                create_simple_cameras()

        except Exception as e:
            print(f"   ❌ 修复失败: {e}")
            create_simple_cameras()
    else:
        print("   ⚠️  文件不存在，创建新文件")
        create_simple_cameras()

    # 3. 创建UTF-8编码的启动器
    print("\n3. 🚀 创建UTF-8启动器...")
    create_utf8_launcher()

    # 4. 添加环境变量修复
    print("\n4. ⚙️ 设置环境变量...")
    create_env_script()

    print("\n" + "=" * 70)
    print("🎉 最终修复完成！")
    print("\n下一步操作：")
    print("1. 关闭所有Python进程")
    print("2. 运行: start_utf8.bat")
    print("3. 测试API连接")


def create_simple_cameras():
    """创建简单的cameras.json"""
    cameras_path = "data/cameras.json"

    simple_data = {
        "simple-test": {
            "id": "simple-test",
            "name": "测试摄像头",
            "rtsp_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "created_at": "2025-12-10T12:00:00.000000",
            "updated_at": "2025-12-10T12:00:00.000000",
            "filters": [
                {
                    "filter_id": "test-vision",
                    "filter_name": "OllamaVision",
                    "enabled": True
                }
            ],
            "is_active": True,
            "stream_status": True,
            "validation_result": {
                "is_valid": True,
                "frames_read": 5,
                "validation_time": 1.0
            }
        }
    }

    # 确保data目录存在
    os.makedirs("data", exist_ok=True)

    with open(cameras_path, 'w', encoding='utf-8') as f:
        json.dump(simple_data, f, ensure_ascii=False, indent=2)

    print("   ✅ 已创建简单cameras.json")


def create_utf8_launcher():
    """创建UTF-8启动脚本"""
    # 创建Python启动脚本
    launcher_content = '''#!/usr/bin/env python
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

# 4. 修复JSON模块
import json

def fix_json_module():
    """修复JSON模块编码问题"""
    original_load = json.load
    original_loads = json.loads

    def safe_load(fp, **kwargs):
        if 'encoding' not in kwargs:
            kwargs['encoding'] = 'utf-8'
        return original_load(fp, **kwargs)

    def safe_loads(s, **kwargs):
        return original_loads(s, **kwargs)

    json.load = safe_load
    json.loads = safe_loads

fix_json_module()
print("✅ 编码修复完成")

# ========== 导入主应用 ==========
try:
    # 导入主应用
    from app.main import app

    import uvicorn
    print("\\n🚀 启动AI摄像头系统...")
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
'''

    with open("launch_utf8.py", 'w', encoding='utf-8', newline='\n') as f:
        f.write(launcher_content)

    print("   ✅ 创建启动脚本: launch_utf8.py")

    # 创建批处理文件
    bat_content = '''@echo off
chcp 65001 > nul
title AI摄像头系统 (UTF-8模式)
echo ========================================
echo AI摄像头系统 - UTF-8编码启动
echo ========================================
echo.

echo 停止现有进程...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 设置Python环境...
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set LANG=zh_CN.UTF-8

echo.
echo 启动系统...
echo 请稍候...
echo.
echo 访问地址:
echo   API文档: http://localhost:8000/docs
echo   健康检查: http://localhost:8000/health
echo.
echo ========================================
echo.

"C:\\Users\\Administrator\\miniconda3\\envs\\pytorch\\python.exe" launch_utf8.py

pause
'''

    with open("start_utf8.bat", 'w', encoding='gbk', newline='\r\n') as f:
        f.write(bat_content)

    print("   ✅ 创建批处理文件: start_utf8.bat")


def create_env_script():
    """创建环境变量设置脚本"""
    env_content = '''# encoding_env.py
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
'''

    with open("encoding_env.py", 'w', encoding='utf-8') as f:
        f.write(env_content)

    print("   ✅ 创建环境变量脚本: encoding_env.py")


def create_simple_test():
    """创建简单的API测试"""
    test_content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的API测试
"""

import requests
import json

def test_api():
    """测试API连接"""
    print("🔍 测试API连接")
    print("=" * 50)

    base_url = "http://localhost:8000/api/v1"

    endpoints = [
        ("/", "根路径"),
        ("/health", "健康检查"),
        ("/cameras", "摄像头列表"),
        ("/contextual/cameras", "上下文摄像头")
    ]

    for endpoint, name in endpoints:
        url = base_url + endpoint if endpoint != "/" else "http://localhost:8000/"

        try:
            print(f"\\n📡 {name}: {endpoint}")
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print(f"   ✅ 成功 (状态码: {response.status_code})")
                try:
                    data = response.json()
                    print(f"     返回数据: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                except:
                    print(f"     返回内容: {response.text[:100]}...")
            else:
                print(f"   ❌ 失败 (状态码: {response.status_code})")
                print(f"     错误: {response.text[:200]}")

        except requests.exceptions.ConnectionError:
            print(f"   ❌ 连接失败 - 服务可能未启动")
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")

    print("\\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    test_api()
'''

    with open("test_api_simple.py", 'w', encoding='utf-8') as f:
        f.write(test_content)

    print("   ✅ 创建API测试脚本: test_api_simple.py")


if __name__ == "__main__":
    fix_all_encoding()
    create_simple_test()