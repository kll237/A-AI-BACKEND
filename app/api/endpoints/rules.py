from fastapi import APIRouter, HTTPException, Body, Query, Path
from typing import List, Optional

from app.models.rule import Rule, RuleCreate, RuleUpdate, RuleResponse
from app.services.rule_service import rule_service
from app.services.camera_service import camera_service

router = APIRouter()

@router.post("/", response_model=RuleResponse, summary="创建规则")
async def create_rule(rule_data: RuleCreate = Body(...)):
    """
    ## ⚙️ 创建检测规则
    
    创建新的智能检测规则。
    
    ### 📋 功能说明：
    - 创建新的检测规则
    - 配置检测条件和触发动作
    - 关联摄像头设备
    - 设置规则启用状态
    
    ### 📝 参数说明：
    - **name** (必填): 规则名称，用于识别
    - **event** (必填): 事件类型
      - attendance: 考勤检测
      - intrusion: 入侵检测
      - counting: 人数统计
      - custom: 自定义检测
    - **condition** (必填): 检测条件配置
      - 对象类型、置信度阈值
      - 区域设置、时间条件
    - **enabled** (可选): 是否立即启用规则
    - **days** (可选): 生效日期设置
      - 示例: ["mon", "tue", "wed", "thu", "fri"]
    - **cameraId** (必填): 关联的摄像头ID
    
    ### ✅ 返回信息：
    - 规则创建成功的确认信息
    - 规则ID和详细配置
    - 关联的摄像头信息
    - 规则状态信息
    
    ### ⚠️ 注意事项：
    - 摄像头必须已存在于系统中
    - 条件配置需要与事件类型匹配
    - 复杂的规则可能需要分步配置
    """
    try:
        # Verify camera exists
        camera = camera_service.get_camera(rule_data.cameraId)
        if not camera:
            raise HTTPException(
                status_code=404,
                detail=f"摄像头ID {rule_data.cameraId} 不存在"
            )

        # Create the rule
        new_rule = rule_service.create_rule(rule_data)

        return RuleResponse(
            id=new_rule.id,
            name=new_rule.name,
            event=new_rule.event,
            condition=new_rule.condition,
            enabled=new_rule.enabled,
            days=new_rule.days,
            cameraId=new_rule.cameraId,
            cameraName=new_rule.cameraName,
            created_at=new_rule.created_at,
            updated_at=new_rule.updated_at,
            message="规则创建成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建规则时出错: {str(e)}")


@router.get("/", response_model=List[RuleResponse], summary="获取所有规则")
async def get_all_rules(
    camera_id: Optional[str] = Query(None, description="按摄像头ID筛选规则"),
    event_type: Optional[str] = Query(None, description="按事件类型筛选规则")
):
    """
    ## 📋 获取所有规则列表
    
    获取系统中所有已配置的检测规则。
    
    ### 📋 功能说明：
    - 列出所有规则的详细信息
    - 支持按摄像头筛选
    - 支持按事件类型筛选
    - 显示规则状态（启用/禁用）
    
    ### 📝 参数说明：
    - **camera_id** (可选): 摄像头ID，筛选该摄像头的规则
    - **event_type** (可选): 事件类型，筛选指定类型的规则
      - attendance: 考勤规则
      - intrusion: 入侵规则
      - counting: 计数规则
    
    ### ✅ 返回信息：
    - 规则列表（数组）
    - 每个规则的完整信息：
      - ID、名称、事件类型
      - 条件配置、启用状态
      - 关联摄像头信息
      - 创建时间、更新时间
    
    ### 💡 使用场景：
    - 规则管理界面
    - 规则状态监控
    - 规则效果分析
    - 摄像头规则配置查看
    """
    try:
        rules = rule_service.list_rules(camera_id=camera_id, event_type=event_type)

        return [
            RuleResponse(
                id=rule.id,
                name=rule.name,
                event=rule.event,
                condition=rule.condition,
                enabled=rule.enabled,
                days=rule.days,
                cameraId=rule.cameraId,
                cameraName=rule.cameraName,
                created_at=rule.created_at,
                updated_at=rule.updated_at,
                message="规则获取成功"
            ) for rule in rules
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规则列表时出错: {str(e)}")


@router.get("/{rule_id}", response_model=RuleResponse, summary="获取规则详情")
async def get_rule(rule_id: str = Path(..., description="规则ID")):
    """
    ## 🔍 获取规则详情
    
    根据规则ID获取具体的规则配置信息。
    
    ### 📝 参数说明：
    - **rule_id** (必填): 规则唯一标识符
    
    ### ✅ 返回信息：
    - 规则的完整详细信息
    - 条件配置详情
    - 关联摄像头信息
    - 规则历史记录
    
    ### ⚠️ 注意事项：
    - 需要有效的规则ID
    - 规则必须已存在于系统中
    """
    try:
        rule = rule_service.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail=f"规则ID {rule_id} 不存在")

        return RuleResponse(
            id=rule.id,
            name=rule.name,
            event=rule.event,
            condition=rule.condition,
            enabled=rule.enabled,
            days=rule.days,
            cameraId=rule.cameraId,
            cameraName=rule.cameraName,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            message="规则详情获取成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规则详情时出错: {str(e)}")


@router.put("/{rule_id}", response_model=RuleResponse, summary="更新规则")
async def update_rule(
    rule_id: str = Path(..., description="要更新的规则ID"),
    rule_data: RuleUpdate = Body(...)
):
    """
    ## ✏️ 更新规则配置
    
    修改指定规则的配置信息。
    
    ### 📝 参数说明：
    - **rule_id** (必填): 要更新的规则ID
    - **rule_data** (必填): 新的规则配置数据
    
    ### ✅ 返回信息：
    - 更新操作结果
    - 更新后的规则配置
    - 修改时间戳
    
    ### ⚠️ 注意事项：
    - 只能更新已存在的规则
    - 部分字段更新可能需要重启相关服务
    - 摄像头变更需要验证新摄像头存在
    """
    try:
        # Check if rule exists
        existing_rule = rule_service.get_rule(rule_id)
        if not existing_rule:
            raise HTTPException(status_code=404, detail=f"规则ID {rule_id} 不存在")

        # Verify camera exists if cameraId is being updated
        if hasattr(rule_data, 'cameraId') and rule_data.cameraId:
            camera = camera_service.get_camera(rule_data.cameraId)
            if not camera:
                raise HTTPException(
                    status_code=404,
                    detail=f"摄像头ID {rule_data.cameraId} 不存在"
                )

        # Update the rule
        updated_rule = rule_service.update_rule(rule_id, rule_data)

        return RuleResponse(
            id=updated_rule.id,
            name=updated_rule.name,
            event=updated_rule.event,
            condition=updated_rule.condition,
            enabled=updated_rule.enabled,
            days=updated_rule.days,
            cameraId=updated_rule.cameraId,
            cameraName=updated_rule.cameraName,
            created_at=updated_rule.created_at,
            updated_at=updated_rule.updated_at,
            message="规则更新成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新规则时出错: {str(e)}")


@router.delete("/{rule_id}", response_model=dict, summary="删除规则")
async def delete_rule(rule_id: str = Path(..., description="要删除的规则ID")):
    """
    ## 🗑️ 删除规则
    
    从系统中删除指定的规则。
    
    ### 📝 参数说明：
    - **rule_id** (必填): 要删除的规则ID
    
    ### ✅ 返回信息：
    - 删除操作结果
    - 被删除的规则信息
    
    ### ⚠️ 注意事项：
    - 删除操作不可逆
    - 关联的分析任务也会被停止
    - 确保不再需要该规则的检测功能
    """
    try:
        rule = rule_service.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail=f"规则ID {rule_id} 不存在")

        rule_service.delete_rule(rule_id)

        return {
            "状态": "成功",
            "消息": "规则已删除",
            "被删除的规则": {
                "id": rule.id,
                "name": rule.name,
                "cameraName": rule.cameraName
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除规则时出错: {str(e)}")


@router.patch("/{rule_id}", response_model=RuleResponse, summary="切换规则状态")
async def toggle_rule_status(
    rule_id: str = Path(..., description="规则ID"),
    enabled: bool = Body(..., embed=True, description="新的启用状态")
):
    """
    ## 🔄 切换规则状态
    
    启用或禁用指定的规则。
    
    ### 📝 参数说明：
    - **rule_id** (必填): 规则ID
    - **enabled** (必填): 新的启用状态
      - true: 启用规则
      - false: 禁用规则
    
    ### ✅ 返回信息：
    - 状态切换结果
    - 规则当前状态
    - 操作确认信息
    
    ### 💡 使用场景：
    - 临时禁用故障规则
    - 按需启用/禁用规则
    - 规则维护和测试
    """
    try:
        rule = rule_service.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail=f"规则ID {rule_id} 不存在")

        updated_rule = rule_service.update_rule_status(rule_id, enabled)

        status_text = "已启用" if enabled else "已禁用"
        return RuleResponse(
            id=updated_rule.id,
            name=updated_rule.name,
            event=updated_rule.event,
            condition=updated_rule.condition,
            enabled=updated_rule.enabled,
            days=updated_rule.days,
            cameraId=updated_rule.cameraId,
            cameraName=updated_rule.cameraName,
            created_at=updated_rule.created_at,
            updated_at=updated_rule.updated_at,
            message=f"规则状态已切换为: {status_text}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换规则状态时出错: {str(e)}")
