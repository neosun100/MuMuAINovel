"""风格分析 API"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.models.chapter import Chapter
from app.models.project import Project
from app.services.style_analyzer import StyleAnalyzer
from app.api.settings import get_user_ai_service
from app.services.ai_service import AIService
from app.logger import get_logger

router = APIRouter(prefix="/style-analysis", tags=["风格分析"])
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


@router.get("/chapter/{chapter_id}/metrics", summary="获取章节基础风格指标")
async def get_chapter_metrics(
    chapter_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    获取章节的基础文本指标（不需要 AI）
    包括：句子长度、段落长度、对话比例等
    """
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    await verify_project_access(chapter.project_id, user_id, db)
    
    if not chapter.content:
        raise HTTPException(status_code=400, detail="章节内容为空")
    
    analyzer = StyleAnalyzer()
    metrics = analyzer.analyze_basic_metrics(chapter.content)
    metrics["chapter_id"] = chapter_id
    metrics["chapter_number"] = chapter.chapter_number
    
    return metrics


@router.post("/chapter/{chapter_id}/analyze", summary="AI 分析章节写作风格")
async def analyze_chapter_style(
    chapter_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_user_ai_service)
):
    """
    使用 AI 分析章节的写作风格特征
    """
    user_id = getattr(request.state, 'user_id', None)
    
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    project = await verify_project_access(chapter.project_id, user_id, db)
    
    if not chapter.content:
        raise HTTPException(status_code=400, detail="章节内容为空")
    
    analyzer = StyleAnalyzer(ai_service)
    
    # 基础指标
    basic_metrics = analyzer.analyze_basic_metrics(chapter.content)
    
    # AI 分析
    ai_analysis = await analyzer.analyze_style_with_ai(chapter.content, project)
    
    return {
        "chapter_id": chapter_id,
        "chapter_number": chapter.chapter_number,
        "basic_metrics": basic_metrics,
        "ai_analysis": ai_analysis
    }


@router.get("/project/{project_id}/learn", summary="学习项目整体风格")
async def learn_project_style(
    project_id: str,
    request: Request,
    sample_count: int = 3,
    db: AsyncSession = Depends(get_db)
):
    """
    从项目已有章节学习整体写作风格
    """
    user_id = getattr(request.state, 'user_id', None)
    await verify_project_access(project_id, user_id, db)
    
    analyzer = StyleAnalyzer()
    result = await analyzer.learn_project_style(project_id, db, sample_count)
    
    return {
        "project_id": project_id,
        **result
    }


@router.post("/project/{project_id}/generate-guide", summary="生成风格指南")
async def generate_style_guide(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_user_ai_service)
):
    """
    根据已有章节生成风格指南（用于 AI 生成时参考）
    """
    user_id = getattr(request.state, 'user_id', None)
    project = await verify_project_access(project_id, user_id, db)
    
    # 获取已完成章节
    result = await db.execute(
        select(Chapter).where(
            Chapter.project_id == project_id,
            Chapter.content != None,
            Chapter.content != ""
        ).order_by(Chapter.chapter_number).limit(5)
    )
    chapters = list(result.scalars().all())
    
    if not chapters:
        raise HTTPException(status_code=400, detail="项目无已完成章节")
    
    analyzer = StyleAnalyzer(ai_service)
    guide = await analyzer.generate_style_guide(project, chapters)
    
    if not guide:
        raise HTTPException(status_code=500, detail="生成风格指南失败")
    
    logger.info(f"✅ 生成风格指南: 项目 {project_id}")
    
    return {
        "project_id": project_id,
        "sample_chapters": len(chapters),
        "style_guide": guide
    }
