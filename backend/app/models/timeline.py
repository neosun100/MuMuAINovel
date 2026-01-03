"""时间线管理模型"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class TimelineEvent(Base):
    """时间线事件"""
    __tablename__ = "timeline_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 事件信息
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_type = Column(String(50), default="plot")  # plot/character/world/other
    
    # 时间信息
    story_time = Column(String(100))  # 故事内时间描述，如 "第一年春天"
    story_day = Column(Integer)  # 故事内第几天（可选，用于精确排序）
    
    # 关联信息
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="SET NULL"))
    chapter_number = Column(Integer)
    related_characters = Column(JSON, default=list)  # 相关角色ID列表
    
    # 重要性
    importance = Column(Integer, default=5)  # 1-10
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "event_type": self.event_type,
            "story_time": self.story_time,
            "story_day": self.story_day,
            "chapter_id": self.chapter_id,
            "chapter_number": self.chapter_number,
            "related_characters": self.related_characters or [],
            "importance": self.importance,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
