"""重复内容检测 API - 支持流式返回"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
import json
import asyncio

from app.database import get_db
from app.api.auth import get_current_user
from app.services.duplicate_detector import DuplicateDetector

router = APIRouter(prefix="/api/duplicate", tags=["重复检测"])


@router.get("/chapter/{chapter_id}/check", summary="检测章节内部重复")
async def check_chapter_duplicates(
    chapter_id: str,
    threshold: float = Query(0.7, ge=0.5, le=1.0, description="相似度阈值"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    检测单个章节内部的重复内容
    
    - **chapter_id**: 章节ID
    - **threshold**: 相似度阈值 (0.5-1.0)，默认0.7
    
    返回章节内部重复片段列表
    """
    detector = DuplicateDetector(similarity_threshold=threshold)
    result = await detector.check_chapter(chapter_id, db)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/project/{project_id}/check", summary="检测项目章节间重复")
async def check_project_duplicates(
    project_id: str,
    threshold: float = Query(0.7, ge=0.5, le=1.0, description="相似度阈值"),
    max_chapters: int = Query(20, ge=2, le=100, description="最大检查章节数"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    检测项目所有章节间的重复内容
    
    - **project_id**: 项目ID
    - **threshold**: 相似度阈值 (0.5-1.0)
    - **max_chapters**: 最大检查章节数 (2-100)
    
    注意：章节数较多时可能耗时较长，建议使用流式接口
    """
    detector = DuplicateDetector(similarity_threshold=threshold)
    result = await detector.check_project(project_id, db, max_chapters)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/project/{project_id}/check-stream", summary="流式检测项目重复（推荐）")
async def check_project_duplicates_stream(
    project_id: str,
    threshold: float = Query(0.7, ge=0.5, le=1.0, description="相似度阈值"),
    max_chapters: int = Query(50, ge=2, le=100, description="最大检查章节数"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    流式检测项目章节间重复内容（SSE）
    
    实时返回检测进度，适合大量章节的检测任务
    
    事件类型：
    - `progress`: 检测进度 {"current": 1, "total": 10, "phase": "internal/cross"}
    - `internal`: 章节内部重复结果
    - `cross`: 章节间重复结果
    - `complete`: 检测完成，包含汇总统计
    - `error`: 错误信息
    """
    async def generate() -> AsyncGenerator[str, None]:
        detector = DuplicateDetector(similarity_threshold=threshold)
        
        try:
            async for event in detector.check_project_stream(project_id, db, max_chapters):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)  # 防止阻塞
        except Exception as e:
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
