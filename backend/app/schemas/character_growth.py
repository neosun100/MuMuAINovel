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


class CharacterGrowthTimeline(BaseModel):
    """角色成长时间线"""
    character_id: str
    character_name: str
    total_records: int
    growth_records: List[CharacterGrowthResponse]
