#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
摄像头管理API - 简化版
避免编码问题
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from app.services.camera_service import camera_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]], summary="获取所有摄像头")
async def get_all_cameras():
    """
    ## 📹 获取所有摄像头列表

    获取系统中所有摄像头的详细信息。
    """
    try:
        cameras_dict = camera_service.get_all_cameras()

        # 转换为简单格式
        cameras_list = []
        for camera_id, camera in cameras_dict.items():
            camera_info = {
                "id": camera.id,
                "name": camera.name,
                "rtsp_url": camera.rtsp_url,
                "is_active": camera.is_active,
                "stream_status": getattr(camera, 'stream_status', False),
                "filters": [
                    {
                        "filter_id": f.filter_id,
                        "filter_name": f.filter_name,
                        "enabled": f.enabled
                    }
                    for f in camera.filters
                ] if hasattr(camera, 'filters') else []
            }
            cameras_list.append(camera_info)

        return cameras_list

    except Exception as e:
        logger.error(f"获取摄像头列表时出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取摄像头列表失败: {str(e)}"
        )

@router.get("/with-filters", response_model=List[Dict[str, Any]], summary="获取带过滤器的摄像头")
async def get_cameras_with_filters():
    """
    ## 🔧 获取带过滤器的摄像头

    获取所有摄像头及其过滤器配置。
    """
    try:
        cameras_dict = camera_service.get_all_cameras()

        cameras_list = []
        for camera_id, camera in cameras_dict.items():
            camera_info = {
                "id": camera.id,
                "name": camera.name,
                "rtsp_url": camera.rtsp_url,
                "is_active": camera.is_active,
                "filters": [
                    {
                        "filter_id": f.filter_id,
                        "filter_name": f.filter_name,
                        "enabled": f.enabled
                    }
                    for f in camera.filters
                ]
            }
            cameras_list.append(camera_info)

        return cameras_list

    except Exception as e:
        logger.error(f"获取带过滤器的摄像头时出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取摄像头信息失败: {str(e)}"
        )
