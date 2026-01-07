"""章节优化记录数据模型"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid


class ChapterRefinement(Base):
    """章节优化记录表"""
    __tablename__ = "chapter_refinements"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="CASCADE"), index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    chapter_number = Column(Integer, comment="章节序号")
    
    # 版本管理
    version = Column(Integer, default=1, comment="优化版本号")
    
    # 原始内容（永久保留）
    original_content = Column(Text, comment="原始内容")
    original_word_count = Column(Integer, comment="原始字数")
    
    # 三段分段结果
    segment1_original = Column(Text, comment="第1段原文")
    segment1_refined = Column(Text, comment="第1段优化后")
    segment1_word_count = Column(Integer, comment="第1段优化后字数")
    
    segment2_original = Column(Text, comment="第2段原文")
    segment2_refined = Column(Text, comment="第2段优化后")
    segment2_word_count = Column(Integer, comment="第2段优化后字数")
    
    segment3_original = Column(Text, comment="第3段原文")
    segment3_refined = Column(Text, comment="第3段优化后")
    segment3_word_count = Column(Integer, comment="第3段优化后字数")
    
    # 最终合并内容
    refined_content = Column(Text, comment="优化后完整内容")
    refined_word_count = Column(Integer, comment="优化后总字数")
    
    # 模型信息
    model_used = Column(String(100), comment="使用的模型")
    
    # 状态: pending / segment1 / segment2 / segment3 / merging / completed / failed
    status = Column(String(20), default="pending", index=True, comment="优化状态")
    current_segment = Column(Integer, default=0, comment="当前处理段落")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 审核状态
    review_status = Column(String(20), nullable=True, comment="审核状态: approved/rejected/pending")
    review_comment = Column(Text, nullable=True, comment="审核备注")
    reviewed_at = Column(DateTime, nullable=True, comment="审核时间")
    
    def __repr__(self):
        return f"<ChapterRefinement(id={self.id}, chapter_number={self.chapter_number}, status={self.status})>"
