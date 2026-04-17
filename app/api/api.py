from fastapi import APIRouter

from app.api.endpoints import ai_vision, users, cameras, rules, notifications

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["摄像头管理"])
api_router.include_router(rules.router, prefix="/rules", tags=["规则管理"])
api_router.include_router(ai_vision.router, prefix="/contextual", tags=["智能分析"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["通知管理"])
