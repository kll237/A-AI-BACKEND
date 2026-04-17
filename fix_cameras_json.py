import json
import os
import sys


def fix_cameras_json():
    """修复cameras.json编码问题"""
    file_path = "D:/jsjxm/A-AI-BACKEND/data/cameras.json"

    print("🔧 修复cameras.json编码问题")
    print("=" * 60)

    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False

    try:
        # 1. 读取原始内容（尝试多种编码）
        content = None
        encodings_to_try = ['utf-8', 'gbk', 'latin-1', 'cp1252']

        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✅ 使用 {encoding} 编码读取成功")
                break
            except UnicodeDecodeError as e:
                print(f"❌ {encoding} 编码失败: {e}")
                continue

        if content is None:
            print("❌ 所有编码尝试都失败")
            return False

        # 2. 检查问题位置
        print(f"\n📊 文件信息:")
        print(f"   文件大小: {len(content)} 字符")

        # 查找可能的问题字符
        problematic_position = 2322  # 根据错误信息
        if len(content) > problematic_position:
            problem_char = content[problematic_position - 5:problematic_position + 5]
            print(f"   问题位置附近的字符: ...{problem_char}...")

            # 显示问题字符的编码
            for i, char in enumerate(problem_char):
                pos = problematic_position - 5 + i
                print(f"     位置 {pos}: '{char}' (Unicode: U+{ord(char):04X})")

        # 3. 清理内容
        print("\n🧹 清理JSON内容...")
        # 移除可能的BOM
        if content.startswith('\ufeff'):
            content = content[1:]
            print("   移除了UTF-8 BOM标记")

        # 移除可能的非法字符
        cleaned_content = ''
        illegal_chars = 0
        for i, char in enumerate(content):
            try:
                # 检查字符是否可以编码为UTF-8
                char.encode('utf-8')
                cleaned_content += char
            except UnicodeEncodeError:
                illegal_chars += 1
                # 替换非法字符
                cleaned_content += ' '
                print(f"   位置 {i}: 发现非法字符 U+{ord(char):04X}，已替换为空格")

        if illegal_chars > 0:
            print(f"   总共替换了 {illegal_chars} 个非法字符")

        # 4. 解析JSON
        print("\n📝 解析JSON...")
        try:
            data = json.loads(cleaned_content)
            print(f"   JSON解析成功，包含 {len(data)} 个摄像头")

            # 显示摄像头信息
            for cam_id, cam_info in list(data.items())[:3]:  # 只显示前3个
                print(f"   - {cam_info.get('name', '未命名')}: {cam_info.get('rtsp_url', '无URL')[:50]}...")

            if len(data) > 3:
                print(f"   ... 还有 {len(data) - 3} 个摄像头")

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return False

        # 5. 重新写入文件（UTF-8编码，无BOM）
        print("\n💾 保存修复后的文件...")
        backup_path = file_path + '.backup'
        os.rename(file_path, backup_path)
        print(f"   已创建备份: {backup_path}")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 文件已修复并保存: {file_path}")

        # 6. 验证修复
        print("\n🔍 验证修复...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                verify_data = json.load(f)
            print("✅ 验证通过：文件可正常读取")
            return True

        except Exception as e:
            print(f"❌ 验证失败: {e}")
            # 恢复备份
            os.rename(backup_path, file_path)
            print("⚠️  已恢复备份文件")
            return False

    except Exception as e:
        print(f"❌ 修复过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_simple_cameras_json():
    """创建简单的cameras.json文件"""
    file_path = "D:/jsjxm/A-AI-BACKEND/data/cameras.json"

    simple_data = {
        "simple-test-camera": {
            "id": "simple-test-camera",
            "name": "简单测试摄像头",
            "rtsp_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "created_at": "2025-12-10T21:00:00.000000",
            "updated_at": "2025-12-10T21:00:00.000000",
            "filters": [
                {
                    "filter_id": "ollamavision-simple",
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

    try:
        # 创建备份
        if os.path.exists(file_path):
            backup_path = file_path + '.backup2'
            os.rename(file_path, backup_path)
            print(f"📦 已创建备份: {backup_path}")

        # 写入新文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(simple_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 已创建简单的cameras.json文件")
        print(f"   包含1个测试摄像头")

        return True
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("AI摄像头系统 - JSON文件编码修复工具")
    print("=" * 60)

    choice = input("\n请选择操作:\n1. 修复现有文件\n2. 创建简单测试文件\n3. 直接查看问题位置\n\n请输入数字 (1/2/3): ")

    if choice == '1':
        success = fix_cameras_json()
    elif choice == '2':
        success = create_simple_cameras_json()
    elif choice == '3':
        # 直接查看问题
        file_path = "D:/jsjxm/A-AI-BACKEND/data/cameras.json"
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()

            pos = 2322
            if len(content) > pos:
                print(f"\n问题位置 {pos} 附近的字节:")
                start = max(0, pos - 50)
                end = min(len(content), pos + 50)
                hex_dump = content[start:end].hex()

                # 格式化显示
                for i in range(0, len(hex_dump), 32):
                    chunk = hex_dump[i:i + 32]
                    ascii_chunk = ''
                    for j in range(0, len(chunk), 2):
                        byte_val = int(chunk[j:j + 2], 16)
                        if 32 <= byte_val <= 126:
                            ascii_chunk += chr(byte_val)
                        else:
                            ascii_chunk += '.'

                    print(f"{start + i // 2:08X}: {chunk}  {ascii_chunk}")

                # 具体问题字节
                print(f"\n具体问题字节 (位置 {pos}):")
                problem_byte = content[pos]
                print(f"   十进制: {problem_byte}")
                print(f"   十六进制: {problem_byte:02X}")
                print(f"   二进制: {problem_byte:08b}")

                try:
                    # 尝试解码
                    decoded = content[pos:pos + 5].decode('utf-8')
                    print(f"   UTF-8解码: {decoded}")
                except:
                    print("   UTF-8解码失败")

                try:
                    decoded = content[pos:pos + 5].decode('gbk')
                    print(f"   GBK解码: {decoded}")
                except:
                    print("   GBK解码失败")
            else:
                print(f"文件只有 {len(content)} 字节，小于问题位置 {pos}")
    else:
        print("无效选择")

    print("\n" + "=" * 60)
    print("完成！请重启AI系统测试API。")