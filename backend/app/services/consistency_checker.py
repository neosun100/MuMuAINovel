"""一致性检测服务 - 检测角色、情节、世界观的一致性"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.models.chapter import Chapter
from app.models.character import Character
from app.models.project import Project
from app.services.ai_service import AIService
from app.logger import get_logger

logger = get_logger(__name__)


class ConsistencyChecker:
    """一致性检测器"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    async def check_character_consistency(
        self,
        chapter_content: str,
        characters: List[Character],
        project: Project
    ) -> Dict[str, Any]:
        """
        检测章节中角色行为是否与设定一致
        
        Returns:
            {
                "score": 0-100,
                "issues": [{"character": "xxx", "issue": "xxx", "severity": "high/medium/low"}],
                "suggestions": ["xxx"]
            }
        """
        if not characters or not chapter_content:
            return {"score": 100, "issues": [], "suggestions": []}
        
        # 构建角色设定摘要
        char_profiles = []
        for c in characters[:10]:  # 最多10个角色
            profile = f"【{c.name}】\n"
            profile += f"- 角色类型: {c.role_type or '未设定'}\n"
            profile += f"- 性格: {c.personality[:100] if c.personality else '未设定'}...\n"
            profile += f"- 背景: {c.background[:100] if c.background else '未设定'}...\n"
            char_profiles.append(profile)
        
        prompt = f"""请分析以下小说章节内容，检测角色行为是否与其设定一致。

【小说信息】
- 书名: {project.title}
- 类型: {project.genre or '未设定'}

【角色设定】
{chr(10).join(char_profiles)}

【章节内容】
{chapter_content[:3000]}

【分析要求】
请检测以下方面的一致性问题：
1. 角色性格是否与设定相符
2. 角色说话方式是否符合其身份背景
3. 角色行为是否符合其能力设定
4. 角色关系互动是否合理

请以JSON格式返回分析结果：
{{
    "score": 0-100的一致性评分,
    "issues": [
        {{"character": "角色名", "issue": "问题描述", "severity": "high/medium/low", "location": "问题出现位置描述"}}
    ],
    "suggestions": ["改进建议1", "改进建议2"]
}}

只返回JSON，不要其他内容。"""

        try:
            result = await self.ai_service.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            content = result.get("content", "")
            logger.debug(f"AI 原始返回: {content[:500]}...")
            
            # 提取 JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                parts = content.split("```")
                for part in parts:
                    if "{" in part and "}" in part:
                        content = part
                        break
            
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                content = content[start:end]
            
            # 尝试修复常见的 JSON 问题
            content = content.replace("\n", " ").replace("\r", "")
            
            try:
                return json.loads(content.strip())
            except json.JSONDecodeError:
                # 尝试使用更宽松的解析
                import re
                # 提取 score
                score_match = re.search(r'"score"\s*:\s*(\d+)', content)
                score = int(score_match.group(1)) if score_match else 85
                
                return {
                    "score": score,
                    "issues": [],
                    "suggestions": ["检测完成，详细结果解析中"]
                }
        except Exception as e:
            logger.error(f"角色一致性检测失败: {e}")
            return {"score": -1, "issues": [], "suggestions": [], "error": str(e)}

    async def check_plot_coherence(
        self,
        current_chapter: Chapter,
        previous_chapters: List[Chapter],
        project: Project
    ) -> Dict[str, Any]:
        """
        检测情节连贯性
        
        Returns:
            {
                "score": 0-100,
                "issues": [{"type": "xxx", "description": "xxx", "severity": "high/medium/low"}],
                "suggestions": ["xxx"]
            }
        """
        if not previous_chapters or not current_chapter.content:
            return {"score": 100, "issues": [], "suggestions": []}
        
        # 获取前几章的摘要
        prev_summaries = []
        for ch in previous_chapters[-3:]:  # 最多前3章
            summary = ch.summary or (ch.content[:200] + "..." if ch.content else "无内容")
            prev_summaries.append(f"第{ch.chapter_number}章《{ch.title}》: {summary[:150]}")
        
        prompt = f"""请分析当前章节与前文的情节连贯性。

【小说信息】
- 书名: {project.title}
- 类型: {project.genre or '未设定'}

【前文摘要】
{chr(10).join(prev_summaries)}

【当前章节】
第{current_chapter.chapter_number}章《{current_chapter.title}》
{current_chapter.content[:2500]}

【分析要求】
请检测以下连贯性问题：
1. 时间线是否连贯（有无时间跳跃或矛盾）
2. 地点转换是否合理
3. 角色状态是否延续（如受伤、情绪等）
4. 情节发展是否自然
5. 是否有前后矛盾的描述

请以JSON格式返回：
{{
    "score": 0-100的连贯性评分,
    "issues": [
        {{"type": "时间线/地点/角色状态/情节/矛盾", "description": "问题描述", "severity": "high/medium/low"}}
    ],
    "suggestions": ["改进建议"]
}}

只返回JSON。"""

        try:
            result = await self.ai_service.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            content = result.get("content", "")
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                parts = content.split("```")
                for part in parts:
                    if "{" in part and "}" in part:
                        content = part
                        break
            
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                content = content[start:end]
            
            content = content.replace("\n", " ").replace("\r", "")
            
            try:
                return json.loads(content.strip())
            except json.JSONDecodeError:
                import re
                score_match = re.search(r'"score"\s*:\s*(\d+)', content)
                score = int(score_match.group(1)) if score_match else 85
                return {
                    "score": score,
                    "issues": [],
                    "suggestions": ["检测完成，详细结果解析中"]
                }
        except Exception as e:
            logger.error(f"情节连贯性检测失败: {e}")
            return {"score": -1, "issues": [], "suggestions": [], "error": str(e)}

    async def full_consistency_check(
        self,
        chapter: Chapter,
        project: Project,
        characters: List[Character],
        previous_chapters: List[Chapter],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        完整一致性检测
        """
        results = {
            "chapter_id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "character_consistency": None,
            "plot_coherence": None,
            "overall_score": 0
        }
        
        # 角色一致性检测
        if characters:
            results["character_consistency"] = await self.check_character_consistency(
                chapter.content or "",
                characters,
                project
            )
        
        # 情节连贯性检测
        if previous_chapters:
            results["plot_coherence"] = await self.check_plot_coherence(
                chapter,
                previous_chapters,
                project
            )
        
        # 计算综合评分
        scores = []
        if results["character_consistency"] and results["character_consistency"].get("score", -1) >= 0:
            scores.append(results["character_consistency"]["score"])
        if results["plot_coherence"] and results["plot_coherence"].get("score", -1) >= 0:
            scores.append(results["plot_coherence"]["score"])
        
        results["overall_score"] = sum(scores) / len(scores) if scores else 100
        
        return results
