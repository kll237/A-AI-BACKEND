import cv2
import argparse
import time
import os


def main():
    parser = argparse.ArgumentParser(description='简单视频查看器')
    parser.add_argument('--source', type=str, required=True, help='视频源: 文件路径、摄像头ID、RTSP/HTTP URL')
    parser.add_argument('--width', type=int, default=1280, help='显示宽度')
    parser.add_argument('--height', type=int, default=720, help='显示高度')

    args = parser.parse_args()

    source = args.source
    display_width = args.width
    display_height = args.height

    print("=" * 60)
    print("简单视频查看器")
    print("=" * 60)
    print(f"视频源: {source}")

    # 尝试不同方式打开视频
    cap = None

    # 方法1：如果是数字，当作摄像头
    if source.isdigit():
        camera_id = int(source)
        print(f"尝试打开摄像头 #{camera_id}")
        cap = cv2.VideoCapture(camera_id)
        # Windows上尝试用DSHOW后端
        if not cap.isOpened():
            print(f"尝试用DSHOW后端打开摄像头 #{camera_id}")
            cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)

    # 方法2：如果是文件路径
    elif os.path.exists(source):
        print(f"打开本地文件: {source}")
        cap = cv2.VideoCapture(source)

    # 方法3：直接作为URL/RTSP
    else:
        print(f"作为URL/RTSP流打开: {source}")
        cap = cv2.VideoCapture(source)

    # 检查是否打开成功
    if not cap or not cap.isOpened():
        print("错误：无法打开视频源！")
        print("可能的原因：")
        print("1. 文件不存在或格式不支持")
        print("2. 摄像头未连接或ID错误")
        print("3. 网络流地址错误或无网络连接")
        print("4. 缺少编解码器")
        return

    print("✓ 视频源打开成功！")

    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0  # 默认值

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"原始尺寸: {frame_width} x {frame_height}")
    print(f"帧率: {fps:.2f} FPS")

    # 创建窗口
    window_name = f"视频查看器: {source[:50]}..."
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, display_width, display_height)

    print("\n控制键：")
    print("  Q / ESC - 退出")
    print("  P / 空格 - 暂停/继续")
    print("  S - 保存当前帧为图片")
    print("  F - 全屏切换")
    print("  +/- - 调整播放速度")
    print("=" * 60)

    paused = False
    frame_count = 0
    play_speed = 1.0  # 播放速度倍数
    start_time = time.time()
    fullscreen = False

    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print(f"视频结束 (共 {frame_count} 帧)")
                    break

                frame_count += 1

                # 每100帧显示一次状态
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    actual_fps = frame_count / elapsed
                    print(f"帧数: {frame_count}, 实际FPS: {actual_fps:.1f}")

                # 调整尺寸
                if frame_width != display_width or frame_height != display_height:
                    frame = cv2.resize(frame, (display_width, display_height))

                # 在画面上显示信息
                info_text = f"Frame: {frame_count} | FPS: {actual_fps:.1f}" if frame_count > 1 else "Loading..."
                if paused:
                    info_text += " [PAUSED]"

                cv2.putText(frame, info_text, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Press Q to quit, P to pause", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

                cv2.imshow(window_name, frame)

            # 处理按键
            wait_time = int(1000 / (fps * play_speed)) if not paused else 100
            key = cv2.waitKey(wait_time) & 0xFF

            if key in [27, ord('q'), ord('Q')]:  # ESC 或 Q
                print("用户退出")
                break
            elif key in [ord('p'), ord('P'), 32]:  # P 或 空格
                paused = not paused
                status = "暂停" if paused else "继续"
                print(f"{status}播放")
            elif key == ord('s') or key == ord('S'):
                # 保存截图
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.jpg"
                if not paused:
                    ret, frame_to_save = cap.read()
                    if ret:
                        cv2.imwrite(filename, frame_to_save)
                        print(f"截图已保存: {filename}")
                else:
                    cv2.imwrite(filename, frame)
                    print(f"截图已保存: {filename}")
            elif key == ord('f') or key == ord('F'):
                # 全屏切换
                fullscreen = not fullscreen
                if fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                print(f"全屏: {'开' if fullscreen else '关'}")
            elif key == ord('+'):
                play_speed = min(play_speed + 0.25, 4.0)
                print(f"播放速度: {play_speed:.2f}x")
            elif key == ord('-'):
                play_speed = max(play_speed - 0.25, 0.25)
                print(f"播放速度: {play_speed:.2f}x")

    except KeyboardInterrupt:
        print("\n程序被中断")
    except Exception as e:
        print(f"运行时错误: {e}")
    finally:
        # 清理
        if cap:
            cap.release()
        cv2.destroyAllWindows()

        # 显示统计信息
        if frame_count > 0:
            elapsed = time.time() - start_time
            actual_fps = frame_count / elapsed
            print("\n" + "=" * 60)
            print("播放统计:")
            print(f"总帧数: {frame_count}")
            print(f"总时间: {elapsed:.2f} 秒")
            print(f"平均FPS: {actual_fps:.2f}")
            print("=" * 60)


if __name__ == "__main__":
    main()