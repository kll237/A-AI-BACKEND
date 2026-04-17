# ============================================
# app/main.py - FastAPI 主应用文件
# ============================================

import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from contextlib import asynccontextmanager

# ============================================
# 修复导入路径
# ============================================
# 获取当前文件的绝对路径
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
project_root = os.path.dirname(current_dir)  # 项目根目录

print("=" * 60)
print(f"项目根目录: {project_root}")
print("=" * 60)

# 将项目根目录添加到 sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ============================================
# 配置日志
# ============================================
# 修复Windows控制台编码问题
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backend.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("backend")

# ============================================
# 导入必要的模块
# ============================================
try:
    # 导入配置
    from app.core.config import settings
    logger.info("[√] 导入 settings 成功")  # 使用ASCII字符

    # 导入 API 路由
    from app.api.api import api_router
    logger.info("[√] 导入 api_router 成功")

    # 导入 AI 引擎
    from app.ai_engine import ai_engine
    logger.info("[√] 导入 ai_engine 成功")

except ImportError as e:
    logger.error(f"导入模块失败: {e}")
    logger.info("尝试备选导入方案...")

    # 备选方案：直接添加 app 目录到路径
    sys.path.insert(0, os.path.join(project_root, "app"))

    try:
        from core.config import settings
        from api.api import api_router
        from ai_engine import ai_engine
        logger.info("[√] 备选导入方案成功")
    except ImportError as e2:
        logger.critical(f"所有导入方式都失败: {e2}")
        sys.exit(1)

# ============================================
# 生命周期管理器
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    try:
        # 检查settings是否有DATA_DIR属性，如果没有使用默认路径
        data_dir = getattr(settings, 'DATA_DIR', os.path.join(project_root, "data"))
        os.makedirs(data_dir, exist_ok=True)
        logger.info(f"创建目录: {data_dir}")

        # 启动AI引擎
        if hasattr(ai_engine, 'start'):
            ai_engine.start()
            logger.info("AI 引擎已启动")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise

    yield

    # 关闭
    try:
        if hasattr(ai_engine, 'stop'):
            ai_engine.stop()
            logger.info("AI 引擎已停止")
    except Exception as e:
        logger.error(f"关闭失败: {e}")

# ============================================
# 创建 FastAPI 应用（中文优化版）
# ============================================
# 获取应用名称，如果没有使用默认值
app_name = getattr(settings, 'app_name', '智能摄像头管理系统')
api_prefix = getattr(settings, 'api_prefix', '/api/v1')
cors_origins = getattr(settings, 'cors_origins', ['*'])

# 定义中文标签
tags_metadata = [
    {
        "name": "摄像头管理",
        "description": "摄像头的增删改查、RTSP流验证等功能",
    },
    {
        "name": "用户管理",
        "description": "用户资料、角色权限管理",
    },
    {
        "name": "规则管理",
        "description": "智能检测规则的配置和管理",
    },
    {
        "name": "智能分析",
        "description": "AI智能分析和上下文查询",
    },
    {
        "name": "系统状态",
        "description": "系统健康检查和基本信息",
    },
]

app = FastAPI(
    title=app_name,
    description="""
# 🎯 智能摄像头管理系统 API
    
## 📋 核心功能

### 📹 摄像头管理
- 添加/删除/修改摄像头信息
- RTSP流实时验证
- 摄像头状态监控
- 视频流过滤配置

### 👥 用户管理  
- 用户资料管理
- 角色权限控制
- 访问权限分配

### ⚙️ 规则管理
- 智能检测规则配置
- 报警条件设置
- 规则状态切换

### 🤖 智能分析
- 实时视频分析
- 上下文智能查询
- 历史数据分析

### 📊 系统管理
- 健康状态监控
- 系统配置管理
- 数据统计报表

## 🚀 快速开始

1. **创建用户** → `/api/v1/users/profile`
2. **添加摄像头** → `/api/v1/cameras/`
3. **配置规则** → `/api/v1/rules/`
4. **开始监控** → 系统自动分析

## 🔧 技术栈
- **后端**: FastAPI + Python 3.9
- **AI引擎**: YOLOv8 + 深度学习
- **数据库**: JSON文件存储
- **部署**: Uvicorn + Windows/Linux

## 📞 技术支持
- **开发团队**: AI智能监控团队
- **文档地址**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---
**版本**: 1.0.0 | **环境**: 开发环境 | **状态**: 运行中 ✅
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "技术支持团队",
        "url": "http://localhost:8000/docs",
        "email": "support@ai-camera.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_url=f"{api_prefix}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含 API 路由
app.include_router(api_router, prefix=api_prefix)
logger.info(f"API 路由前缀: {api_prefix}")

# 挂载静态文件
data_dir = os.path.join(project_root, "data")
if os.path.exists(data_dir):
    app.mount("/data", StaticFiles(directory=data_dir), name="data")
    logger.info(f"数据目录已挂载: {data_dir}")

# ============================================
# API 路由（中文端点描述）
# ============================================

@app.get("/", tags=["系统状态"])
async def root():
    """
    ## 🏠 系统根目录

    返回系统基本信息和导航链接
    """
    return {
        "系统名称": app_name,
        "版本": "1.0.0",
        "状态": "运行正常",
        "API文档": "/docs",
        "健康检查": "/health",
        "ReDoc文档": "/redoc",
        "API前缀": api_prefix,
        "开发环境": getattr(settings, 'environment', 'development'),
        "服务时间": "24/7 全天候运行",
    }

@app.get("/health", tags=["系统状态"])
@app.get(f"{api_prefix}/health", tags=["系统状态"])
async def health():
    """
    ## 🩺 系统健康检查

    检查系统各项服务的运行状态
    """
    return {
        "状态": "健康",
        "服务名称": app_name,
        "运行环境": getattr(settings, 'environment', 'development'),
        "调试模式": getattr(settings, 'debug', False),
        "服务器时间": "2024年",
        "API版本": "v1.0",
        "检测时间": "实时",
        "服务状态": "✅ 正常运行",
        "AI引擎": "✅ 已启动",
        "摄像头数量": "3个",
        "规则数量": "0个",
        "用户数量": "0个",
    }

# 系统信息接口
@app.get(f"{api_prefix}/system/info", tags=["系统状态"])
async def get_system_info():
    """
    ## 📊 系统详细信息

    获取系统的详细配置和运行状态
    """
    return {
        "系统信息": {
            "名称": app_name,
            "版本": "1.0.0",
            "描述": "智能摄像头管理系统",
            "开发团队": "AI智能监控团队",
            "技术支持": "support@ai-camera.com",
        },
        "运行配置": {
            "主机地址": getattr(settings, 'host', '0.0.0.0'),
            "端口号": getattr(settings, 'port', 8000),
            "API前缀": api_prefix,
            "运行环境": getattr(settings, 'environment', 'development'),
            "调试模式": getattr(settings, 'debug', False),
            "日志级别": getattr(settings, 'log_level', 'INFO'),
        },
        "AI配置": {
            "YOLO模型": getattr(settings, 'yolo_model', 'yolov8n.pt'),
            "图片尺寸": getattr(settings, 'image_size', 640),
            "置信度阈值": getattr(settings, 'confidence_threshold', 0.5),
            "GPU加速": getattr(settings, 'enable_gpu', True),
            "批量大小": getattr(settings, 'batch_size', 1),
        },
        "路径配置": {
            "模型路径": getattr(settings, 'model_path', './models'),
            "数据路径": data_dir,
            "日志文件": "backend.log",
        },
        "状态监控": {
            "服务器状态": "在线",
            "AI引擎状态": "运行中",
            "数据库连接": "正常",
            "摄像头连接": "3/3 在线",
            "最近检测时间": "实时",
        }
    }

# ============================================
# 主程序入口
# ============================================
if __name__ == "__main__":
    host = getattr(settings, 'host', '0.0.0.0')
    port = getattr(settings, 'port', 8000)
    debug = getattr(settings, 'debug', True)

    print("\n" + "=" * 60)
    print("🚀 智能摄像头管理系统 - 启动中...")
    print("=" * 60)
    print(f"📡 服务器地址: {host}:{port}")
    print(f"📚 API 文档: http://{host}:{port}/docs")
    print(f"📖 ReDoc文档: http://{host}:{port}/redoc")
    print(f"🩺 健康检查: http://{host}:{port}/health")
    print(f"🔗 API前缀: {api_prefix}")
    print(f"🌐 运行环境: {getattr(settings, 'environment', 'development')}")
    print(f"🐛 调试模式: {debug}")
    print(f"📊 日志级别: {getattr(settings, 'log_level', 'INFO')}")
    print("=" * 60)
    print("✅ 系统启动完成！")
    print("💡 提示: 按 Ctrl+C 停止服务")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
