"""
智能视觉分析API端点
处理AI视觉查询和分析功能
"""

import logging
import sys
import os
import json
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

# ========== 编码修复 ==========
# 确保标准输出使用UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# ========== 导入项目模块 ==========
try:
    from app.core.config import settings
    from app.services.camera_service import camera_service
    from app.ai_engine.engine import AIEngine
    from app.ai_engine import ai_engine  # Import the ai_engine instance directly
except ImportError as e:
    # 尝试备选导入路径
    import sys
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        from app.core.config import settings
        from app.services.camera_service import camera_service
        from app.ai_engine.engine import AIEngine
        from app.ai_engine import ai_engine
    except ImportError:
        raise ImportError(f"无法导入项目模块: {e}")

logger = logging.getLogger(__name__)

router = APIRouter()


class QueryRequest(BaseModel):
    camera_id: str
    query: str


class QueryResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    camera_id: Optional[str] = None
    camera_name: Optional[str] = None
    timestamp: Optional[str] = None
    model: Optional[str] = None


def safe_json_loads(data):
    """安全的JSON加载函数，处理编码问题"""
    if isinstance(data, bytes):
        # 尝试多种编码
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                decoded = data.decode(encoding)
                return json.loads(decoded)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        raise ValueError("无法解码JSON数据")
    return json.loads(data)


@router.post("/query", response_model=QueryResponse, summary="智能视觉查询")
async def process_contextual_query(request: QueryRequest):
    """
    ## 🤖 智能视觉查询

    对摄像头视频流进行AI视觉智能分析查询。

    ### 📋 功能说明：
    - 对指定摄像头的实时视频进行AI分析
    - 支持自然语言问题查询
    - 使用Gemini Flash 2.0视觉模型
    - 返回智能分析结果

    ### 📝 参数说明：
    - **camera_id** (必填): 摄像头ID
    - **query** (必填): 查询问题
      - 示例: "画面中有多少人？"
      - 示例: "检测到哪些物体？"
      - 示例: "描述当前场景"

    ### ✅ 返回信息：
    - 查询处理结果（成功/失败）
    - AI分析回答内容
    - 摄像头信息和时间戳
    - 使用的AI模型信息

    ### ⚠️ 注意事项：
    - 摄像头必须已启用视觉分析过滤器
    - 需要摄像头在线且视频流正常
    - 复杂的查询可能需要更长的处理时间

    ### 💡 使用场景：
    - 实时场景分析
    - 物体检测和识别
    - 异常行为识别
    - 场景描述和报告
    """
    try:
        # Check if the camera exists
        camera = camera_service.get_camera(request.camera_id)
        if not camera:
            logger.error(f"摄像头不存在: {request.camera_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"摄像头不存在: {request.camera_id}"
            )

        # Check if the camera has the Vision filter enabled
        vision_filter_enabled = False
        for filter_config in camera.filters:
            if filter_config.filter_name == "OllamaVision" and filter_config.enabled:
                vision_filter_enabled = True
                break

        if not vision_filter_enabled:
            logger.error(f"摄像头 {request.camera_id} 未启用视觉分析功能")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"摄像头 {request.camera_id} 未启用视觉分析功能"
            )

        # Get or create the Vision processor for this camera
        processor_key = f"ollamavision_{request.camera_id}"

        if processor_key not in ai_engine.active_processors:
            # Import here to avoid circular imports
            from app.ai_engine.processors.ai_vision_processor import OllamaVisionProcessor

            # Create the output directory
            output_dir = settings.DATA_DIR / "unauthorized"

            # Create the processor
            logger.info(f"为摄像头 {camera.name} (ID: {request.camera_id}) 创建智能查询处理器")

            # Convert Camera object to dictionary for the processor
            try:
                # Try model_dump() (Pydantic v2)
                filters_list = [filter_config.model_dump() for filter_config in camera.filters]
            except AttributeError:
                try:
                    # Try dict() (Pydantic v1)
                    filters_list = [filter_config.dict() for filter_config in camera.filters]
                except AttributeError:
                    # Fallback to manual dictionary creation
                    filters_list = []
                    for filter_config in camera.filters:
                        filters_list.append({
                            "filter_id": filter_config.filter_id,
                            "filter_name": filter_config.filter_name,
                            "enabled": filter_config.enabled
                        })

            camera_dict = {
                "id": camera.id,
                "name": camera.name,
                "rtsp_url": camera.rtsp_url,
                "filters": filters_list,
                "is_active": camera.is_active
            }

            processor = OllamaVisionProcessor(
                camera_dict,
                output_dir=output_dir,
                model_name="gemini-flash-2.0"
            )
            ai_engine.active_processors[processor_key] = processor

        # Get the processor and process the query
        processor = ai_engine.active_processors[processor_key]

        try:
            response_text = processor.process_query(request.query)

            return QueryResponse(
                success=True,
                response=response_text,
                camera_id=request.camera_id,
                camera_name=camera.name,
                timestamp=datetime.now().isoformat(),
                model="Gemini Flash 2.0"
            )
        except Exception as query_error:
            logger.error(f"处理查询时出错: {str(query_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI分析查询失败: {str(query_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"智能查询处理出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能查询处理出错: {str(e)}"
        )


@router.get("/cameras", response_model=List[Dict], summary="获取支持视觉分析的摄像头")
async def get_vision_cameras():
    """
    ## 📹 获取支持视觉分析的摄像头列表

    获取系统中所有已启用AI视觉分析功能的摄像头。

    ### 📋 功能说明：
    - 列出所有支持AI分析的摄像头
    - 显示摄像头的视觉分析状态
    - 返回摄像头基本信息和配置

    ### ✅ 返回信息：
    - 支持视觉分析的摄像头列表
    - 每个摄像头的详细信息：
      - ID、名称、RTSP地址
      - 视觉分析启用状态
      - 支持的AI模型
      - 最后分析时间

    ### 💡 使用场景：
    - 选择可分析的摄像头
    - 监控视觉分析状态
    - 配置管理界面显示
    """
    try:
        # Get all cameras
        cameras_dict = camera_service.get_all_cameras()

        # Filter cameras with Vision enabled
        vision_cameras = []
        for camera_id, camera in cameras_dict.items():
            vision_filter_enabled = False
            for filter_config in camera.filters:
                if filter_config.filter_name == "OllamaVision" and filter_config.enabled:
                    vision_filter_enabled = True
                    break

            if vision_filter_enabled:
                # Check if the processor is active
                processor_key = f"ollamavision_{camera_id}"
                is_active = processor_key in ai_engine.active_processors and ai_engine.active_processors[
                    processor_key].is_active

                # Add camera with active status
                camera_info = {
                    "id": camera.id,
                    "name": camera.name,
                    "is_active": is_active,
                    "model": "gemini-2.0-flash",
                    "timestamp": datetime.now().isoformat()
                }
                vision_cameras.append(camera_info)

        return vision_cameras

    except Exception as e:
        logger.error(f"获取视觉分析摄像头时出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取视觉分析摄像头时出错: {str(e)}"
        )


# 添加一个简单的健康检查端点
@router.get("/health", summary="视觉分析服务健康检查")
async def health_check():
    """检查视觉分析服务是否正常"""
    try:
        # 尝试获取摄像头数量
        cameras_dict = camera_service.get_all_cameras()
        vision_count = 0

        for camera_id, camera in cameras_dict.items():
            for filter_config in camera.filters:
                if filter_config.filter_name == "OllamaVision" and filter_config.enabled:
                    vision_count += 1
                    break

        return {
            "status": "healthy",
            "service": "ai_vision",
            "vision_cameras_count": vision_count,
            "active_processors": len(ai_engine.active_processors),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "ai_vision",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }