"""风格分析服务 - 从章节内容学习和分析写作风格"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import re

from app.models.chapter import Chapter
from app.models.project import Project
from app.services.ai_service import AIService
from app.logger import get_logger

logger = get_logger(__name__)


class StyleAnalyzer:
    """写作风格分析器"""
    
    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service
    
    def analyze_basic_metrics(self, content: str) -> Dict[str, Any]:
        """
        分析基础文本指标（不需要 AI）
        """
        if not content:
            return {}
        
        # 分段
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        # 分句
        sentences = re.split(r'[。！？…]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 对话统计
        dialogue_pattern = r'[""「」『』].*?[""「」『』]|".*?"|「.*?」'
        dialogues = re.findall(dialogue_pattern, content)
        dialogue_chars = sum(len(d) for d in dialogues)
        
        # 计算指标
        total_chars = len(content)
        avg_sentence_len = total_chars / len(sentences) if sentences else 0
        avg_paragraph_len = total_chars / len(paragraphs) if paragraphs else 0
        dialogue_ratio = dialogue_chars / total_chars if total_chars > 0 else 0
        
        # 标点密度
        punctuation = re.findall(r'[，。！？、；：""''「」『』…—]', content)
        punctuation_density = len(punctuation) / total_chars if total_chars > 0 else 0
        
        return {
            "total_chars": total_chars,
            "paragraph_count": len(paragraphs),
            "sentence_count": len(sentences),
            "avg_sentence_length": round(avg_sentence_len, 1),
            "avg_paragraph_length": round(avg_paragraph_len, 1),
            "dialogue_ratio": round(dialogue_ratio * 100, 1),
            "punctuation_density": round(punctuation_density * 100, 1),
            "dialogue_count": len(dialogues)
        }
    
    async def analyze_style_with_ai(
        self,
        content: str,
        project: Project
    ) -> Dict[str, Any]:
        """
        使用 AI 分析写作风格特征
        """
        if not self.ai_service or not content:
            return {}
        
        prompt = f"""请分析以下小说章节的写作风格特征。

【小说信息】
- 书名: {project.title}
- 类型: {project.genre or '未设定'}

【章节内容】
{content[:3000]}

【分析要求】
请从以下维度分析写作风格：

1. 叙事风格: 客观冷静/热情洋溢/幽默诙谐/沉郁深沉/轻松明快
2. 描写特点: 细腻详尽/简洁明快/意象丰富/写实直白
3. 节奏感: 快节奏/中等/慢节奏/张弛有度
4. 语言特色: 文言古风/现代白话/网络流行/诗意优美/通俗易懂
5. 情感基调: 热血激昂/温馨治愈/紧张刺激/悲伤忧郁/轻松愉快

请以JSON格式返回：
{{
    "narrative_style": "叙事风格",
    "description_style": "描写特点", 
    "pacing": "节奏感",
    "language_style": "语言特色",
    "emotional_tone": "情感基调",
    "unique_features": ["特色1", "特色2"],
    "style_summary": "50字以内的风格总结"
}}

只返回JSON。"""

        try:
            result = await self.ai_service.generate_text(
                prompt=prompt,
                max_tokens=8000,
                temperature=0.3
            )
            
            content_str = result.get("content", "")
            logger.debug(f"AI 风格分析原始返回: {content_str[:200]}...")
            
            if not content_str:
                # 尝试从 reasoning_content 获取
                content_str = result.get("reasoning_content", "")
            
            if not content_str:
                return {"error": "AI 返回为空", "raw": str(result)[:200]}
            
            # 提取 JSON
            start = content_str.find("{")
            end = content_str.rfind("}") + 1
            if start >= 0 and end > start:
                content_str = content_str[start:end]
                return json.loads(content_str.strip())
            
            # 如果没有 JSON，返回原始内容
            return {
                "style_summary": content_str[:200],
                "raw_analysis": True
            }
        except json.JSONDecodeError as e:
            logger.warning(f"AI 风格分析 JSON 解析失败: {e}")
            return {
                "narrative_style": "分析中",
                "style_summary": "风格分析完成，详细结果解析中"
            }
        except Exception as e:
            logger.error(f"AI 风格分析失败: {e}")
            return {"error": str(e)}

    async def learn_project_style(
        self,
        project_id: str,
        db: AsyncSession,
        sample_count: int = 3
    ) -> Dict[str, Any]:
        """
        从项目已有章节学习整体写作风格
        """
        # 获取已完成的章节
        result = await db.execute(
            select(Chapter).where(
                Chapter.project_id == project_id,
                Chapter.content != None,
                Chapter.content != ""
            ).order_by(Chapter.chapter_number).limit(sample_count)
        )
        chapters = result.scalars().all()
        
        if not chapters:
            return {"error": "项目无已完成章节"}
        
        # 合并基础指标
        all_metrics = []
        for ch in chapters:
            metrics = self.analyze_basic_metrics(ch.content)
            metrics["chapter_number"] = ch.chapter_number
            all_metrics.append(metrics)
        
        # 计算平均值
        avg_metrics = {
            "sample_chapters": len(chapters),
            "avg_sentence_length": round(sum(m.get("avg_sentence_length", 0) for m in all_metrics) / len(all_metrics), 1),
            "avg_paragraph_length": round(sum(m.get("avg_paragraph_length", 0) for m in all_metrics) / len(all_metrics), 1),
            "avg_dialogue_ratio": round(sum(m.get("dialogue_ratio", 0) for m in all_metrics) / len(all_metrics), 1),
            "chapter_metrics": all_metrics
        }
        
        return avg_metrics

    async def generate_style_guide(
        self,
        project: Project,
        chapters: List[Chapter]
    ) -> str:
        """
        根据已有章节生成风格指南（用于 AI 生成时参考）
        """
        if not self.ai_service or not chapters:
            return ""
        
        # 收集样本
        samples = []
        for ch in chapters[:3]:
            if ch.content:
                samples.append(f"【第{ch.chapter_number}章片段】\n{ch.content[:500]}...")
        
        if not samples:
            return ""
        
        prompt = f"""请根据以下小说章节样本，总结出一份简洁的写作风格指南。

【小说信息】
- 书名: {project.title}
- 类型: {project.genre or '未设定'}

【章节样本】
{chr(10).join(samples)}

【任务】
请总结出一份200字以内的写作风格指南，包括：
1. 叙事视角和语气
2. 句式和段落特点
3. 对话风格
4. 描写偏好
5. 需要保持的独特风格元素

直接输出风格指南文本，不要JSON格式。"""

        try:
            result = await self.ai_service.generate_text(
                prompt=prompt,
                max_tokens=500,
                temperature=0.5
            )
            return result.get("content", "").strip()
        except Exception as e:
            logger.error(f"生成风格指南失败: {e}")
            return ""
