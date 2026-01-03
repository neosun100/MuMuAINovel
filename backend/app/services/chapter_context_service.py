"""章节上下文构建服务 - 实现RTCO框架的智能上下文构建"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.models.chapter import Chapter
from app.models.project import Project
from app.models.outline import Outline
from app.models.character import Character
from app.models.career import Career, CharacterCareer
from app.models.memory import StoryMemory
from app.models.foreshadow import Foreshadow, ForeshadowStatus
from app.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ChapterContext:
    """
    章节上下文数据结构
    
    采用RTCO框架的分层设计：
    - P0-核心（必须）：大纲、衔接点、字数要求
    - P1-重要（按需）：角色、情感基调、风格
    - P2-参考（条件触发）：记忆、故事骨架、MCP资料
    """
    
    # === P0-核心信息（必须包含）===
    chapter_outline: str = ""           # 本章大纲
    continuation_point: Optional[str] = None  # 衔接锚点（上一章结尾）
    target_word_count: int = 3000       # 目标字数
    min_word_count: int = 2500          # 最小字数
    max_word_count: int = 4000          # 最大字数
    narrative_perspective: str = "第三人称"  # 叙事视角
    
    # === 本章基本信息 ===
    chapter_number: int = 1             # 章节序号
    chapter_title: str = ""             # 章节标题
    
    # === 项目基本信息 ===
    title: str = ""                     # 书名
    genre: str = ""                     # 类型
    theme: str = ""                     # 主题
    
    # === P1-重要信息（按需包含）===
    chapter_characters: str = ""        # 本章涉及角色（精简）
    emotional_tone: str = ""            # 情感基调
    style_instruction: str = ""         # 写作风格指令（摘要化）
    
    # === P2-参考信息（条件触发）===
    relevant_memories: Optional[str] = None   # 相关记忆（精简版）
    story_skeleton: Optional[str] = None      # 故事骨架（50章+启用）
    mcp_references: Optional[str] = None      # MCP参考资料
    foreshadow_context: Optional[str] = None  # 伏笔上下文（待回收/需埋设）
    style_guide: Optional[str] = None         # 风格指南（从已有章节学习）
    
    # === 元信息 ===
    context_stats: Dict[str, Any] = field(default_factory=dict)  # 统计信息
    
    def get_total_context_length(self) -> int:
        """计算总上下文长度"""
        total = 0
        for field_name in ['chapter_outline', 'continuation_point', 'chapter_characters',
                          'relevant_memories', 'story_skeleton', 'style_instruction', 'foreshadow_context', 'style_guide']:
            value = getattr(self, field_name, None)
            if value:
                total += len(value)
        return total


class ChapterContextBuilder:
    """
    章节上下文构建器
    
    实现动态裁剪逻辑，根据章节序号自动调整上下文复杂度：
    - 第1章：无前置上下文，仅提供大纲和角色
    - 第2-10章：上一章结尾300字 + 涉及角色
    - 第11-50章：上一章结尾500字 + 相关记忆3条
    - 第51章+：上一章结尾500字 + 故事骨架 + 智能记忆5条
    """
    
    # 配置常量
    ENDING_LENGTH_SHORT = 300    # 1-10章：短衔接
    ENDING_LENGTH_NORMAL = 500   # 11章+：标准衔接
    MEMORY_COUNT_LIGHT = 3       # 11-50章：轻量记忆
    MEMORY_COUNT_FULL = 5        # 51章+：完整记忆
    SKELETON_THRESHOLD = 50      # 启用故事骨架的章节阈值
    SKELETON_SAMPLE_INTERVAL = 10  # 故事骨架采样间隔
    MEMORY_IMPORTANCE_THRESHOLD = 0.7  # 记忆重要性阈值
    STYLE_MAX_LENGTH = 200       # 风格描述最大长度
    MAX_CONTEXT_LENGTH = 3000    # 总上下文最大字符数
    
    def __init__(self, memory_service=None):
        """
        初始化构建器
        
        Args:
            memory_service: 记忆服务实例（可选，用于检索相关记忆）
        """
        self.memory_service = memory_service
    
    async def build(
        self,
        chapter: Chapter,
        project: Project,
        outline: Optional[Outline],
        user_id: str,
        db: AsyncSession,
        style_content: Optional[str] = None,
        target_word_count: int = 3000,
        temp_narrative_perspective: Optional[str] = None
    ) -> ChapterContext:
        """
        构建章节生成所需的上下文
        
        Args:
            chapter: 章节对象
            project: 项目对象
            outline: 大纲对象（可选）
            user_id: 用户ID
            db: 数据库会话
            style_content: 写作风格内容（可选）
            target_word_count: 目标字数
            temp_narrative_perspective: 临时叙事视角（可选，覆盖项目默认）
        
        Returns:
            ChapterContext: 结构化的上下文对象
        """
        chapter_number = chapter.chapter_number
        logger.info(f"📝 开始构建章节上下文: 第{chapter_number}章")
        
        # 确定叙事视角
        narrative_perspective = (
            temp_narrative_perspective or
            project.narrative_perspective or
            "第三人称"
        )
        
        # 初始化上下文
        context = ChapterContext(
            chapter_number=chapter_number,
            chapter_title=chapter.title or "",
            title=project.title or "",
            genre=project.genre or "",
            theme=project.theme or "",
            target_word_count=target_word_count,
            min_word_count=max(500, target_word_count - 500),
            max_word_count=target_word_count + 1000,
            narrative_perspective=narrative_perspective
        )
        
        # === P0-核心信息（始终构建）===
        context.chapter_outline = await self._build_chapter_outline(
            chapter, outline, project.outline_mode
        )
        
        # === 衔接锚点（根据章节调整长度）===
        if chapter_number == 1:
            context.continuation_point = None
            logger.info("  ✅ 第1章无需衔接锚点")
        elif chapter_number <= 10:
            context.continuation_point = await self._get_last_ending(
                chapter, db, self.ENDING_LENGTH_SHORT
            )
            logger.info(f"  ✅ 衔接锚点（短）: {len(context.continuation_point or '')}字符")
        else:
            context.continuation_point = await self._get_last_ending(
                chapter, db, self.ENDING_LENGTH_NORMAL
            )
            logger.info(f"  ✅ 衔接锚点（标准）: {len(context.continuation_point or '')}字符")
        
        # === P1-重要信息 ===
        context.chapter_characters = await self._build_chapter_characters(
            chapter, project, outline, db
        )
        context.emotional_tone = self._extract_emotional_tone(chapter, outline)
        
        # 写作风格（摘要化）
        if style_content:
            context.style_instruction = self._summarize_style(style_content)
        
        # === P2-参考信息（条件触发）===
        if chapter_number > 10 and self.memory_service:
            memory_limit = (
                self.MEMORY_COUNT_LIGHT if chapter_number <= 50
                else self.MEMORY_COUNT_FULL
            )
            context.relevant_memories = await self._get_relevant_memories(
                user_id, project.id, chapter_number, 
                context.chapter_outline,
                limit=memory_limit
            )
            logger.info(f"  ✅ 相关记忆: {len(context.relevant_memories or '')}字符")
        
        # 故事骨架（50章+）
        if chapter_number > self.SKELETON_THRESHOLD:
            context.story_skeleton = await self._build_story_skeleton(
                project.id, chapter_number, db
            )
            logger.info(f"  ✅ 故事骨架: {len(context.story_skeleton or '')}字符")
        
        # === 伏笔上下文（始终构建）===
        context.foreshadow_context = await self._build_foreshadow_context(
            project.id, chapter_number, db
        )
        if context.foreshadow_context:
            logger.info(f"  ✅ 伏笔上下文: {len(context.foreshadow_context)}字符")
        
        # === 风格指南（章节数 >= 3 时启用）===
        if chapter_number >= 3:
            context.style_guide = await self._build_style_guide(project, db)
            if context.style_guide:
                logger.info(f"  ✅ 风格指南: {len(context.style_guide)}字符")
        
        # === 统计信息 ===
        context.context_stats = {
            "chapter_number": chapter_number,
            "has_continuation": context.continuation_point is not None,
            "continuation_length": len(context.continuation_point or ""),
            "characters_length": len(context.chapter_characters),
            "memories_length": len(context.relevant_memories or ""),
            "skeleton_length": len(context.story_skeleton or ""),
            "foreshadow_length": len(context.foreshadow_context or ""),
            "style_guide_length": len(context.style_guide or ""),
            "total_length": context.get_total_context_length()
        }
        
        logger.info(f"📊 上下文构建完成: 总长度 {context.context_stats['total_length']} 字符")
        
        return context
    
    async def _build_chapter_outline(
        self,
        chapter: Chapter,
        outline: Optional[Outline],
        outline_mode: str
    ) -> str:
        """
        构建本章大纲内容
        
        Args:
            chapter: 章节对象
            outline: 大纲对象
            outline_mode: 大纲模式（one-to-one/one-to-many）
        
        Returns:
            本章大纲文本
        """
        if outline_mode == 'one-to-one':
            # 一对一模式：使用大纲的 content
            return outline.content if outline else chapter.summary or '暂无大纲'
        else:
            # 一对多模式：优先使用 expansion_plan 的详细规划
            if chapter.expansion_plan:
                try:
                    plan = json.loads(chapter.expansion_plan)
                    outline_content = f"""剧情摘要：{plan.get('plot_summary', '无')}

关键事件：
{chr(10).join(f'- {event}' for event in plan.get('key_events', []))}

角色焦点：{', '.join(plan.get('character_focus', []))}
情感基调：{plan.get('emotional_tone', '未设定')}
叙事目标：{plan.get('narrative_goal', '未设定')}
冲突类型：{plan.get('conflict_type', '未设定')}"""
                    return outline_content
                except json.JSONDecodeError:
                    pass
            
            # 回退到大纲内容
            return outline.content if outline else chapter.summary or '暂无大纲'
    
    async def _get_last_ending(
        self,
        chapter: Chapter,
        db: AsyncSession,
        max_length: int
    ) -> Optional[str]:
        """
        获取上一章结尾内容作为衔接锚点
        
        Args:
            chapter: 当前章节
            db: 数据库会话
            max_length: 最大长度
        
        Returns:
            上一章结尾内容
        """
        if chapter.chapter_number <= 1:
            return None
        
        # 查询上一章
        result = await db.execute(
            select(Chapter)
            .where(Chapter.project_id == chapter.project_id)
            .where(Chapter.chapter_number == chapter.chapter_number - 1)
        )
        prev_chapter = result.scalar_one_or_none()
        
        if not prev_chapter or not prev_chapter.content:
            return None
        
        # 提取结尾内容
        content = prev_chapter.content.strip()
        if len(content) <= max_length:
            return content
        
        return content[-max_length:]
    
    async def _build_chapter_characters(
        self,
        chapter: Chapter,
        project: Project,
        outline: Optional[Outline],
        db: AsyncSession
    ) -> str:
        """
        构建本章涉及的角色信息（精简版）
        
        只返回本章相关的角色，而非全部角色
        
        Args:
            chapter: 章节对象
            project: 项目对象
            outline: 大纲对象
            db: 数据库会话
        
        Returns:
            本章角色信息文本
        """
        # 获取所有角色
        characters_result = await db.execute(
            select(Character).where(Character.project_id == project.id)
        )
        characters = characters_result.scalars().all()
        
        if not characters:
            return "暂无角色信息"
        
        # 提取本章相关角色名单
        filter_character_names = None
        
        # 从大纲或扩展计划中提取角色
        if project.outline_mode == 'one-to-one':
            if outline and outline.structure:
                try:
                    structure = json.loads(outline.structure)
                    filter_character_names = structure.get('characters', [])
                except json.JSONDecodeError:
                    pass
        else:
            if chapter.expansion_plan:
                try:
                    plan = json.loads(chapter.expansion_plan)
                    filter_character_names = plan.get('character_focus', [])
                except json.JSONDecodeError:
                    pass
        
        # 筛选角色
        if filter_character_names:
            characters = [c for c in characters if c.name in filter_character_names]
        
        if not characters:
            return "暂无相关角色"
        
        # 构建精简的角色信息（每个角色最多100字符）
        char_lines = []
        for c in characters[:10]:  # 最多10个角色
            role_type = "主角" if c.role_type == "protagonist" else (
                "反派" if c.role_type == "antagonist" else "配角"
            )
            
            # 性格摘要（最多50字符）
            personality_brief = ""
            if c.personality:
                personality_brief = c.personality[:50]
                if len(c.personality) > 50:
                    personality_brief += "..."
            
            char_lines.append(f"- {c.name}({role_type}): {personality_brief}")
        
        return "\n".join(char_lines)
    
    def _extract_emotional_tone(
        self,
        chapter: Chapter,
        outline: Optional[Outline]
    ) -> str:
        """
        提取本章情感基调
        
        Args:
            chapter: 章节对象
            outline: 大纲对象
        
        Returns:
            情感基调描述
        """
        # 尝试从扩展计划中提取
        if chapter.expansion_plan:
            try:
                plan = json.loads(chapter.expansion_plan)
                tone = plan.get('emotional_tone')
                if tone:
                    return tone
            except json.JSONDecodeError:
                pass
        
        # 尝试从大纲结构中提取
        if outline and outline.structure:
            try:
                structure = json.loads(outline.structure)
                tone = structure.get('emotion') or structure.get('emotional_tone')
                if tone:
                    return tone
            except json.JSONDecodeError:
                pass
        
        return "未设定"
    
    def _summarize_style(self, style_content: str) -> str:
        """
        将风格描述压缩为关键要点
        
        Args:
            style_content: 完整风格描述
        
        Returns:
            摘要化的风格描述
        """
        if not style_content:
            return ""
        
        if len(style_content) <= self.STYLE_MAX_LENGTH:
            return style_content
        
        # 简单截断（后续可以用AI提取关键词）
        return style_content[:self.STYLE_MAX_LENGTH] + "..."
    
    async def _get_relevant_memories(
        self,
        user_id: str,
        project_id: str,
        chapter_number: int,
        chapter_outline: str,
        limit: int = 3
    ) -> Optional[str]:
        """
        获取与本章最相关的记忆（精简版）
        
        策略：
        1. 仅检索与大纲语义最相关的记忆
        2. 提高重要性阈值，过滤低质量记忆
        3. 优先返回未回收的伏笔
        
        Args:
            user_id: 用户ID
            project_id: 项目ID
            chapter_number: 当前章节号
            chapter_outline: 本章大纲
            limit: 返回数量限制
        
        Returns:
            格式化的记忆文本
        """
        if not self.memory_service:
            return None
        
        try:
            # 1. 语义检索相关记忆（提高阈值）
            relevant = await self.memory_service.search_memories(
                user_id=user_id,
                project_id=project_id,
                query=chapter_outline,
                limit=limit,
                min_importance=self.MEMORY_IMPORTANCE_THRESHOLD
            )
            
            # 2. 检查即将到期的伏笔
            foreshadows = await self._get_due_foreshadows(
                user_id, project_id, chapter_number,
                lookahead=5  # 仅看5章内需要回收的
            )
            
            # 3. 合并并格式化
            return self._format_memories(relevant, foreshadows, max_length=500)
            
        except Exception as e:
            logger.error(f"❌ 获取相关记忆失败: {str(e)}")
            return None
    
    async def _get_due_foreshadows(
        self,
        user_id: str,
        project_id: str,
        chapter_number: int,
        lookahead: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取即将需要回收的伏笔
        
        Args:
            user_id: 用户ID
            project_id: 项目ID
            chapter_number: 当前章节号
            lookahead: 往前看的章节数
        
        Returns:
            待回收伏笔列表
        """
        if not self.memory_service:
            return []
        
        try:
            foreshadows = await self.memory_service.find_unresolved_foreshadows(
                user_id, project_id, chapter_number
            )
            
            # 过滤：只保留埋下时间较长（超过lookahead章）的伏笔
            due_foreshadows = []
            for fs in foreshadows:
                meta = fs.get('metadata', {})
                fs_chapter = meta.get('chapter_number', 0)
                if chapter_number - fs_chapter >= lookahead:
                    due_foreshadows.append({
                        'chapter': fs_chapter,
                        'content': fs.get('content', '')[:60],
                        'importance': meta.get('importance', 0.5)
                    })
            
            return due_foreshadows[:2]  # 最多2条
            
        except Exception as e:
            logger.error(f"❌ 获取待回收伏笔失败: {str(e)}")
            return []
    
    def _format_memories(
        self,
        relevant: List[Dict[str, Any]],
        foreshadows: List[Dict[str, Any]],
        max_length: int = 500
    ) -> str:
        """
        格式化记忆为简洁文本，严格限制长度
        
        Args:
            relevant: 相关记忆列表
            foreshadows: 待回收伏笔列表
            max_length: 最大长度
        
        Returns:
            格式化的记忆文本
        """
        lines = []
        current_length = 0
        
        # 优先添加待回收伏笔
        if foreshadows:
            lines.append("【待回收伏笔】")
            for fs in foreshadows[:2]:
                text = f"- 第{fs['chapter']}章埋下：{fs['content']}"
                if current_length + len(text) > max_length:
                    break
                lines.append(text)
                current_length += len(text)
        
        # 添加相关记忆
        if relevant and current_length < max_length:
            lines.append("【相关记忆】")
            for mem in relevant:
                content = mem.get('content', '')[:80]
                text = f"- {content}"
                if current_length + len(text) > max_length:
                    break
                lines.append(text)
                current_length += len(text)
        
        return "\n".join(lines) if lines else None
    
    async def _build_story_skeleton(
        self,
        project_id: str,
        chapter_number: int,
        db: AsyncSession
    ) -> Optional[str]:
        """
        构建故事骨架（每N章采样）
        
        Args:
            project_id: 项目ID
            chapter_number: 当前章节号
            db: 数据库会话
        
        Returns:
            故事骨架文本
        """
        try:
            # 获取所有已完成章节的摘要
            result = await db.execute(
                select(Chapter.chapter_number, Chapter.title)
                .where(Chapter.project_id == project_id)
                .where(Chapter.chapter_number < chapter_number)
                .where(Chapter.content != None)
                .where(Chapter.content != "")
                .order_by(Chapter.chapter_number)
            )
            chapters = result.all()
            
            if not chapters:
                return None
            
            # 采样：每N章取一个
            skeleton_lines = ["【故事骨架】"]
            for i, (ch_num, ch_title) in enumerate(chapters):
                if i % self.SKELETON_SAMPLE_INTERVAL == 0:
                    # 尝试获取章节摘要
                    summary_result = await db.execute(
                        select(StoryMemory.content)
                        .where(StoryMemory.project_id == project_id)
                        .where(StoryMemory.story_timeline == ch_num)
                        .where(StoryMemory.memory_type == 'chapter_summary')
                        .limit(1)
                    )
                    summary = summary_result.scalar_one_or_none()
                    
                    if summary:
                        skeleton_lines.append(f"第{ch_num}章《{ch_title}》：{summary[:100]}")
                    else:
                        skeleton_lines.append(f"第{ch_num}章《{ch_title}》")
            
            if len(skeleton_lines) <= 1:
                return None
            
            return "\n".join(skeleton_lines)
            
        except Exception as e:
            logger.error(f"❌ 构建故事骨架失败: {str(e)}")
            return None

    async def _build_foreshadow_context(
        self,
        project_id: str,
        chapter_number: int,
        db: AsyncSession
    ) -> Optional[str]:
        """
        构建伏笔上下文（从数据库直接查询）
        
        包含：
        1. 即将需要回收的伏笔（提醒）
        2. 当前活跃的伏笔（可以暗示）
        """
        try:
            result = await db.execute(
                select(Foreshadow).where(
                    Foreshadow.project_id == project_id,
                    Foreshadow.status.in_([
                        ForeshadowStatus.PLANTED.value,
                        ForeshadowStatus.HINTED.value
                    ])
                ).order_by(Foreshadow.importance.desc())
            )
            foreshadows = result.scalars().all()
            
            if not foreshadows:
                return None
            
            lines = []
            urgent = []
            active = []
            
            for f in foreshadows:
                if f.resolved_chapter_number:
                    remaining = f.resolved_chapter_number - chapter_number
                    if remaining <= f.remind_before_chapters and remaining >= 0:
                        urgent.append(f)
                    elif remaining > 0:
                        active.append(f)
                else:
                    active.append(f)
            
            if urgent:
                lines.append("【⚠️ 即将回收的伏笔】")
                for f in urgent[:3]:
                    remaining = f.resolved_chapter_number - chapter_number
                    lines.append(f"- 【{f.title}】(剩余{remaining}章): {f.description[:80]}...")
            
            if active and len(lines) < 200:
                lines.append("【📌 活跃伏笔（可适当暗示）】")
                for f in active[:5]:
                    lines.append(f"- 【{f.title}】: {f.description[:50]}...")
            
            return "\n".join(lines) if lines else None
            
        except Exception as e:
            logger.error(f"❌ 构建伏笔上下文失败: {str(e)}")
            return None

    async def _build_style_guide(
        self,
        project: Project,
        db: AsyncSession
    ) -> Optional[str]:
        """
        构建风格指南（从已有章节学习）
        
        当项目有 3+ 已完成章节时，生成简洁的风格指南
        """
        try:
            from app.services.style_analyzer import StyleAnalyzer
            
            # 获取已完成章节
            result = await db.execute(
                select(Chapter).where(
                    Chapter.project_id == project.id,
                    Chapter.content != None,
                    Chapter.content != ""
                ).order_by(Chapter.chapter_number).limit(3)
            )
            chapters = result.scalars().all()
            
            if len(chapters) < 2:
                return None
            
            # 使用 StyleAnalyzer 生成风格指南
            analyzer = StyleAnalyzer()
            
            # 收集基础指标
            metrics_list = []
            for ch in chapters:
                m = analyzer.analyze_basic_metrics(ch.content)
                metrics_list.append(m)
            
            # 计算平均值
            avg_sentence = sum(m.get("avg_sentence_length", 0) for m in metrics_list) / len(metrics_list)
            avg_dialogue = sum(m.get("dialogue_ratio", 0) for m in metrics_list) / len(metrics_list)
            
            # 生成简洁的风格指南
            guide_lines = ["【写作风格参考】"]
            
            if avg_sentence < 20:
                guide_lines.append("- 句式：短句为主，节奏明快")
            elif avg_sentence > 35:
                guide_lines.append("- 句式：长句为主，描写细腻")
            else:
                guide_lines.append("- 句式：长短结合，张弛有度")
            
            if avg_dialogue > 30:
                guide_lines.append("- 对话：对话丰富，注重人物互动")
            elif avg_dialogue < 10:
                guide_lines.append("- 对话：以叙述为主，对话精简")
            else:
                guide_lines.append("- 对话：叙述与对话均衡")
            
            guide_lines.append(f"- 参考数据：平均句长{avg_sentence:.0f}字，对话占比{avg_dialogue:.0f}%")
            
            return "\n".join(guide_lines)
            
        except Exception as e:
            logger.error(f"❌ 构建风格指南失败: {str(e)}")
            return None


class FocusedMemoryRetriever:
    """
    精简记忆检索器
    
    相比原有的memory_service，提供更精准、更简洁的记忆检索
    """
    
    def __init__(self, memory_service):
        """
        初始化检索器
        
        Args:
            memory_service: 基础记忆服务实例
        """
        self.memory_service = memory_service
    
    async def get_relevant_memories(
        self,
        user_id: str,
        project_id: str,
        chapter_number: int,
        chapter_outline: str,
        limit: int = 3
    ) -> str:
        """
        获取与本章最相关的记忆
        
        策略：
        1. 仅检索与大纲语义最相关的记忆
        2. 提高重要性阈值，过滤低质量记忆
        3. 优先返回未回收的伏笔
        
        Args:
            user_id: 用户ID
            project_id: 项目ID
            chapter_number: 当前章节号
            chapter_outline: 本章大纲
            limit: 返回数量限制
        
        Returns:
            格式化的记忆文本
        """
        # 1. 语义检索相关记忆（提高阈值）
        relevant = await self.memory_service.search_memories(
            user_id=user_id,
            project_id=project_id,
            query=chapter_outline,
            limit=limit,
            min_importance=0.7  # 从0.4提高到0.7
        )
        
        # 2. 检查即将到期的伏笔
        due_foreshadows = await self._get_due_foreshadows(
            user_id, project_id, chapter_number,
            lookahead=5  # 仅看5章内需要回收的
        )
        
        # 3. 合并并格式化
        return self._format_memories(relevant, due_foreshadows, max_length=500)
    
    async def _get_due_foreshadows(
        self,
        user_id: str,
        project_id: str,
        chapter_number: int,
        lookahead: int = 5
    ) -> List[Dict[str, Any]]:
        """获取即将需要回收的伏笔"""
        foreshadows = await self.memory_service.find_unresolved_foreshadows(
            user_id, project_id, chapter_number
        )
        
        # 过滤：只保留埋下时间较长的伏笔
        due_foreshadows = []
        for fs in foreshadows:
            meta = fs.get('metadata', {})
            fs_chapter = meta.get('chapter_number', 0)
            if chapter_number - fs_chapter >= lookahead:
                due_foreshadows.append({
                    'chapter': fs_chapter,
                    'content': fs.get('content', '')[:60],
                    'importance': meta.get('importance', 0.5)
                })
        
        return due_foreshadows[:2]  # 最多2条
    
    def _format_memories(
        self,
        relevant: List[Dict[str, Any]],
        foreshadows: List[Dict[str, Any]],
        max_length: int = 500
    ) -> str:
        """格式化为简洁文本，严格限制长度"""
        lines = []
        current_length = 0
        
        # 优先添加待回收伏笔
        if foreshadows:
            lines.append("【待回收伏笔】")
            for fs in foreshadows[:2]:
                text = f"- 第{fs['chapter']}章埋下：{fs['content']}"
                if current_length + len(text) > max_length:
                    break
                lines.append(text)
                current_length += len(text)
        
        # 添加相关记忆
        if relevant and current_length < max_length:
            lines.append("【相关记忆】")
            for mem in relevant:
                content = mem.get('content', '')[:80]
                text = f"- {content}"
                if current_length + len(text) > max_length:
                    break
                lines.append(text)
                current_length += len(text)
        
        return "\n".join(lines) if lines else ""
