"""
AI Engine Module
"""
import logging
from .engine import AIEngine

logger = logging.getLogger(__name__)

# 创建全局实例
ai_engine = AIEngine()

# 导出
__all__ = ['AIEngine', 'ai_engine']

logger.info("AI Engine模块加载完成")
