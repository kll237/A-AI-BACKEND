# D:\jsjxm\A-AI-BACKEND\multi_detection.py
import cv2
import numpy as np
from datetime import datetime
import time


def main():
    print("=" * 60)
    print("智能摄像头 - 多目标检测测试")
    print("=" * 60)

    # 测试不同的摄像头索引
    camera_indices = [0, 1, 2]
    selected_camera = 0

    for idx in camera_indices:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            print(f"✓ 找到摄像头 {idx}")
            cap.release()
            selected_camera = idx
            break
        else:
            print(f"✗ 摄像头 {idx} 不可用")

    print(f"\n使用摄像头: {selected_camera}")

    # 创建YOLO模型
    try:
        from ultralytics import YOLO
        print("正在加载YOLO模型...")
        model = YOLO('yolov8n.pt')
        print("✓ YOLOv8n模型加载成功")

        # 显示支持的类别
        print(f"模型支持 {len(model.names)} 种物体检测")
        print("常见物体：人、汽车、自行车、手机、书包等")

    except ImportError as e:
        print(f"✗ 无法导入YOLO: {e}")
        print("请安装: pip install ultralytics")
        return
    except Exception as e:
        print(f"✗ 加载模型失败: {e}")
        # 使用OpenCV的Haar级联作为备选
        print("使用OpenCV基础检测...")
        model = None

    # 打开摄像头
    cap = cv2.VideoCapture(selected_camera)
    if not cap.isOpened():
        print("✗ 无法打开摄像头")
        return

    print("\n" + "=" * 60)
    print("操作说明:")
    print("1. 按 'q' 退出程序")
    print("2. 按 's' 保存当前截图")
    print("3. 按 'd' 显示/隐藏检测框")
    print("4. 按 'i' 显示检测信息")
    print("=" * 60)
    print("\n摄像头已启动，请将物体放在摄像头前...")

    show_detections = True
    show_info = True
    frame_count = 0
    fps = 0
    last_time = time.time()

    # 常见物体的中文名称映射
    chinese_names = {
        "person": "👤 人",
        "bicycle": "🚲 自行车",
        "car": "🚗 汽车",
        "motorcycle": "🏍️ 摩托车",
        "bus": "🚌 公交车",
        "truck": "🚚 卡车",
        "handbag": "👜 手提包",
        "umbrella": "☂️ 雨伞",
        "backpack": "🎒 背包",
        "cell phone": "📱 手机",
        "laptop": "💻 笔记本电脑",
        "book": "📖 书",
        "bottle": "🍶 瓶子",
        "cup": "🥤 杯子",
        "chair": "🪑 椅子",
        "dog": "🐕 狗",
        "cat": "🐈 猫"
    }

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("读取帧失败，重新尝试...")
                time.sleep(0.1)
                continue

            frame_count += 1

            # 计算FPS
            current_time = time.time()
            if current_time - last_time >= 1.0:
                fps = frame_count
                frame_count = 0
                last_time = current_time

            display_frame = frame.copy()

            # 使用YOLO进行检测
            if model and show_detections:
                results = model(frame, verbose=False)

                if len(results) > 0:
                    detections = results[0]

                    # 绘制检测框
                    annotated_frame = detections.plot()
                    display_frame = annotated_frame

                    # 收集检测到的物体
                    detected_items = {}
                    if detections.boxes is not None and len(detections.boxes) > 0:
                        for box, cls, conf in zip(detections.boxes.xyxy,
                                                  detections.boxes.cls,
                                                  detections.boxes.conf):
                            class_name = model.names[int(cls)]
                            confidence = float(conf)

                            if confidence > 0.25:  # 置信度阈值
                                chinese_name = chinese_names.get(class_name, f"📦 {class_name}")
                                detected_items[chinese_name] = detected_items.get(chinese_name, 0) + 1

                    # 显示检测统计
                    if show_info and detected_items:
                        y_offset = 70
                        cv2.putText(display_frame, "检测到的物体:", (10, y_offset),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                        y_offset += 25

                        for item, count in list(detected_items.items())[:6]:  # 最多显示6种
                            cv2.putText(display_frame, f"  {item}: {count}个", (10, y_offset),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2)
                            y_offset += 22

            # 显示FPS和状态信息
            status_text = f"FPS: {fps} | 检测: {'开' if show_detections else '关'} | 信息: {'开' if show_info else '关'}"
            cv2.putText(display_frame, status_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # 显示提示
            cv2.putText(display_frame, "按 'q' 退出 | 's' 保存 | 'd' 切换检测 | 'i' 切换信息",
                        (10, display_frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # 显示窗口
            cv2.imshow('多目标检测测试', display_frame)

            # 键盘控制
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存截图
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"detection_test_{timestamp}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"✓ 截图已保存: {filename}")
            elif key == ord('d'):
                show_detections = not show_detections
                print(f"检测框: {'开启' if show_detections else '关闭'}")
            elif key == ord('i'):
                show_info = not show_info
                print(f"检测信息: {'开启' if show_info else '关闭'}")

    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n测试结束")


if __name__ == "__main__":
    main()