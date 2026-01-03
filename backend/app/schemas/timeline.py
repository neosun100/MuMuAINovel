"""时间线管理 Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    PLOT = "plot"
    CHARACTER = "character"
    WORLD = "world"
    OTHER = "other"


class TimelineEventCreate(BaseModel):
    """创建时间线事件"""
    project_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: EventType = EventType.PLOT
    story_time: Optional[str] = None
    story_day: Optional[int] = None
    chapter_id: Optional[str] = None
    chapter_number: Optional[int] = None
    related_characters: List[str] = Field(default_factory=list)
    importance: int = Field(default=5, ge=1, le=10)


class TimelineEventUpdate(BaseModel):
    """更新时间线事件"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    story_time: Optional[str] = None
    story_day: Optional[int] = None
    chapter_id: Optional[str] = None
    chapter_number: Optional[int] = None
    related_characters: Optional[List[str]] = None
    importance: Optional[int] = Field(None, ge=1, le=10)


class TimelineEventResponse(BaseModel):
    """时间线事件响应"""
    id: str
    project_id: str
    title: str
    description: Optional[str] = None
    event_type: str
    story_time: Optional[str] = None
    story_day: Optional[int] = None
    chapter_id: Optional[str] = None
    chapter_number: Optional[int] = None
    related_characters: List[str] = []
    importance: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TimelineListResponse(BaseModel):
    """时间线列表响应"""
    items: List[TimelineEventResponse]
    total: int
