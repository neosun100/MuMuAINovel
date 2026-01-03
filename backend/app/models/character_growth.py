"""角色成长轨迹模型"""
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class CharacterGrowth(Base):
    """角色成长记录"""
    __tablename__ = "character_growth"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(String(255), nullable=False, index=True)
    project_id = Column(String(255), nullable=False, index=True)
    chapter_id = Column(String(255), nullable=True)
    chapter_number = Column(Integer, nullable=True)
    
    # 成长类型: ability(能力), relationship(关系), psychology(心理), status(状态)
    growth_type = Column(String(50), nullable=False, index=True)
    
    # 成长内容
    title = Column(String(200), nullable=False)  # 简短标题
    description = Column(Text, nullable=True)  # 详细描述
    before_state = Column(Text, nullable=True)  # 变化前状态
    after_state = Column(Text, nullable=True)  # 变化后状态
    
    # 额外数据 (JSON)
    extra_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
