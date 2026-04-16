import cv2
import numpy as np


def detect_cameras():
    """检测所有可用的摄像头"""
    print("正在检测摄像头...")
    print("=" * 50)

    available_cameras = []

    # 尝试索引0-10
    for index in range(0, 11):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # Windows使用DirectShow

        if cap.isOpened():
            # 尝试读取一帧
            ret, frame = cap.read()
            if ret:
                # 获取摄像头信息
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)

                print(f"摄像头 {index}: 可用")
                print(f"  分辨率: {width}x{height}")
                print(f"  FPS: {fps}")

                # 保存一帧作为预览
                cv2.imwrite(f'camera_{index}_preview.jpg', frame)
                print(f"  预览已保存: camera_{index}_preview.jpg")

                available_cameras.append(index)
            else:
                print(f"摄像头 {index}: 可打开但无法读取帧")

            cap.release()
        else:
            print(f"摄像头 {index}: 不可用")

    print("=" * 50)
    return available_cameras


def test_usb_camera_stream(index=0):
    """测试摄像头流"""
    print(f"\n测试摄像头 {index} 的实时流...")

    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("无法打开摄像头")
        return

    # 设置合适的参数
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    print("按 'q' 键退出预览")
    print("按 's' 键保存当前帧")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取帧")
            break

        # 显示帧
        cv2.imshow(f'Camera {index} - Press Q to quit', frame)

        frame_count += 1
        if frame_count % 30 == 0:
            print(f"已处理 {frame_count} 帧")

        # 按键处理
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite(f'captured_frame_{frame_count}.jpg', frame)
            print(f"帧已保存: captured_frame_{frame_count}.jpg")

    cap.release()
    cv2.destroyAllWindows()
    print(f"测试完成，总共处理 {frame_count} 帧")


if __name__ == "__main__":
    # 第一步：检测所有摄像头
    cameras = detect_cameras()

    if cameras:
        print(f"\n找到 {len(cameras)} 个可用摄像头: {cameras}")

        # 第二步：测试第一个摄像头
        test_index = cameras[0]
        test = input(f"\n是否测试摄像头 {test_index}？(y/n): ")

        if test.lower() == 'y':
            test_usb_camera_stream(test_index)
    else:
        print("\n未找到可用的摄像头！")
        print("请检查：")
        print("1. 摄像头是否正确连接")
        print("2. 摄像头驱动程序是否安装")
        print("3. 是否被其他程序占用")