"""章节二次优化API"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.refinement import ChapterRefinement
from app.models.chapter import Chapter
from app.services.refinement_service import ChapterRefinementService
from app.config import RefinementConfig
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/refinement", tags=["refinement"])


# ==================== Schemas ====================

class RefinementRequest(BaseModel):
    model: Optional[str] = None  # opus / sonnet


class BatchRefinementRequest(BaseModel):
    start_chapter: Optional[int] = 1
    end_chapter: Optional[int] = 100
    model: Optional[str] = None


class RefinementResult(BaseModel):
    chapter_id: str
    chapter_number: int
    original_words: int
    refined_words: int
    model_used: str
    segments_processed: int
    status: str


class RefinementStatus(BaseModel):
    total: int
    completed: int
    failed: int
    pending: int
    current_chapter: Optional[int]
    current_segment: Optional[int]
    status: str


class SegmentDiff(BaseModel):
    segment: int
    original: Optional[str]
    refined: Optional[str]
    original_words: int
    refined_words: int


class RefinementDiff(BaseModel):
    chapter_id: str
    chapter_number: int
    version: int
    model_used: str
    original_word_count: int
    refined_word_count: int
    segments: List[SegmentDiff]
    status: str
    created_at: datetime


# ==================== 后台任务 ====================

async def run_batch_refinement(
    project_id: str,
    start_chapter: int,
    end_chapter: int,
    model: str,
    db: AsyncSession
):
    """后台执行批量优化"""
    service = ChapterRefinementService(db)
    
    async for result in service.refine_all_chapters(
        project_id=project_id,
        start_chapter=start_chapter,
        end_chapter=end_chapter,
        model=model
    ):
        logger.info(f"优化进度: 第{result.get('chapter')}章 - {result.get('status')}")


# ==================== API 接口 ====================

@router.get("/models")
async def list_available_models():
    """获取可用的优化模型列表"""
    return {
        "models": [
            {"key": "opus", "name": "Claude Opus 4.5", "description": "最高质量，推荐历史类小说"},
            {"key": "sonnet", "name": "Claude Sonnet 4.5", "description": "性价比高，速度更快"}
        ],
        "default": "opus"
    }


@router.post("/chapter/{chapter_id}", response_model=RefinementResult)
async def refine_single_chapter(
    chapter_id: str,
    request: RefinementRequest = None,
    db: AsyncSession = Depends(get_db)
):
    """
    优化单个章节（三段论）
    
    - 可选指定模型（opus/sonnet），不指定则使用默认
    - 同步执行，返回优化结果
    """
    service = ChapterRefinementService(db)
    
    model = request.model if request else None
    
    try:
        result = await service.refine_chapter(
            chapter_id=chapter_id,
            model=model
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/{project_id}/all")
async def refine_all_chapters(
    project_id: str,
    request: BatchRefinementRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    批量优化所有章节（后台任务）
    
    - 串行处理，第N章使用第N-1章优化版作为上下文
    - 可选指定模型
    - 返回任务状态，通过 /status 接口查询进度
    """
    # 检查项目是否存在
    result = await db.execute(
        select(func.count(Chapter.id))
        .where(Chapter.project_id == project_id)
    )
    chapter_count = result.scalar()
    
    if chapter_count == 0:
        raise HTTPException(status_code=404, detail="项目不存在或没有章节")
    
    # 启动后台任务
    background_tasks.add_task(
        run_batch_refinement,
        project_id=project_id,
        start_chapter=request.start_chapter or 1,
        end_chapter=min(request.end_chapter or 100, chapter_count),
        model=request.model,
        db=db
    )
    
    return {
        "status": "started",
        "message": f"开始优化第{request.start_chapter or 1}-{min(request.end_chapter or 100, chapter_count)}章",
        "total_chapters": chapter_count,
        "model": request.model or "opus (default)"
    }


@router.get("/project/{project_id}/status", response_model=RefinementStatus)
async def get_refinement_status(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取优化进度"""
    
    # 统计各状态数量
    result = await db.execute(
        select(
            ChapterRefinement.status,
            func.count(ChapterRefinement.id)
        )
        .where(ChapterRefinement.project_id == project_id)
        .group_by(ChapterRefinement.status)
    )
    status_counts = {row[0]: row[1] for row in result.all()}
    
    completed = status_counts.get("completed", 0)
    failed = status_counts.get("failed", 0)
    pending = sum(v for k, v in status_counts.items() if k not in ["completed", "failed"])
    total = completed + failed + pending
    
    # 找当前处理中的
    result = await db.execute(
        select(ChapterRefinement)
        .where(
            ChapterRefinement.project_id == project_id,
            ChapterRefinement.status.notin_(["completed", "failed"])
        )
        .order_by(ChapterRefinement.chapter_number)
        .limit(1)
    )
    processing = result.scalar_one_or_none()
    
    overall_status = "idle"
    if processing:
        overall_status = "processing"
    elif total > 0 and pending == 0:
        overall_status = "completed"
    
    return RefinementStatus(
        total=total,
        completed=completed,
        failed=failed,
        pending=pending,
        current_chapter=processing.chapter_number if processing else None,
        current_segment=processing.current_segment if processing else None,
        status=overall_status
    )


@router.get("/chapter/{chapter_id}/diff", response_model=RefinementDiff)
async def get_refinement_diff(
    chapter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取优化前后对比"""
    
    result = await db.execute(
        select(ChapterRefinement)
        .where(ChapterRefinement.chapter_id == chapter_id)
        .order_by(ChapterRefinement.version.desc())
        .limit(1)
    )
    refinement = result.scalar_one_or_none()
    
    if not refinement:
        raise HTTPException(status_code=404, detail="未找到优化记录")
    
    segments = [
        SegmentDiff(
            segment=1,
            original=refinement.segment1_original,
            refined=refinement.segment1_refined,
            original_words=len(refinement.segment1_original or ""),
            refined_words=refinement.segment1_word_count or 0
        ),
        SegmentDiff(
            segment=2,
            original=refinement.segment2_original,
            refined=refinement.segment2_refined,
            original_words=len(refinement.segment2_original or ""),
            refined_words=refinement.segment2_word_count or 0
        ),
        SegmentDiff(
            segment=3,
            original=refinement.segment3_original,
            refined=refinement.segment3_refined,
            original_words=len(refinement.segment3_original or ""),
            refined_words=refinement.segment3_word_count or 0
        )
    ]
    
    return RefinementDiff(
        chapter_id=chapter_id,
        chapter_number=refinement.chapter_number,
        version=refinement.version,
        model_used=refinement.model_used,
        original_word_count=refinement.original_word_count,
        refined_word_count=refinement.refined_word_count or 0,
        segments=segments,
        status=refinement.status,
        created_at=refinement.created_at
    )


@router.post("/chapter/{chapter_id}/rollback")
async def rollback_to_original(
    chapter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """将章节内容回滚到优化前的原文"""
    
    # 获取优化记录
    result = await db.execute(
        select(ChapterRefinement)
        .where(ChapterRefinement.chapter_id == chapter_id)
        .order_by(ChapterRefinement.version.desc())
        .limit(1)
    )
    refinement = result.scalar_one_or_none()
    
    if not refinement:
        raise HTTPException(status_code=404, detail="未找到优化记录")
    
    if not refinement.original_content:
        raise HTTPException(status_code=400, detail="原始内容不存在")
    
    # 获取章节
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    # 恢复原文
    chapter.content = refinement.original_content
    chapter.word_count = len(refinement.original_content)
    chapter.is_refined = False
    chapter.refined_at = None
    chapter.refinement_id = None
    chapter.refinement_model = None
    
    await db.commit()
    
    return {
        "status": "rolled_back",
        "chapter_id": chapter_id,
        "chapter_number": chapter.chapter_number,
        "word_count": len(refinement.original_content)
    }


@router.get("/project/{project_id}/chapters")
async def list_refined_chapters(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取项目所有章节的优化状态"""
    
    result = await db.execute(
        select(
            Chapter.id,
            Chapter.chapter_number,
            Chapter.title,
            Chapter.word_count,
            Chapter.is_refined,
            Chapter.refined_at,
            Chapter.refinement_model
        )
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.chapter_number)
    )
    chapters = result.all()
    
    return {
        "chapters": [
            {
                "id": ch.id,
                "chapter_number": ch.chapter_number,
                "title": ch.title,
                "word_count": ch.word_count,
                "is_refined": ch.is_refined or False,
                "refined_at": ch.refined_at,
                "model": ch.refinement_model
            }
            for ch in chapters
        ]
    }
