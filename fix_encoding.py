import sys
import os
import json


def fix_encoding_issues():
    """修复编码问题"""

    # 1. 设置系统默认编码
    if sys.version_info.major == 3:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

    # 2. 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

    # 3. 修复JSON文件编码
    fix_json_files()

    print("编码修复完成")
    return True


def fix_json_files():
    """修复所有JSON文件的编码"""
    data_dir = "D:/jsjxm/A-AI-BACKEND/data"

    json_files = [
        "cameras.json",
        "users.json",
        "rules.json"
    ]

    for filename in json_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            try:
                # 读取文件（使用utf-8编码）
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 确保是有效的JSON
                data = json.loads(content)

                # 重新写入（使用utf-8编码）
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                print(f"✓ 已修复: {filename}")
            except Exception as e:
                print(f"✗ 修复失败 {filename}: {e}")
        else:
            print(f"⚠ 文件不存在: {filename}")


def create_default_files():
    """创建默认文件（如果不存在）"""
    data_dir = "D:/jsjxm/A-AI-BACKEND/data"
    os.makedirs(data_dir, exist_ok=True)

    # 创建默认的cameras.json（简化版）
    cameras_data = {
        "simple-camera": {
            "id": "simple-camera",
            "name": "简单测试摄像头",
            "rtsp_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "filters": [
                {
                    "filter_id": "simple-filter",
                    "filter_name": "OllamaVision",
                    "enabled": True
                }
            ],
            "is_active": True
        }
    }

    with open(os.path.join(data_dir, "cameras.json"), 'w', encoding='utf-8') as f:
        json.dump(cameras_data, f, ensure_ascii=False, indent=2)

    print("已创建简化版配置文件")


if __name__ == "__main__":
    print("正在修复编码问题...")
    fix_encoding_issues()
    print("\n建议重启AI系统")