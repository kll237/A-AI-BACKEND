# test_local_cam.py
import cv2

print("测试本地摄像头...")
for i in range(5):  # 测试索引 0-4
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✓ 找到摄像头 {i}")
        ret, frame = cap.read()
        if ret:
            print(f"  可以读取，帧尺寸: {frame.shape}")
            cv2.imshow(f'Camera {i}', frame)
            cv2.waitKey(1000)  # 显示1秒
            cv2.destroyAllWindows()
        else:
            print("  但无法读取帧")
        cap.release()
    else:
        print(f"✗ 摄像头 {i} 不可用")