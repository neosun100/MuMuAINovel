"""章节质量评分 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.auth import get_current_user
from app.services.quality_scorer import QualityScorer
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/quality", tags=["质量评分"])


@router.get("/chapter/{chapter_id}/basic")
async def get_basic_score(
    chapter_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """获取章节基础质量指标"""
    from sqlalchemy import select
    from app.models.chapter import Chapter
    
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id)
    )
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    scorer = QualityScorer()
    basic = scorer.calculate_basic_score(chapter.content or "")
    
    return {
        "chapter_id": chapter_id,
        "chapter_number": chapter.chapter_number,
        **basic
    }


@router.post("/chapter/{chapter_id}/evaluate")
async def evaluate_chapter_quality(
    chapter_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """AI 综合质量评估"""
    ai_service = AIService()
    scorer = QualityScorer(ai_service)
    
    result = await scorer.full_quality_check(chapter_id, db)
    
    if "error" in result and not result.get("basic_metrics"):
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
