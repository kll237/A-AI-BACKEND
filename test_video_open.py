import cv2
import os

print("Testing video file opening...")
video_path = "test_video.mp4"
print(f"File exists: {os.path.exists(video_path)}")
print(f"File size: {os.path.getsize(video_path)} bytes")

# 尝试用OpenCV打开
cap = cv2.VideoCapture(video_path)
if cap.isOpened():
    print("Video opened successfully!")
    ret, frame = cap.read()
    if ret:
        print(f"Frame shape: {frame.shape}")
    else:
        print("Failed to read frame")
    cap.release()
else:
    print("Failed to open video")
    # 显示OpenCV信息
    print(f"OpenCV version: {cv2.__version__}")

