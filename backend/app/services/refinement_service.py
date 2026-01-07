"""章节二次优化服务 - 三段论实现"""
import uuid
import httpx
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, AsyncGenerator
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chapter import Chapter
from app.models.refinement import ChapterRefinement
from app.models.project import Project
from app.models.character import Character
from app.models.outline import Outline
from app.config import RefinementConfig
from app.logger import get_logger

logger = get_logger(__name__)


# ==================== 提示词模板 ====================

SEGMENT1_PROMPT = """# 角色设定
你是一位资深小说编辑，专门负责长篇历史小说的深度优化工作。你的任务是在保持原文核心情节和风格的基础上，提升文章质量。

# 当前任务
优化《{project_title}》第{chapter_number}章《{chapter_title}》的【第1部分】（约占全章40%）

---

# 背景信息

## 小说基本信息
{background}

## 本章涉及的主要角色
{characters}

## 前情摘要（故事骨架）
{story_skeleton}

## 上一章结尾（第{prev_chapter_number}章优化版）
{previous_chapter_ending}

## 本章大纲
{outline}

---

# 待优化内容

## 原文第1部分（{segment_word_count}字）
{segment_content}

## 后续内容摘要（供参考，确保连贯）
{remaining_summary}

---

# 优化要求

## 1. 修正错误（最重要）
- 修正任何历史事实错误（年代、人物、事件、官职、地名等）
- 修正时间线矛盾（与前文不符的时间描述）
- 修正角色行为不一致（性格、能力、立场与设定不符）
- 修正逻辑漏洞（因果关系、空间移动等）

## 2. 提升文笔
- 优化句式结构，避免重复单调
- 丰富环境描写（视觉、听觉、嗅觉、触觉）
- 增强动作描写的画面感
- 优化对话的自然度和个性化
- 增强情感表达的细腻度

## 3. 保持连贯
- 确保与上一章结尾自然衔接（语气、情绪、场景）
- 保持角色性格一致
- 保持叙事风格统一

## 4. 字数控制
- 原文约{segment_word_count}字
- 优化后应在{min_words}-{max_words}字（±10%）

## 5. 绝对禁止
- ❌ 不要改变核心情节走向
- ❌ 不要添加原文没有的重要情节
- ❌ 这是第1部分，后面还有内容，不要写成结尾的感觉
- ❌ 不要添加任何说明、注释、点评

---

# 输出要求
直接输出优化后的第1部分内容，保持原有的段落结构。
"""

SEGMENT2_PROMPT = """# 角色设定
你是一位资深小说编辑，正在继续优化《{project_title}》第{chapter_number}章《{chapter_title}》。

# 当前任务
优化【第2部分】（约占全章40%），确保与已优化的第1部分自然衔接。

---

# 背景信息

## 小说基本信息
{background}

## 本章涉及的主要角色
{characters}

## 前情摘要（故事骨架）
{story_skeleton}

## 上一章结尾（第{prev_chapter_number}章优化版）
{previous_chapter_ending}

## 本章大纲
{outline}

---

# 已完成内容

## 已优化的第1部分
{segment1_refined}

---

# 待优化内容

## 原文第2部分（{segment_word_count}字）
{segment_content}

## 后续内容摘要
{remaining_summary}

---

# 优化要求

## 1. 衔接第1部分
- 语气、节奏与第1部分保持一致
- 情节发展自然承接
- 不要重复第1部分已经描述的内容

## 2. 修正错误
- 历史事实、时间线、角色行为、逻辑漏洞

## 3. 提升文笔
- 句式、环境描写、动作描写、对话、情感

## 4. 字数控制
- 原文约{segment_word_count}字
- 优化后应在{min_words}-{max_words}字（±10%）

## 5. 绝对禁止
- ❌ 不要改变核心情节
- ❌ 这是第2部分，后面还有结尾，不要写成结尾的感觉
- ❌ 不要添加任何说明、注释

---

# 输出要求
直接输出优化后的第2部分内容。
"""

SEGMENT3_PROMPT = """# 角色设定
你是一位资深小说编辑，正在完成《{project_title}》第{chapter_number}章《{chapter_title}》的最后优化。

# 当前任务
优化【结尾部分】（约占全章20%），这是本章的收尾，需要特别注意结尾处理。

---

# 背景信息

## 小说基本信息
{background}

## 本章涉及的主要角色
{characters}

## 前情摘要（故事骨架）
{story_skeleton}

## 上一章结尾（第{prev_chapter_number}章优化版）
{previous_chapter_ending}

## 本章大纲
{outline}

---

# 已完成内容

## 已优化的第1部分
{segment1_refined}

## 已优化的第2部分
{segment2_refined}

---

# 待优化内容

## 原文结尾部分（{segment_word_count}字）
{segment_content}

---

# 优化要求

## 1. 衔接前文
- 与第2部分自然衔接
- 情节发展符合逻辑

## 2. 修正错误
- 历史事实、时间线、角色行为、逻辑漏洞

## 3. 提升文笔
- 句式、环境描写、动作描写、对话、情感

## 4. ⚠️ 结尾处理（极其重要）

### 必须做到：
- ✅ 以悬念结尾（留下未解决的问题或冲突）
- ✅ 或以情感高点结尾（强烈的情感冲击）
- ✅ 或以转折结尾（意外的发展）
- ✅ 让读者产生"想继续看下一章"的欲望

### 绝对禁止：
- ❌ 禁止出现"本章讲述了..."、"至此..."等总结性文字
- ❌ 禁止出现"欲知后事如何，请看下回分解"
- ❌ 禁止出现"综上所述"、"总而言之"、"总之"
- ❌ 禁止出现"（本章完）"、"（未完待续）"
- ❌ 禁止对本章内容进行任何形式的回顾或总结

## 5. 字数控制
- 原文约{segment_word_count}字
- 优化后应在{min_words}-{max_words}字（±10%）

---

# 输出要求
直接输出优化后的结尾部分内容。记住：以悬念、高潮或转折结尾，绝对不要总结！
"""


# ==================== 工具函数 ====================

def split_chapter_for_refinement(content: str) -> List[Dict]:
    """将章节分成3段用于优化（40%/40%/20%）"""
    total_length = len(content)
    
    target_seg1_end = int(total_length * 0.4)
    target_seg2_end = int(total_length * 0.8)
    
    seg1_end = _find_best_split_point(content, target_seg1_end)
    seg2_end = _find_best_split_point(content, target_seg2_end)
    
    return [
        {
            "segment": 1,
            "content": content[:seg1_end].strip(),
            "word_count": len(content[:seg1_end].strip()),
            "is_ending": False
        },
        {
            "segment": 2,
            "content": content[seg1_end:seg2_end].strip(),
            "word_count": len(content[seg1_end:seg2_end].strip()),
            "is_ending": False
        },
        {
            "segment": 3,
            "content": content[seg2_end:].strip(),
            "word_count": len(content[seg2_end:].strip()),
            "is_ending": True
        }
    ]


def _find_best_split_point(content: str, target: int, search_range: int = 500) -> int:
    """在目标位置附近找最佳切分点"""
    start = max(0, target - search_range)
    end = min(len(content), target + search_range)
    search_area = content[start:end]
    
    # 优先找双换行
    pos = search_area.rfind('\n\n')
    if pos != -1:
        return start + pos + 2
    
    # 其次找单换行
    pos = search_area.rfind('\n')
    if pos != -1:
        return start + pos + 1
    
    # 最后找句号
    for punct in ['。', '！', '？', '.', '!', '?']:
        pos = search_area.rfind(punct)
        if pos != -1:
            return start + pos + 1
    
    return target


def generate_segment_summary(content: str, max_chars: int = 200) -> str:
    """生成段落摘要"""
    if not content:
        return "（无后续内容）"
    
    summary = content[:max_chars]
    for punct in ['。', '！', '？', '.', '!', '?']:
        last_punct = summary.rfind(punct)
        if last_punct > max_chars * 0.5:
            summary = summary[:last_punct + 1]
            break
    
    return summary + "..."


# ==================== 核心服务 ====================

class ChapterRefinementService:
    """章节二次优化服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def refine_chapter(
        self,
        chapter_id: str,
        previous_refined_content: str = None,
        model: str = None
    ) -> Dict:
        """优化单个章节（三段论）"""
        
        # 1. 获取章节和项目
        chapter = await self._get_chapter(chapter_id)
        if not chapter:
            raise ValueError(f"章节不存在: {chapter_id}")
        
        project = await self._get_project(chapter.project_id)
        
        # 2. 确定使用的模型
        actual_model = RefinementConfig.get_model(model)
        logger.info(f"开始优化第{chapter.chapter_number}章，使用模型: {actual_model}")
        
        # 3. 构建固定上下文
        fixed_context = await self._build_fixed_context(
            chapter=chapter,
            project=project,
            previous_refined=previous_refined_content
        )
        
        # 4. 分段
        segments = split_chapter_for_refinement(chapter.content)
        
        # 5. 创建优化记录
        refinement = await self._create_refinement_record(chapter, segments, actual_model)
        
        # 6. 逐段优化
        refined_segments = []
        
        try:
            for i, seg in enumerate(segments):
                await self._update_status(refinement.id, f"segment{i+1}", i+1)
                
                refined = await self._refine_single_segment(
                    segment_index=i,
                    segment=seg,
                    fixed_context=fixed_context,
                    chapter=chapter,
                    project=project,
                    refined_segments=refined_segments,
                    remaining_segments=segments[i+1:],
                    model=actual_model
                )
                
                refined_segments.append(refined)
                await self._save_segment_result(refinement.id, i+1, seg["content"], refined)
                logger.info(f"第{chapter.chapter_number}章 第{i+1}段优化完成")
            
            # 7. 合并
            await self._update_status(refinement.id, "merging", 3)
            final_content = "\n\n".join(refined_segments)
            final_content = self._post_process(final_content)
            
            # 8. 保存最终结果
            await self._save_final_result(refinement.id, final_content)
            await self._update_chapter_content(chapter, final_content, refinement.id, actual_model)
            
            logger.info(f"第{chapter.chapter_number}章优化完成，原{len(chapter.content)}字 → {len(final_content)}字")
            
            return {
                "chapter_id": chapter_id,
                "chapter_number": chapter.chapter_number,
                "original_words": len(chapter.content),
                "refined_words": len(final_content),
                "model_used": actual_model,
                "segments_processed": 3,
                "status": "completed"
            }
            
        except Exception as e:
            await self._mark_failed(refinement.id, str(e))
            logger.error(f"第{chapter.chapter_number}章优化失败: {e}")
            raise
    
    async def refine_all_chapters(
        self,
        project_id: str,
        start_chapter: int = 1,
        end_chapter: int = 100,
        model: str = None
    ) -> AsyncGenerator[Dict, None]:
        """串行优化所有章节"""
        
        previous_refined = None
        
        for chapter_num in range(start_chapter, end_chapter + 1):
            chapter = await self._get_chapter_by_number(project_id, chapter_num)
            
            if not chapter:
                yield {"chapter": chapter_num, "status": "skipped", "reason": "not found"}
                continue
            
            if not chapter.content or len(chapter.content) < 100:
                yield {"chapter": chapter_num, "status": "skipped", "reason": "no content"}
                previous_refined = None
                continue
            
            try:
                result = await self.refine_chapter(
                    chapter_id=chapter.id,
                    previous_refined_content=previous_refined,
                    model=model
                )
                
                # 获取优化后内容作为下一章的上下文
                refinement = await self._get_refinement(chapter.id)
                previous_refined = refinement.refined_content if refinement else chapter.content
                
                yield {"chapter": chapter_num, "status": "completed", **result}
                
            except Exception as e:
                yield {"chapter": chapter_num, "status": "failed", "error": str(e)}
                previous_refined = chapter.content
    
    async def _refine_single_segment(
        self,
        segment_index: int,
        segment: Dict,
        fixed_context: Dict,
        chapter: Chapter,
        project: Project,
        refined_segments: List[str],
        remaining_segments: List[Dict],
        model: str
    ) -> str:
        """优化单个段落"""
        
        # 构建提示词
        remaining_summary = "\n".join([
            f"第{s['segment']}部分开头: {generate_segment_summary(s['content'])}"
            for s in remaining_segments
        ]) if remaining_segments else "（无后续内容）"
        
        word_count = segment["word_count"]
        min_words = int(word_count * 0.9)
        max_words = int(word_count * 1.1)
        
        base_params = {
            "project_title": project.title,
            "chapter_number": chapter.chapter_number,
            "chapter_title": chapter.title,
            "background": fixed_context["background"],
            "characters": fixed_context["characters"],
            "story_skeleton": fixed_context["story_skeleton"],
            "prev_chapter_number": fixed_context["prev_chapter_number"],
            "previous_chapter_ending": fixed_context["previous_chapter"],
            "outline": fixed_context["outline"],
            "segment_content": segment["content"],
            "segment_word_count": word_count,
            "min_words": min_words,
            "max_words": max_words,
            "remaining_summary": remaining_summary
        }
        
        if segment_index == 0:
            prompt = SEGMENT1_PROMPT.format(**base_params)
        elif segment_index == 1:
            prompt = SEGMENT2_PROMPT.format(
                **base_params,
                segment1_refined=refined_segments[0]
            )
        else:
            prompt = SEGMENT3_PROMPT.format(
                **base_params,
                segment1_refined=refined_segments[0],
                segment2_refined=refined_segments[1]
            )
        
        # 调用模型
        result = await self._call_model(prompt, model)
        return self._clean_output(result)
    
    async def _call_model(self, prompt: str, model: str, max_retries: int = 3) -> str:
        """调用LiteLLM模型，使用流式响应避免网关超时"""
        
        api_base = RefinementConfig.get_api_base()
        api_key = RefinementConfig.get_api_key()
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
                    async with client.stream(
                        "POST",
                        api_base,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 8000,
                            "temperature": 0.3,
                            "stream": True
                        }
                    ) as response:
                        if response.status_code != 200:
                            error_text = await response.aread()
                            if response.status_code in [502, 503, 504]:
                                logger.warning(f"API网关错误 (尝试 {attempt+1}/{max_retries}): {response.status_code}")
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(5 * (attempt + 1))
                                    continue
                            raise Exception(f"API调用失败: {response.status_code} - {error_text.decode()[:500]}")
                        
                        # 收集流式响应
                        content_parts = []
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]
                                if data == "[DONE]":
                                    break
                                try:
                                    import json
                                    chunk = json.loads(data)
                                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                                    if "content" in delta and delta["content"]:
                                        content_parts.append(delta["content"])
                                except:
                                    pass
                        
                        return "".join(content_parts)
                    
            except httpx.TimeoutException:
                logger.warning(f"请求超时 (尝试 {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5 * (attempt + 1))
                    continue
                raise Exception("API请求超时，已重试3次")
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"请求异常 (尝试 {attempt+1}/{max_retries}): {e}")
                    await asyncio.sleep(5 * (attempt + 1))
                    continue
                raise
        
        raise Exception("API调用失败，已达最大重试次数")
    
    async def _build_fixed_context(
        self,
        chapter: Chapter,
        project: Project,
        previous_refined: str = None
    ) -> Dict:
        """构建固定上下文"""
        
        context = {}
        
        # 1. 项目背景
        context["background"] = f"""标题: {project.title}
类型: {project.genre or '未设定'}
简介: {project.description or '未设定'}
时代背景: {project.world_time_period or '未设定'}
地点: {project.world_location or '未设定'}"""
        
        # 2. 涉及角色
        characters = await self._get_characters(project.id)
        if characters:
            char_list = [f"- {c.name}: {c.role_type or ''}，{c.personality[:100] if c.personality else ''}" 
                        for c in characters[:10]]
            context["characters"] = "\n".join(char_list)
        else:
            context["characters"] = "（无角色信息）"
        
        # 3. 故事骨架
        if chapter.chapter_number > 1:
            summaries = await self._get_chapter_summaries(project.id, chapter.chapter_number - 1)
            context["story_skeleton"] = summaries or "（无前情摘要）"
        else:
            context["story_skeleton"] = "（第一章，无前文）"
        
        # 4. 上一章结尾
        if previous_refined:
            context["previous_chapter"] = previous_refined[-5000:] if len(previous_refined) > 5000 else previous_refined
            context["prev_chapter_number"] = chapter.chapter_number - 1
        else:
            context["previous_chapter"] = "（第一章，无前文）"
            context["prev_chapter_number"] = 0
        
        # 5. 本章大纲
        outline = await self._get_outline(chapter.outline_id) if chapter.outline_id else None
        context["outline"] = outline.content if outline else "（无大纲）"
        
        return context
    
    def _post_process(self, content: str) -> str:
        """后处理"""
        import re
        
        # 移除前缀
        prefixes = ["优化后：", "优化后的内容：", "【优化后】", "---", "```"]
        for prefix in prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
        
        # 移除后缀总结
        patterns = [
            r'\n\n【本章总结】.*$',
            r'\n\n本章讲述了.*$',
            r'\n\n综上所述.*$',
        ]
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        return content.strip()
    
    def _clean_output(self, output: str) -> str:
        """清理输出"""
        if output.startswith("```"):
            lines = output.split("\n")
            output = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
        return output.strip()
    
    # ==================== 数据库操作 ====================
    
    async def _get_chapter(self, chapter_id: str) -> Optional[Chapter]:
        result = await self.db.execute(select(Chapter).where(Chapter.id == chapter_id))
        return result.scalar_one_or_none()
    
    async def _get_chapter_by_number(self, project_id: str, chapter_number: int) -> Optional[Chapter]:
        result = await self.db.execute(
            select(Chapter).where(
                Chapter.project_id == project_id,
                Chapter.chapter_number == chapter_number
            )
        )
        return result.scalar_one_or_none()
    
    async def _get_project(self, project_id: str) -> Optional[Project]:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()
    
    async def _get_characters(self, project_id: str) -> List[Character]:
        result = await self.db.execute(
            select(Character).where(Character.project_id == project_id).limit(20)
        )
        return result.scalars().all()
    
    async def _get_outline(self, outline_id: str) -> Optional[Outline]:
        if not outline_id:
            return None
        result = await self.db.execute(select(Outline).where(Outline.id == outline_id))
        return result.scalar_one_or_none()
    
    async def _get_chapter_summaries(self, project_id: str, end_chapter: int) -> str:
        result = await self.db.execute(
            select(Chapter.chapter_number, Chapter.title, Chapter.summary)
            .where(Chapter.project_id == project_id, Chapter.chapter_number <= end_chapter)
            .order_by(Chapter.chapter_number)
        )
        chapters = result.all()
        
        summaries = []
        for ch in chapters[-10:]:  # 最近10章
            summary = ch.summary[:200] if ch.summary else "（无摘要）"
            summaries.append(f"第{ch.chapter_number}章《{ch.title}》: {summary}")
        
        return "\n".join(summaries)
    
    async def _get_refinement(self, chapter_id: str) -> Optional[ChapterRefinement]:
        result = await self.db.execute(
            select(ChapterRefinement)
            .where(ChapterRefinement.chapter_id == chapter_id)
            .order_by(ChapterRefinement.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def _create_refinement_record(
        self,
        chapter: Chapter,
        segments: List[Dict],
        model: str
    ) -> ChapterRefinement:
        refinement = ChapterRefinement(
            id=str(uuid.uuid4()),
            chapter_id=chapter.id,
            project_id=chapter.project_id,
            chapter_number=chapter.chapter_number,
            original_content=chapter.content,
            original_word_count=len(chapter.content),
            segment1_original=segments[0]["content"],
            segment2_original=segments[1]["content"],
            segment3_original=segments[2]["content"],
            model_used=model,
            status="pending"
        )
        self.db.add(refinement)
        await self.db.commit()
        return refinement
    
    async def _update_status(self, refinement_id: str, status: str, current_segment: int):
        await self.db.execute(
            update(ChapterRefinement)
            .where(ChapterRefinement.id == refinement_id)
            .values(status=status, current_segment=current_segment, updated_at=datetime.now())
        )
        await self.db.commit()
    
    async def _save_segment_result(self, refinement_id: str, segment_num: int, original: str, refined: str):
        values = {
            f"segment{segment_num}_refined": refined,
            f"segment{segment_num}_word_count": len(refined),
            "updated_at": datetime.now()
        }
        await self.db.execute(
            update(ChapterRefinement)
            .where(ChapterRefinement.id == refinement_id)
            .values(**values)
        )
        await self.db.commit()
    
    async def _save_final_result(self, refinement_id: str, final_content: str):
        await self.db.execute(
            update(ChapterRefinement)
            .where(ChapterRefinement.id == refinement_id)
            .values(
                refined_content=final_content,
                refined_word_count=len(final_content),
                status="completed",
                completed_at=datetime.now()
            )
        )
        await self.db.commit()
    
    async def _update_chapter_content(
        self,
        chapter: Chapter,
        refined_content: str,
        refinement_id: str,
        model: str
    ):
        await self.db.execute(
            update(Chapter)
            .where(Chapter.id == chapter.id)
            .values(
                content=refined_content,
                word_count=len(refined_content),
                is_refined=True,
                refined_at=datetime.now(),
                refinement_id=refinement_id,
                refinement_model=model
            )
        )
        await self.db.commit()
    
    async def _mark_failed(self, refinement_id: str, error: str):
        await self.db.execute(
            update(ChapterRefinement)
            .where(ChapterRefinement.id == refinement_id)
            .values(status="failed", error_message=error, updated_at=datetime.now())
        )
        await self.db.commit()
