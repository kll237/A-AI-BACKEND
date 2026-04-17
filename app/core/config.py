from typing import List, Optional, Dict, Any
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, validator, model_validator
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # ==================== 项目基础配置 ====================
    PROJECT_NAME: str = "智能摄像头管理系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, testing, production
    
    # ==================== 服务器配置 ====================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = True
    
    # ==================== CORS 配置 ====================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",  # Vite 默认端口
        "http://127.0.0.1:5173"
    ]
    
    # ==================== 路径配置 ====================
    # 项目根目录
    PROJECT_ROOT: Optional[Path] = None
    
    # 数据目录
    DATA_DIR: Optional[Path] = None
    
    # 模型目录
    MODELS_DIR: Optional[Path] = None
    
    # 日志目录
    LOGS_DIR: Optional[Path] = None
    
    # SQLite 数据库路径
    SQLITE_DB_PATH: Optional[Path] = None
    
    # ==================== AI 模型配置 ====================
    # YOLO 配置（从 .env 文件读取）
    YOLO_MODEL: str = "yolov8n.pt"
    IMAGE_SIZE: int = 640
    BATCH_SIZE: int = 1
    CONFIDENCE_THRESHOLD: float = 0.3
    IOU_THRESHOLD: float = 0.45
    MAX_DETECTIONS: int = 300
    
    # GPU 配置
    ENABLE_GPU: bool = True
    CUDA_DEVICE: str = "cuda:0"
    
    # ==================== 摄像头配置 ====================
    CAMERA_RTSP_TIMEOUT: int = 10
    CAMERA_BUFFER_SIZE: int = 10
    DEFAULT_FPS: int = 30
    MAX_CAMERAS: int = 10
    
    # ==================== 后端配置 ====================
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # ==================== 安全配置 ====================
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ==================== 数据库配置 ====================
    DATABASE_URL: Optional[str] = None
    
    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ==================== 文件上传配置 ====================
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/jpg"]
    ALLOWED_VIDEO_TYPES: List[str] = ["video/mp4", "video/avi", "video/mkv"]
    
    # ==================== 数据处理配置 ====================
    SAVE_DETECTIONS: bool = True
    SAVE_ANNOTATIONS: bool = True
    ANNOTATION_FORMAT: str = "yolo"  # yolo, coco, pascal_voc
    
    # ==================== 定时任务配置 ====================
    CLEANUP_INTERVAL_HOURS: int = 24
    MAX_LOG_DAYS: int = 30
    MAX_DATA_DAYS: int = 90
    
    # ==================== 模型验证器 ====================
    @model_validator(mode='after')
    def set_paths(self) -> 'Settings':
        """设置所有路径"""
        # 设置项目根目录
        if self.PROJECT_ROOT is None:
            self.PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
        
        # 设置数据目录
        if self.DATA_DIR is None:
            self.DATA_DIR = self.PROJECT_ROOT / "data"
        
        # 设置模型目录
        if self.MODELS_DIR is None:
            self.MODELS_DIR = self.PROJECT_ROOT / "models"
        
        # 设置日志目录
        if self.LOGS_DIR is None:
            self.LOGS_DIR = self.PROJECT_ROOT / "logs"
        
        # 设置 SQLite 数据库路径
        if self.SQLITE_DB_PATH is None:
            self.SQLITE_DB_PATH = self.DATA_DIR / "database.db"
        
        # 确保所有目录存在
        for path in [self.DATA_DIR, self.MODELS_DIR, self.LOGS_DIR]:
            path.mkdir(parents=True, exist_ok=True)
        
        return self
    
    @validator('ENABLE_GPU')
    def validate_gpu(cls, v: bool) -> bool:
        """验证 GPU 配置"""
        if v:
            try:
                import torch
                if not torch.cuda.is_available():
                    logger.warning("GPU 已启用但 CUDA 不可用，将使用 CPU")
                    return False
            except ImportError:
                logger.warning("PyTorch 未安装，将使用 CPU")
                return False
        return v
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v: str) -> str:
        """验证密钥"""
        if v == "your-secret-key-change-in-production":
            logger.warning("使用默认密钥，在生产环境中请修改 SECRET_KEY")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略 .env 中未定义的额外字段

# ==================== 初始化设置 ====================
# 创建 settings 实例
try:
    settings = Settings()
    logger.info(f"配置加载成功: {settings.PROJECT_NAME} v{settings.VERSION}")
except Exception as e:
    logger.error(f"配置加载失败: {e}")
    # 使用默认配置
    settings = Settings(_env_file=None)

# ==================== 配置检查 ====================
def print_settings_summary():
    """打印配置摘要"""
    print("=" * 60)
    print(f"{settings.PROJECT_NAME} 配置摘要")
    print("=" * 60)
    
    print(f"\n📁 路径配置:")
    print(f"  项目根目录: {settings.PROJECT_ROOT}")
    print(f"  数据目录: {settings.DATA_DIR}")
    print(f"  模型目录: {settings.MODELS_DIR}")
    print(f"  日志目录: {settings.LOGS_DIR}")
    print(f"  数据库路径: {settings.SQLITE_DB_PATH}")
    
    print(f"\n🖥️  服务器配置:")
    print(f"  服务器地址: {settings.HOST}:{settings.PORT}")
    print(f"  环境: {settings.ENVIRONMENT}")
    print(f"  调试模式: {settings.DEBUG}")
    
    print(f"\n🤖 AI 模型配置:")
    print(f"  YOLO 模型: {settings.YOLO_MODEL}")
    print(f"  图像大小: {settings.IMAGE_SIZE}")
    print(f"  批大小: {settings.BATCH_SIZE}")
    print(f"  置信度阈值: {settings.CONFIDENCE_THRESHOLD}")
    print(f"  启用 GPU: {settings.ENABLE_GPU}")
    
    print(f"\n🔒 安全配置:")
    print(f"  CORS 允许来源: {', '.join(settings.CORS_ORIGINS[:3])}...")
    
    print(f"\n📊 其他配置:")
    print(f"  API 前缀: {settings.API_V1_STR}")
    print(f"  最大摄像头数: {settings.MAX_CAMERAS}")
    print(f"  最大上传大小: {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB")
    
    print("=" * 60)

# ==================== 工具函数 ====================
def get_database_url() -> str:
    """获取数据库 URL"""
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    else:
        # 使用 SQLite
        return f"sqlite:///{settings.SQLITE_DB_PATH}"

def get_model_path() -> Path:
    """获取模型完整路径"""
    model_name = settings.YOLO_MODEL
    if not model_name.endswith('.pt'):
        model_name += '.pt'
    
    # 首先检查 models 目录
    model_path = settings.MODELS_DIR / model_name
    if model_path.exists():
        return model_path
    
    # 如果没有，使用默认路径
    return settings.PROJECT_ROOT / "models" / model_name

def get_data_dir() -> Path:
    """获取数据目录"""
    return settings.DATA_DIR

def get_logs_dir() -> Path:
    """获取日志目录"""
    return settings.LOGS_DIR

def is_development() -> bool:
    """是否开发环境"""
    return settings.ENVIRONMENT == "development"

def is_production() -> bool:
    """是否生产环境"""
    return settings.ENVIRONMENT == "production"

def is_testing() -> bool:
    """是否测试环境"""
    return settings.ENVIRONMENT == "testing"

# ==================== 初始化检查 ====================
def initialize_directories():
    """初始化所有必要目录"""
    directories = [
        settings.DATA_DIR,
        settings.MODELS_DIR,
        settings.LOGS_DIR,
        settings.DATA_DIR / "images",
        settings.DATA_DIR / "videos",
        settings.DATA_DIR / "detections",
        settings.DATA_DIR / "annotations",
        settings.LOGS_DIR / "app",
        settings.LOGS_DIR / "ai"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"确保目录存在: {directory}")

# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=settings.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(settings.LOGS_DIR / "config_test.log")
        ]
    )
    
    print_settings_summary()
    
    # 初始化目录
    initialize_directories()
    
    # 测试工具函数
    print(f"\n🔧 工具函数测试:")
    print(f"  数据库 URL: {get_database_url()}")
    print(f"  模型路径: {get_model_path()}")
    print(f"  数据目录: {get_data_dir()}")
    print(f"  日志目录: {get_logs_dir()}")
    print(f"  开发环境: {is_development()}")
    print(f"  生产环境: {is_production()}")
    
    # 验证路径
    print(f"\n✅ 路径验证:")
    for path_name, path in [
        ("项目根目录", settings.PROJECT_ROOT),
        ("数据目录", settings.DATA_DIR),
        ("模型目录", settings.MODELS_DIR),
        ("日志目录", settings.LOGS_DIR)
    ]:
        if path.exists():
            print(f"  {path_name}: {path} (存在)")
        else:
            print(f"  {path_name}: {path} (不存在)")
    
    print(f"\n🎉 配置测试完成!")