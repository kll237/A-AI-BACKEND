#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
摄像头服务模块
处理摄像头的CRUD操作和数据持久化
"""

import json
import os
import uuid
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime

from app.core.config import settings
from app.models.camera import Camera, CameraCreate, FilterConfig
from app.utils.stream_validator import StreamValidator
from app.core.websocket_manager import manager


class CameraService:
    def __init__(self):
        """初始化摄像头服务"""
        # 确保数据目录存在
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        self.cameras_file = settings.DATA_DIR / "cameras.json"

        # 如果cameras.json不存在，初始化一个空文件
        if not os.path.exists(self.cameras_file):
            with open(self.cameras_file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print(f"初始化空的摄像头文件: {self.cameras_file}")

    def _safe_json_load(self, filepath):
        """安全的JSON加载，处理编码问题"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(filepath, "rb") as f:
                content = f.read()

            # 尝试常见编码
            encodings = ['utf-8-sig', 'gbk', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    decoded = content.decode(encoding)
                    return json.loads(decoded)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue

            # 如果所有编码都失败，返回空字典
            print(f"警告: 无法读取文件 {filepath}，使用空数据")
            return {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _read_cameras(self) -> Dict:
        """从JSON文件读取摄像头数据"""
        try:
            cameras_data = self._safe_json_load(self.cameras_file)

            # 确保数据格式正确
            result = {}
            for cam_id, cam_details in cameras_data.items():
                if not isinstance(cam_details, dict):
                    continue

                # 确保必要字段存在
                if "is_active" not in cam_details:
                    cam_details["is_active"] = False
                if "stream_status" not in cam_details:
                    cam_details["stream_status"] = False
                if "filters" not in cam_details:
                    cam_details["filters"] = []

                result[cam_id] = cam_details
            return result

        except Exception as e:
            print(f"读取摄像头数据时出错: {e}")
            return {}

    def _write_cameras(self, cameras_data: Dict) -> None:
        """将摄像头数据写入JSON文件"""
        try:
            with open(self.cameras_file, "w", encoding="utf-8") as f:
                json.dump(cameras_data, f, ensure_ascii=False, indent=2)
            print(f"摄像头数据已保存: {self.cameras_file}")
        except Exception as e:
            print(f"保存摄像头数据时出错: {e}")
            raise

    def create_or_update_camera(self, camera_data: CameraCreate,
                                validation_result: Optional[Dict[str, Any]] = None) -> Camera:
        """创建或更新摄像头，包含可选的验证结果"""
        # 读取现有摄像头
        cameras = self._read_cameras()

        # 查找是否已有同名摄像头（更新）或创建新ID
        camera_id = None
        for cam_id, cam_info in cameras.items():
            if cam_info.get("name") == camera_data.name:
                camera_id = cam_id
                break

        if camera_id:
            # 更新现有摄像头
            cameras[camera_id]["rtsp_url"] = camera_data.rtsp_url
            cameras[camera_id]["updated_at"] = datetime.now().isoformat()
            cameras[camera_id]["filters"] = []

            # 处理过滤器
            if camera_data.filters:
                for filter_config in camera_data.filters:
                    try:
                        # 尝试使用model_dump() (Pydantic v2)
                        filter_dict = filter_config.model_dump()
                    except AttributeError:
                        try:
                            # 尝试使用dict() (Pydantic v1)
                            filter_dict = filter_config.dict()
                        except AttributeError:
                            # 手动创建字典
                            filter_dict = {
                                "filter_id": getattr(filter_config, "filter_id", str(uuid.uuid4())[:8]),
                                "filter_name": getattr(filter_config, "filter_name", ""),
                                "enabled": getattr(filter_config, "enabled", True)
                            }
                    cameras[camera_id]["filters"].append(filter_dict)

            # 添加验证结果（如果提供）
            if validation_result:
                cameras[camera_id]["stream_status"] = validation_result.get("is_valid", False)
                cameras[camera_id]["validation_result"] = validation_result
                cameras[camera_id]["is_active"] = validation_result.get("is_valid", False)
        else:
            # 创建新摄像头
            camera_id = str(uuid.uuid4())

            # 准备摄像头数据
            camera_dict = {
                "id": camera_id,
                "name": camera_data.name,
                "rtsp_url": camera_data.rtsp_url,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "filters": [],
                "is_active": False,
                "stream_status": False
            }

            # 处理过滤器
            if camera_data.filters:
                for filter_config in camera_data.filters:
                    try:
                        filter_dict = filter_config.model_dump()
                    except AttributeError:
                        try:
                            filter_dict = filter_config.dict()
                        except AttributeError:
                            filter_dict = {
                                "filter_id": str(uuid.uuid4())[:8],
                                "filter_name": getattr(filter_config, "filter_name", ""),
                                "enabled": getattr(filter_config, "enabled", True)
                            }
                    camera_dict["filters"].append(filter_dict)

            # 添加验证结果（如果提供）
            if validation_result:
                camera_dict["stream_status"] = validation_result.get("is_valid", False)
                camera_dict["validation_result"] = validation_result
                camera_dict["is_active"] = validation_result.get("is_valid", False)

            cameras[camera_id] = camera_dict

        # 保存更改
        self._write_cameras(cameras)

        # 返回摄像头对象
        return Camera(**cameras[camera_id])

    def get_camera(self, camera_id: str) -> Optional[Camera]:
        """通过ID获取摄像头"""
        cameras = self._read_cameras()
        if camera_id not in cameras:
            return None

        try:
            return Camera(**cameras[camera_id])
        except Exception as e:
            print(f"创建摄像头对象时出错 {camera_id}: {e}")
            return None

    def get_camera_by_id(self, camera_id: str) -> Optional[Camera]:
        """通过ID获取摄像头 - get_camera的别名"""
        return self.get_camera(camera_id)

    def get_camera_by_name(self, name: str) -> Optional[Camera]:
        """通过名称获取摄像头"""
        cameras = self._read_cameras()
        for camera_id, camera_info in cameras.items():
            if camera_info.get("name") == name:
                try:
                    return Camera(**camera_info)
                except Exception as e:
                    print(f"创建摄像头对象时出错 {camera_id}: {e}")
                    return None

        return None

    def update_camera_filters(self, camera_id: str, filters: List[Dict[str, Any]]) -> Optional[Camera]:
        """更新摄像头的过滤器"""
        cameras = self._read_cameras()
        if camera_id not in cameras:
            return None

        # 验证过滤器数据
        validated_filters = []
        for filter_data in filters:
            if not isinstance(filter_data, dict):
                continue

            # 确保必要字段
            validated_filter = {
                "filter_id": filter_data.get("filter_id", str(uuid.uuid4())[:8]),
                "filter_name": filter_data.get("filter_name", "未命名过滤器"),
                "enabled": filter_data.get("enabled", True)
            }
            validated_filters.append(validated_filter)

        # 更新摄像头
        cameras[camera_id]["filters"] = validated_filters
        cameras[camera_id]["updated_at"] = datetime.now().isoformat()

        # 保存更改
        self._write_cameras(cameras)

        # 返回更新后的摄像头
        try:
            return Camera(**cameras[camera_id])
        except Exception as e:
            print(f"创建摄像头对象时出错 {camera_id}: {e}")
            return None

    def delete_camera(self, camera_id: str) -> bool:
        """通过ID删除摄像头"""
        cameras = self._read_cameras()
        if camera_id not in cameras:
            return False

        # 从cameras.json中删除
        del cameras[camera_id]
        self._write_cameras(cameras)

        return True

    def delete_camera_by_name(self, name: str) -> bool:
        """通过名称删除摄像头"""
        cameras = self._read_cameras()
        camera_id = None

        for cam_id, cam_info in cameras.items():
            if cam_info.get("name") == name:
                camera_id = cam_id
                break

        if not camera_id:
            return False

        # 从cameras.json中删除
        del cameras[camera_id]
        self._write_cameras(cameras)

        return True

    def list_cameras(self) -> List[Camera]:
        """列出所有摄像头"""
        cameras = self._read_cameras()
        result = []

        for camera_data in cameras.values():
            try:
                camera_obj = Camera(**camera_data)
                result.append(camera_obj)
            except Exception as e:
                print(f"创建摄像头对象时出错: {e}")
                continue

        return result

    def get_all_cameras(self) -> Dict[str, Camera]:
        """获取所有摄像头作为字典，摄像头ID为键"""
        cameras = self._read_cameras()
        result = {}

        for camera_id, camera_data in cameras.items():
            try:
                camera_obj = Camera(**camera_data)
                result[camera_id] = camera_obj
            except Exception as e:
                print(f"创建摄像头对象时出错 {camera_id}: {e}")
                continue

        return result

    async def update_camera_active_status(self, camera_id: str, is_active: bool) -> Optional[Camera]:
        """更新摄像头的活动状态并广播更改"""
        cameras = self._read_cameras()
        if camera_id not in cameras:
            return None

        # 检查状态是否有变化
        current_active = cameras[camera_id].get("is_active", False)
        if current_active == is_active:
            try:
                return Camera(**cameras[camera_id])
            except Exception as e:
                print(f"创建摄像头对象时出错 {camera_id}: {e}")
                return None

        # 更新状态
        cameras[camera_id]["is_active"] = is_active
        cameras[camera_id]["updated_at"] = datetime.now().isoformat()
        self._write_cameras(cameras)

        # 准备广播消息
        notification_payload = {
            "type": "camera_status_update",
            "camera_id": camera_id,
            "name": cameras[camera_id].get("name", "未知摄像头"),
            "is_active": is_active,
            "timestamp": datetime.now().isoformat()
        }

        # 异步广播
        try:
            asyncio.create_task(manager.broadcast_json(notification_payload))
        except Exception as e:
            print(f"广播摄像头状态更新时出错: {e}")

        # 返回更新后的摄像头
        try:
            return Camera(**cameras[camera_id])
        except Exception as e:
            print(f"创建摄像头对象时出错 {camera_id}: {e}")
            return None

    def validate_camera_stream(self, camera_id: str) -> Optional[Dict]:
        """验证现有摄像头的视频流"""
        camera = self.get_camera(camera_id)
        if not camera:
            return None

        # 验证视频流
        validation_result = StreamValidator.validate_rtsp_stream(camera.rtsp_url)

        # 更新摄像头数据
        cameras = self._read_cameras()
        if camera_id in cameras:
            cameras[camera_id]["stream_status"] = validation_result.get("is_valid", False)
            cameras[camera_id]["validation_result"] = validation_result
            cameras[camera_id]["updated_at"] = datetime.now().isoformat()
            cameras[camera_id]["is_active"] = validation_result.get("is_valid", False)

            self._write_cameras(cameras)

        # 异步更新活动状态
        try:
            asyncio.create_task(self.update_camera_active_status(
                camera_id,
                validation_result.get("is_valid", False)
            ))
        except Exception as e:
            print(f"异步更新摄像头状态时出错: {e}")

        return validation_result


# 创建单例实例供全局使用
camera_service = CameraService()


def get_camera_by_id(camera_id: str) -> Optional[Camera]:
    """通过ID获取摄像头 - 模块级函数"""
    return camera_service.get_camera(camera_id)


def get_all_cameras() -> Dict[str, Camera]:
    """获取所有摄像头 - 模块级函数"""
    return camera_service.get_all_cameras()