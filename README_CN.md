# AI智能视频监控系统后端

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)](https://fastapi.tiangolo.com)
[![YOLO](https://img.shields.io/badge/YOLO-v8-orange.svg)](https://ultralytics.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.7+-red.svg)](https://opencv.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AI智能视频监控系统 - 集成计算机视觉、实时分析和智能安全监控的高级后端系统**

</div>

---

## 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [安装部署](#安装部署)
- [API文档](#api文档)
- [配置说明](#配置说明)
- [功能详解](#功能详解)
- [模型训练](#模型训练)
- [测试验证](#测试验证)
- [性能监控](#性能监控)
- [开发指南](#开发指南)
- [安全隐私](#安全隐私)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目简介

本系统是为**AI智能视频监控**项目开发的高级后端系统，结合了前沿的计算机视觉、机器学习和实时分析技术，提供智能监控、目标检测和自动化管理能力。

### 核心目标

- **实时安全监控**：先进的人员检测和人脸识别
- **智能视觉分析**：基于Gemini Vision API的上下文理解
- **物体计数**：仓库/农业场景的麻袋计数
- **视频流管理**：多摄像头RTSP流处理和管理
- **考勤管理**：基于授权检测的自动化考勤系统

---

## 核心功能

### 多摄像头管理系统
- **RTSP流处理**：支持多路IP摄像头实时验证
- **动态过滤器**：每个摄像头可配置AI过滤器
- **流健康监控**：自动重连和状态跟踪
- **WebSocket集成**：实时状态更新和通知

### 先进AI引擎
- **YOLO v8目标检测**：高性能人员和物体检测
- **人脸识别**：多种算法支持（face_recognition、InsightFace）
- **Gemini视觉集成**：自然语言查询视频内容
- **自定义模型支持**：特定用例的已训练模型

### 安全与授权
- **实时人员认证**：基于人脸的授权系统
- **未授权入侵检测**：自动记录安全违规
- **角色访问控制**：不同用户不同权限
- **考勤跟踪**：自动化进出记录

### 数据分析与监控
- **实时处理**：低延迟实时视频分析
- **性能指标**：帧率跟踪、检测精度、系统健康度
- **数据持久化**：JSON文件存储和结构化日志
- **查询接口**：摄像头画面的自然语言查询

### 专业应用
- **麻袋计数**：农业/仓库库存管理
- **人群分析**：人员计数和移动轨迹跟踪
- **事件检测**：安全事件自动告警

---

## 系统架构

```
A-AI-BACKEND/
├── app/                          # 主应用程序
│   ├── main.py                   # FastAPI应用入口
│   ├── ai_engine/               # AI处理核心
│   │   ├── models/              # AI模型
│   │   │   ├── yolo_model.py     # YOLO实现
│   │   │   └── deploy.prototxt  # 模型配置
│   │   └── processors/          # 处理模块
│   ├── api/                     # REST API
│   ├── core/                    # 核心配置
│   ├── models/                  # 数据模型
│   └── services/                # 业务逻辑
├── data/                        # 数据存储
│   ├── cameras.json            # 摄像头配置
│   ├── users.json              # 用户数据库
│   ├── rules.json              # 安全规则
│   ├── attendance/             # 考勤记录
│   └── unauthorized/           # 安全日志
├── logs/                       # 应用日志
└── requirements.txt            # Python依赖
```

---

## 快速开始

### 环境要求
- Python 3.8+
- CUDA兼容GPU（可选，加速推理）
- 支持RTSP的摄像头或网络摄像头

### 1. 克隆与安装

```bash
git clone https://github.com/kll237/A-AI-BACKEND.git
cd A-AI-BACKEND

# 创建虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境配置

```bash
# 创建.env文件
cat > .env << EOF
BACKEND_URL=http://localhost:8000
SECRET_KEY=your-super-secret-key-here
DATA_DIR=data
ENABLE_GPU=false
AI_ENGINE_MONITOR_INTERVAL_SECONDS=30
EOF
```

### 3. 启动服务

```bash
# 开发模式
python app/main.py

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 访问服务
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/v1/cameras/
- **WebSocket**: ws://localhost:8000/ws

---

## 安装部署

### Windows

```powershell
# 从 python.org 安装 Python 3.8+
# 从 git-scm.com 安装 Git

git clone https://github.com/kll237/A-AI-BACKEND.git
cd A-AI-BACKEND
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux (Ubuntu/Debian)

```bash
# 系统依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
sudo apt install -y ffmpeg libavcodec-dev libavformat-dev libswscale-dev

git clone https://github.com/kll237/A-AI-BACKEND.git
cd A-AI-BACKEND
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### macOS

```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install python@3.11 ffmpeg opencv

git clone https://github.com/kll237/A-AI-BACKEND.git
cd A-AI-BACKEND
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Docker

```bash
# 构建Docker镜像
docker build -t ai-backend .

# 运行容器
docker run -d \
  --name ai-backend \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  ai-backend
```

---

## API文档

### 摄像头管理

#### 创建摄像头
```http
POST /api/v1/cameras/
Content-Type: multipart/form-data

name: "主入口"
rtsp_url: "rtsp://admin:password@192.168.1.100/stream"
verify_stream: true
```

#### 摄像头列表
```http
GET /api/v1/cameras/
```

#### 更新摄像头过滤器
```http
PUT /api/v1/cameras/{camera_id}/filters
Content-Type: application/json

{
  "filters": [
    {"filter_name": "authorized_entry", "enabled": true},
    {"filter_name": "OllamaVision", "enabled": true}
  ]
}
```

### AI视觉查询

#### 处理上下文查询
```http
POST /api/v1/ai-vision/query
Content-Type: application/json

{
  "camera_id": "camera-uuid",
  "query": "场景中有多少人？"
}
```

### 用户管理

#### 添加用户
```http
POST /api/v1/users/
Content-Type: multipart/form-data

name: "张三"
role: "employee"
image: [图片文件]
```

#### 用户列表
```http
GET /api/v1/users/
```

### 数据分析

#### 获取考勤记录
```http
GET /api/v1/analytics/attendance?date=2024-01-15
```

#### 获取未授权记录
```http
GET /api/v1/analytics/unauthorized
```

---

## 配置说明

### 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `BACKEND_URL` | `http://localhost:8000` | 后端服务器URL |
| `SECRET_KEY` | `your-secret-key-here` | JWT密钥 |
| `DATA_DIR` | `data` | 数据存储目录 |
| `ENABLE_GPU` | `false` | 启用GPU加速 |
| `AI_ENGINE_MONITOR_INTERVAL_SECONDS` | `30` | AI引擎监控间隔 |

### 可用过滤器

- **`authorized_entry`**：人员授权和访问控制
- **`OllamaVision`**：AI驱动的上下文分析
- **`attendance`**：自动考勤跟踪
- **`object_counting`**：通用物体计数

---

## 功能详解

### 1. 多摄像头RTSP管理

系统支持无限数量的IP摄像头，具有高级流管理功能：
- **实时流验证**：添加前自动测试RTSP流
- **动态重连**：优雅处理网络中断
- **性能监控**：跟踪帧率、延迟和流健康度
- **并发处理**：同时处理多个摄像头

支持的摄像头类型：
- 支持RTSP的IP摄像头
- USB网络摄像头（通过OpenCV）
- 网络视频录像机（NVR）
- ONVIF兼容设备

### 2. YOLO v8目标检测

基于Ultralytics YOLO v8的先进目标检测：
- **人员检测**：各种条件下高精度人体检测
- **实时处理**：针对实时视频流优化
- **自定义训练**：支持特定领域模型
- **多尺度检测**：处理各种尺寸的物体

### 3. 先进人脸识别

多算法高精度的面部识别系统：
- **face_recognition库**：基于dlib的深度学习
- **InsightFace**：最先进的面部分析
- **OpenCV人脸检测**：备用方法
- **自定义增强**：图像预处理提高精度

### 4. Gemini视觉集成

使用Google Gemini 2.0 Flash模型的AI驱动上下文分析：
- **自然语言查询**：询问摄像头画面相关问题
- **场景理解**：综合视觉分析
- **物体计数**：统计画面中的人数
- **活动识别**：识别人物行为
- **安全评估**：检测安全违规

### 5. 麻袋计数系统

农业/仓库应用的专业计算机视觉解决方案：
- **自定义YOLO模型**：专门训练的麻袋检测
- **实时计数**：带计数叠加的实时视频分析
- **批量处理**：处理录制的视频
- **导出功能**：保存带标注的结果

### 6. 安全与授权系统

具有实时告警的综合安全监控：
- **基于人脸的认证**：自动人员识别
- **基于角色的访问**：不同授权级别
- **未授权检测**：实时安全违规告警
- **进出日志**：全面的访问跟踪

---

## 模型训练

### 自定义YOLO训练

```bash
# 准备训练数据
python prepare_training_data.py \
  --input_dir "raw_images/" \
  --output_dir "data/gunny_bag_dataset/" \
  --train_split 0.8

# 训练YOLO模型
python train_yolo.py \
  --data "data/gunny_bag_dataset/dataset.yaml" \
  --epochs 100 \
  --imgsz 640 \
  --batch 16
```

### 训练指标

| 指标 | 数值 | 描述 |
|------|------|------|
| **mAP@0.5** | 0.85+ | IoU 0.5下的平均精度 |
| **精度** | 0.90+ | 真阳性率 |
| **召回率** | 0.88+ | 检测率 |
| **推理速度** | 15ms | 每帧平均推理时间 |

---

## 测试验证

```bash
# 运行所有测试
pytest tests/ -v

# 测试特定模块
pytest tests/test_yolo_model.py -v
pytest tests/test_face_recognition.py -v
pytest tests/test_api_endpoints.py -v
```

---

## 性能监控

### 性能指标

| 组件 | 指标 | 目标 | 实际 |
|------|------|------|------|
| **YOLO检测** | FPS | 30+ | 35+ |
| **人脸识别** | 处理时间 | <100ms | 85ms |
| **API响应** | 延迟 | <200ms | 150ms |
| **内存使用** | RAM | <2GB | 1.5GB |

---

## 开发指南

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 代码格式化
black app/
isort app/

# 类型检查
mypy app/
```

### 代码规范

- **PEP 8** 规范
- **Black** 代码格式化
- **isort** 导入排序
- 所有函数使用**类型提示**
- 所有模块/类使用**文档字符串**

---

## 安全隐私

### 安全特性

- **数据加密**：静态敏感数据加密
- **安全传输**：所有通信使用HTTPS/WSS
- **访问控制**：基于角色的权限
- **审计日志**：全面的安全事件日志

### 隐私合规

- **数据最小化**：仅收集必要数据
- **保留策略**：自动数据清理
- **匿名化**：使用人脸编码而非原始图像
- **同意管理**：用户权限跟踪

---

## 常见问题

### 1. CUDA内存不足
```bash
# 解决：减小批量大小或模型大小
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### 2. RTSP流连接失败
```python
# 使用OpenCV检查流
cap = cv2.VideoCapture(rtsp_url)
if not cap.isOpened():
    # 尝试不同的传输协议
    cap = cv2.VideoCapture(rtsp_url + "?rtsp_transport=tcp")
```

### 3. 人脸识别精度低
```python
# 提高图像质量和光照
enhanced_img = cv2.convertScaleAbs(img, alpha=1.3, beta=30)
face_locations = face_recognition.face_locations(enhanced_img, model="cnn")
```

---

## 贡献指南

### 开发流程

1. **Fork** 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 贡献指南

- **代码风格**：遵循PEP 8并使用Black格式化
- **测试**：为新功能添加测试
- **文档**：更新README和docstrings
- **性能**：考虑更改的性能影响

---

## 许可证

本项目基于**MIT许可证** - 详见 [LICENSE](LICENSE) 文件。

---

## 致谢

- **Ultralytics** 提供优秀的YOLO实现
- **Google** 提供Gemini视觉API
- **OpenCV** 社区提供计算机视觉工具
- **FastAPI** 团队提供出色的Web框架

---

## 联系方式

- **GitHub Issues**: [提交问题](https://github.com/kll237/A-AI-BACKEND/issues)
- **邮箱**: 联系GitHub仓库所有者

---

<div align="center">

如果你觉得这个项目有帮助，请给我一个Star！

**AI智能视频监控系统 - 让监控更智能**

[回到顶部](#ai智能视频监控系统后端)

</div>
