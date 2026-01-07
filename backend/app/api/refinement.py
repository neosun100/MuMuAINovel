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
        .where(
            ChapterRefinement.chapter_id == chapter_id,
            ChapterRefinement.status == "completed"
        )
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


# ==================== 审核功能 ====================

class ReviewRequest(BaseModel):
    status: str  # approved / rejected / pending
    comment: Optional[str] = None


@router.post("/chapter/{chapter_id}/review")
async def review_chapter(
    chapter_id: str,
    request: ReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """审核章节优化结果"""
    
    # 查找已完成的优化记录
    result = await db.execute(
        select(ChapterRefinement)
        .where(
            ChapterRefinement.chapter_id == chapter_id,
            ChapterRefinement.status == "completed"
        )
        .order_by(ChapterRefinement.version.desc())
        .limit(1)
    )
    refinement = result.scalar_one_or_none()
    
    if not refinement:
        raise HTTPException(status_code=404, detail="未找到已完成的优化记录")
    
    refinement.review_status = request.status
    refinement.review_comment = request.comment
    refinement.reviewed_at = datetime.now()
    
    await db.commit()
    
    return {
        "chapter_id": chapter_id,
        "review_status": request.status,
        "message": "审核完成"
    }


@router.get("/project/{project_id}/review-summary")
async def get_review_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取项目审核统计"""
    
    result = await db.execute(
        select(
            ChapterRefinement.review_status,
            func.count(ChapterRefinement.id)
        )
        .where(
            ChapterRefinement.project_id == project_id,
            ChapterRefinement.status == "completed"
        )
        .group_by(ChapterRefinement.review_status)
    )
    counts = {row[0] or "pending": row[1] for row in result.all()}
    
    return {
        "total": sum(counts.values()),
        "approved": counts.get("approved", 0),
        "rejected": counts.get("rejected", 0),
        "pending": counts.get("pending", 0) + counts.get(None, 0)
    }


# ==================== 导出功能 ====================

from fastapi.responses import StreamingResponse
import io
import zipfile
import json as json_lib
from urllib.parse import quote


@router.get("/project/{project_id}/export")
async def export_refined_novel(
    project_id: str,
    format: str = "txt",  # txt / markdown / json
    include_original: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """导出优化后的小说"""
    
    # 获取项目信息
    from app.models.project import Project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 获取所有章节
    result = await db.execute(
        select(Chapter)
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.chapter_number)
    )
    chapters = result.scalars().all()
    
    if format == "json":
        # JSON格式导出
        data = {
            "title": project.title,
            "genre": project.genre,
            "description": project.description,
            "total_chapters": len(chapters),
            "total_words": sum(ch.word_count or 0 for ch in chapters),
            "chapters": [
                {
                    "number": ch.chapter_number,
                    "title": ch.title,
                    "content": ch.content,
                    "word_count": ch.word_count,
                    "is_refined": ch.is_refined
                }
                for ch in chapters
            ]
        }
        
        content = json_lib.dumps(data, ensure_ascii=False, indent=2)
        filename = f"{project.title}.json"
        media_type = "application/json"
        
    elif format == "markdown":
        # Markdown格式
        lines = [f"# {project.title}\n\n"]
        if project.description:
            lines.append(f"> {project.description}\n\n")
        lines.append("---\n\n")
        
        for ch in chapters:
            lines.append(f"## {ch.title}\n\n")
            lines.append(f"{ch.content or ''}\n\n")
            lines.append("---\n\n")
        
        content = "".join(lines)
        filename = f"{project.title}.md"
        media_type = "text/markdown"
        
    else:
        # TXT格式
        lines = [f"{project.title}\n", "=" * 50 + "\n\n"]
        
        for ch in chapters:
            lines.append(f"{ch.title}\n")
            lines.append("-" * 30 + "\n\n")
            lines.append(f"{ch.content or ''}\n\n\n")
        
        content = "".join(lines)
        filename = f"{project.title}.txt"
        media_type = "text/plain"
    
    # 如果需要包含原文对比，创建ZIP
    if include_original:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 优化后版本
            zf.writestr(f"refined/{filename}", content.encode('utf-8'))
            
            # 原文版本
            result = await db.execute(
                select(ChapterRefinement)
                .where(
                    ChapterRefinement.project_id == project_id,
                    ChapterRefinement.status == "completed"
                )
                .order_by(ChapterRefinement.chapter_number)
            )
            refinements = result.scalars().all()
            
            original_lines = [f"{project.title} (原文)\n", "=" * 50 + "\n\n"]
            for ref in refinements:
                original_lines.append(f"第{ref.chapter_number}章\n")
                original_lines.append("-" * 30 + "\n\n")
                original_lines.append(f"{ref.original_content or ''}\n\n\n")
            
            zf.writestr(f"original/{project.title}_原文.txt", "".join(original_lines).encode('utf-8'))
        
        buffer.seek(0)
        encoded_filename = quote(f"{project.title}.zip")
        return StreamingResponse(
            buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    
    encoded_filename = quote(filename)
    return StreamingResponse(
        io.BytesIO(content.encode('utf-8')),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )


@router.get("/project/{project_id}/export-diff")
async def export_diff_report(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """导出优化对比报告"""
    
    from app.models.project import Project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    result = await db.execute(
        select(ChapterRefinement)
        .where(
            ChapterRefinement.project_id == project_id,
            ChapterRefinement.status == "completed"
        )
        .order_by(ChapterRefinement.chapter_number)
    )
    refinements = result.scalars().all()
    
    lines = [
        f"# {project.title} - 优化对比报告\n\n",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n",
        "---\n\n"
    ]
    
    total_original = 0
    total_refined = 0
    
    for ref in refinements:
        orig_words = ref.original_word_count or 0
        ref_words = ref.refined_word_count or 0
        total_original += orig_words
        total_refined += ref_words
        
        change = ref_words - orig_words
        change_pct = (change / orig_words * 100) if orig_words > 0 else 0
        
        lines.append(f"## 第{ref.chapter_number}章\n\n")
        lines.append(f"- 原文字数: {orig_words}\n")
        lines.append(f"- 优化后字数: {ref_words}\n")
        lines.append(f"- 变化: {change:+d} ({change_pct:+.1f}%)\n")
        lines.append(f"- 审核状态: {ref.review_status or '待审核'}\n\n")
        
        # 显示前300字对比
        lines.append("### 开头对比\n\n")
        lines.append("**原文:**\n")
        lines.append(f"```\n{(ref.segment1_original or '')[:300]}...\n```\n\n")
        lines.append("**优化后:**\n")
        lines.append(f"```\n{(ref.segment1_refined or '')[:300]}...\n```\n\n")
        lines.append("---\n\n")
    
    # 总结
    lines.insert(3, f"## 总体统计\n\n")
    lines.insert(4, f"- 总章节: {len(refinements)}\n")
    lines.insert(5, f"- 原文总字数: {total_original:,}\n")
    lines.insert(6, f"- 优化后总字数: {total_refined:,}\n")
    lines.insert(7, f"- 总变化: {total_refined - total_original:+,} ({(total_refined - total_original) / total_original * 100 if total_original > 0 else 0:+.1f}%)\n\n")
    
    content = "".join(lines)
    encoded_filename = quote(f"{project.title}_对比报告.md")
    
    return StreamingResponse(
        io.BytesIO(content.encode('utf-8')),
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )
