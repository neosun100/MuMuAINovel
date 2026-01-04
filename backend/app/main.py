"""FastAPI应用主入口"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from pathlib import Path

from app.config import settings as config_settings
from app.database import close_db, _session_stats
from app.logger import setup_logging, get_logger
from app.middleware import RequestIDMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.mcp.registry import mcp_registry

setup_logging(
    level=config_settings.log_level,
    log_to_file=config_settings.log_to_file,
    log_file_path=config_settings.log_file_path,
    max_bytes=config_settings.log_max_bytes,
    backup_count=config_settings.log_backup_count
)
logger = get_logger(__name__)


async def resume_interrupted_tasks():
    """恢复中断的批量生成任务"""
    from app.database import AsyncSessionLocal
    from app.models.batch_generation_task import BatchGenerationTask
    from app.models.chapter import Chapter
    from sqlalchemy import select, and_
    
    try:
        async with AsyncSessionLocal() as db:
            # 查找所有running状态的任务（说明是被中断的）
            result = await db.execute(
                select(BatchGenerationTask).where(
                    BatchGenerationTask.status.in_(['running', 'pending'])
                )
            )
            interrupted_tasks = result.scalars().all()
            
            if not interrupted_tasks:
                logger.info("📋 没有需要恢复的中断任务")
                return
            
            logger.info(f"📋 发现 {len(interrupted_tasks)} 个中断任务，准备恢复...")
            
            for task in interrupted_tasks:
                # 统计已完成的章节数
                result = await db.execute(
                    select(Chapter).where(
                        and_(
                            Chapter.project_id == task.project_id,
                            Chapter.content != None,
                            Chapter.content != ''
                        )
                    )
                )
                completed_chapters = len(result.scalars().all())
                
                # 计算需要继续的起始章节
                next_chapter = completed_chapters + 1
                remaining = task.start_chapter_number + task.chapter_count - next_chapter
                
                if remaining <= 0:
                    # 任务实际已完成
                    task.status = 'completed'
                    task.completed_chapters = task.chapter_count
                    logger.info(f"  ✅ 任务 {task.id[:8]} 实际已完成")
                else:
                    # 标记为interrupted，等待手动或自动恢复
                    task.status = 'interrupted'
                    task.completed_chapters = completed_chapters
                    logger.info(f"  ⚠️ 任务 {task.id[:8]} 已中断: {completed_chapters}/{task.chapter_count}章完成，需从第{next_chapter}章继续")
            
            await db.commit()
            logger.info("📋 中断任务状态已更新")
            
    except Exception as e:
        logger.error(f"恢复中断任务时出错: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("应用启动中...")
    
    # 恢复中断的任务
    await resume_interrupted_tasks()
    
    logger.info("应用启动完成")
    
    yield
    
    # 清理MCP插件
    await mcp_registry.cleanup_all()
    
    # 清理HTTP客户端池
    from app.services.ai_service import cleanup_http_clients
    await cleanup_http_clients()
    
    # 关闭数据库连接
    await close_db()
    
    logger.info("应用已关闭")


app = FastAPI(
    title=config_settings.app_name,
    version=config_settings.app_version,
    description="AI写小说工具 - 智能小说创作助手",
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    logger.error(f"请求验证失败: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "请求参数验证失败",
            "errors": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"未处理的异常: {type(exc).__name__}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "服务器内部错误",
            "message": str(exc) if config_settings.debug else "请稍后重试"
        }
    )

app.add_middleware(RequestIDMiddleware)
app.add_middleware(AuthMiddleware)

if config_settings.debug:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


@app.get("/health/db-sessions")
async def db_session_stats():
    """
    数据库会话统计（监控连接泄漏）
    
    返回：
    - created: 总创建会话数
    - closed: 总关闭会话数
    - active: 当前活跃会话数（应该接近0）
    - errors: 错误次数
    - generator_exits: SSE断开次数
    - last_check: 最后检查时间
    """
    return {
        "status": "ok",
        "session_stats": _session_stats,
        "warning": "活跃会话数过多" if _session_stats["active"] > 10 else None
    }


from app.api import (
    projects, outlines, characters, chapters,
    wizard_stream, relationships, organizations,
    auth, users, settings, writing_styles, memories,
    mcp_plugins, admin, inspiration, prompt_templates,
    changelog, careers, foreshadows, consistency, timeline,
    style_analysis, quality, duplicate, character_growth,
    refinement
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

app.include_router(projects.router, prefix="/api")
app.include_router(wizard_stream.router, prefix="/api")
app.include_router(inspiration.router, prefix="/api")
app.include_router(outlines.router, prefix="/api")
app.include_router(characters.router, prefix="/api")
app.include_router(careers.router, prefix="/api")  # 职业管理API
app.include_router(chapters.router, prefix="/api")
app.include_router(relationships.router, prefix="/api")
app.include_router(organizations.router, prefix="/api")
app.include_router(writing_styles.router, prefix="/api")
app.include_router(memories.router)  # 记忆管理API (已包含/api前缀)
app.include_router(mcp_plugins.router, prefix="/api")  # MCP插件管理API
app.include_router(prompt_templates.router, prefix="/api")  # 提示词模板管理API
app.include_router(foreshadows.router, prefix="/api")  # 伏笔管理API
app.include_router(consistency.router, prefix="/api")  # 一致性检测API
app.include_router(timeline.router, prefix="/api")  # 时间线管理API
app.include_router(style_analysis.router, prefix="/api")  # 风格分析API
app.include_router(quality.router)  # 质量评分API
app.include_router(duplicate.router)  # 重复检测API
app.include_router(character_growth.router)  # 角色成长API
app.include_router(changelog.router, prefix="/api")  # 更新日志API
app.include_router(refinement.router)  # 二次优化API (已包含/api前缀)

static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """服务单页应用，所有非API路径返回index.html"""
        if full_path.startswith("api/"):
            return JSONResponse(
                status_code=404,
                content={"detail": "API路径不存在"}
            )
        
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        
        return JSONResponse(
            status_code=404,
            content={"detail": "页面不存在"}
        )
else:
    logger.warning("静态文件目录不存在，请先构建前端: cd frontend && npm run build")
    
    @app.get("/")
    async def root():
        return {
            "message": "欢迎使用AI Story Creator",
            "version": config_settings.app_version,
            "docs": "/docs",
            "notice": "请先构建前端: cd frontend && npm run build"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config_settings.app_host,
        port=config_settings.app_port,
        reload=config_settings.debug
    )