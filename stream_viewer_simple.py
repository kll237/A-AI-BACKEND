import cv2
import argparse
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera-id', type=str, help='Camera ID')
    parser.add_argument('--rtsp-url', type=str, help='RTSP URL')
    parser.add_argument('--role', type=str, default='user')
    parser.add_argument('--width', type=int, default=1280)
    parser.add_argument('--height', type=int, default=720)

    args = parser.parse_args()

    # Determine video source
    if args.rtsp_url:
        source = args.rtsp_url
    elif args.camera_id:
        source = args.camera_id
    else:
        logger.error("Need --camera-id or --rtsp-url")
        return

    logger.info(f"Opening video source: {source}")

    # Direct open, skip validation
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        logger.warning("First attempt failed, trying alternative...")
        if isinstance(source, str) and source.isdigit():
            cap = cv2.VideoCapture(int(source), cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        logger.error("Cannot open video source")
        return

    logger.info("Video opened successfully")

    window_name = "Stream Viewer"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame")
                break

            frame_count += 1

            # Show info
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                logger.info(f"Frame: {frame_count}, FPS: {fps:.1f}")

            # Resize
            frame = cv2.resize(frame, (args.width, args.height))

            # Add text
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        logger.info("Interrupted")
    finally:
        cap.release()
        cv2.destroyAllWindows()

        elapsed = time.time() - start_time
        if frame_count > 0:
            logger.info(f"Playback ended - Frames: {frame_count}, FPS: {frame_count / elapsed:.1f}")


if __name__ == "__main__":
    main()