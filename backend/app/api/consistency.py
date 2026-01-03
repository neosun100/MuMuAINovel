"""一致性检测 API"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.models.chapter import Chapter
from app.models.character import Character
from app.models.project import Project
from app.services.consistency_checker import ConsistencyChecker
from app.api.settings import get_user_ai_service
from app.services.ai_service import AIService
from app.logger import get_logger

router = APIRouter(prefix="/consistency", tags=["一致性检测"])
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


@router.post("/chapter/{chapter_id}/check", summary="检测章节一致性")
async def check_chapter_consistency(
    chapter_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_user_ai_service)
):
    """
    对指定章节进行完整的一致性检测
    
    包括：
    - 角色一致性检测
    - 情节连贯性检测
    """
    user_id = getattr(request.state, 'user_id', None)
    
    # 获取章节
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    # 验证权限
    project = await verify_project_access(chapter.project_id, user_id, db)
    
    if not chapter.content:
        raise HTTPException(status_code=400, detail="章节内容为空，无法检测")
    
    # 获取角色
    char_result = await db.execute(
        select(Character).where(Character.project_id == project.id)
    )
    characters = char_result.scalars().all()
    
    # 获取前置章节
    prev_result = await db.execute(
        select(Chapter).where(
            Chapter.project_id == project.id,
            Chapter.chapter_number < chapter.chapter_number,
            Chapter.content != None
        ).order_by(Chapter.chapter_number.desc()).limit(3)
    )
    previous_chapters = list(prev_result.scalars().all())
    previous_chapters.reverse()
    
    # 执行检测
    checker = ConsistencyChecker(ai_service)
    result = await checker.full_consistency_check(
        chapter=chapter,
        project=project,
        characters=list(characters),
        previous_chapters=previous_chapters,
        db=db
    )
    
    logger.info(f"✅ 一致性检测完成: 章节 {chapter.chapter_number}, 评分 {result['overall_score']}")
    
    return result


@router.post("/chapter/{chapter_id}/character-check", summary="检测角色一致性")
async def check_character_consistency(
    chapter_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_user_ai_service)
):
    """仅检测角色一致性"""
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    project = await verify_project_access(chapter.project_id, user_id, db)
    
    if not chapter.content:
        raise HTTPException(status_code=400, detail="章节内容为空")
    
    char_result = await db.execute(
        select(Character).where(Character.project_id == project.id)
    )
    characters = list(char_result.scalars().all())
    
    if not characters:
        return {"score": 100, "issues": [], "suggestions": [], "message": "项目无角色设定"}
    
    checker = ConsistencyChecker(ai_service)
    return await checker.check_character_consistency(
        chapter.content,
        characters,
        project
    )


@router.post("/chapter/{chapter_id}/plot-check", summary="检测情节连贯性")
async def check_plot_coherence(
    chapter_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_user_ai_service)
):
    """仅检测情节连贯性"""
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    project = await verify_project_access(chapter.project_id, user_id, db)
    
    if not chapter.content:
        raise HTTPException(status_code=400, detail="章节内容为空")
    
    # 获取前置章节
    prev_result = await db.execute(
        select(Chapter).where(
            Chapter.project_id == project.id,
            Chapter.chapter_number < chapter.chapter_number,
            Chapter.content != None
        ).order_by(Chapter.chapter_number.desc()).limit(3)
    )
    previous_chapters = list(prev_result.scalars().all())
    previous_chapters.reverse()
    
    if not previous_chapters:
        return {"score": 100, "issues": [], "suggestions": [], "message": "无前置章节"}
    
    checker = ConsistencyChecker(ai_service)
    return await checker.check_plot_coherence(chapter, previous_chapters, project)
