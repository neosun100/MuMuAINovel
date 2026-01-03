"""角色成长轨迹 Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class CharacterGrowthCreate(BaseModel):
    character_id: str
    project_id: str
    chapter_id: Optional[str] = None
    chapter_number: Optional[int] = None
    growth_type: str = Field(..., description="成长类型: ability/relationship/psychology/status")
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    before_state: Optional[str] = None
    after_state: Optional[str] = None
    extra_data: Optional[dict] = None


class CharacterGrowthUpdate(BaseModel):
    growth_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    before_state: Optional[str] = None
    after_state: Optional[str] = None
    chapter_id: Optional[str] = None
    chapter_number: Optional[int] = None
    extra_data: Optional[dict] = None


class CharacterGrowthResponse(BaseModel):
    id: str
    character_id: str
    project_id: str
    chapter_id: Optional[str]
    chapter_number: Optional[int]
    growth_type: str
    title: str
    description: Optional[str]
    before_state: Optional[str]
    after_state: Optional[str]
    extra_data: Optional[dict]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """自定义验证，处理 UUID 转换"""
        if hasattr(obj, '__dict__'):
            data = {
                'id': str(obj.id),
                'character_id': str(obj.character_id),
                'project_id': str(obj.project_id),
                'chapter_id': str(obj.chapter_id) if obj.chapter_id else None,
                'chapter_number': obj.chapter_number,
                'growth_type': obj.growth_type,
                'title': obj.title,
                'description': obj.description,
                'before_state': obj.before_state,
                'after_state': obj.after_state,
                'extra_data': obj.extra_data,
                'created_at': obj.created_at,
                'updated_at': obj.updated_at
            }
            return cls(**data)
        return super().model_validate(obj, **kwargs)


class CharacterGrowthTimeline(BaseModel):
    """角色成长时间线"""
    character_id: str
    character_name: str
    total_records: int
    growth_records: List[CharacterGrowthResponse]
