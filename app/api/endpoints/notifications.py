from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class Notification(BaseModel):
    id: str
    title: str
    message: str
    type: str = "info"  # info, warning, error, success
    timestamp: str
    read: bool = False
    source: Optional[str] = None
    camera_id: Optional[str] = None
    rule_id: Optional[str] = None

class NotificationResponse(BaseModel):
    notifications: List[Notification]
    total: int
    unread_count: int

@router.get("/", response_model=NotificationResponse, summary="获取通知列表")
async def get_notifications(
    limit: int = Query(50, description="返回通知数量限制"),
    offset: int = Query(0, description="分页偏移量"),
    unread_only: bool = Query(False, description="只显示未读通知"),
    notification_type: Optional[str] = Query(None, description="按类型筛选通知")
):
    """
    ## 🔔 获取通知列表
    
    获取系统中的所有通知消息。
    
    ### 📋 功能说明：
    - 列出所有通知消息
    - 支持分页和筛选
    - 可筛选未读通知
    - 按通知类型筛选
    
    ### 📝 参数说明：
    - **limit** (可选): 返回通知数量限制，默认50
    - **offset** (可选): 分页偏移量，默认0
    - **unread_only** (可选): 只显示未读通知，默认false
    - **notification_type** (可选): 按类型筛选通知
      - info: 信息通知
      - warning: 警告通知
      - error: 错误通知
      - success: 成功通知
    
    ### ✅ 返回信息：
    - 通知列表（数组）
    - 通知总数统计
    - 未读通知数量
    - 分页信息
    
    ### 💡 使用场景：
    - 通知中心显示
    - 实时告警监控
    - 历史通知查询
    """
    try:
        # 示例数据 - 在实际应用中应从数据库获取
        example_notifications = [
            Notification(
                id="notif_1",
                title="摄像头上线",
                message="摄像头 '入口监控' 已上线并正常工作",
                type="success",
                timestamp=datetime.now().isoformat(),
                read=False,
                source="camera_monitor",
                camera_id="cam_001"
            ),
            Notification(
                id="notif_2",
                title="规则触发",
                message="考勤规则 '上班打卡' 已触发",
                type="info",
                timestamp=datetime.now().isoformat(),
                read=True,
                source="rule_engine",
                camera_id="cam_001",
                rule_id="rule_001"
            ),
            Notification(
                id="notif_3",
                title="系统警告",
                message="视频流延迟较高，请检查网络连接",
                type="warning",
                timestamp=datetime.now().isoformat(),
                read=False,
                source="stream_monitor",
                camera_id="cam_002"
            )
        ]
        
        # 筛选通知
        filtered_notifications = example_notifications
        
        if unread_only:
            filtered_notifications = [n for n in filtered_notifications if not n.read]
        
        if notification_type:
            filtered_notifications = [n for n in filtered_notifications if n.type == notification_type]
        
        # 应用分页
        total = len(filtered_notifications)
        paginated_notifications = filtered_notifications[offset:offset + limit]
        
        # 计算未读数量
        unread_count = sum(1 for n in filtered_notifications if not n.read)
        
        return NotificationResponse(
            notifications=paginated_notifications,
            total=total,
            unread_count=unread_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取通知列表时出错: {str(e)}")


@router.get("/unread/count", response_model=Dict[str, int], summary="获取未读通知数量")
async def get_unread_count():
    """
    ## 🔴 获取未读通知数量
    
    获取系统中当前未读通知的总数。
    
    ### 📋 功能说明：
    - 统计未读通知数量
    - 按通知类型分类统计
    - 返回实时统计数据
    
    ### ✅ 返回信息：
    - 未读通知总数
    - 各类型未读通知数量
    - 统计时间戳
    
    ### 💡 使用场景：
    - 通知角标显示
    - 实时告警监控
    - 系统状态仪表盘
    """
    try:
        # 示例数据 - 在实际应用中应从数据库统计
        return {
            "total_unread": 2,
            "info_unread": 0,
            "warning_unread": 1,
            "error_unread": 0,
            "success_unread": 1,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取未读通知数量时出错: {str(e)}")


@router.post("/{notification_id}/read", response_model=Dict[str, Any], summary="标记通知为已读")
async def mark_as_read(notification_id: str):
    """
    ## ✅ 标记通知为已读
    
    将指定的通知标记为已读状态。
    
    ### 📝 参数说明：
    - **notification_id** (必填): 通知ID
    
    ### ✅ 返回信息：
    - 操作结果状态
    - 被标记的通知信息
    - 更新后的未读数量
    
    ### 💡 使用场景：
    - 用户阅读通知后标记
    - 批量标记通知为已读
    - 自动清理已读通知
    """
    try:
        # 在实际应用中应更新数据库
        return {
            "状态": "成功",
            "消息": f"通知 {notification_id} 已标记为已读",
            "通知ID": notification_id,
            "操作时间": datetime.now().isoformat(),
            "更新后的未读数量": 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"标记通知为已读时出错: {str(e)}")


@router.delete("/{notification_id}", response_model=Dict[str, Any], summary="删除通知")
async def delete_notification(notification_id: str):
    """
    ## 🗑️ 删除通知
    
    从系统中删除指定的通知。
    
    ### 📝 参数说明：
    - **notification_id** (必填): 通知ID
    
    ### ✅ 返回信息：
    - 删除操作结果
    - 被删除的通知信息
    - 剩余通知数量
    
    ### ⚠️ 注意事项：
    - 删除操作不可逆
    - 重要通知建议归档而非删除
    - 系统通知可能无法删除
    """
    try:
        # 在实际应用中应从数据库删除
        return {
            "状态": "成功",
            "消息": f"通知 {notification_id} 已删除",
            "通知ID": notification_id,
            "删除时间": datetime.now().isoformat(),
            "剩余通知数量": 2
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除通知时出错: {str(e)}")


@router.delete("/", response_model=Dict[str, Any], summary="清空所有通知")
async def clear_all_notifications():
    """
    ## 🧹 清空所有通知
    
    清空系统中的所有通知消息。
    
    ### 📋 功能说明：
    - 清空所有已读通知
    - 可选保留未读通知
    - 支持按类型清空
    
    ### ⚠️ 注意事项：
    - 清空操作不可逆
    - 重要通知建议先备份
    - 系统通知不会被清空
    """
    try:
        # 在实际应用中应清空数据库
        return {
            "状态": "成功",
            "消息": "所有通知已清空",
            "清空时间": datetime.now().isoformat(),
            "清空数量": 3,
            "保留未读通知": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空通知时出错: {str(e)}")
