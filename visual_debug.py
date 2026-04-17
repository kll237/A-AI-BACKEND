import cv2
from ultralytics import YOLO
import time

print("可视化调试模式")
print("将显示所有检测结果和详细信息")

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)

frame_count = 0
total_detections = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        original_frame = frame.copy()

        # 进行检测
        start_time = time.time()
        results = model(frame, verbose=False)[0]
        inference_time = (time.time() - start_time) * 1000  # 转为毫秒

        detections_this_frame = 0

        if results.boxes is not None:
            for i, box in enumerate(results.boxes):
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # 不同置信度用不同颜色
                if conf > 0.7:
                    color = (0, 255, 0)  # 绿色 - 高置信度
                elif conf > 0.5:
                    color = (0, 255, 255)  # 黄色 - 中置信度
                else:
                    color = (0, 165, 255)  # 橙色 - 低置信度

                # 绘制框
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # 标签背景
                label = f"{class_name} {conf:.2f}"
                (label_width, label_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(frame, (x1, y1 - label_height - 10),
                              (x1 + label_width, y1), color, -1)

                # 标签文字
                cv2.putText(frame, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

                detections_this_frame += 1
                total_detections += 1

        # 显示统计信息
        info_y = 30
        line_height = 25

        cv2.putText(frame, f"Frame: {frame_count}", (10, info_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        info_y += line_height

        cv2.putText(frame, f"Inference: {inference_time:.1f}ms", (10, info_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        info_y += line_height

        cv2.putText(frame, f"Detections: {detections_this_frame}", (10, info_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        info_y += line_height

        cv2.putText(frame, f"Total: {total_detections}", (10, info_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 显示帮助
        cv2.putText(frame, "拿物品到摄像头前: 手机, 书, 杯子, 人等", (10, frame.shape[0] - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, "按 Q 退出", (10, frame.shape[0] - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # 并排显示原始帧和检测帧
        combined = cv2.hconcat([original_frame, frame])
        cv2.imshow("Left: Original | Right: Detections", combined)

        # 在控制台也输出信息
        if detections_this_frame > 0:
            print(f"Frame {frame_count}: 检测到 {detections_this_frame} 个物体, 耗时 {inference_time:.1f}ms")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("程序中断")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n=== 统计信息 ===")
    print(f"总帧数: {frame_count}")
    print(f"总检测数: {total_detections}")
    print(f"平均每帧检测数: {total_detections / max(1, frame_count):.2f}")