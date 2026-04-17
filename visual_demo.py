"""
AI视频功能可视化演示系统
实时展示各种AI处理功能在视频上的可视化效果
"""

import cv2
import numpy as np
import time
import json
import os
import sys
from datetime import datetime
import random

class VideoVisualizer:
    def __init__(self, config_file="visual_config.json"):
        """
        初始化可视化器
        """
        self.config = self.load_config(config_file)
        self.functions = self.load_functions()

        # 性能统计
        self.stats = {
            'total_frames': 0,
            'processing_time': 0,
            'fps': 0,
            'detection_count': 0
        }

        # 颜色表
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

        # 跟踪历史
        self.tracking_history = {}
        self.next_track_id = 1

    def load_config(self, config_file):
        """
        加载可视化配置
        """
        default_config = {
            "display_settings": {
                "show_detection": True,
                "show_tracking": True,
                "show_faces": True,
                "show_statistics": True,
                "transparency": 0.3
            },
            "visual_style": {
                "box_thickness": 2,
                "font_scale": 0.6,
                "font_thickness": 1
            },
            "demo_modes": {
                "object_detection": {"enabled": True},
                "face_recognition": {"enabled": True},
                "object_tracking": {"enabled": True},
                "crowd_counting": {"enabled": True},
                "intrusion_detection": {"enabled": True}
            }
        }

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 简单合并
                    for key in user_config:
                        if key in default_config:
                            if isinstance(default_config[key], dict):
                                default_config[key].update(user_config[key])
                            else:
                                default_config[key] = user_config[key]
                print(f"✓ 加载可视化配置: {config_file}")
            except Exception as e:
                print(f"⚠ 配置加载失败: {e}")

        return default_config

    def load_functions(self):
        """
        加载AI功能
        """
        return {
            'object_detection': {
                'name': '目标检测',
                'description': '检测和分类视频中的物体',
                'simulate': self.simulate_detection,
                'visualize': self.visualize_detection
            },
            'face_recognition': {
                'name': '人脸识别',
                'description': '检测人脸和表情',
                'simulate': self.simulate_faces,
                'visualize': self.visualize_faces
            },
            'object_tracking': {
                'name': '目标跟踪',
                'description': '跟踪物体运动轨迹',
                'simulate': self.simulate_tracking,
                'visualize': self.visualize_tracking
            },
            'crowd_counting': {
                'name': '人流统计',
                'description': '统计人数和密度',
                'simulate': self.simulate_crowd,
                'visualize': self.visualize_crowd
            },
            'intrusion_detection': {
                'name': '区域入侵',
                'description': '检测禁区入侵',
                'simulate': self.simulate_intrusion,
                'visualize': self.visualize_intrusion
            }
        }

    # =============== 模拟函数 ===============

    def simulate_detection(self, frame):
        """模拟目标检测"""
        height, width = frame.shape[:2]
        detections = []

        num_objects = random.randint(1, 5)
        for i in range(num_objects):
            x = random.randint(0, width - 100)
            y = random.randint(0, height - 100)
            w = random.randint(30, 100)
            h = random.randint(30, 100)

            classes = ['person', 'car', 'bicycle', 'dog', 'cat']
            cls = random.choice(classes)

            detections.append({
                'bbox': [x, y, w, h],
                'class': cls,
                'confidence': random.uniform(0.5, 0.95),
                'color': self.color_palette[i % len(self.color_palette)]
            })

        return detections

    def simulate_faces(self, frame):
        """模拟人脸检测"""
        height, width = frame.shape[:2]
        faces = []

        num_faces = random.randint(0, 3)
        for i in range(num_faces):
            face_size = random.randint(50, 120)
            x = random.randint(0, width - face_size)
            y = random.randint(0, height - face_size)

            landmarks = []
            for _ in range(5):
                lx = x + random.randint(0, face_size)
                ly = y + random.randint(0, face_size)
                landmarks.append((lx, ly))

            emotions = ['happy', 'neutral', 'sad']
            emotion = random.choice(emotions)

            faces.append({
                'bbox': [x, y, face_size, face_size],
                'landmarks': landmarks,
                'emotion': emotion
            })

        return faces

    def simulate_tracking(self, frame):
        """模拟目标跟踪"""
        height, width = frame.shape[:2]

        # 更新现有轨迹
        for track_id in list(self.tracking_history.keys()):
            if track_id in self.tracking_history:
                last_pos = self.tracking_history[track_id]['positions'][-1]
                dx = random.randint(-10, 10)
                dy = random.randint(-10, 10)
                new_x = max(0, min(width-50, last_pos[0] + dx))
                new_y = max(0, min(height-50, last_pos[1] + dy))

                self.tracking_history[track_id]['positions'].append((new_x, new_y))

                if len(self.tracking_history[track_id]['positions']) > 15:
                    self.tracking_history[track_id]['positions'].pop(0)

        # 随机添加新目标
        if random.random() < 0.05:
            new_id = self.next_track_id
            self.next_track_id += 1

            x = random.randint(0, width - 50)
            y = random.randint(0, height - 50)

            self.tracking_history[new_id] = {
                'positions': [(x, y)],
                'class': random.choice(['person', 'car'])
            }

        return list(self.tracking_history.keys())

    def simulate_crowd(self, frame):
        """模拟人流统计"""
        return {
            'count': random.randint(0, 15),
            'density': random.choice(['低', '中', '高']),
            'total': random.randint(100, 500)
        }

    def simulate_intrusion(self, frame):
        """模拟入侵检测"""
        return {
            'intrusion': random.random() < 0.03,  # 3%概率
            'zone': 'A区'
        }

    # =============== 可视化函数 ===============

    def visualize_detection(self, frame, detections):
        """可视化检测结果"""
        display_frame = frame.copy()

        for det in detections:
            x, y, w, h = det['bbox']
            cls = det['class']
            confidence = det['confidence']
            color = det['color']

            # 绘制框
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)

            # 绘制标签
            label = f"{cls} {confidence:.1%}"
            (label_width, label_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )

            # 标签背景
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
        """可视化人脸"""
        display_frame = frame.copy()

        for face in faces:
            x, y, w, h = face['bbox']

            # 人脸框
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 255), 2)

            # 关键点
            for landmark in face['landmarks']:
                cv2.circle(display_frame, landmark, 3, (0, 0, 255), -1)

            # 表情
            emotion = face['emotion']
            cv2.putText(display_frame, emotion,
                       (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       (0, 255, 255), 2)

        return display_frame

    def visualize_tracking(self, frame, track_ids):
        """可视化跟踪"""
        display_frame = frame.copy()

        for track_id in track_ids:
            if track_id in self.tracking_history:
                positions = self.tracking_history[track_id]['positions']
                color = self.color_palette[track_id % len(self.color_palette)]

                # 绘制轨迹
                if len(positions) > 1:
                    for i in range(1, len(positions)):
                        cv2.line(display_frame,
                                positions[i-1],
                                positions[i],
                                color,
                                2)

                # 当前位置
                if positions:
                    current_pos = positions[-1]
                    cv2.circle(display_frame, current_pos, 8, color, -1)

                    # ID标签
                    id_text = f"ID:{track_id}"
                    cv2.putText(display_frame, id_text,
                               (current_pos[0] + 10, current_pos[1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                               color, 2)

        return display_frame

    def visualize_crowd(self, frame, crowd_data):
        """可视化人流统计"""
        display_frame = frame.copy()
        height, width = frame.shape[:2]

        # 统计面板
        stats_text = [
            f"当前人数: {crowd_data['count']}",
            f"区域密度: {crowd_data['density']}",
            f"累计人数: {crowd_data['total']}"
        ]

        y_offset = 30
        for text in stats_text:
            cv2.putText(display_frame, text,
                       (width - 200, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                       (255, 255, 255), 2)
            y_offset += 25

        return display_frame

    def visualize_intrusion(self, frame, intrusion_data):
        """可视化入侵检测"""
        display_frame = frame.copy()
        height, width = frame.shape[:2]

        # 绘制警戒区域
        roi_points = [
            (width//4, height//4),
            (3*width//4, height//4),
            (3*width//4, 3*height//4),
            (width//4, 3*height//4)
        ]

        pts = np.array(roi_points, np.int32).reshape((-1, 1, 2))
        cv2.polylines(display_frame, [pts], True, (0, 0, 255), 2)

        # 半透明填充
        overlay = display_frame.copy()
        cv2.fillPoly(overlay, [pts], (0, 0, 100))
        cv2.addWeighted(overlay, 0.3, display_frame, 0.7, 0, display_frame)

        # 入侵警告
        if intrusion_data['intrusion']:
            warning_text = "⚠ 区域入侵!"
            text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = width//2 - text_size[0]//2
            text_y = height//2

            cv2.putText(display_frame, warning_text,
                       (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1,
                       (0, 0, 255), 3)

        return display_frame

    def visualize_statistics(self, frame):
        """可视化统计信息"""
        display_frame = frame.copy()
        height, width = frame.shape[:2]

        # 信息面板
        info_lines = [
            f"时间: {datetime.now().strftime('%H:%M:%S')}",
            f"帧率: {self.stats['fps']:.1f} FPS",
            f"总帧数: {self.stats['total_frames']}",
            f"检测目标: {self.stats['detection_count']}"
        ]

        # 绘制面板背景
        panel_height = len(info_lines) * 25 + 10
        cv2.rectangle(display_frame,
                     (10, 10),
                     (250, panel_height),
                     (0, 0, 0),
                     -1)

        # 透明效果
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (10, 10), (250, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, display_frame, 0.5, 0, display_frame)

        # 绘制文字
        y_offset = 35
        for line in info_lines:
            cv2.putText(display_frame, line,
                       (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                       (255, 255, 255), 1)
            y_offset += 25

        return display_frame

    def apply_visualizations(self, frame):
        """应用所有可视化"""
        start_time = time.time()
        display_frame = frame.copy()

        # 更新帧统计
        self.stats['total_frames'] += 1

        # 1. 目标检测
        if self.config['demo_modes']['object_detection']['enabled']:
            detections = self.simulate_detection(frame)
            display_frame = self.visualize_detection(display_frame, detections)
            self.stats['detection_count'] = len(detections)

        # 2. 人脸识别
        if self.config['demo_modes']['face_recognition']['enabled']:
            faces = self.simulate_faces(frame)
            display_frame = self.visualize_faces(display_frame, faces)

        # 3. 目标跟踪
        if self.config['demo_modes']['object_tracking']['enabled']:
            track_ids = self.simulate_tracking(frame)
            display_frame = self.visualize_tracking(display_frame, track_ids)

        # 4. 人流统计
        if self.config['demo_modes']['crowd_counting']['enabled']:
            crowd_data = self.simulate_crowd(frame)
            display_frame = self.visualize_crowd(display_frame, crowd_data)

        # 5. 入侵检测
        if self.config['demo_modes']['intrusion_detection']['enabled']:
            intrusion_data = self.simulate_intrusion(frame)
            display_frame = self.visualize_intrusion(display_frame, intrusion_data)

        # 6. 统计信息
        if self.config['display_settings']['show_statistics']:
            processing_time = time.time() - start_time
            if processing_time > 0:
                self.stats['fps'] = 1.0 / processing_time
            display_frame = self.visualize_statistics(display_frame)

        return display_frame

    def run_demo(self, video_source):
        """运行演示"""
        # 确定视频源类型
        if isinstance(video_source, str) and video_source.isdigit():
            video_source = int(video_source)

        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"无法打开视频源: {video_source}")
            return False

        print("=" * 60)
        print("AI视频功能可视化演示")
        print("=" * 60)
        print("启用的功能:")
        for func_id, func_info in self.functions.items():
            if self.config['demo_modes'][func_id]['enabled']:
                print(f"  ✓ {func_info['name']}")
        print("\n控制键:")
        print("  q: 退出")
        print("  s: 截图")
        print("  p: 暂停")
        print("  1-5: 切换功能 (1:检测, 2:人脸, 3:跟踪, 4:人流, 5:入侵)")
        print("=" * 60)

        while True:
            ret, frame = cap.read()
            if not ret:
                # 循环播放
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # 处理帧
            display_frame = self.apply_visualizations(frame)

            # 显示
            cv2.imshow("AI视频分析演示", display_frame)

            # 键盘控制
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"截图已保存: {filename}")
            elif key == ord('p'):
                print("暂停，按任意键继续...")
                cv2.waitKey(0)
            elif ord('1') <= key <= ord('5'):
                func_index = key - ord('1')
                func_ids = list(self.functions.keys())
                if func_index < len(func_ids):
                    func_id = func_ids[func_index]
                    current = self.config['demo_modes'][func_id]['enabled']
                    self.config['demo_modes'][func_id]['enabled'] = not current
                    state = "启用" if not current else "禁用"
                    print(f"{state}: {self.functions[func_id]['name']}")

        cap.release()
        cv2.destroyAllWindows()
        return True

def main():
    """主函数"""
    print("AI视频功能可视化演示系统")
    print("=" * 50)

    # 创建可视化器
    visualizer = VideoVisualizer()

    # 命令行参数处理
    if len(sys.argv) > 1:
        video_source = sys.argv[1]
        visualizer.run_demo(video_source)
    else:
        # 交互模式
        print("\n选择视频源:")
        print("1. 摄像头 (索引0)")
        print("2. 视频文件")

        choice = input("请选择 (1-2): ").strip()

        if choice == "1":
            camera_id = input("摄像头索引 (默认0): ").strip() or "0"
            video_source = camera_id
        else:
            video_file = input("视频文件路径: ").strip()
            if not video_file:
                video_file = "test_videos/1.mp4"
                print(f"使用默认文件: {video_file}")
            video_source = video_file

        visualizer.run_demo(video_source)

if __name__ == "__main__":
    main()