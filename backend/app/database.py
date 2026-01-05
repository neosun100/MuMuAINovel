"""数据库连接和会话管理 - PostgreSQL 多用户数据隔离"""
import asyncio
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi import Request, HTTPException
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

# 创建基类
Base = declarative_base()

# 导入所有模型，确保 Base.metadata 能够发现它们
# 这必须在 Base 创建之后、init_db 之前导入
from app.models import (
    Project, Outline, Character, Chapter, GenerationHistory,
    Settings, WritingStyle, ProjectDefaultStyle,
    RelationshipType, CharacterRelationship, Organization, OrganizationMember,
    StoryMemory, PlotAnalysis, AnalysisTask, BatchGenerationTask,
    RegenerationTask, Career, CharacterCareer, User, MCPPlugin, PromptTemplate,
    ChapterRefinement
)

# 引擎缓存：每个用户一个引擎
_engine_cache: Dict[str, Any] = {}

# 锁管理：用于保护引擎创建过程
_engine_locks: Dict[str, asyncio.Lock] = {}
_cache_lock = asyncio.Lock()

# 会话统计（用于监控连接泄漏）
_session_stats = {
    "created": 0,
    "closed": 0,
    "active": 0,
    "errors": 0,
    "generator_exits": 0,
    "last_check": None
}

# 全局 AsyncSessionLocal（用于启动时的任务恢复等）
_global_engine = None
AsyncSessionLocal = None


async def _init_global_session():
    """初始化全局会话工厂"""
    global _global_engine, AsyncSessionLocal
    if _global_engine is None:
        _global_engine = create_async_engine(
            settings.database_url,
            pool_size=5,
            max_overflow=5,
            pool_pre_ping=True
        )
        AsyncSessionLocal = async_sessionmaker(
            _global_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )


async def get_engine(user_id: str):
    """获取或创建用户专属的数据库引擎（线程安全）
    
    PostgreSQL: 所有用户共享一个数据库，通过user_id字段隔离数据
    
    Args:
        user_id: 用户ID
        
    Returns:
        用户专属的异步引擎
    """
    # PostgreSQL模式：所有用户共享同一个引擎
    cache_key = "shared_postgres"
    if cache_key in _engine_cache:
        return _engine_cache[cache_key]
    
    async with _cache_lock:
        if cache_key not in _engine_cache:
            # 检测数据库类型
            is_sqlite = 'sqlite' in settings.database_url.lower()
            
            # 基础引擎参数
            engine_args = {
                "echo": settings.database_echo_pool,
                "echo_pool": settings.database_echo_pool,
                "future": True,
            }
            
            if is_sqlite:
                # SQLite 配置（使用 NullPool，不支持连接池参数）
                engine_args["connect_args"] = {
                    "check_same_thread": False,
                    "timeout": 30.0,  # 等待锁释放的超时时间（秒）
                }
                # 启用连接前检测以支持更好的并发
                engine_args["pool_pre_ping"] = True
                
                logger.info("📊 使用 SQLite 数据库（NullPool，超时30秒，WAL模式）")
            else:
                # PostgreSQL 配置（完整连接池支持）
                connect_args = {
                    "server_settings": {
                        "application_name": settings.app_name,
                        "jit": "off",
                        "search_path": "public",
                    },
                    "command_timeout": 60,
                    "statement_cache_size": 500,
                }
                
                engine_args.update({
                    "pool_size": settings.database_pool_size,
                    "max_overflow": settings.database_max_overflow,
                    "pool_timeout": settings.database_pool_timeout,
                    "pool_pre_ping": settings.database_pool_pre_ping,
                    "pool_recycle": settings.database_pool_recycle,
                    "pool_use_lifo": settings.database_pool_use_lifo,
                    "pool_reset_on_return": settings.database_pool_reset_on_return,
                    "max_identifier_length": settings.database_max_identifier_length,
                    "connect_args": connect_args
                })
                
                total_connections = settings.database_pool_size + settings.database_max_overflow
                estimated_concurrent_users = total_connections * 2
                
                logger.info(
                    f"📊 PostgreSQL 连接池配置:\n"
                    f"   ├─ 核心连接: {settings.database_pool_size}\n"
                    f"   ├─ 溢出连接: {settings.database_max_overflow}\n"
                    f"   ├─ 总连接数: {total_connections}\n"
                    f"   ├─ 获取超时: {settings.database_pool_timeout}秒\n"
                    f"   ├─ 连接回收: {settings.database_pool_recycle}秒\n"
                    f"   └─ 预估并发: {estimated_concurrent_users}+用户"
                )
            
            engine = create_async_engine(settings.database_url, **engine_args)
            _engine_cache[cache_key] = engine
            
            # 如果是 SQLite，启用 WAL 模式以支持读写并发
            if is_sqlite:
                try:
                    from sqlalchemy import event
                    from sqlalchemy.pool import NullPool
                    
                    @event.listens_for(engine.sync_engine, "connect")
                    def set_sqlite_pragma(dbapi_conn, connection_record):
                        cursor = dbapi_conn.cursor()
                        cursor.execute("PRAGMA journal_mode=WAL")
                        cursor.execute("PRAGMA synchronous=NORMAL")
                        cursor.execute("PRAGMA cache_size=-64000")  # 64MB 缓存
                        cursor.execute("PRAGMA busy_timeout=30000")  # 30秒超时
                        cursor.close()
                    
                    logger.info("✅ SQLite WAL 模式已启用（支持读写并发）")
                except Exception as e:
                    logger.warning(f"⚠️ 启用 WAL 模式失败: {e}，使用默认配置")
        
        return _engine_cache[cache_key]


async def get_db(request: Request):
    """获取数据库会话的依赖函数
    
    从 request.state.user_id 获取用户ID，然后返回该用户的数据库会话
    """
    user_id = getattr(request.state, "user_id", None)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录或用户ID缺失")
    
    engine = await get_engine(user_id)
    
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    session = AsyncSessionLocal()
    session_id = id(session)
    
    global _session_stats
    _session_stats["created"] += 1
    _session_stats["active"] += 1
    
    logger.debug(f"📊 会话创建 [User:{user_id}][ID:{session_id}] - 活跃:{_session_stats['active']}, 总创建:{_session_stats['created']}, 总关闭:{_session_stats['closed']}")
    
    try:
        yield session
        if session.in_transaction():
            await session.rollback()
    except GeneratorExit:
        _session_stats["generator_exits"] += 1
        logger.warning(f"⚠️ GeneratorExit [User:{user_id}][ID:{session_id}] - SSE连接断开（总计:{_session_stats['generator_exits']}次）")
        try:
            if session.in_transaction():
                await session.rollback()
                logger.info(f"✅ 事务已回滚 [User:{user_id}][ID:{session_id}]（GeneratorExit）")
        except Exception as rollback_error:
            _session_stats["errors"] += 1
            logger.error(f"❌ GeneratorExit回滚失败 [User:{user_id}][ID:{session_id}]: {str(rollback_error)}")
    except Exception as e:
        _session_stats["errors"] += 1
        logger.error(f"❌ 会话异常 [User:{user_id}][ID:{session_id}]: {str(e)}")
        try:
            if session.in_transaction():
                await session.rollback()
                logger.info(f"✅ 事务已回滚 [User:{user_id}][ID:{session_id}]（异常）")
        except Exception as rollback_error:
            logger.error(f"❌ 异常回滚失败 [User:{user_id}][ID:{session_id}]: {str(rollback_error)}")
        raise
    finally:
        try:
            if session.in_transaction():
                await session.rollback()
                logger.warning(f"⚠️ finally中发现未提交事务 [User:{user_id}][ID:{session_id}]，已回滚")
            
            await session.close()
            
            _session_stats["closed"] += 1
            _session_stats["active"] -= 1
            _session_stats["last_check"] = datetime.now().isoformat()
            
            logger.debug(f"📊 会话关闭 [User:{user_id}][ID:{session_id}] - 活跃:{_session_stats['active']}, 总创建:{_session_stats['created']}, 总关闭:{_session_stats['closed']}, 错误:{_session_stats['errors']}")
            
            # 使用优化后的会话监控阈值
            if _session_stats["active"] > settings.database_session_leak_threshold:
                logger.error(f"🚨 严重告警：活跃会话数 {_session_stats['active']} 超过泄漏阈值 {settings.database_session_leak_threshold}！")
            elif _session_stats["active"] > settings.database_session_max_active:
                logger.warning(f"⚠️ 警告：活跃会话数 {_session_stats['active']} 超过警告阈值 {settings.database_session_max_active}，可能存在连接泄漏！")
            elif _session_stats["active"] < 0:
                logger.error(f"🚨 活跃会话数异常: {_session_stats['active']}，统计可能不准确！")
                
        except Exception as e:
            _session_stats["errors"] += 1
            logger.error(f"❌ 关闭会话时出错 [User:{user_id}][ID:{session_id}]: {str(e)}", exc_info=True)
            try:
                await session.close()
            except:
                pass

async def init_db(user_id: str = None):
    """
    初始化数据库（已弃用）
    
    ⚠️ 此函数已弃用，仅保留用于向后兼容
    
    新的最佳实践:
    - 表结构管理: 使用 'alembic upgrade head'
    - 用户配置: Settings 在首次访问时自动创建（延迟初始化）
    
    Args:
        user_id: 用户ID (已不再使用)
    """
    logger.warning(
        "⚠️ init_db() 已弃用且无实际作用！\n"
        "   - 表结构: 由 Alembic 管理\n"
        "   - 用户配置: Settings API 自动创建\n"
        "   建议移除此调用"
    )


async def close_db():
    """关闭所有数据库连接"""
    try:
        logger.info("正在关闭所有数据库连接...")
        for user_id, engine in _engine_cache.items():
            await engine.dispose()
            logger.info(f"用户 {user_id} 的数据库连接已关闭")
        _engine_cache.clear()
        logger.info("所有数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {str(e)}", exc_info=True)
        raise

async def get_database_stats():
    """获取数据库连接和会话统计信息
    
    Returns:
        dict: 包含数据库统计信息的字典
    """
    from app.config import settings
    
    # 获取连接池详细状态
    pool_stats = {}
    cache_key = "shared_postgres"
    if cache_key in _engine_cache:
        engine = _engine_cache[cache_key]
        try:
            pool = engine.pool
            pool_stats = {
                "size": pool.size(),  # 当前连接池大小
                "checked_in": pool.checkedin(),  # 可用连接数
                "checked_out": pool.checkedout(),  # 正在使用的连接数
                "overflow": pool.overflow(),  # 溢出连接数
                "usage_percent": (pool.checkedout() / (settings.database_pool_size + settings.database_max_overflow)) * 100,
            }
        except Exception as e:
            logger.warning(f"获取连接池状态失败: {e}")
            pool_stats = {"error": str(e)}
    
    stats = {
        "session_stats": {
            "created": _session_stats["created"],
            "closed": _session_stats["closed"],
            "active": _session_stats["active"],
            "errors": _session_stats["errors"],
            "generator_exits": _session_stats["generator_exits"],
            "last_check": _session_stats["last_check"],
        },
        "pool_stats": pool_stats,  # 新增：连接池实时状态
        "engine_cache": {
            "total_engines": len(_engine_cache),
            "engine_keys": list(_engine_cache.keys()),
        },
        "config": {
            "database_type": "PostgreSQL",
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
            "total_connections": settings.database_pool_size + settings.database_max_overflow,
            "pool_timeout": settings.database_pool_timeout,
            "pool_recycle": settings.database_pool_recycle,
            "session_max_active_threshold": settings.database_session_max_active,
            "session_leak_threshold": settings.database_session_leak_threshold,
        },
        "health": {
            "status": "healthy",
            "warnings": [],
            "errors": [],
        }
    }
    
    # 健康检查
    if _session_stats["active"] > settings.database_session_leak_threshold:
        stats["health"]["status"] = "critical"
        stats["health"]["errors"].append(
            f"活跃会话数 {_session_stats['active']} 超过泄漏阈值 {settings.database_session_leak_threshold}"
        )
    elif _session_stats["active"] > settings.database_session_max_active:
        stats["health"]["status"] = "warning"
        stats["health"]["warnings"].append(
            f"活跃会话数 {_session_stats['active']} 超过警告阈值 {settings.database_session_max_active}"
        )
    
    if _session_stats["active"] < 0:
        stats["health"]["status"] = "error"
        stats["health"]["errors"].append(f"活跃会话数异常: {_session_stats['active']}")
    
    # 连接池使用率检查
    if pool_stats and "usage_percent" in pool_stats:
        usage = pool_stats["usage_percent"]
        if usage > 90:
            stats["health"]["status"] = "warning"
            stats["health"]["warnings"].append(f"连接池使用率过高: {usage:.1f}%")
        elif usage > 95:
            stats["health"]["status"] = "critical"
            stats["health"]["errors"].append(f"连接池几乎耗尽: {usage:.1f}%")
    
    error_rate = (_session_stats["errors"] / max(_session_stats["created"], 1)) * 100
    if error_rate > 5:
        if stats["health"]["status"] == "healthy":
            stats["health"]["status"] = "warning"
        stats["health"]["warnings"].append(f"会话错误率过高: {error_rate:.2f}%")
    
    stats["health"]["error_rate"] = f"{error_rate:.2f}%"
    
    return stats


async def check_database_health(user_id: str = None) -> dict:
    """检查数据库连接健康状态
    
    Args:
        user_id: 可选的用户ID，如果提供则检查特定用户的数据库
        
    Returns:
        dict: 健康检查结果
    """
    result = {
        "healthy": True,
        "checks": {},
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # 检查引擎是否存在
        cache_key = "shared_postgres"
        if user_id:
            engine = await get_engine(user_id)
        else:
            if cache_key not in _engine_cache:
                result["checks"]["engine"] = {"status": "not_initialized", "healthy": True}
                return result
            engine = _engine_cache[cache_key]
        
        # 测试数据库连接
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            # 执行简单查询测试连接
            await session.execute(text("SELECT 1"))
            result["checks"]["connection"] = {"status": "ok", "healthy": True}
            
        # 检查连接池状态（仅PostgreSQL）
        if hasattr(engine.pool, 'size'):
            pool_status = {
                "size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
                "healthy": True
            }
            
            # 连接池健康检查
            if engine.pool.overflow() >= settings.database_max_overflow:
                pool_status["healthy"] = False
                pool_status["warning"] = "连接池溢出已满"
                result["healthy"] = False
            
            result["checks"]["pool"] = pool_status
        
    except Exception as e:
        result["healthy"] = False
        result["checks"]["error"] = {
            "status": "error",
            "message": str(e),
            "healthy": False
        }
        logger.error(f"数据库健康检查失败: {str(e)}", exc_info=True)
    
    return result


async def reset_session_stats():
    """重置会话统计信息（用于测试或维护）"""
    global _session_stats
    _session_stats = {
        "created": 0,
        "closed": 0,
        "active": 0,
        "errors": 0,
        "generator_exits": 0,
        "last_check": datetime.now().isoformat()
    }
    logger.info("✅ 会话统计信息已重置")
    return _session_stats