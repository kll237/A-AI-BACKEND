import cv2
import numpy as np
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler


class CameraHandler(BaseHTTPRequestHandler):
    camera = None

    def do_GET(self):
        if self.path == '/video':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()

            while True:
                ret, frame = CameraHandler.camera.read()
                if not ret:
                    # 生成一个测试图案
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, "Camera Stream", (50, 240),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # 编码为JPEG
                ret, jpeg = cv2.imencode('.jpg', frame)
                data = jpeg.tobytes()

                # 发送帧
                self.wfile.write(b'--frame\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(data))
                self.end_headers()
                self.wfile.write(data)
                self.wfile.write(b'\r\n')

                time.sleep(0.033)  # ~30 FPS


def start_server():
    # 打开摄像头
    CameraHandler.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    CameraHandler.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    CameraHandler.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not CameraHandler.camera.isOpened():
        print("无法打开摄像头")
        return

    print("摄像头服务器已启动")
    print("访问地址: http://localhost:8000/video")

    # 启动HTTP服务器
    server = HTTPServer(('localhost', 8000), CameraHandler)
    print("按 Ctrl+C 停止服务器")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    finally:
        CameraHandler.camera.release()
        server.server_close()


if __name__ == "__main__":
    start_server()