"""章节数据模型"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Chapter(Base):
    """章节表"""
    __tablename__ = "chapters"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    chapter_number = Column(Integer, nullable=False, comment="章节序号")
    title = Column(String(200), nullable=False, comment="章节标题")
    content = Column(Text, comment="章节内容")
    summary = Column(Text, comment="章节摘要")
    word_count = Column(Integer, default=0, comment="字数统计")
    status = Column(String(20), default="draft", comment="章节状态")
    
    # 大纲关联字段（实现一对多关系）
    outline_id = Column(String(36), ForeignKey("outlines.id", ondelete="SET NULL"), nullable=True, comment="关联的大纲ID")
    sub_index = Column(Integer, default=1, comment="大纲下的子章节序号")
    
    # 大纲展开规划数据（JSON格式）
    expansion_plan = Column(Text, comment="展开规划详情(JSON): 包含key_events, character_focus, emotional_tone等")
    
    # 二次优化状态
    is_refined = Column(Boolean, default=False, index=True, comment="是否已优化")
    refined_at = Column(DateTime, nullable=True, comment="优化时间")
    refinement_id = Column(String(36), nullable=True, comment="关联优化记录ID")
    refinement_model = Column(String(100), nullable=True, comment="优化使用的模型")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, chapter_number={self.chapter_number}, title={self.title}, outline_id={self.outline_id})>"