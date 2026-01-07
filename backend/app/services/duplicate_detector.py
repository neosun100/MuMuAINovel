"""重复内容检测服务 - 支持流式返回"""
from typing import Dict, Any, List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re
from difflib import SequenceMatcher

from app.models.chapter import Chapter
from app.logger import get_logger

logger = get_logger(__name__)


class DuplicateDetector:
    """重复内容检测器"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.threshold = similarity_threshold
    
    def extract_segments(self, content: str, min_length: int = 30) -> List[str]:
        """提取文本片段用于比较"""
        if not content:
            return []
        
        sentences = re.split(r'[。！？\n]', content)
        segments = []
        
        for s in sentences:
            s = s.strip()
            if len(s) >= min_length:
                segments.append(s)
        
        return segments
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的相似度"""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1, text2).ratio()
    
    def find_duplicates_in_chapter(self, content: str, min_length: int = 30) -> List[Dict[str, Any]]:
        """检测章节内部重复"""
        segments = self.extract_segments(content, min_length)
        duplicates = []
        checked = set()
        
        for i, seg1 in enumerate(segments):
            for j, seg2 in enumerate(segments):
                if i >= j:
                    continue
                
                pair_key = (min(i, j), max(i, j))
                if pair_key in checked:
                    continue
                checked.add(pair_key)
                
                similarity = self.calculate_similarity(seg1, seg2)
                if similarity >= self.threshold:
                    duplicates.append({
                        "segment1": seg1[:100] + "..." if len(seg1) > 100 else seg1,
                        "segment2": seg2[:100] + "..." if len(seg2) > 100 else seg2,
                        "similarity": round(similarity * 100, 1),
                        "position1": i,
                        "position2": j
                    })
        
        return duplicates
    
    def find_duplicates_between_chapters(
        self,
        content1: str,
        content2: str,
        chapter1_info: Dict,
        chapter2_info: Dict,
        min_length: int = 30
    ) -> List[Dict[str, Any]]:
        """检测两章节间重复"""
        segments1 = self.extract_segments(content1, min_length)
        segments2 = self.extract_segments(content2, min_length)
        duplicates = []
        
        for seg1 in segments1:
            for seg2 in segments2:
                similarity = self.calculate_similarity(seg1, seg2)
                if similarity >= self.threshold:
                    duplicates.append({
                        "chapter1": chapter1_info,
                        "chapter2": chapter2_info,
                        "segment1": seg1[:100] + "..." if len(seg1) > 100 else seg1,
                        "segment2": seg2[:100] + "..." if len(seg2) > 100 else seg2,
                        "similarity": round(similarity * 100, 1)
                    })
        
        return duplicates
    
    async def check_chapter(self, chapter_id: str, db: AsyncSession) -> Dict[str, Any]:
        """检测单章节内部重复"""
        result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
        chapter = result.scalar_one_or_none()
        
        if not chapter or not chapter.content:
            return {"error": "章节不存在或内容为空"}
        
        duplicates = self.find_duplicates_in_chapter(chapter.content)
        
        return {
            "chapter_id": chapter_id,
            "chapter_number": chapter.chapter_number,
            "internal_duplicates": duplicates,
            "duplicate_count": len(duplicates),
            "has_issues": len(duplicates) > 0
        }
    
    async def check_project(self, project_id: str, db: AsyncSession, max_chapters: int = 20) -> Dict[str, Any]:
        """检测项目所有章节间重复（同步版本）"""
        result = await db.execute(
            select(Chapter).where(
                Chapter.project_id == project_id,
                Chapter.content != None,
                Chapter.content != ""
            ).order_by(Chapter.chapter_number).limit(max_chapters)
        )
        chapters = result.scalars().all()
        
        if len(chapters) < 2:
            return {"error": "需要至少2个已完成章节"}
        
        cross_duplicates = []
        internal_issues = []
        
        for ch in chapters:
            internal = self.find_duplicates_in_chapter(ch.content)
            if internal:
                internal_issues.append({
                    "chapter_number": ch.chapter_number,
                    "chapter_title": ch.title,
                    "duplicates": internal[:5]
                })
        
        for i, ch1 in enumerate(chapters):
            for j, ch2 in enumerate(chapters):
                if i >= j:
                    continue
                
                cross = self.find_duplicates_between_chapters(
                    ch1.content, ch2.content,
                    {"number": ch1.chapter_number, "title": ch1.title},
                    {"number": ch2.chapter_number, "title": ch2.title}
                )
                cross_duplicates.extend(cross[:3])
        
        return {
            "project_id": project_id,
            "chapters_checked": len(chapters),
            "internal_issues": internal_issues,
            "cross_chapter_duplicates": cross_duplicates[:20],
            "total_issues": len(internal_issues) + len(cross_duplicates),
            "has_issues": len(internal_issues) > 0 or len(cross_duplicates) > 0
        }
    
    async def check_project_stream(
        self, 
        project_id: str, 
        db: AsyncSession, 
        max_chapters: int = 50
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式检测项目章节间重复"""
        result = await db.execute(
            select(Chapter).where(
                Chapter.project_id == project_id,
                Chapter.content != None,
                Chapter.content != ""
            ).order_by(Chapter.chapter_number).limit(max_chapters)
        )
        chapters = list(result.scalars().all())
        
        if len(chapters) < 2:
            yield {"type": "error", "message": "需要至少2个已完成章节"}
            return
        
        total = len(chapters)
        internal_count = 0
        cross_count = 0
        
        # 阶段1: 检测每章内部重复
        yield {"type": "progress", "phase": "internal", "current": 0, "total": total, "message": "开始检测章节内部重复..."}
        
        for i, ch in enumerate(chapters):
            internal = self.find_duplicates_in_chapter(ch.content)
            if internal:
                internal_count += len(internal)
                yield {
                    "type": "internal",
                    "chapter_number": ch.chapter_number,
                    "chapter_title": ch.title,
                    "duplicates": internal[:5],
                    "count": len(internal)
                }
            
            yield {"type": "progress", "phase": "internal", "current": i + 1, "total": total}
        
        # 阶段2: 检测章节间重复
        pairs_total = total * (total - 1) // 2
        yield {"type": "progress", "phase": "cross", "current": 0, "total": pairs_total, "message": "开始检测章节间重复..."}
        
        pair_count = 0
        for i, ch1 in enumerate(chapters):
            for j, ch2 in enumerate(chapters):
                if i >= j:
                    continue
                
                pair_count += 1
                cross = self.find_duplicates_between_chapters(
                    ch1.content, ch2.content,
                    {"number": ch1.chapter_number, "title": ch1.title},
                    {"number": ch2.chapter_number, "title": ch2.title}
                )
                
                if cross:
                    cross_count += len(cross)
                    yield {
                        "type": "cross",
                        "chapter1": {"number": ch1.chapter_number, "title": ch1.title},
                        "chapter2": {"number": ch2.chapter_number, "title": ch2.title},
                        "duplicates": cross[:3],
                        "count": len(cross)
                    }
                
                if pair_count % 10 == 0:
                    yield {"type": "progress", "phase": "cross", "current": pair_count, "total": pairs_total}
        
        # 完成
        yield {
            "type": "complete",
            "project_id": project_id,
            "chapters_checked": total,
            "internal_issues_count": internal_count,
            "cross_issues_count": cross_count,
            "total_issues": internal_count + cross_count,
            "has_issues": internal_count > 0 or cross_count > 0
        }
