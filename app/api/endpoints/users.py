from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
import shutil
import os
from typing import Optional, List
import json
from datetime import datetime
from pathlib import Path
import uuid

from app.core.config import settings
from app.models.user import UserProfile, UserProfileCreate, UserProfileResponse
from app.services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.post("/profile", response_model=UserProfileResponse, summary="创建用户资料")
async def create_user_profile(
    username: str = Form(..., description="用户名，必填项"),
    full_name: str = Form(..., description="用户全名，必填项"),
    age: int = Form(..., description="用户年龄，必填项"),
    role: str = Form(..., description="用户角色，必填项"),
    photo: Optional[UploadFile] = File(None, description="用户头像照片，可选")
):
    """
    ## 👤 创建或更新用户资料
    
    创建新用户或更新现有用户的个人信息，支持上传头像照片。
    
    ### 📋 功能说明：
    - 创建新用户账号
    - 更新现有用户信息
    - 上传用户头像照片
    - 设置用户角色权限
    
    ### 📝 参数说明：
    - **username** (必填): 用户名，用于登录和识别
    - **full_name** (必填): 用户的真实姓名
    - **age** (必填): 用户年龄
    - **role** (必填): 用户角色
      - admin: 管理员，拥有所有权限
      - user: 普通用户，基本操作权限
      - guest: 访客，只读权限
    - **photo** (可选): 用户头像照片
      - 支持格式: jpg, png
      - 最大大小: 5MB
    
    ### ✅ 返回信息：
    - 用户创建/更新成功的确认信息
    - 用户资料详情
    - 头像访问地址
    
    ### ⚠️ 注意事项：
    - 用户名必须是唯一的
    - 头像文件大小不超过5MB
    - 仅支持jpg和png格式的图片
    """
    try:
        # Handle photo upload if provided
        photo_path = None
        if photo:
            # Validate file type
            if photo.content_type not in settings.ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"只支持 {', '.join(settings.ALLOWED_IMAGE_TYPES)} 格式的图片"
                )

            # Generate a unique ID for this upload
            unique_id = str(uuid.uuid4())

            # Create directory structure data/uniqueid/
            unique_dir = settings.DATA_DIR / unique_id
            os.makedirs(unique_dir, exist_ok=True)

            # Get file extension
            file_extension = os.path.splitext(photo.filename)[1]

            # Use username as the filename with the original extension
            filename = f"{username}{file_extension}"
            photo_path = str(unique_dir / filename)

            # Save the file
            with open(photo_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)

        # Create user profile
        user_data = UserProfileCreate(
            username=username,
            full_name=full_name,
            age=age,
            role=role,
            photo_path=photo_path,
            created_at=datetime.now().isoformat()
        )

        # Get the full user profile with photo_url from the service
        user_profile = user_service.create_or_update_profile(user_data)

        return UserProfileResponse(
            username=user_profile.username,
            full_name=user_profile.full_name,
            age=user_profile.age,
            role=user_profile.role,
            photo_url=user_profile.photo_url,
            message="用户资料创建成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户资料时出错: {str(e)}")


@router.get("/profile/{username}", response_model=UserProfileResponse, summary="获取用户资料")
async def get_user_profile(username: str):
    """
    ## 🔍 获取用户资料详情
    
    根据用户名获取用户的完整个人资料。
    
    ### 📝 参数说明：
    - **username** (必填): 要查询的用户名
    
    ### ✅ 返回信息：
    - 用户的完整个人资料
    - 角色权限信息
    - 头像访问地址
    
    ### ⚠️ 注意事项：
    - 需要有效的用户名
    - 用户必须已存在于系统中
    """
    try:
        user_profile = user_service.get_profile(username)
        if not user_profile:
            raise HTTPException(status_code=404, detail=f"用户 {username} 不存在")

        return UserProfileResponse(
            username=user_profile.username,
            full_name=user_profile.full_name,
            age=user_profile.age,
            role=user_profile.role,
            photo_url=user_profile.photo_url,
            message="用户资料获取成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户资料时出错: {str(e)}")


@router.get("/profiles", response_model=List[UserProfileResponse], summary="获取所有用户资料")
async def get_all_user_profiles():
    """
    ## 📋 获取所有用户列表
    
    获取系统中所有用户的个人资料信息。
    
    ### 📋 功能说明：
    - 列出所有用户的详细信息
    - 显示用户角色和权限
    - 返回用户创建时间
    
    ### ✅ 返回信息：
    - 用户列表（数组）
    - 每个用户的完整信息：
      - 用户名、全名、年龄
      - 角色、头像地址
      - 创建时间
    
    ### 💡 使用场景：
    - 用户管理界面
    - 权限配置和审核
    - 系统用户统计
    """
    try:
        user_profiles = user_service.list_profiles()

        # Convert to response models using saved photo_url
        response_profiles = []
        for profile in user_profiles:
            response_profiles.append(
                UserProfileResponse(
                    username=profile.username,
                    full_name=profile.full_name,
                    age=profile.age,
                    role=profile.role,
                    photo_url=profile.photo_url,
                    message="用户资料获取成功"
                )
            )

        return response_profiles

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表时出错: {str(e)}")


@router.delete("/profile/{username}", response_model=dict, summary="删除用户资料")
async def delete_user_profile(username: str):
    """
    ## 🗑️ 删除用户资料
    
    从系统中删除指定用户的个人资料。
    
    ### 📝 参数说明：
    - **username** (必填): 要删除的用户名
    
    ### ✅ 返回信息：
    - 删除操作结果
    - 被删除的用户信息
    
    ### ⚠️ 注意事项：
    - 删除操作不可逆
    - 管理员权限可能需要
    - 用户关联的数据也会被清理
    """
    try:
        success = user_service.delete_profile(username)
        if not success:
            raise HTTPException(status_code=404, detail=f"用户 {username} 不存在")

        return {
            "username": username,
            "状态": "成功",
            "消息": f"用户资料 {username} 已成功删除"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户资料时出错: {str(e)}")


@router.get("/roles", response_model=List[str], summary="获取所有角色")
async def get_all_roles():
    """
    ## 🏷️ 获取系统支持的所有角色
    
    获取系统中定义的所有用户角色类型。
    
    ### 📋 功能说明：
    - 列出所有可用的用户角色
    - 显示角色权限说明
    - 返回角色配置信息
    
    ### ✅ 返回信息：
    - 角色名称列表（按字母排序）
    - 角色数量统计
    
    ### 💡 使用场景：
    - 用户权限配置
    - 角色管理和分配
    - 权限验证和检查
    """
    try:
        users_file = os.path.join(settings.DATA_DIR, "users.json")

        if not os.path.exists(users_file):
            return []

        # Read users data
        with open(users_file, "r") as f:
            users_data = json.load(f)

        # Extract all unique roles
        roles = set()
        for username, user_data in users_data.items():
            if "role" in user_data and user_data["role"]:
                roles.add(user_data["role"])

        return sorted(list(roles))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色列表时出错: {str(e)}")
