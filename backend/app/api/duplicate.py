"""重复内容检测 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.auth import get_current_user
from app.services.duplicate_detector import DuplicateDetector

router = APIRouter(prefix="/api/duplicate", tags=["重复检测"])


@router.get("/chapter/{chapter_id}/check")
async def check_chapter_duplicates(
    chapter_id: str,
    threshold: float = Query(0.7, ge=0.5, le=1.0, description="相似度阈值"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """检测章节内部重复内容"""
    detector = DuplicateDetector(similarity_threshold=threshold)
    result = await detector.check_chapter(chapter_id, db)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/project/{project_id}/check")
async def check_project_duplicates(
    project_id: str,
    threshold: float = Query(0.7, ge=0.5, le=1.0, description="相似度阈值"),
    max_chapters: int = Query(20, ge=2, le=50, description="最大检查章节数"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """检测项目所有章节间重复内容"""
    detector = DuplicateDetector(similarity_threshold=threshold)
    result = await detector.check_project(project_id, db, max_chapters)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
