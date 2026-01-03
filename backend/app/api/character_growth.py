"""角色成长轨迹 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional, List

from app.database import get_db
from app.api.auth import get_current_user
from app.models.character_growth import CharacterGrowth
from app.models.character import Character
from app.schemas.character_growth import (
    CharacterGrowthCreate,
    CharacterGrowthUpdate,
    CharacterGrowthResponse,
    CharacterGrowthTimeline
)

router = APIRouter(prefix="/api/character-growth", tags=["角色成长"])


@router.post("", response_model=CharacterGrowthResponse)
async def create_growth_record(
    data: CharacterGrowthCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """创建角色成长记录"""
    record = CharacterGrowth(**data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/character/{character_id}", response_model=CharacterGrowthTimeline)
async def get_character_growth_timeline(
    character_id: str,
    growth_type: Optional[str] = Query(None, description="筛选成长类型"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """获取角色成长时间线"""
    # 获取角色信息
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 查询成长记录
    query = select(CharacterGrowth).where(
        CharacterGrowth.character_id == character_id
    )
    if growth_type:
        query = query.where(CharacterGrowth.growth_type == growth_type)
    query = query.order_by(CharacterGrowth.chapter_number.asc().nullslast(), CharacterGrowth.created_at)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return CharacterGrowthTimeline(
        character_id=character_id,
        character_name=character.name,
        total_records=len(records),
        growth_records=records
    )


@router.get("/project/{project_id}")
async def get_project_growth_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """获取项目所有角色成长概览"""
    result = await db.execute(
        select(CharacterGrowth).where(
            CharacterGrowth.project_id == project_id
        ).order_by(CharacterGrowth.chapter_number.asc().nullslast())
    )
    records = result.scalars().all()
    
    # 按角色分组
    by_character = {}
    for r in records:
        cid = str(r.character_id)
        if cid not in by_character:
            by_character[cid] = []
        by_character[cid].append(CharacterGrowthResponse.model_validate(r))
    
    return {
        "project_id": str(project_id),
        "total_records": len(records),
        "characters_count": len(by_character),
        "by_character": by_character
    }


@router.get("/{record_id}", response_model=CharacterGrowthResponse)
async def get_growth_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """获取单条成长记录"""
    result = await db.execute(
        select(CharacterGrowth).where(CharacterGrowth.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.put("/{record_id}", response_model=CharacterGrowthResponse)
async def update_growth_record(
    record_id: str,
    data: CharacterGrowthUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """更新成长记录"""
    result = await db.execute(
        select(CharacterGrowth).where(CharacterGrowth.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    
    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/{record_id}")
async def delete_growth_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """删除成长记录"""
    result = await db.execute(
        delete(CharacterGrowth).where(CharacterGrowth.id == record_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.commit()
    return {"success": True, "message": "删除成功"}
