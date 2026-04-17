"""
多个人脸检测器演示
展示三种不同的检测方法：
1. Haar级联检测器（基础）
2. 轮廓检测器（侧面人脸）
3. 替代检测器（模糊图像）
"""
import cv2
import sys
import os
import time
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("多个人脸检测器演示")
print("=" * 60)

try:
    # 导入人脸检测器
    from app.ai_engine.utils.face_detector import FaceDetector

    print("✓ 成功导入FaceDetector类")

    # 创建人脸检测器实例
    print("\n初始化人脸检测器...")
    face_detector = FaceDetector(min_face_size=(50, 50))
    print("✓ 人脸检测器初始化完成")

    # 查看检测器数量
    print(f"\n总共有 {len(face_detector.detection_methods)} 种检测方法:")

    # 获取可用的检测方法名称
    method_names = []
    if hasattr(face_detector, 'face_cascade') and not face_detector.face_cascade.empty():
        method_names.append("Haar Cascade (正面)")
    if hasattr(face_detector, 'profile_cascade') and not face_detector.profile_cascade.empty():
        method_names.append("Profile Cascade (侧面)")
    if hasattr(face_detector, 'alt_face_cascade') and not face_detector.alt_face_cascade.empty():
        method_names.append("Alternative Cascade (模糊)")

    for i, name in enumerate(method_names):
        print(f"  方法 {i + 1}: {name}")

    # 打开摄像头
    print("\n打开摄像头...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("✗ 无法打开摄像头，尝试使用test_video.mp4...")
        if os.path.exists("test_video.mp4"):
            cap = cv2.VideoCapture("test_video.mp4")
        else:
            print("✗ 无法打开任何视频源")
            exit(1)

    print("✓ 视频源打开成功")

    # 获取摄像头分辨率
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"  分辨率: {width}x{height}")
    print(f"  帧率: {fps if fps > 0 else 'N/A'}")

    # 创建显示窗口
    cv2.namedWindow("人脸检测演示", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("人脸检测演示", 1200, 800)

    print("\n" + "=" * 60)
    print("控制说明:")
    print("  SPACE  - 切换检测方法")
    print("  1/2/3  - 选择方法1/2/3")
    print("  A      - 显示所有方法结果")
    print("  S      - 保存当前帧")
    print("  Q/ESC  - 退出")
    print("=" * 60)

    # 检测方法配置
    current_method = 0  # 0: Haar, 1: Profile, 2: Alt, 3: 全部
    show_all_methods = False

    frame_count = 0
    start_time = time.time()

    # 不同方法的颜色
    method_colors = {
        'Haar Cascade (正面)': (0, 255, 0),  # 绿色
        'Profile Cascade (侧面)': (255, 0, 0),  # 蓝色
        'Alternative Cascade (模糊)': (0, 0, 255)  # 红色
    }

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("无法读取帧，可能视频结束")
                break

            frame_count += 1

            # 复制原始帧用于显示
            display_frame = frame.copy()
            height, width = frame.shape[:2]

            # 计算FPS
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                actual_fps = frame_count / elapsed
                print(f"帧数: {frame_count}, FPS: {actual_fps:.1f}")

            # 检测人脸
            faces = []
            method_used = ""

            if show_all_methods:
                # 使用所有方法
                all_faces = []
                for i, method_name in enumerate(method_names):
                    if i == 0 and hasattr(face_detector, 'face_cascade'):
                        faces_temp = face_detector.face_cascade.detectMultiScale(
                            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(50, 50)
                        )
                        all_faces.extend([(rect, method_name) for rect in faces_temp])

                    elif i == 1 and hasattr(face_detector, 'profile_cascade'):
                        # 检测左侧轮廓
                        faces_temp = face_detector.profile_cascade.detectMultiScale(
                            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(50, 50)
                        )
                        all_faces.extend([(rect, method_name) for rect in faces_temp])

                        # 检测右侧轮廓（翻转图像）
                        flipped = cv2.flip(frame, 1)
                        faces_temp = face_detector.profile_cascade.detectMultiScale(
                            cv2.cvtColor(flipped, cv2.COLOR_BGR2GRAY),
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(50, 50)
                        )
                        # 调整坐标
                        for (x, y, w, h) in faces_temp:
                            all_faces.append(((width - x - w, y, w, h), method_name))

                    elif i == 2 and hasattr(face_detector, 'alt_face_cascade'):
                        faces_temp = face_detector.alt_face_cascade.detectMultiScale(
                            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(50, 50)
                        )
                        all_faces.extend([(rect, method_name) for rect in faces_temp])

                # 绘制所有检测结果
                for (x, y, w, h), method_name in all_faces:
                    color = method_colors.get(method_name, (255, 255, 255))
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(display_frame, method_name.split()[0],
                                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                faces = [rect for rect, _ in all_faces]
                method_used = "所有方法"

            else:
                # 使用当前选择的方法
                if current_method < len(method_names):
                    method_name = method_names[current_method]

                    if current_method == 0 and hasattr(face_detector, 'face_cascade'):
                        faces = face_detector.face_cascade.detectMultiScale(
                            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(50, 50)
                        )

                    elif current_method == 1 and hasattr(face_detector, 'profile_cascade'):
                        # 检测左侧轮廓
                        faces_left = face_detector.profile_cascade.detectMultiScale(
                            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(50, 50)
                        )

                        # 检测右侧轮廓（翻转图像）
                        flipped = cv2.flip(frame, 1)
                        faces_right = face_detector.profile_cascade.detectMultiScale(
                            cv2.cvtColor(flipped, cv2.COLOR_BGR2GRAY),
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(50, 50)
                        )

                        # 合并结果
                        faces = list(faces_left)
                        for (x, y, w, h) in faces_right:
                            faces.append((width - x - w, y, w, h))

                    elif current_method == 2 and hasattr(face_detector, 'alt_face_cascade'):
                        faces = face_detector.alt_face_cascade.detectMultiScale(
                            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(50, 50)
                        )

                    # 绘制检测结果
                    color = method_colors.get(method_name, (255, 255, 255))
                    for (x, y, w, h) in faces:
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(display_frame, f"Face",
                                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                    method_used = method_name

            # 显示信息面板
            info_y = 30
            line_height = 25

            # 方法信息
            cv2.putText(display_frame, f"方法: {method_used}", (10, info_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            info_y += line_height

            # 检测到的人脸数量
            cv2.putText(display_frame, f"检测到人脸: {len(faces)}", (10, info_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            info_y += line_height

            # 帧数
            cv2.putText(display_frame, f"帧: {frame_count}", (10, info_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # 颜色图例
            legend_y = height - 100
            if show_all_methods:
                cv2.putText(display_frame, "颜色图例:", (10, legend_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                legend_y += 20

                for i, (method_name, color) in enumerate(method_colors.items()):
                    cv2.circle(display_frame, (20, legend_y + i * 20), 5, color, -1)
                    cv2.putText(display_frame, method_name, (30, legend_y + i * 20 + 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

            # 帮助文本
            help_text = "空格:切换方法 | 1/2/3:选择方法 | A:显示全部 | S:截图 | Q:退出"
            cv2.putText(display_frame, help_text, (10, height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

            # 显示图像
            cv2.imshow("人脸检测演示", display_frame)

            # 按键处理
            key = cv2.waitKey(1) & 0xFF

            if key in [27, ord('q'), ord('Q')]:  # ESC 或 Q
                print("用户退出")
                break

            elif key == 32:  # 空格键
                if show_all_methods:
                    show_all_methods = False
                    current_method = 0
                else:
                    current_method = (current_method + 1) % len(method_names)
                print(f"切换到方法: {method_names[current_method] if current_method < len(method_names) else '未知'}")

            elif key == ord('a') or key == ord('A'):
                show_all_methods = not show_all_methods
                status = "开启" if show_all_methods else "关闭"
                print(f"所有方法显示: {status}")

            elif key in [ord('1'), ord('2'), ord('3')]:
                method_index = key - ord('1')
                if method_index < len(method_names):
                    current_method = method_index
                    show_all_methods = False
                    print(f"选择方法 {method_index + 1}: {method_names[method_index]}")

            elif key == ord('s') or key == ord('S'):
                # 保存截图
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"face_detection_{timestamp}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"截图已保存: {filename}")

    except KeyboardInterrupt:
        print("\n程序被中断")

    except Exception as e:
        print(f"运行时错误: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # 清理
        cap.release()
        cv2.destroyAllWindows()

        # 显示统计信息
        if frame_count > 0:
            total_time = time.time() - start_time
            avg_fps = frame_count / total_time
            print("\n" + "=" * 60)
            print("演示统计:")
            print(f"总帧数: {frame_count}")
            print(f"总时间: {total_time:.2f} 秒")
            print(f"平均FPS: {avg_fps:.2f}")
            print("=" * 60)

except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print("请确保在项目根目录运行此脚本")
    print("当前目录:", os.getcwd())

except Exception as e:
    print(f"✗ 初始化失败: {e}")
    import traceback

    traceback.print_exc()