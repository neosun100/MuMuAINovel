"""伏笔管理数据模型"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Float, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class ForeshadowStatus(str, enum.Enum):
    """伏笔状态"""
    PLANTED = "planted"      # 已埋下
    HINTED = "hinted"        # 已暗示（部分揭示）
    RESOLVED = "resolved"    # 已回收
    ABANDONED = "abandoned"  # 已放弃


class ForeshadowType(str, enum.Enum):
    """伏笔类型"""
    CHARACTER = "character"      # 角色相关（身世、能力、秘密）
    PLOT = "plot"               # 情节相关（事件、阴谋）
    ITEM = "item"               # 物品相关（道具、信物）
    SETTING = "setting"         # 设定相关（世界观、规则）
    RELATIONSHIP = "relationship"  # 关系相关（人物关系变化）


class Foreshadow(Base):
    """伏笔表 - 追踪故事中的伏笔埋设与回收"""
    __tablename__ = "foreshadows"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 基本信息
    title = Column(String(200), nullable=False, comment="伏笔标题/简述")
    description = Column(Text, nullable=False, comment="伏笔详细描述")
    foreshadow_type = Column(String(50), default=ForeshadowType.PLOT.value, comment="伏笔类型")
    
    # 状态追踪
    status = Column(String(20), default=ForeshadowStatus.PLANTED.value, index=True, comment="伏笔状态")
    importance = Column(Integer, default=5, comment="重要程度 1-10")
    
    # 埋设信息
    planted_chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="SET NULL"), comment="埋设章节ID")
    planted_chapter_number = Column(Integer, comment="埋设章节号")
    planted_content = Column(Text, comment="埋设时的原文摘录")
    planted_at = Column(DateTime, server_default=func.now(), comment="埋设时间")
    
    # 回收信息
    resolved_chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="SET NULL"), comment="回收章节ID")
    resolved_chapter_number = Column(Integer, comment="预期/实际回收章节号")
    resolved_content = Column(Text, comment="回收时的原文摘录")
    resolved_at = Column(DateTime, comment="回收时间")
    
    # 关联信息
    related_characters = Column(JSON, default=list, comment="关联角色ID列表")
    related_foreshadows = Column(JSON, default=list, comment="关联伏笔ID列表（伏笔链）")
    tags = Column(JSON, default=list, comment="标签列表")
    
    # 提醒设置
    remind_before_chapters = Column(Integer, default=5, comment="提前N章提醒回收")
    auto_remind = Column(Integer, default=1, comment="是否自动提醒: 0=否, 1=是")
    
    # 备注
    notes = Column(Text, comment="作者备注")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "foreshadow_type": self.foreshadow_type,
            "status": self.status,
            "importance": self.importance,
            "planted_chapter_id": self.planted_chapter_id,
            "planted_chapter_number": self.planted_chapter_number,
            "planted_content": self.planted_content,
            "planted_at": self.planted_at.isoformat() if self.planted_at else None,
            "resolved_chapter_id": self.resolved_chapter_id,
            "resolved_chapter_number": self.resolved_chapter_number,
            "resolved_content": self.resolved_content,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "related_characters": self.related_characters or [],
            "related_foreshadows": self.related_foreshadows or [],
            "tags": self.tags or [],
            "remind_before_chapters": self.remind_before_chapters,
            "auto_remind": self.auto_remind,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
