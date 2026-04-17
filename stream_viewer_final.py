import os
import sys
import cv2
import json
import time
import argparse
import numpy as np
import logging
import subprocess
import platform
import urllib.request

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("stream_viewer")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print("=" * 60)
print("AI视频流查看器 - 网络流兼容版 (窗口优化版)")
print("=" * 60)


class SimpleYOLOModel:
    def __init__(self):
        logger.info("初始化简化的YOLO模型")
        try:
            from ultralytics import YOLO
            self.model = YOLO('yolov8n.pt')
            self.has_yolo = True
            logger.info("✓ 加载YOLOv8模型成功")
        except ImportError:
            self.has_yolo = False
            logger.warning("✗ 无法导入ultralytics，使用简化检测")

    def detect_persons(self, frame):
        if not self.has_yolo: return []
        try:
            results = self.model(frame, verbose=False)[0]
            detections = []
            if results.boxes is not None:
                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    if cls_id == 0 and conf > 0.5:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        detections.append({"bbox": (x1, y1, x2, y2), "confidence": conf, "class_name": "person"})
            return detections
        except Exception as e:
            logger.error(f"YOLO检测错误:{e}");return []


class SimpleFaceDetector:
    def __init__(self, min_face_size=(50, 50)):
        logger.info("初始化人脸检测器")
        self.min_face_size = min_face_size
        self.face_cascade = None
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if self.face_cascade.empty():
                logger.warning("Haar级联检测器加载失败")
                self.face_cascade = None
            else:
                logger.info("✓ Haar人脸检测器加载成功")
        except Exception as e:
            logger.warning(f"人脸检测器初始化错误:{e}")

    def detect_faces(self, frame):
        """检测人脸"""
        if self.face_cascade is None:
            return []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=self.min_face_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            return faces
        except Exception as e:
            logger.error(f"人脸检测错误: {e}")
            return []


def check_ffmpeg_installed():
    """最终修复版：检查FFmpeg是否安装"""
    print("正在检查FFmpeg安装...")
    ffmpeg_found = False
    possible_paths = [
        r"C:\Program Files\FFmpeg\bin",
        r"C:\FFmpeg\bin",
        r"D:\Program Files\FFmpeg\bin",
        r"D:\FFmpeg\bin",
        r"E:\FFmpeg\bin",
        r"C:\Users\Public\FFmpeg\bin",
        r"C:\Users\{}\AppData\Local\ffmpeg\bin".format(os.getenv("USERNAME")),
    ]
    original_path = os.environ.get('PATH', '')
    for path in possible_paths:
        ffmpeg_exe = os.path.join(path, 'ffmpeg.exe')
        if os.path.exists(ffmpeg_exe):
            print(f"✓ 在以下位置找到FFmpeg: {path}")
            os.environ['PATH'] = path + ';' + original_path
            ffmpeg_found = True
            break
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, shell=True, timeout=10)
        if result.returncode == 0 and 'ffmpeg version' in result.stdout:
            lines = result.stdout.split('\n')
            if lines: version_line = lines[0].strip();print(f"✓ FFmpeg 已正确安装");print(f"  版本: {version_line}")
            try:
                where_result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True, shell=True,
                                              timeout=5)
                if where_result.returncode == 0 and where_result.stdout.strip():
                    path = where_result.stdout.strip().split('\n')[0]
                    print(f"  路径: {path}")
            except:
                pass
            return True
        else:
            if ffmpeg_found:
                print("✓ FFmpeg 文件存在但可能有问题")
                return True
            else:
                print("⚠ FFmpeg 命令执行失败")
    except subprocess.TimeoutExpired:
        if ffmpeg_found:
            print("✓ FFmpeg 存在但检测超时");return True
        else:
            print("⚠ FFmpeg 检测超时")
    except FileNotFoundError:
        if ffmpeg_found:
            print("✓ FFmpeg 文件存在但不在PATH");return True
        else:
            print("⚠ 未找到FFmpeg，建议安装以获得更好的网络流支持")
    except Exception as e:
        if ffmpeg_found:
            print(f"✓ FFmpeg 存在但检测异常: {str(e)[:50]}");return True
        else:
            print(f"⚠ FFmpeg 检测异常: {str(e)[:50]}")
    return ffmpeg_found


def validate_video_source(source, timeout=5):
    print(f"\n正在验证视频源:{source}")
    if source.isdigit():
        print("检测到本地摄像头索引")
        backends = [None, cv2.CAP_DSHOW, cv2.CAP_V4L2, cv2.CAP_ANY]
        for backend in backends:
            try:
                if backend:
                    cap = cv2.VideoCapture(int(source), backend)
                else:
                    cap = cv2.VideoCapture(int(source))
                if cap.isOpened():
                    for _ in range(10):
                        ret, frame = cap.read()
                        if ret: cap.release();print(f"✓ 本地摄像头{source}验证成功");return True
                        time.sleep(0.1)
                    print(f"⚠ 摄像头{source}打开成功但无法立即读取帧");
                    cap.release();
                    return True
                cap.release()
            except:
                pass
        print(f"✗ 本地摄像头{source}不可用");
        return False
    if os.path.exists(source):
        print("检测到本地文件")
        ext = os.path.splitext(source)[1].lower()
        common_video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpg', '.mpeg']
        if ext in common_video_exts:
            backends = [None, cv2.CAP_FFMPEG, cv2.CAP_ANY]
            for backend in backends:
                try:
                    if backend:
                        cap = cv2.VideoCapture(source, backend)
                    else:
                        cap = cv2.VideoCapture(source)
                    if cap.isOpened():
                        for _ in range(5):
                            ret, frame = cap.read()
                            if ret: cap.release();print(f"✓ 视频文件验证成功");return True
                            time.sleep(0.1)
                        cap.release()
                except:
                    pass
            print(f"✗ 无法打开视频文件:{source}");
            return False
        else:
            print(f"⚠ 不常见的文件扩展名:{ext}")
            cap = cv2.VideoCapture(source)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret: print(f"✓ 文件验证成功");return True
            print(f"✗ 无法打开文件:{source}");
            return False
    print("检测到网络流")
    if source.startswith(('rtsp://', 'rtmp://', 'http://', 'https://')):
        print(f"URL格式:{source[:50]}...")
        check_ffmpeg_installed()
        max_timeout = 15
        start_time = time.time()
        backends_and_methods = [(cv2.CAP_FFMPEG, "FFMPEG后端"), (cv2.CAP_ANY, "自动后端"), (None, "默认后端")]
        for backend, method_name in backends_and_methods:
            if time.time() - start_time > max_timeout: break
            print(f"尝试使用{method_name}...")
            try:
                if backend:
                    cap = cv2.VideoCapture(source, backend)
                else:
                    cap = cv2.VideoCapture(source)
                if cap.isOpened():
                    if source.startswith('rtsp://'):
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 30000)
                    frame_count = 0
                    for attempt in range(15):
                        if time.time() - start_time > max_timeout: break
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            cap.release();
                            print(f"✓ 网络流验证成功({method_name})")
                            print(f"  读取到有效帧:{frame.shape}");
                            return True
                        elif ret:
                            frame_count += 1
                            if frame_count >= 2: cap.release();print(f"✓ 网络流验证成功({method_name})");return True
                        time.sleep(0.2)
                    cap.release()
                    print(f"⚠ 流打开成功但无法立即读取({method_name})")
            except Exception as e:
                print(f"  {method_name}错误:{str(e)[:100]}")
        print("尝试备用验证方法...")
        try:
            cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
            if cap.isOpened():
                time.sleep(1);
                cap.release();
                print("⚠ 流可以打开但无法验证内容");
                return True
        except:
            pass
        if source.startswith('http://') or source.startswith('https://'):
            try:
                print("尝试HTTP请求测试...")
                req = urllib.request.Request(source, headers={'User-Agent': 'Mozilla/5.0'})
                response = urllib.request.urlopen(req, timeout=10)
                if response.getcode() == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if 'image' in content_type or 'video' in content_type or 'stream' in content_type:
                        print(f"✓ HTTP资源验证成功:{content_type}");
                        return True
            except Exception as e:
                print(f"HTTP测试错误:{str(e)[:100]}")
        print("✗ 所有验证方法都失败");
        return False
    print("未知类型的视频源")
    try:
        cap = cv2.VideoCapture(source, cv2.CAP_ANY)
        if cap.isOpened():
            cap.release();
            print("⚠ 源可以打开但类型未知");
            return True
    except:
        pass
    print("✗ 无法识别或打开视频源");
    return False


def resize_frame_keep_ratio(frame, target_width, target_height):
    """保持比例调整帧大小，确保完整显示"""
    h, w = frame.shape[:2]

    # 计算缩放比例
    scale_w = target_width / w
    scale_h = target_height / h
    scale = min(scale_w, scale_h)

    # 计算新尺寸
    new_w = int(w * scale)
    new_h = int(h * scale)

    # 调整大小
    resized_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # 创建目标大小的画布，将调整后的帧居中显示
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    offset_x = (target_width - new_w) // 2
    offset_y = (target_height - new_h) // 2
    canvas[offset_y:offset_y + new_h, offset_x:offset_x + new_w] = resized_frame

    return canvas


def preview_video_source(source, preview_time=5):
    print(f"\n正在预览视频源:{source}")
    cap = None
    try:
        if source.isdigit():
            cap = cv2.VideoCapture(int(source), cv2.CAP_ANY)
        elif source.startswith('rtsp://'):
            cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
        elif source.startswith(('http://', 'https://')):
            cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
        else:
            cap = cv2.VideoCapture(source, cv2.CAP_ANY)

        if not cap.isOpened():
            print("✗ 无法打开视频源");
            return False

        preview_window = "视频源预览 - 按任意键继续"
        cv2.namedWindow(preview_window, cv2.WINDOW_NORMAL)
        # 预览窗口设置为更小的尺寸 640x480
        cv2.resizeWindow(preview_window, 640, 480)

        print(f"显示视频预览中({preview_time}秒)...");
        print("按任意键提前结束预览")
        start_time = time.time();
        frame_count = 0;
        fps = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"无法读取帧(已读取{frame_count}帧)");
                break

            frame_count += 1
            current_time = time.time();
            elapsed = current_time - start_time
            if elapsed > 0: fps = frame_count / elapsed

            # 调整帧大小以适应预览窗口
            display_frame = resize_frame_keep_ratio(frame, 640, 480)

            info_frame = display_frame.copy()
            info_texts = [
                f"视频源:{source[:40]}...",
                f"帧数:{frame_count}",
                f"FPS:{fps:.1f}",
                f"原始分辨率:{frame.shape[1]}x{frame.shape[0]}",
                f"显示分辨率:640x480",
                f"时间:{elapsed:.1f}/{preview_time}秒",
                "按任意键继续..."
            ]
            y_offset = 30
            for text in info_texts:
                cv2.putText(info_frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                y_offset += 25

            cv2.imshow(preview_window, info_frame)
            elapsed = time.time() - start_time

            if elapsed > preview_time:
                print(f"预览超时({preview_time}秒)");
                break
            if cv2.waitKey(1) != -1:
                print("用户按键结束预览");
                break

        cv2.destroyWindow(preview_window)
        cap.release()

        if frame_count > 0:
            print(f"✓ 预览成功，共读取{frame_count}帧，平均FPS:{fps:.1f}")
            return True
        else:
            print("✗ 预览失败，无法读取任何帧")
            return False

    except Exception as e:
        print(f"✗ 预览错误:{e}")
        if cap: cap.release()
        try:
            cv2.destroyWindow(preview_window)
        except:
            pass
        return False


class StreamViewer:
    def __init__(self, camera_id=None, rtsp_url=None, display_width=800, display_height=600):
        # 默认窗口大小改为800x600（更小更合适）
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.display_width = display_width
        self.display_height = display_height
        self.window_name = "AI视频流查看器"
        self.enable_person_detection = True
        self.enable_face_detection = True
        self.show_info_overlay = True
        self._load_config()
        self.yolo_model = SimpleYOLOModel()
        self.face_detector = SimpleFaceDetector()
        self.fps_history = []
        self.frame_count = 0
        self.start_time = time.time()
        logger.info(f"流查看器初始化完成 - 窗口大小: {display_width}x{display_height}")

    def _load_config(self):
        config_dir = os.path.join("data")
        cameras_file = os.path.join(config_dir, "cameras.json")
        self.cameras = {}
        if os.path.exists(cameras_file):
            try:
                encodings = ['utf-8', 'gbk', 'utf-8-sig', 'latin-1']
                for encoding in encodings:
                    try:
                        with open(cameras_file, 'r', encoding=encoding) as f:
                            self.cameras = json.load(f)
                        logger.info(f"✓ 加载摄像头配置成功({encoding})")
                        logger.info(f"  找到{len(self.cameras)}个摄像头")
                        break
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
            except Exception as e:
                logger.warning(f"加载摄像头配置失败:{e}")
        else:
            logger.warning(f"摄像头配置文件不存在:{cameras_file}")

        if self.camera_id and not self.rtsp_url:
            if self.camera_id in self.cameras:
                camera_info = self.cameras[self.camera_id]
                self.rtsp_url = camera_info.get("rtsp_url", "")
                self.camera_name = camera_info.get("name", f"摄像头{self.camera_id}")
                logger.info(f"使用摄像头:{self.camera_name}")
                logger.info(f"视频源:{self.rtsp_url}")
            else:
                logger.warning(f"摄像头ID{self.camera_id}未找到，使用默认摄像头")
                self.rtsp_url = "0"
                self.camera_name = "默认摄像头"
        else:
            self.camera_name = "视频流"

        if not self.rtsp_url:
            self.rtsp_url = "0"
            self.camera_name = "默认摄像头"
            logger.info(f"使用默认摄像头:{self.rtsp_url}")

    def _calculate_fps(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        if elapsed > 0:
            return self.frame_count / elapsed
        return 0

    def process_frame(self, frame):
        if frame is None or frame.size == 0:
            return frame

        # 先保存原始帧用于处理检测
        original_frame = frame.copy()
        height, width = original_frame.shape[:2]
        self.frame_count += 1

        if self.frame_count % 30 == 0:
            self.current_fps = self._calculate_fps()

        # 调整帧大小以适应显示窗口（保持比例）
        display_frame = resize_frame_keep_ratio(original_frame, self.display_width, self.display_height)
        result_frame = display_frame.copy()

        # 获取调整后的显示尺寸
        display_h, display_w = display_frame.shape[:2]

        if self.show_info_overlay:
            # 信息叠加（调整字体大小适配小窗口）
            cv2.putText(result_frame, f"摄像头:{self.camera_name}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (255, 255, 255), 2)
            fps_text = f"FPS:{getattr(self, 'current_fps', 0):.1f}"
            cv2.putText(result_frame, fps_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(result_frame, f"帧数:{self.frame_count}", (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (255, 255, 255), 2)

            # 显示分辨率信息
            cv2.putText(result_frame, f"原始:{width}x{height}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)
            cv2.putText(result_frame, f"显示:{display_w}x{display_h}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)

            status_y = 145
            if self.enable_person_detection:
                cv2.putText(result_frame, "人体检测:ON", (10, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            else:
                cv2.putText(result_frame, "人体检测:OFF", (10, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            if self.enable_face_detection:
                cv2.putText(result_frame, "人脸检测:ON", (10, status_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 1)
            else:
                cv2.putText(result_frame, "人脸检测:OFF", (10, status_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 255), 1)

        if self.enable_person_detection:
            try:
                detections = self.yolo_model.detect_persons(original_frame)

                # 计算缩放比例（用于将检测框映射到显示帧）
                scale_w = display_w / width
                scale_h = display_h / height
                scale = min(scale_w, scale_h)

                # 计算偏移量
                offset_x = (self.display_width - int(width * scale)) // 2
                offset_y = (self.display_height - int(height * scale)) // 2

                for detection in detections:
                    bbox = detection["bbox"]
                    confidence = detection["confidence"]
                    x1, y1, x2, y2 = bbox
                    color = (0, 255, 0)

                    # 将检测框坐标映射到显示帧
                    x1_display = int(x1 * scale) + offset_x
                    y1_display = int(y1 * scale) + offset_y
                    x2_display = int(x2 * scale) + offset_x
                    y2_display = int(y2 * scale) + offset_y

                    # 绘制检测框
                    cv2.rectangle(result_frame, (x1_display, y1_display), (x2_display, y2_display), color, 2)
                    label = f"Person {confidence:.2f}"

                    # 调整标签大小
                    (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                    cv2.rectangle(result_frame, (x1_display, y1_display - label_height - 8),
                                  (x1_display + label_width, y1_display), color, -1)
                    cv2.putText(result_frame, label, (x1_display, y1_display - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                                (0, 0, 0), 1)

                    if self.enable_face_detection:
                        person_roi = original_frame[y1:y2, x1:x2]
                        if person_roi.size > 0:
                            faces = self.face_detector.detect_faces(person_roi)
                            for (fx, fy, fw, fh) in faces:
                                # 映射人脸坐标到显示帧
                                face_x1 = int((x1 + fx) * scale) + offset_x
                                face_y1 = int((y1 + fy) * scale) + offset_y
                                face_x2 = int((x1 + fx + fw) * scale) + offset_x
                                face_y2 = int((y1 + fy + fh) * scale) + offset_y

                                cv2.rectangle(result_frame, (face_x1, face_y1), (face_x2, face_y2), (0, 0, 255), 1)
                                cv2.putText(result_frame, "Face", (face_x1, face_y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                                            (0, 0, 255), 1)
            except Exception as e:
                logger.error(f"处理帧错误:{e}")

        # 帮助文本（调整字体大小）
        help_text = "Q:退出 | S:截图 | P:暂停 | 1:人体检测 | 2:人脸检测 | 3:信息显示"
        cv2.putText(result_frame, help_text, (10, result_frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    (150, 150, 150), 1)

        return result_frame

    def start(self):
        logger.info(f"打开视频源:{self.rtsp_url}")
        print(f"\n{'=' * 60}")
        print(f"准备打开视频源:{self.rtsp_url}")
        print(f"窗口大小: {self.display_width}x{self.display_height}")
        print(f"{'=' * 60}")

        if not validate_video_source(self.rtsp_url):
            print("⚠️ 视频源验证失败或警告")
            choice = input("是否仍然尝试打开？(y/n,默认y):").strip().lower()
            if choice == 'n':
                return False

        preview = input("\n是否要预览视频源？(y/n,默认n):").strip().lower()
        if preview == 'y':
            preview_time = input("预览时间(秒,默认5):").strip()
            try:
                preview_time = int(preview_time) if preview_time else 5
            except:
                preview_time = 5
            if not preview_video_source(self.rtsp_url, preview_time):
                print("预览失败，是否继续？")
                cont = input("继续打开主程序？(y/n,默认y):").strip().lower()
                if cont == 'n':
                    return False

        print(f"\n{'=' * 60}")
        print("正在打开主视频窗口...")
        print(f"{'=' * 60}")
        cap = None
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                if self.rtsp_url.isdigit():
                    camera_index = int(self.rtsp_url)
                    logger.info(f"使用本地摄像头索引:{camera_index}")
                    backends = [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_V4L2, None]
                    for backend in backends:
                        try:
                            if backend:
                                cap = cv2.VideoCapture(camera_index, backend)
                            else:
                                cap = cv2.VideoCapture(camera_index)
                            if cap.isOpened():
                                break
                        except:
                            continue
                else:
                    logger.info(f"打开视频文件/流:{self.rtsp_url}")
                    if self.rtsp_url.startswith(('rtsp://', 'rtmp://', 'http://', 'https://')):
                        cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
                        if not cap.isOpened():
                            cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_ANY)
                    else:
                        backends = [cv2.CAP_FFMPEG, cv2.CAP_ANY, None]
                        for backend in backends:
                            try:
                                if backend:
                                    cap = cv2.VideoCapture(self.rtsp_url, backend)
                                else:
                                    cap = cv2.VideoCapture(self.rtsp_url)
                                if cap.isOpened():
                                    break
                            except:
                                continue

                if cap and cap.isOpened():
                    logger.info("✓ 视频源打开成功")
                    break
                else:
                    if attempt < max_attempts - 1:
                        logger.info(f"打开失败，尝试备用方法({attempt + 1}/{max_attempts})")
                        time.sleep(1)
                    else:
                        logger.error(f"无法打开视频源:{self.rtsp_url}")
                        print(f"✗ 所有打开方式都失败")
                        if self.rtsp_url.startswith(('rtsp://', 'rtmp://')):
                            print("\n网络流连接建议:")
                            print("1.确保已安装FFmpeg并添加到PATH")
                            print("2.检查网络连接")
                            print("3.确认流服务器在线")
                            print("4.尝试其他流地址")
                        return False
            except Exception as e:
                logger.error(f"打开视频源时出错:{e}")
                if attempt < max_attempts - 1:
                    continue
                else:
                    return False

        # 创建窗口并设置大小（800x600，更小更合适）
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.display_width, self.display_height)

        logger.info("开始播放...")
        logger.info("控制键:Q=退出,S=截图,P=暂停,+/=调整速度")
        logger.info("功能键:1=人体检测开关,2=人脸检测开关,3=信息显示开关")

        paused = False
        play_speed = 1.0
        save_count = 0

        try:
            while True:
                if not paused:
                    ret, frame = cap.read()
                    if not ret:
                        logger.warning("读取帧失败，可能视频结束")
                        if not self.rtsp_url.isdigit():
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            continue
                        else:
                            time.sleep(0.1)
                            continue

                    processed_frame = self.process_frame(frame)
                    cv2.imshow(self.window_name, processed_frame)

                wait_time = int(30 / play_speed) if not paused else 100
                key = cv2.waitKey(wait_time) & 0xFF

                if key == ord('q') or key == 27:
                    logger.info("用户退出")
                    break
                elif key == ord('p') or key == 32:
                    paused = not paused
                    status = "暂停" if paused else "继续"
                    logger.info(f"{status}播放")
                elif key == ord('s'):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp}_{save_count:03d}.jpg"
                    if not paused:
                        ret, frame_to_save = cap.read()
                        if ret:
                            cv2.imwrite(filename, frame_to_save)
                            save_count += 1
                            logger.info(f"截图已保存:{filename}")
                    else:
                        cv2.imwrite(filename, processed_frame)
                        save_count += 1
                        logger.info(f"截图已保存:{filename}")
                elif key == ord('+'):
                    play_speed = min(play_speed + 0.25, 4.0)
                    logger.info(f"播放速度:{play_speed:.2f}x")
                elif key == ord('-'):
                    play_speed = max(play_speed - 0.25, 0.25)
                    logger.info(f"播放速度:{play_speed:.2f}x")
                elif key == ord('1'):
                    self.enable_person_detection = not self.enable_person_detection
                    status = "开启" if self.enable_person_detection else "关闭"
                    logger.info(f"人体检测:{status}")
                elif key == ord('2'):
                    self.enable_face_detection = not self.enable_face_detection
                    status = "开启" if self.enable_face_detection else "关闭"
                    logger.info(f"人脸检测:{status}")
                elif key == ord('3'):
                    self.show_info_overlay = not self.show_info_overlay
                    status = "显示" if self.show_info_overlay else "隐藏"
                    logger.info(f"信息叠加:{status}")
                elif key == ord('f'):
                    if platform.system() == 'Windows':
                        try:
                            import win32gui, win32con
                            hwnd = win32gui.GetForegroundWindow()
                            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                            if style & win32con.WS_MAXIMIZE:
                                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                logger.info("退出全屏")
                            else:
                                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                                logger.info("进入全屏")
                        except ImportError:
                            logger.warning("全屏功能需要pywin32库")

        except KeyboardInterrupt:
            logger.info("程序被中断")
        except Exception as e:
            logger.error(f"运行错误:{e}")
            import traceback
            traceback.print_exc()
        finally:
            if cap:
                cap.release()
            cv2.destroyAllWindows()
            total_time = time.time() - self.start_time
            avg_fps = self.frame_count / total_time if total_time > 0 else 0
            logger.info("=" * 50)
            logger.info("播放统计:")
            logger.info(f"  总帧数:{self.frame_count}")
            logger.info(f"  总时间:{total_time:.2f}秒")
            logger.info(f"  平均FPS:{avg_fps:.2f}")
            logger.info(f"  截图数量:{save_count}")
            logger.info("=" * 50)

        return True


def select_test_source():
    print("\n" + "=" * 60)
    print("选择测试视频源")
    print("=" * 60)
    test_sources = [
        {"id": "1", "name": "Big Buck Bunny (RTSP)",
         "url": "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov", "type": "rtsp",
         "description": "经典动画测试视频"},
        {"id": "2", "name": "本地摄像头0", "url": "0", "type": "camera", "description": "计算机默认摄像头"},
        {"id": "3", "name": "测试视频文件", "url": "test.mp4", "type": "file", "description": "本地测试视频"},
        {"id": "4", "name": "返回主菜单", "url": "", "type": "back", "description": "返回上级菜单"},
    ]
    for source in test_sources:
        print(f"{source['id']}. {source['name']}")
        print(f"   描述:{source['description']}")
        print(f"   类型:{source['type'].upper()}")
        if source['type'] != 'back':
            print(f"   地址:{source['url'][:80]}...")
            print()

    while True:
        choice = input(f"请选择测试源(1-{len(test_sources) - 1})或按0返回:").strip()
        if choice == "0":
            return None
        if choice in [s['id'] for s in test_sources]:
            selected = next(s for s in test_sources if s['id'] == choice)
            if selected['type'] == 'back':
                return None
            print(f"\n选择:{selected['name']}")
            print(f"地址:{selected['url']}")
            if validate_video_source(selected['url']):
                preview = input("是否预览？(y/n,默认n):").strip().lower()
                if preview == 'y':
                    preview_time = input("预览时间(秒,默认3):").strip()
                    try:
                        preview_time = int(preview_time) if preview_time else 3
                    except:
                        preview_time = 3
                    preview_video_source(selected['url'], preview_time)
                use_it = input("使用这个视频源？(y/n,默认y):").strip().lower()
                if use_it != 'n':
                    return {"rtsp_url": selected['url']}
            else:
                print("测试源验证失败，请选择其他源")
                continue
        else:
            print("无效选择")


def interactive_menu():
    print("\n" + "=" * 60)
    print("AI视频流查看器 - 主菜单")
    print("=" * 60)
    print("1.使用本地摄像头")
    print("2.使用视频文件")
    print("3.从配置文件选择摄像头")
    print("4.手动输入视频源")
    print("5.选择测试视频源")
    print("6.列出可用摄像头")
    print("7.检查FFmpeg安装")
    print("8.退出程序")
    print("=" * 60)
    choice = input("请选择(1-8):").strip()

    if choice == "1":
        print("\n" + "=" * 40)
        print("检测本地摄像头...")
        print("=" * 40)
        available_cameras = []
        for i in range(5):
            for backend in [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_V4L2, None]:
                try:
                    if backend:
                        cap = cv2.VideoCapture(i, backend)
                    else:
                        cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        available_cameras.append(i)
                        cap.release()
                        break
                    cap.release()
                except:
                    continue

        if available_cameras:
            print(f"找到{len(available_cameras)}个摄像头:")
            for cam in available_cameras:
                print(f"  摄像头{cam}")

            cam_choice = input(f"\n选择摄像头编号(0-{len(available_cameras) - 1}，默认0):").strip()
            if not cam_choice:
                cam_choice = "0"
            if cam_choice.isdigit() and int(cam_choice) in available_cameras:
                source = cam_choice
                if validate_video_source(source):
                    preview = input("是否预览？(y/n,默认n):").strip().lower()
                    if preview == 'y':
                        preview_time = input("预览时间(秒,默认3):").strip()
                        try:
                            preview_time = int(preview_time) if preview_time else 3
                        except:
                            preview_time = 3
                        preview_video_source(source, preview_time)
                    return {"rtsp_url": source}
            else:
                print("无效的摄像头编号")
        else:
            print("未找到可用摄像头！")
        return None

    elif choice == "2":
        print("\n" + "=" * 40)
        print("使用视频文件")
        print("=" * 40)
        print("支持的格式:.mp4,.avi,.mov,.mkv,.flv,.wmv")
        print("示例:video.mp4 或 C:/videos/sample.mp4")
        print("=" * 40)

        while True:
            video_path = input("\n请输入视频文件路径(或输入'q'返回):").strip()
            if video_path.lower() == 'q':
                return None
            if not video_path:
                print("请输入文件路径")
                continue
            if os.path.exists(video_path):
                if validate_video_source(video_path):
                    preview = input("是否预览？(y/n,默认n):").strip().lower()
                    if preview == 'y':
                        preview_time = input("预览时间(秒,默认3):").strip()
                        try:
                            preview_time = int(preview_time) if preview_time else 3
                        except:
                            preview_time = 3
                        preview_video_source(video_path, preview_time)
                    return {"rtsp_url": video_path}
                else:
                    print("无法打开视频文件")
                    retry = input("是否重试？(y/n):").strip().lower()
                    if retry != 'y':
                        return None
            else:
                print(f"文件不存在:{video_path}")
        return None

    elif choice == "3":
        print("\n" + "=" * 40)
        print("从配置文件选择")
        print("=" * 40)
        cameras_file = os.path.join("data", "cameras.json")
        if not os.path.exists(cameras_file):
            print(f"配置文件不存在:{cameras_file}")
            print("请先创建配置文件或选择其他选项")
            return None

        try:
            with open(cameras_file, 'r', encoding='utf-8') as f:
                cameras = json.load(f)
            if not cameras:
                print("配置文件中没有摄像头")
                return None

            print(f"找到{len(cameras)}个摄像头配置:")
            print("-" * 40)
            cam_list = list(cameras.items())
            for i, (cam_id, cam_info) in enumerate(cam_list):
                name = cam_info.get("name", "未命名")
                url = cam_info.get("rtsp_url", "")
                active = "✓" if cam_info.get("is_active", False) else "✗"
                print(f"{i + 1}.[{active}]{name}")
                print(f"   ID:{cam_id}")
                print(f"   源:{url[:80]}..." if len(url) > 80 else f"   源:{url}")
                print()

            while True:
                cam_index = input(f"选择摄像头(1-{len(cameras)})或按0返回:").strip()
                if cam_index == "0":
                    return None
                if cam_index.isdigit() and 1 <= int(cam_index) <= len(cameras):
                    cam_id, cam_info = cam_list[int(cam_index) - 1]
                    url = cam_info.get("rtsp_url", "")
                    print(f"\n选择:{cam_info.get('name', '未命名')}")
                    print(f"地址:{url}")
                    if validate_video_source(url):
                        preview = input("是否预览？(y/n,默认n):").strip().lower()
                        if preview == 'y':
                            preview_time = input("预览时间(秒,默认3):").strip()
                            try:
                                preview_time = int(preview_time) if preview_time else 3
                            except:
                                preview_time = 3
                            preview_video_source(url, preview_time)
                        return {"camera_id": cam_id}
                    else:
                        print("摄像头验证失败")
                        continue
                else:
                    print("无效的选择")
        except Exception as e:
            print(f"读取配置文件错误:{e}")
        return None

    elif choice == "4":
        print("\n" + "=" * 60)
        print("手动输入视频源")
        print("=" * 60)
        print("支持的类型:本地摄像头(0,1,2...),视频文件,网络流(RTSP/HTTP)")
        print("=" * 60)

        while True:
            source = input("\n请输入视频源(或输入'q'返回):").strip()
            if source.lower() == 'q':
                return None
            if not source:
                print("请输入视频源")
                continue

            print(f"验证:{source}")
            if validate_video_source(source):
                preview = input("是否预览？(y/n,默认n):").strip().lower()
                if preview == 'y':
                    preview_time = input("预览时间(秒,默认3):").strip()
                    try:
                        preview_time = int(preview_time) if preview_time else 3
                    except:
                        preview_time = 3
                    preview_video_source(source, preview_time)
                return {"rtsp_url": source}
            else:
                print("无法连接到视频源")
                retry = input("是否重试？(y/n):").strip().lower()
                if retry != 'y':
                    return None

    elif choice == "5":
        return select_test_source()

    elif choice == "6":
        print("\n" + "=" * 60)
        print("可用摄像头列表")
        print("=" * 60)
        print("本地摄像头:")
        available_cameras = []
        for i in range(5):
            for backend in [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_V4L2, None]:
                try:
                    if backend:
                        cap = cv2.VideoCapture(i, backend)
                    else:
                        cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        available_cameras.append(i)
                        print(f"  ✓ 摄像头{i}:可用")
                        cap.release()
                        break
                    cap.release()
                except:
                    continue

        if not available_cameras:
            print("  未找到本地摄像头")

        cameras_file = os.path.join("data", "cameras.json")
        if os.path.exists(cameras_file):
            try:
                with open(cameras_file, 'r', encoding='utf-8') as f:
                    cameras = json.load(f)
                if cameras:
                    print(f"\n配置文件中的摄像头({len(cameras)}个):")
                    for cam_id, cam_info in cameras.items():
                        name = cam_info.get("name", "未命名")
                        url = cam_info.get("rtsp_url", "")
                        active = "活跃" if cam_info.get("is_active", False) else "非活跃"
                        print(f"  ID:{cam_id}")
                        print(f"    名称:{name}")
                        print(f"    地址:{url[:80]}..." if len(url) > 80 else f"    地址:{url}")
                        print(f"    状态:{active}")
                        print()
            except Exception as e:
                print(f"读取配置文件错误:{e}")

        input("\n按Enter键返回菜单...")
        return None

    elif choice == "7":
        print("\n" + "=" * 60)
        print("检查FFmpeg安装")
        print("=" * 60)
        check_ffmpeg_installed()
        print("\nFFmpeg对于处理网络流(RTSP/RTMP/HTTP)非常重要")
        input("\n按Enter键返回菜单...")
        return None

    elif choice == "8":
        print("退出程序")
        sys.exit(0)

    else:
        print("无效的选择")
        return None


def main():
    parser = argparse.ArgumentParser(description="AI视频流查看器 (窗口优化版)")
    parser.add_argument("--camera-id", help="摄像头ID(从cameras.json)")
    parser.add_argument("--rtsp-url", help="直接视频源URL或路径")
    parser.add_argument("--width", type=int, default=800, help="窗口宽度 (默认: 800)")
    parser.add_argument("--height", type=int, default=600, help="窗口高度 (默认: 600)")
    parser.add_argument("--interactive", action="store_true", help="使用交互式模式")
    parser.add_argument("--list-cameras", action="store_true", help="列出所有摄像头")
    parser.add_argument("--test", action="store_true", help="使用测试视频源")
    parser.add_argument("--check-ffmpeg", action="store_true", help="检查FFmpeg安装")

    args = parser.parse_args()

    if args.check_ffmpeg:
        check_ffmpeg_installed()
        return

    if args.list_cameras:
        print("\n可用的摄像头:")
        print("=" * 50)
        print("本地摄像头:")
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"  摄像头{i}:可用")
                cap.release()
            else:
                print(f"  摄像头{i}:不可用")

        cameras_file = os.path.join("data", "cameras.json")
        if os.path.exists(cameras_file):
            try:
                with open(cameras_file, 'r', encoding='utf-8') as f:
                    cameras = json.load(f)
                print(f"\n配置文件中的摄像头({len(cameras)}个):")
                for cam_id, cam_info in cameras.items():
                    name = cam_info.get("name", "未命名")
                    url = cam_info.get("rtsp_url", "无URL")
                    active = "活跃" if cam_info.get("is_active", False) else "非活跃"
                    print(f"  ID:{cam_id}")
                    print(f"    名称:{name}")
                    print(f"    URL:{url}")
                    print(f"    状态:{active}")
                    print()
            except Exception as e:
                print(f"读取摄像头配置失败:{e}")

        print("=" * 50)
        return

    if args.test:
        print("测试模式...")
        source_config = select_test_source()
        if not source_config:
            return
    elif args.interactive or (not args.camera_id and not args.rtsp_url):
        while True:
            source_config = interactive_menu()
            if source_config:
                break
            elif source_config is None:
                continue
    else:
        source_config = {"camera_id": args.camera_id, "rtsp_url": args.rtsp_url}

    if not source_config:
        print("未选择视频源，程序退出")
        return

    # 使用更小的默认窗口尺寸 800x600
    viewer = StreamViewer(
        camera_id=source_config.get("camera_id"),
        rtsp_url=source_config.get("rtsp_url"),
        display_width=args.width,
        display_height=args.height
    )
    viewer.start()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("检测到无命令行参数，使用交互模式...")
        sys.argv.append("--interactive")
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错:{e}")
        import traceback

        traceback.print_exc()