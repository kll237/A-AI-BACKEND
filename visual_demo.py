"""
视频AI功能可视化演示系统
实时展示多种AI处理功能在视频上的可视化效果
"""

import cv2
import numpy as np
import time
import json
import os
from datetime import datetime
from collections import deque
import random

class VideoVisualizer:
    def __init__(self, config_file="visual_config.json"):
        """
        初始化可视化器
        """
        self.config = self.load_config(config_file)
        self.functions = self.load_functions()

        # 可视化效果缓存
        self.visual_effects = {
            'detection_boxes': [],      # 检测框
            'tracking_paths': {},       # 跟踪轨迹
            'face_landmarks': [],       # 人脸关键点
            'heatmap_data': None,       # 热力图数据
            'text_overlays': [],        # 文字叠加
            'statistics': {},           # 统计数据
            'alerts': []                # 警报信息
        }

        # 性能统计
        self.stats = {
            'total_frames': 0,
            'processing_time': 0,
            'fps': 0,
            'detection_count': 0,
            'function_times': {}
        }

        # 颜色表（用于不同对象）
        self.color_palette = [
            (0, 255, 0),      # 绿色 - 人
            (255, 0, 0),      # 蓝色 - 车
            (0, 0, 255),      # 红色 - 警示
            (255, 255, 0),    # 青色
            (255, 0, 255),    # 紫色
            (0, 255, 255),    # 黄色
            (128, 0, 128),    # 深紫
            (0, 128, 128)     # 橄榄
        ]

    def load_config(self, config_file):
        """
        加载可视化配置
        """
        default_config = {
            "display_settings": {
                "show_detection": True,
                "show_tracking": True,
                "show_faces": True,
                "show_heatmap": False,
                "show_statistics": True,
                "show_timeline": True,
                "show_grid": False,
                "transparency": 0.3
            },
            "visual_style": {
                "box_thickness": 2,
                "tracking_line_width": 2,
                "font_scale": 0.6,
                "font_thickness": 1,
                "heatmap_opacity": 0.5,
                "alert_duration": 3  # 秒
            },
            "demo_modes": {
                "object_detection": {
                    "enabled": True,
                    "classes": ["person", "car", "bicycle", "dog", "cat"],
                    "confidence_threshold": 0.5
                },
                "face_analysis": {
                    "enabled": True,
                    "show_landmarks": True,
                    "show_emotion": True,
                    "show_age_gender": False
                },
                "crowd_counting": {
                    "enabled": True,
                    "show_count": True,
                    "show_density": False
                },
                "traffic_analysis": {
                    "enabled": False,
                    "count_vehicles": True,
                    "detect_speeding": False,
                    "lane_detection": False
                },
                "safety_monitoring": {
                    "enabled": True,
                    "detect_fall": True,
                    "detect_intrusion": True,
                    "detect_fire": False
                }
            }
        }

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 深度合并配置
                    import copy
                    def deep_update(source, overrides):
                        for key, value in overrides.items():
                            if isinstance(value, dict) and key in source:
                                source[key] = deep_update(source.get(key, {}), value)
                            else:
                                source[key] = value
                        return source
                    default_config = deep_update(default_config, user_config)
                print(f"✓ 加载可视化配置: {config_file}")
            except Exception as e:
                print(f"⚠ 配置加载失败，使用默认配置: {e}")

        return default_config

    def load_functions(self):
        """
        加载AI功能模拟器（在没有真实模型的情况下）
        """
        functions = {
            # 1. 目标检测
            'object_detection': {
                'name': '目标检测',
                'description': '检测和分类视频中的物体',
                'visualize': self.visualize_detection,
                'simulate': self.simulate_detection
            },

            # 2. 人脸识别
            'face_recognition': {
                'name': '人脸识别',
                'description': '检测人脸、表情、关键点',
                'visualize': self.visualize_faces,
                'simulate': self.simulate_faces
            },

            # 3. 目标跟踪
            'object_tracking': {
                'name': '目标跟踪',
                'description': '跨帧跟踪物体运动轨迹',
                'visualize': self.visualize_tracking,
                'simulate': self.simulate_tracking
            },

            # 4. 人流统计
            'crowd_counting': {
                'name': '人流统计',
                'description': '统计人数和密度',
                'visualize': self.visualize_crowd,
                'simulate': self.simulate_crowd
            },

            # 5. 行为分析
            'behavior_analysis': {
                'name': '行为分析',
                'description': '识别特定行为和动作',
                'visualize': self.visualize_behavior,
                'simulate': self.simulate_behavior
            },

            # 6. 区域入侵检测
            'intrusion_detection': {
                'name': '区域入侵',
                'description': '检测禁区入侵事件',
                'visualize': self.visualize_intrusion,
                'simulate': self.simulate_intrusion
            },

            # 7. 热力图分析
            'heatmap_analysis': {
                'name': '热力图',
                'description': '显示人员分布热区',
                'visualize': self.visualize_heatmap,
                'simulate': self.simulate_heatmap
            },

            # 8. 车辆分析
            'vehicle_analysis': {
                'name': '车辆分析',
                'description': '检测和统计车辆',
                'visualize': self.visualize_vehicles,
                'simulate': self.simulate_vehicles
            }
        }

        return functions

    # ==================== 模拟AI检测函数 ====================

    def simulate_detection(self, frame):
        """
        模拟目标检测（在没有YOLO模型时使用）
        """
        height, width = frame.shape[:2]
        detections = []

        # 随机生成一些检测框（模拟AI检测结果）
        num_objects = random.randint(1, 8)
        for i in range(num_objects):
            # 随机位置和大小
            x = random.randint(0, width - 100)
            y = random.randint(0, height - 100)
            w = random.randint(30, 150)
            h = random.randint(30, 150)

            # 随机类别
            classes = ['person', 'car', 'bicycle', 'dog', 'cat', 'chair', 'bag', 'phone']
            cls = random.choice(classes)
            confidence = random.uniform(0.5, 0.95)

            detections.append({
                'bbox': [x, y, w, h],
                'class': cls,
                'confidence': confidence,
                'color': self.color_palette[i % len(self.color_palette)]
            })

        return detections

    def simulate_faces(self, frame):
        """
        模拟人脸检测
        """
        height, width = frame.shape[:2]
        faces = []

        num_faces = random.randint(0, 4)
        for i in range(num_faces):
            # 随机人脸位置
            face_size = random.randint(50, 150)
            x = random.randint(0, width - face_size)
            y = random.randint(0, height - face_size)

            # 模拟关键点
            landmarks = []
            for _ in range(5):  # 5个关键点
                lx = x + random.randint(0, face_size)
                ly = y + random.randint(0, face_size)
                landmarks.append((lx, ly))

            # 模拟表情
            emotions = ['happy', 'neutral', 'sad', 'angry', 'surprised']
            emotion = random.choice(emotions)

            faces.append({
                'bbox': [x, y, face_size, face_size],
                'landmarks': landmarks,
                'emotion': emotion,
                'confidence': random.uniform(0.7, 0.98)
            })

        return faces

    def simulate_tracking(self, frame):
        """
        模拟目标跟踪
        """
        if not hasattr(self, 'tracking_history'):
            self.tracking_history = {}
            self.next_track_id = 1

        height, width = frame.shape[:2]
        tracks = []

        # 模拟一些跟踪目标
        for track_id in list(self.tracking_history.keys()):
            # 更新现有轨迹
            last_pos = self.tracking_history[track_id]['positions'][-1]
            dx = random.randint(-15, 15)
            dy = random.randint(-15, 15)
            new_x = max(0, min(width-50, last_pos[0] + dx))
            new_y = max(0, min(height-50, last_pos[1] + dy))

            self.tracking_history[track_id]['positions'].append((new_x, new_y))

            # 保持轨迹长度
            if len(self.tracking_history[track_id]['positions']) > 20:
                self.tracking_history[track_id]['positions'].pop(0)

            tracks.append({
                'id': track_id,
                'position': (new_x, new_y),
                'class': self.tracking_history[track_id]['class'],
                'age': self.tracking_history[track_id]['age'] + 1
            })

        # 随机添加新目标
        if random.random() < 0.1:  # 10%概率添加新目标
            new_id = self.next_track_id
            self.next_track_id += 1

            x = random.randint(0, width - 50)
            y = random.randint(0, height - 50)
            classes = ['person', 'car', 'bicycle']

            self.tracking_history[new_id] = {
                'positions': [(x, y)],
                'class': random.choice(classes),
                'age': 0
            }

        return tracks

    # ==================== 可视化渲染函数 ====================

    def visualize_detection(self, frame, detections):
        """
        可视化目标检测结果
        """
        display_frame = frame.copy()

        for det in detections:
            x, y, w, h = det['bbox']
            cls = det['class']
            confidence = det['confidence']
            color = det['color']

            # 绘制检测框
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)

            # 绘制标签背景
            label = f"{cls} {confidence:.1%}"
            (label_width, label_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )

            # 标签背景框
            cv2.rectangle(display_frame,
                         (x, y - label_height - 5),
                         (x + label_width, y),
                         color, -1)

            # 标签文字
            cv2.putText(display_frame, label,
                       (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                       (255, 255, 255), 1)

        return display_frame

    def visualize_faces(self, frame, faces):
        """
        可视化人脸检测结果
        """
        display_frame = frame.copy()

        for face in faces:
            x, y, w, h = face['bbox']

            # 绘制人脸框
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 255), 2)

            # 绘制关键点
            for landmark in face['landmarks']:
                cv2.circle(display_frame, landmark, 3, (0, 0, 255), -1)

            # 绘制表情标签
            emotion = face['emotion']
            cv2.putText(display_frame, emotion,
                       (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       (0, 255, 255), 2)

        return display_frame

    def visualize_tracking(self, frame, tracks):
        """
        可视化目标跟踪轨迹
        """
        display_frame = frame.copy()

        for track_id, track_info in self.tracking_history.items():
            positions = track_info['positions']
            color = self.color_palette[track_id % len(self.color_palette)]
            cls = track_info['class']

            # 绘制轨迹线
            if len(positions) > 1:
                for i in range(1, len(positions)):
                    thickness = max(1, int(2 * (i / len(positions))))
                    cv2.line(display_frame,
                            positions[i-1],
                            positions[i],
                            color,
                            thickness)

            # 绘制当前位置和目标ID
            if positions:
                current_pos = positions[-1]
                cv2.circle(display_frame, current_pos, 8, color, -1)

                id_text = f"ID:{track_id} {cls}"
                cv2.putText(display_frame, id_text,
                           (current_pos[0] + 10, current_pos[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                           color, 2)

        return display_frame

    def visualize_crowd(self, frame, crowd_data):
        """
        可视化人流统计
        """
        display_frame = frame.copy()
        height, width = frame.shape[:2]

        # 在右上角显示统计信息
        stats_text = [
            f"当前人数: {crowd_data.get('count', 0)}",
            f"区域密度: {crowd_data.get('density', '低')}",
            f"累计人数: {crowd_data.get('total', 0)}"
        ]

        y_offset = 30
        for text in stats_text:
            cv2.putText(display_frame, text,
                       (width - 200, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                       (255, 255, 255), 2)
            y_offset += 25

        # 绘制人数计数器
        count = crowd_data.get('count', 0)
        cv2.circle(display_frame, (width - 50, 70), 30, (0, 200, 0), -1)
        cv2.putText(display_frame, str(count),
                   (width - 60, 80),
                   cv2.FONT_HERSHEY_DUPLEX, 1,
                   (255, 255, 255), 3)

        return display_frame

    def visualize_heatmap(self, frame, heatmap_data):
        """
        可视化热力图
        """
        if heatmap_data is None:
            return frame

        display_frame = frame.copy()
        height, width = frame.shape[:2]

        # 创建热力图叠加层
        heatmap_overlay = np.zeros((height, width, 3), dtype=np.uint8)

        # 绘制热力图点（模拟）
        for _ in range(20):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            radius = random.randint(10, 50)
            intensity = random.randint(100, 255)

            color = (0, 0, intensity)  # 蓝色表示热度
            cv2.circle(heatmap_overlay, (x, y), radius, color, -1)

        # 叠加热力图
        alpha = self.config['visual_style']['heatmap_opacity']
        display_frame = cv2.addWeighted(display_frame, 1 - alpha,
                                       heatmap_overlay, alpha, 0)

        # 添加热力图图例
        cv2.putText(display_frame, "热力图: 人员分布密度",
                   (10, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                   (255, 255, 255), 2)

        return display_frame

    def visualize_intrusion(self, frame, intrusion_data):
        """
        可视化区域入侵检测
        """
        display_frame = frame.copy()
        height, width = frame.shape[:2]

        # 绘制警戒区域
        roi_points = [(width//4, height//4),
                     (3*width//4, height//4),
                     (3*width//4, 3*height//4),
                     (width//4, 3*height//4)]

        # 绘制多边形区域
        pts = np.array(roi_points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(display_frame, [pts], True, (0, 0, 255), 2)

        # 填充半透明区域
        overlay = display_frame.copy()
        cv2.fillPoly(overlay, [pts], (0, 0, 100))
        cv2.addWeighted(overlay, 0.3, display_frame, 0.7, 0, display_frame)

        # 显示入侵警告
        if intrusion_data.get('intrusion', False):
            warning_text = "⚠ 区域入侵警报!"
            cv2.putText(display_frame, warning_text,
                       (width//2 - 150, height//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                       (0, 0, 255), 3)

            # 闪烁效果
            if int(time.time() * 2) % 2 == 0:
                cv2.rectangle(display_frame,
                             (width//2 - 180, height//2 - 40),
                             (width//2 + 180, height//2 + 40),
                             (0, 0, 255), 3)

        return display_frame

    def visualize_statistics(self, frame):
        """
        在画面叠加统计信息
        """
        display_frame = frame.copy()
        height, width = frame.shape[:2]

        # 左上角信息面板
        info_lines = [
            f"时间: {datetime.now().strftime('%H:%M:%S')}",
            f"帧率: {self.stats['fps']:.1f} FPS",
            f"总帧数: {self.stats['total_frames']}",
            f"检测目标: {self.stats['detection_count']}",
            "-" * 20
        ]

        # 添加功能状态
        for func_id, func_info in self.functions.items():
            if self.config['demo_modes'].get(func_id, {}).get('enabled', False):
                info_lines.append(f"✓ {func_info['name']}")

        # 绘制信息面板背景
        panel_height = len(info_lines) * 25 + 10
        cv2.rectangle(display_frame,
                     (10, 10),
                     (250, panel_height),
                     (0, 0, 0, 0.7),  # 半透明黑色
                     -1)

        # 绘制信息文字
        y_offset = 35
        for line in info_lines:
            cv2.putText(display_frame, line,
                       (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                       (255, 255, 255), 1)
            y_offset += 25

        return display_frame

    def apply_all_visualizations(self, frame, functions_enabled=None):
        """
        应用所有启用的可视化效果
        """
        if functions_enabled is None:
            functions_enabled = self.config['demo_modes']

        display_frame = frame.copy()

        # 记录开始时间（用于计算FPS）
        start_time = time.time()

        # 1. 目标检测可视化
        if functions_enabled.get('object_detection', {}).get('enabled', False):
            detections = self.simulate_detection(frame)
            display_frame = self.visualize_detection(display_frame, detections)
            self.stats['detection_count'] = len(detections)

        # 2. 人脸识别可视化
        if functions_enabled.get('face_analysis', {}).get('enabled', False):
            faces = self.simulate_faces(frame)
            display_frame = self.visualize_faces(display_frame, faces)

        # 3. 目标跟踪可视化
        if functions_enabled.get('object_tracking', {}).get('enabled', False):
            tracks = self.simulate_tracking(frame)
            display_frame = self.visualize_tracking(display_frame, tracks)

        # 4. 人流统计可视化
        if functions_enabled.get('crowd_counting', {}).get('enabled', False):
            crowd_data = {'count': random.randint(0, 20), 'density': '中'}
            display_frame = self.visualize_crowd(display_frame, crowd_data)

        # 5. 热力图可视化
        if functions_enabled.get('heatmap_analysis', {}).get('enabled', False):
            display_frame = self.visualize_heatmap(display_frame, None)

        # 6. 区域入侵可视化
        if functions_enabled.get('intrusion_detection', {}).get('enabled', False):
            intrusion_data = {'intrusion': random.random() < 0.05}  # 5%概率触发
            display_frame = self.visualize_intrusion(display_frame, intrusion_data)

        # 7. 统计信息叠加
        if self.config['display_settings']['show_statistics']:
            # 更新FPS
            processing_time = time.time() - start_time
            self.stats['processing_time'] = processing_time
            self.stats['total_frames'] += 1

            if self.stats['total_frames'] > 1:
                self.stats['fps'] = 1.0 / processing_time

            display_frame = self.visualize_statistics(display_frame)

        return display_frame

    def create_function_demo(self, video_source, function_id):
        """
        创建单个功能演示
        """
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"无法打开视频源: {video_source}")
            return

        print(f"演示功能: {self.functions[function_id]['name']}")
        print(f"描述: {self.functions[function_id]['description']}")
        print("按 'q' 退出演示")

        # 启用特定功能
        functions_enabled = {func: {'enabled': False} for func in self.functions.keys()}
        functions_enabled[function_id] = {'enabled': True}

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 应用特定功能可视化
            display_frame = self.apply_all_visualizations(frame, functions_enabled)

            # 显示功能名称
            func_name = self.functions[function_id]['name']
            cv2.putText(display_frame, f"演示功能: {func_name}",
                       (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1,
                       (0, 255, 255), 3)

            # 显示窗口
            cv2.imshow(f"功能演示: {func_name}", display_frame)

            # 退出控制
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def create_comprehensive_demo(self, video_source):
        """
        创建综合功能演示（显示所有功能）
        """
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"无法打开视频源: {video_source}")
            return

        print("综合功能演示")
        print("=" * 50)
        print("启用的功能:")
        for func_id, func_info in self.functions.items():
            if self.config['demo_modes'].get(func_id, {}).get('enabled', False):
                print(f"  ✓ {func_info['name']}: {func_info['description']}")

        print("\n控制键:")
        print("  q: 退出演示")
        print("  s: 截图保存")
        print("  p: 暂停/继续")
        print("  f: 切换全屏")
        print("  1-8: 切换功能开关")

        fullscreen = False

        while True:
            ret, frame = cap.read()
            if not ret:
                # 循环播放
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # 应用所有可视化效果
            display_frame = self.apply_all_visualizations(frame)

            # 显示窗口
            window_name = "AI视频分析 - 综合演示"
            cv2.imshow(window_name, display_frame)

            # 键盘控制
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('s'):
                # 截图保存
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"截图已保存: {filename}")
            elif key == ord('p'):
                # 暂停
                print("播放暂停，按任意键继续...")
                cv2.waitKey(0)
            elif key == ord('f'):
                # 切换全屏
                fullscreen = not fullscreen
                if fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            elif ord('1') <= key <= ord('8'):
                # 切换功能开关
                func_index = key - ord('1')
                func_ids = list(self.functions.keys())
                if func_index < len(func_ids):
                    func_id = func_ids[func_index]
                    current_state = self.config['demo_modes'].get(func_id, {}).get('enabled', False)
                    self.config['demo_modes'][func_id]['enabled'] = not current_state
                    state = "启用" if not current_state else "禁用"
                    print(f"{state}功能: {self.functions[func_id]['name']}")

        cap.release()
        cv2.destroyAllWindows()

    def run_interactive_demo(self):
        """
        运行交互式演示界面
        """
        print("=" * 60)
        print("AI视频分析功能可视化演示系统")
        print("=" * 60)

        while True:
            print("\n选择演示模式:")
            print("1. 单功能演示")
            print("2. 综合功能演示")
            print("3. 功能对比演示")
            print("4. 配置可视化选项")
            print("5. 退出")

            choice = input("请选择 (1-5): ").strip()

            if choice == "1":
                print("\n选择要演示的功能:")
                for i, (func_id, func_info) in enumerate(self.functions.items(), 1):
                    print(f"{i}. {func_info['name']} - {func_info['description']}")

                func_choice = input("选择功能编号 (1-8): ").strip()
                try:
                    func_index = int(func_choice) - 1
                    func_ids = list(self.functions.keys())
                    if 0 <= func_index < len(func_ids):
                        func_id = func_ids[func_index]

                        # 选择视频源
                        print("\n选择视频源:")
                        print("1. 使用摄像头")
                        print("2. 使用视频文件")
                        source_choice = input("选择 (1-2): ").strip()

                        if source_choice == "1":
                            camera_id = input("摄像头索引 (默认0): ").strip() or "0"
                            video_source = int(camera_id) if camera_id.isdigit() else camera_id
                        else:
                            video_file = input("视频文件路径: ").strip()
                            video_source = video_file

                        self.create_function_demo(video_source, func_id)
                    else:
                        print("无效的功能编号")
                except ValueError:
                    print("请输入有效的数字")

            elif choice == "2":
                print("\n选择视频源:")
                print("1. 使用摄像头")
                print("2. 使用视频文件")
                source_choice = input("选择 (1-2): ").strip()

                if source_choice == "1":
                    camera_id = input("摄像头索引 (默认0): ").strip() or "0"
                    video_source = int(camera_id) if camera_id.isdigit() else camera_id
                else:
                    video_file = input("视频文件路径: ").strip()
                    video_source = video_file

                self.create_comprehensive_demo(video_source)

            elif choice == "3":
                self.create_comparison_demo()

            elif choice == "4":
                self.configure_visualization()

            elif choice == "5":
                print("退出演示系统")
                break

    def create_comparison_demo(self):
        """
        创建功能对比演示（分屏显示）
        """
        print("\n功能对比演示 - 开发中...")
        # 这里可以实现分屏显示不同功能效果

    def configure_visualization(self):
        """
        配置可视化选项
        """
        print("\n可视化配置:")
        print("=" * 40)

        for key, value in self.config['display_settings'].items():
            current = "✓" if value else "✗"
            print(f"{current} {key}: {value}")

        print("\n1. 切换显示选项")
        print("2. 修改视觉样式")
        print("3. 返回")

        choice = input("选择: ").strip()

        if choice == "1":
            for i, (key, value) in enumerate(self.config['display_settings'].items(), 1):
                current = "开启" if value else "关闭"
                print(f"{i}. {key}: {current}")

            try:
                option_idx = int(input("选择要切换的选项编号: ")) - 1
                keys = list(self.config['display_settings'].keys())
                if 0 <= option_idx < len(keys):
                    key = keys[option_idx]
                    self.config['display_settings'][key] = not self.config['display_settings'][key]
                    print(f"已切换 {key}")
            except ValueError:
                print("无效输入")

    def save_config(self, filename="visual_config_modified.json"):
        """
        保存当前配置
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"配置已保存到: {filename}")

def main():
    """
    主函数
    """
    import sys

    # 创建可视化演示器
    visualizer = VideoVisualizer()

    # 命令行参数处理
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo" and len(sys.argv) > 2:
            # 直接运行演示: python visual_demo.py demo test_videos/1.mp4
            video_source = sys.argv[2]
            visualizer.create_comprehensive_demo(video_source)
        elif sys.argv[1] == "func" and len(sys.argv) > 3:
            # 运行特定功能: python visual_demo.py func object_detection test_videos/1.mp4
            func_id = sys.argv[2]
            video_source = sys.argv[3]
            visualizer.create_function_demo(video_source, func_id)
        else:
            print("用法:")
            print("  python visual_demo.py demo <视频文件或摄像头索引>")
            print("  python visual_demo.py func <功能ID> <视频源>")
            print("  无参数: 进入交互模式")
            return
    else:
        visualizer.run_interactive_demo()

if __name__ == "__main__":
    main()