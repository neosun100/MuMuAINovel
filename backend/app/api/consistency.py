"""一致性检测 API - 支持流式返回"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator
import json
import asyncio

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
    对指定章节进行完整的一致性检测（同步）
    
    包括：
    - 角色一致性检测：角色行为是否符合设定
    - 情节连贯性检测：与前文是否连贯
    
    注意：此接口需要AI分析，可能耗时10-30秒，建议使用流式接口
    """
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    project = await verify_project_access(chapter.project_id, user_id, db)
    
    if not chapter.content:
        raise HTTPException(status_code=400, detail="章节内容为空，无法检测")
    
    char_result = await db.execute(
        select(Character).where(Character.project_id == project.id)
    )
    characters = char_result.scalars().all()
    
    prev_result = await db.execute(
        select(Chapter).where(
            Chapter.project_id == project.id,
            Chapter.chapter_number < chapter.chapter_number,
            Chapter.content != None
        ).order_by(Chapter.chapter_number.desc()).limit(3)
    )
    previous_chapters = list(prev_result.scalars().all())
    previous_chapters.reverse()
    
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


@router.post("/chapter/{chapter_id}/check-stream", summary="流式检测章节一致性（推荐）")
async def check_chapter_consistency_stream(
    chapter_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_user_ai_service)
):
    """
    流式检测章节一致性（SSE）
    
    实时返回检测进度和结果，适合前端展示进度
    
    事件类型：
    - `start`: 开始检测
    - `progress`: 检测进度 {"step": "character/plot", "message": "..."}
    - `character_result`: 角色一致性检测结果
    - `plot_result`: 情节连贯性检测结果
    - `complete`: 检测完成，包含综合评分
    - `error`: 错误信息
    """
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
    
    prev_result = await db.execute(
        select(Chapter).where(
            Chapter.project_id == project.id,
            Chapter.chapter_number < chapter.chapter_number,
            Chapter.content != None
        ).order_by(Chapter.chapter_number.desc()).limit(3)
    )
    previous_chapters = list(prev_result.scalars().all())
    previous_chapters.reverse()
    
    async def generate() -> AsyncGenerator[str, None]:
        checker = ConsistencyChecker(ai_service)
        
        try:
            async for event in checker.full_consistency_check_stream(
                chapter=chapter,
                project=project,
                characters=characters,
                previous_chapters=previous_chapters
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"一致性检测流式错误: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chapter/{chapter_id}/character-check", summary="检测角色一致性")
async def check_character_consistency(
    chapter_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_user_ai_service)
):
    """
    仅检测角色一致性
    
    检测章节中角色的行为、对话是否符合其设定
    """
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
    return await checker.check_character_consistency(chapter.content, characters, project)


@router.post("/chapter/{chapter_id}/plot-check", summary="检测情节连贯性")
async def check_plot_coherence(
    chapter_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_user_ai_service)
):
    """
    仅检测情节连贯性
    
    检测当前章节与前几章的情节是否连贯
    """
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    project = await verify_project_access(chapter.project_id, user_id, db)
    
    if not chapter.content:
        raise HTTPException(status_code=400, detail="章节内容为空")
    
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
