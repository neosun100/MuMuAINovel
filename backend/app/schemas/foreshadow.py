"""伏笔管理 Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ForeshadowStatus(str, Enum):
    PLANTED = "planted"
    HINTED = "hinted"
    RESOLVED = "resolved"
    ABANDONED = "abandoned"


class ForeshadowType(str, Enum):
    CHARACTER = "character"
    PLOT = "plot"
    ITEM = "item"
    SETTING = "setting"
    RELATIONSHIP = "relationship"


class ForeshadowCreate(BaseModel):
    """创建伏笔"""
    project_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    foreshadow_type: ForeshadowType = ForeshadowType.PLOT
    importance: int = Field(default=5, ge=1, le=10)
    planted_chapter_id: Optional[str] = None
    planted_chapter_number: Optional[int] = None
    planted_content: Optional[str] = None
    resolved_chapter_number: Optional[int] = Field(None, description="预期回收章节号")
    related_characters: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    remind_before_chapters: int = Field(default=5, ge=1, le=50)
    auto_remind: bool = True
    notes: Optional[str] = None


class ForeshadowUpdate(BaseModel):
    """更新伏笔"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    foreshadow_type: Optional[ForeshadowType] = None
    status: Optional[ForeshadowStatus] = None
    importance: Optional[int] = Field(None, ge=1, le=10)
    planted_chapter_id: Optional[str] = None
    planted_chapter_number: Optional[int] = None
    planted_content: Optional[str] = None
    resolved_chapter_id: Optional[str] = None
    resolved_chapter_number: Optional[int] = None
    resolved_content: Optional[str] = None
    related_characters: Optional[List[str]] = None
    related_foreshadows: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    remind_before_chapters: Optional[int] = Field(None, ge=1, le=50)
    auto_remind: Optional[bool] = None
    notes: Optional[str] = None


class ForeshadowResponse(BaseModel):
    """伏笔响应"""
    id: str
    project_id: str
    title: str
    description: str
    foreshadow_type: str
    status: str
    importance: int
    planted_chapter_id: Optional[str] = None
    planted_chapter_number: Optional[int] = None
    planted_content: Optional[str] = None
    planted_at: Optional[datetime] = None
    resolved_chapter_id: Optional[str] = None
    resolved_chapter_number: Optional[int] = None
    resolved_content: Optional[str] = None
    resolved_at: Optional[datetime] = None
    related_characters: List[str] = []
    related_foreshadows: List[str] = []
    tags: List[str] = []
    remind_before_chapters: int = 5
    auto_remind: bool = True
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ForeshadowListResponse(BaseModel):
    """伏笔列表响应"""
    items: List[ForeshadowResponse]
    total: int
    planted_count: int = 0
    resolved_count: int = 0
    pending_count: int = 0  # 待回收数量


class ForeshadowReminder(BaseModel):
    """伏笔提醒"""
    foreshadow_id: str
    title: str
    description: str
    planted_chapter_number: int
    expected_resolve_chapter: int
    current_chapter: int
    chapters_remaining: int
    importance: int
    related_characters: List[str] = []


class ForeshadowReminderResponse(BaseModel):
    """伏笔提醒响应"""
    reminders: List[ForeshadowReminder]
    total: int


class ResolveForeshadowRequest(BaseModel):
    """回收伏笔请求"""
    resolved_chapter_id: Optional[str] = None  # 可选，如果提供需要是有效章节ID
    resolved_chapter_number: int
    resolved_content: Optional[str] = None
    notes: Optional[str] = None
