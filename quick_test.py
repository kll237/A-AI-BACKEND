# quick_test.py - 最简单的摄像头测试
import cv2
import time


def main():
    # 走廊摄像头的RTSP
    url = "rtsp://admin:SrxnS@2005@117.199.228.85:554/Streaming/Channels/401"

    print(f"尝试连接: {url}")
    print("按 Ctrl+C 停止")

    # 设置超时
    cv2.setNumThreads(1)

    # 尝试打开
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

    # 设置超时时间（毫秒）
    cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)  # 10秒

    start = time.time()

    try:
        if not cap.isOpened():
            print(f"连接失败! 耗时: {time.time() - start:.2f}秒")
            return

        print(f"连接成功! 耗时: {time.time() - start:.2f}秒")

        # 尝试读取一帧
        ret, frame = cap.read()
        if ret:
            print(f"成功读取帧! 尺寸: {frame.shape}")

            # 显示
            cv2.imshow('Test', frame)
            print("窗口已显示，按任意键关闭")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("读取帧失败")

    except Exception as e:
        print(f"错误: {e}")
    finally:
        cap.release()
        print("测试结束")


if __name__ == "__main__":
    main()