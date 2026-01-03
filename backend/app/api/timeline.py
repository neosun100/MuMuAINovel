"""时间线管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.database import get_db
from app.models.timeline import TimelineEvent
from app.models.project import Project
from app.schemas.timeline import (
    TimelineEventCreate,
    TimelineEventUpdate,
    TimelineEventResponse,
    TimelineListResponse
)
from app.logger import get_logger

router = APIRouter(prefix="/timeline", tags=["时间线管理"])
logger = get_logger(__name__)


async def verify_project_access(project_id: str, user_id: str, db: AsyncSession) -> Project:
    """验证用户项目访问权限"""
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权访问")
    return project


@router.post("", response_model=TimelineEventResponse, summary="创建时间线事件")
async def create_timeline_event(
    data: TimelineEventCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建新的时间线事件"""
    user_id = getattr(request.state, 'user_id', None)
    await verify_project_access(data.project_id, user_id, db)
    
    event = TimelineEvent(
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        event_type=data.event_type.value,
        story_time=data.story_time,
        story_day=data.story_day,
        chapter_id=data.chapter_id,
        chapter_number=data.chapter_number,
        related_characters=data.related_characters,
        importance=data.importance
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    logger.info(f"✅ 创建时间线事件: {event.title}")
    return TimelineEventResponse(**event.to_dict())


@router.get("", response_model=TimelineListResponse, summary="获取时间线事件列表")
async def list_timeline_events(
    request: Request,
    project_id: str = Query(..., description="项目ID"),
    event_type: Optional[str] = Query(None, description="事件类型筛选"),
    chapter_number: Optional[int] = Query(None, description="章节号筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取项目的时间线事件列表"""
    user_id = getattr(request.state, 'user_id', None)
    await verify_project_access(project_id, user_id, db)
    
    query = select(TimelineEvent).where(TimelineEvent.project_id == project_id)
    
    if event_type:
        query = query.where(TimelineEvent.event_type == event_type)
    if chapter_number:
        query = query.where(TimelineEvent.chapter_number == chapter_number)
    
    # 按故事天数排序，然后按章节号
    query = query.order_by(
        TimelineEvent.story_day.nullslast(),
        TimelineEvent.chapter_number.nullslast(),
        TimelineEvent.importance.desc()
    )
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return TimelineListResponse(
        items=[TimelineEventResponse(**e.to_dict()) for e in events],
        total=len(events)
    )


@router.get("/{event_id}", response_model=TimelineEventResponse, summary="获取时间线事件详情")
async def get_timeline_event(
    event_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """获取单个时间线事件详情"""
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(select(TimelineEvent).where(TimelineEvent.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    await verify_project_access(event.project_id, user_id, db)
    return TimelineEventResponse(**event.to_dict())


@router.put("/{event_id}", response_model=TimelineEventResponse, summary="更新时间线事件")
async def update_timeline_event(
    event_id: str,
    data: TimelineEventUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """更新时间线事件"""
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(select(TimelineEvent).where(TimelineEvent.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    await verify_project_access(event.project_id, user_id, db)
    
    update_data = data.model_dump(exclude_unset=True)
    if 'event_type' in update_data and update_data['event_type']:
        update_data['event_type'] = update_data['event_type'].value
    
    for key, value in update_data.items():
        setattr(event, key, value)
    
    await db.commit()
    await db.refresh(event)
    
    logger.info(f"✅ 更新时间线事件: {event.title}")
    return TimelineEventResponse(**event.to_dict())


@router.delete("/{event_id}", summary="删除时间线事件")
async def delete_timeline_event(
    event_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """删除时间线事件"""
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(select(TimelineEvent).where(TimelineEvent.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    await verify_project_access(event.project_id, user_id, db)
    
    await db.delete(event)
    await db.commit()
    
    logger.info(f"✅ 删除时间线事件: {event.title}")
    return {"success": True, "message": "事件已删除"}


@router.get("/chapter/{chapter_id}/events", summary="获取章节相关事件")
async def get_chapter_events(
    chapter_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """获取与指定章节相关的时间线事件"""
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(
        select(TimelineEvent).where(TimelineEvent.chapter_id == chapter_id)
        .order_by(TimelineEvent.story_day.nullslast(), TimelineEvent.importance.desc())
    )
    events = result.scalars().all()
    
    if events:
        await verify_project_access(events[0].project_id, user_id, db)
    
    return {
        "chapter_id": chapter_id,
        "events": [TimelineEventResponse(**e.to_dict()) for e in events],
        "total": len(events)
    }
