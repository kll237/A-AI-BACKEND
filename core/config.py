# config.py
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
from pathlib import Path
import os


class Settings(BaseSettings):
    # ==================== 项目基础配置 ====================
    PROJECT_NAME: str = "智能摄像头管理系统"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"  # development, testing, production

    # ==================== 服务器配置 ====================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = True
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # ==================== CORS 配置 ====================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "*"  # 允许所有来源（仅用于开发）
    ]

    # ==================== 文件路径配置 ====================
    # 项目根目录
    BASE_DIR: Path = Path(__file__).parent.parent.parent

    # 数据目录
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_PATH: Path = DATA_DIR / "database.db"

    # 模型目录
    MODELS_DIR: Path = BASE_DIR / "models"

    # 日志目录
    LOGS_DIR: Path = BASE_DIR / "logs"

    # ==================== AI 模型配置 ====================
    YOLO_MODEL: str = "yolov8n.pt"
    IMAGE_SIZE: int = 640
    BATCH_SIZE: int = 1
    ENABLE_GPU: bool = True
    CONFIDENCE_THRESHOLD: float = 0.5

    # 人脸识别配置
    FACE_DETECTION_ENABLED: bool = True
    FACE_RECOGNITION_ENABLED: bool = False
    FACE_CONFIDENCE_THRESHOLD: float = 0.6

    # ==================== 摄像头配置 ====================
    CAMERA_CONFIG_PATH: Path = DATA_DIR / "cameras.json"
    MAX_CAMERAS: int = 10
    DEFAULT_FRAME_RATE: int = 30
    DEFAULT_RESOLUTION_WIDTH: int = 1920
    DEFAULT_RESOLUTION_HEIGHT: int = 1080

    # ==================== 安全配置 ====================
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==================== 数据库配置 ====================
    DATABASE_URL: str = f"sqlite:///{DATA_DIR}/database.db"
    DATABASE_ECHO: bool = False

    # ==================== 用户配置 ====================
    DEFAULT_USER_ROLE: str = "user"
    ADMIN_USER_ROLE: str = "admin"
    USER_CONFIG_PATH: Path = DATA_DIR / "users.json"

    # ==================== 规则配置 ====================
    RULES_CONFIG_PATH: Path = DATA_DIR / "rules.json"

    # ==================== API 配置 ====================
    API_TIMEOUT: int = 30  # 秒
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB

    # ==================== 可选的外部服务配置 ====================
    # OpenAI API（可选）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # HuggingFace（可选）
    HUGGINGFACE_TOKEN: Optional[str] = None

    # Ollama（可选）
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"

    # ==================== 监控配置 ====================
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # ==================== 验证器 ====================
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"

    @property
    def api_url(self) -> str:
        return f"http://{self.HOST}:{self.PORT}{self.API_V1_STR}"

    @property
    def database_path(self) -> Path:
        """获取数据库文件路径"""
        return self.DATA_DIR / "database.db"

    @property
    def logs_path(self) -> Path:
        """获取日志文件路径"""
        return self.LOGS_DIR / f"{self.PROJECT_NAME.lower().replace(' ', '_')}.log"

    def create_dirs(self):
        """创建必要的目录"""
        dirs_to_create = [
            self.DATA_DIR,
            self.MODELS_DIR,
            self.LOGS_DIR
        ]

        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ 目录已创建/存在: {directory}")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量


# 创建设置实例
settings = Settings()

# 自动创建必要的目录
try:
    settings.create_dirs()
    print(f"✓ 配置加载成功: {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    print(f"✓ 环境: {settings.ENVIRONMENT}")
    print(f"✓ 服务器: {settings.HOST}:{settings.PORT}")
    print(f"✓ 调试模式: {settings.DEBUG}")
    print(f"✓ 数据目录: {settings.DATA_DIR}")
except Exception as e:
    print(f"⚠ 警告: 创建目录时出错: {e}")