"""章节质量评分服务"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import re

from app.models.chapter import Chapter
from app.models.project import Project
from app.services.ai_service import AIService
from app.logger import get_logger

logger = get_logger(__name__)


class QualityScorer:
    """章节质量评分器"""
    
    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service
    
    def calculate_basic_score(self, content: str) -> Dict[str, Any]:
        """基础质量指标（不需要 AI）"""
        if not content:
            return {"total_score": 0, "error": "内容为空"}
        
        scores = {}
        
        # 1. 长度评分 (0-20)
        length = len(content)
        if length < 500:
            scores["length_score"] = 5
        elif length < 1000:
            scores["length_score"] = 10
        elif length < 3000:
            scores["length_score"] = 18
        else:
            scores["length_score"] = 20
        
        # 2. 段落结构评分 (0-20)
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        para_count = len(paragraphs)
        avg_para_len = length / para_count if para_count > 0 else 0
        
        if para_count < 3:
            scores["structure_score"] = 5
        elif 50 < avg_para_len < 200:
            scores["structure_score"] = 20
        elif 30 < avg_para_len < 300:
            scores["structure_score"] = 15
        else:
            scores["structure_score"] = 10
        
        # 3. 对话比例评分 (0-20)
        dialogue_pattern = r'[""「」『』].*?[""「」『』]|".*?"|「.*?」'
        dialogues = re.findall(dialogue_pattern, content)
        dialogue_chars = sum(len(d) for d in dialogues)
        dialogue_ratio = dialogue_chars / length if length > 0 else 0
        
        if 0.15 < dialogue_ratio < 0.45:
            scores["dialogue_score"] = 20
        elif 0.05 < dialogue_ratio < 0.6:
            scores["dialogue_score"] = 15
        else:
            scores["dialogue_score"] = 8
        
        # 4. 标点多样性评分 (0-20)
        punctuations = set(re.findall(r'[，。！？、；：…—]', content))
        if len(punctuations) >= 6:
            scores["punctuation_score"] = 20
        elif len(punctuations) >= 4:
            scores["punctuation_score"] = 15
        else:
            scores["punctuation_score"] = 10
        
        # 5. 句式变化评分 (0-20)
        sentences = re.split(r'[。！？]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        if sentences:
            lengths = [len(s) for s in sentences]
            variance = sum((l - sum(lengths)/len(lengths))**2 for l in lengths) / len(lengths)
            if variance > 200:
                scores["variety_score"] = 20
            elif variance > 100:
                scores["variety_score"] = 15
            else:
                scores["variety_score"] = 10
        else:
            scores["variety_score"] = 5
        
        total = sum(scores.values())
        
        return {
            "basic_total": total,
            "max_basic": 100,
            **scores,
            "details": {
                "char_count": length,
                "paragraph_count": para_count,
                "dialogue_ratio": round(dialogue_ratio * 100, 1),
                "punctuation_types": len(punctuations)
            }
        }
    
    async def evaluate_with_ai(
        self,
        content: str,
        project: Project,
        chapter: Chapter
    ) -> Dict[str, Any]:
        """AI 综合质量评估"""
        if not self.ai_service or not content:
            return {}
        
        prompt = f"""请评估以下小说章节的写作质量。

【小说信息】
- 书名: {project.title}
- 类型: {project.genre or '未设定'}
- 章节: 第{chapter.chapter_number}章 {chapter.title or ''}

【章节内容】
{content[:4000]}

【评估维度】（每项0-25分，总分100）

1. 文笔质量: 语言流畅度、用词准确性、修辞运用
2. 节奏把控: 情节推进速度、张弛有度、悬念设置
3. 情节设计: 逻辑合理性、吸引力、与主线关联
4. 对话质量: 符合人物性格、推动剧情、自然生动

请以JSON格式返回：
{{
    "writing_score": 0-25,
    "pacing_score": 0-25,
    "plot_score": 0-25,
    "dialogue_score": 0-25,
    "total_score": 0-100,
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["不足1", "不足2"],
    "suggestions": ["建议1", "建议2"],
    "summary": "50字以内的总体评价"
}}

只返回JSON。"""

        try:
            result = await self.ai_service.generate_text(
                prompt=prompt,
                max_tokens=8000,
                temperature=0.3
            )
            
            content_str = result.get("content", "") or result.get("reasoning_content", "")
            
            if not content_str:
                return {"error": "AI 返回为空"}
            
            # 提取 JSON
            start = content_str.find("{")
            end = content_str.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content_str[start:end])
            
            return {"error": "无法解析 AI 返回", "raw": content_str[:200]}
            
        except json.JSONDecodeError as e:
            logger.warning(f"质量评分 JSON 解析失败: {e}")
            return {"error": "JSON 解析失败"}
        except Exception as e:
            logger.error(f"AI 质量评估失败: {e}")
            return {"error": str(e)}
    
    async def full_quality_check(
        self,
        chapter_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """完整质量检查"""
        # 获取章节
        result = await db.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        chapter = result.scalar_one_or_none()
        
        if not chapter or not chapter.content:
            return {"error": "章节不存在或内容为空"}
        
        # 获取项目
        result = await db.execute(
            select(Project).where(Project.id == chapter.project_id)
        )
        project = result.scalar_one_or_none()
        
        # 基础评分
        basic = self.calculate_basic_score(chapter.content)
        
        # AI 评分
        ai_eval = {}
        if self.ai_service:
            ai_eval = await self.evaluate_with_ai(chapter.content, project, chapter)
        
        # 综合评分
        final_score = ai_eval.get("total_score", basic["basic_total"])
        
        return {
            "chapter_id": chapter_id,
            "chapter_number": chapter.chapter_number,
            "chapter_title": chapter.title,
            "basic_metrics": basic,
            "ai_evaluation": ai_eval,
            "final_score": final_score,
            "grade": self._score_to_grade(final_score)
        }
    
    def _score_to_grade(self, score: int) -> str:
        """分数转等级"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"
