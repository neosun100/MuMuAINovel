"""伏笔管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.foreshadow import Foreshadow, ForeshadowStatus, ForeshadowType
from app.models.project import Project
from app.models.chapter import Chapter
from app.models.character import Character
from app.schemas.foreshadow import (
    ForeshadowCreate,
    ForeshadowUpdate,
    ForeshadowResponse,
    ForeshadowListResponse,
    ForeshadowReminder,
    ForeshadowReminderResponse,
    ResolveForeshadowRequest
)
from app.logger import get_logger

router = APIRouter(prefix="/foreshadows", tags=["伏笔管理"])
logger = get_logger(__name__)


async def verify_project_access(project_id: str, user_id: str, db: AsyncSession) -> Project:
    """验证用户项目访问权限"""
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == user_id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权访问")
    
    return project


@router.post("", response_model=ForeshadowResponse, summary="创建伏笔")
async def create_foreshadow(
    data: ForeshadowCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """创建新伏笔"""
    user_id = getattr(request.state, 'user_id', None)
    await verify_project_access(data.project_id, user_id, db)
    
    foreshadow = Foreshadow(
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        foreshadow_type=data.foreshadow_type.value,
        importance=data.importance,
        planted_chapter_id=data.planted_chapter_id,
        planted_chapter_number=data.planted_chapter_number,
        planted_content=data.planted_content,
        resolved_chapter_number=data.resolved_chapter_number,
        related_characters=data.related_characters,
        tags=data.tags,
        remind_before_chapters=data.remind_before_chapters,
        auto_remind=1 if data.auto_remind else 0,
        notes=data.notes,
        status=ForeshadowStatus.PLANTED.value
    )
    
    db.add(foreshadow)
    await db.commit()
    await db.refresh(foreshadow)
    
    logger.info(f"✅ 创建伏笔: {foreshadow.title} (project={data.project_id})")
    return ForeshadowResponse(**foreshadow.to_dict())


@router.get("", response_model=ForeshadowListResponse, summary="获取伏笔列表")
async def list_foreshadows(
    request: Request,
    project_id: str = Query(..., description="项目ID"),
    status: Optional[str] = Query(None, description="状态筛选"),
    foreshadow_type: Optional[str] = Query(None, description="类型筛选"),
    chapter_number: Optional[int] = Query(None, description="章节号筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取项目的伏笔列表"""
    user_id = getattr(request.state, 'user_id', None)
    await verify_project_access(project_id, user_id, db)
    
    query = select(Foreshadow).where(Foreshadow.project_id == project_id)
    
    if status:
        query = query.where(Foreshadow.status == status)
    if foreshadow_type:
        query = query.where(Foreshadow.foreshadow_type == foreshadow_type)
    if chapter_number:
        query = query.where(
            or_(
                Foreshadow.planted_chapter_number == chapter_number,
                Foreshadow.resolved_chapter_number == chapter_number
            )
        )
    
    query = query.order_by(Foreshadow.importance.desc(), Foreshadow.planted_chapter_number)
    
    result = await db.execute(query)
    foreshadows = result.scalars().all()
    
    # 统计
    planted_count = sum(1 for f in foreshadows if f.status == ForeshadowStatus.PLANTED.value)
    resolved_count = sum(1 for f in foreshadows if f.status == ForeshadowStatus.RESOLVED.value)
    pending_count = sum(1 for f in foreshadows if f.status in [ForeshadowStatus.PLANTED.value, ForeshadowStatus.HINTED.value])
    
    return ForeshadowListResponse(
        items=[ForeshadowResponse(**f.to_dict()) for f in foreshadows],
        total=len(foreshadows),
        planted_count=planted_count,
        resolved_count=resolved_count,
        pending_count=pending_count
    )


@router.get("/reminders", response_model=ForeshadowReminderResponse, summary="获取伏笔提醒")
async def get_foreshadow_reminders(
    request: Request,
    project_id: str = Query(..., description="项目ID"),
    current_chapter: int = Query(..., description="当前章节号"),
    db: AsyncSession = Depends(get_db)
):
    """获取需要提醒的伏笔（即将到期或已过期未回收）"""
    user_id = getattr(request.state, 'user_id', None)
    await verify_project_access(project_id, user_id, db)
    
    # 查询未回收的伏笔
    result = await db.execute(
        select(Foreshadow).where(
            Foreshadow.project_id == project_id,
            Foreshadow.status.in_([ForeshadowStatus.PLANTED.value, ForeshadowStatus.HINTED.value]),
            Foreshadow.auto_remind == 1,
            Foreshadow.resolved_chapter_number.isnot(None)
        ).order_by(Foreshadow.resolved_chapter_number)
    )
    foreshadows = result.scalars().all()
    
    reminders = []
    for f in foreshadows:
        chapters_remaining = f.resolved_chapter_number - current_chapter
        # 在提醒范围内或已过期
        if chapters_remaining <= f.remind_before_chapters:
            reminders.append(ForeshadowReminder(
                foreshadow_id=f.id,
                title=f.title,
                description=f.description,
                planted_chapter_number=f.planted_chapter_number or 0,
                expected_resolve_chapter=f.resolved_chapter_number,
                current_chapter=current_chapter,
                chapters_remaining=max(0, chapters_remaining),
                importance=f.importance,
                related_characters=f.related_characters or []
            ))
    
    # 按紧急程度排序（剩余章节少的优先，重要度高的优先）
    reminders.sort(key=lambda x: (x.chapters_remaining, -x.importance))
    
    return ForeshadowReminderResponse(reminders=reminders, total=len(reminders))


@router.get("/{foreshadow_id}", response_model=ForeshadowResponse, summary="获取伏笔详情")
async def get_foreshadow(
    foreshadow_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """获取单个伏笔详情"""
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(
        select(Foreshadow).where(Foreshadow.id == foreshadow_id)
    )
    foreshadow = result.scalar_one_or_none()
    
    if not foreshadow:
        raise HTTPException(status_code=404, detail="伏笔不存在")
    
    await verify_project_access(foreshadow.project_id, user_id, db)
    
    return ForeshadowResponse(**foreshadow.to_dict())


@router.put("/{foreshadow_id}", response_model=ForeshadowResponse, summary="更新伏笔")
async def update_foreshadow(
    foreshadow_id: str,
    data: ForeshadowUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """更新伏笔信息"""
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(
        select(Foreshadow).where(Foreshadow.id == foreshadow_id)
    )
    foreshadow = result.scalar_one_or_none()
    
    if not foreshadow:
        raise HTTPException(status_code=404, detail="伏笔不存在")
    
    await verify_project_access(foreshadow.project_id, user_id, db)
    
    update_data = data.model_dump(exclude_unset=True)
    
    # 处理枚举值
    if 'status' in update_data and update_data['status']:
        update_data['status'] = update_data['status'].value
    if 'foreshadow_type' in update_data and update_data['foreshadow_type']:
        update_data['foreshadow_type'] = update_data['foreshadow_type'].value
    if 'auto_remind' in update_data:
        update_data['auto_remind'] = 1 if update_data['auto_remind'] else 0
    
    for key, value in update_data.items():
        setattr(foreshadow, key, value)
    
    await db.commit()
    await db.refresh(foreshadow)
    
    logger.info(f"✅ 更新伏笔: {foreshadow.title}")
    return ForeshadowResponse(**foreshadow.to_dict())


@router.post("/{foreshadow_id}/resolve", response_model=ForeshadowResponse, summary="回收伏笔")
async def resolve_foreshadow(
    foreshadow_id: str,
    data: ResolveForeshadowRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """标记伏笔为已回收"""
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(
        select(Foreshadow).where(Foreshadow.id == foreshadow_id)
    )
    foreshadow = result.scalar_one_or_none()
    
    if not foreshadow:
        raise HTTPException(status_code=404, detail="伏笔不存在")
    
    await verify_project_access(foreshadow.project_id, user_id, db)
    
    foreshadow.status = ForeshadowStatus.RESOLVED.value
    if data.resolved_chapter_id:
        foreshadow.resolved_chapter_id = data.resolved_chapter_id
    foreshadow.resolved_chapter_number = data.resolved_chapter_number
    foreshadow.resolved_content = data.resolved_content
    foreshadow.resolved_at = datetime.now()
    if data.notes:
        foreshadow.notes = data.notes
    
    await db.commit()
    await db.refresh(foreshadow)
    
    logger.info(f"✅ 回收伏笔: {foreshadow.title} (章节 {data.resolved_chapter_number})")
    return ForeshadowResponse(**foreshadow.to_dict())


@router.delete("/{foreshadow_id}", summary="删除伏笔")
async def delete_foreshadow(
    foreshadow_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """删除伏笔"""
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(
        select(Foreshadow).where(Foreshadow.id == foreshadow_id)
    )
    foreshadow = result.scalar_one_or_none()
    
    if not foreshadow:
        raise HTTPException(status_code=404, detail="伏笔不存在")
    
    await verify_project_access(foreshadow.project_id, user_id, db)
    
    await db.delete(foreshadow)
    await db.commit()
    
    logger.info(f"✅ 删除伏笔: {foreshadow.title}")
    return {"success": True, "message": "伏笔已删除"}


@router.get("/chapter/{chapter_id}/context", summary="获取章节相关伏笔上下文")
async def get_chapter_foreshadow_context(
    chapter_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """获取与指定章节相关的伏笔上下文（用于 AI 生成时注入）"""
    user_id = getattr(request.state, 'user_id', None)
    
    # 获取章节信息
    chapter_result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id)
    )
    chapter = chapter_result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    await verify_project_access(chapter.project_id, user_id, db)
    
    current_chapter_number = chapter.chapter_number
    
    # 查询未回收的伏笔
    result = await db.execute(
        select(Foreshadow).where(
            Foreshadow.project_id == chapter.project_id,
            Foreshadow.status.in_([ForeshadowStatus.PLANTED.value, ForeshadowStatus.HINTED.value])
        ).order_by(Foreshadow.importance.desc())
    )
    pending_foreshadows = result.scalars().all()
    
    # 构建上下文
    context_parts = []
    urgent_foreshadows = []
    
    for f in pending_foreshadows:
        if f.resolved_chapter_number and f.resolved_chapter_number <= current_chapter_number + 3:
            urgent_foreshadows.append(f)
        context_parts.append(f"- 【{f.title}】(重要度:{f.importance}/10): {f.description[:100]}...")
    
    context = {
        "total_pending": len(pending_foreshadows),
        "urgent_count": len(urgent_foreshadows),
        "foreshadow_summary": "\n".join(context_parts[:10]),  # 最多10条
        "urgent_foreshadows": [
            {
                "id": f.id,
                "title": f.title,
                "description": f.description,
                "expected_chapter": f.resolved_chapter_number,
                "importance": f.importance
            }
            for f in urgent_foreshadows
        ]
    }
    
    return context
