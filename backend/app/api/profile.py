from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.clothes import Clothes
from app.models.outfit import Outfit
from app.models.favorite import FavoriteOutfit
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/profile", tags=["个人中心"])


class ProfileStats(BaseModel):
    """用户统计信息"""
    clothes_count: int
    favorites_count: int


class FavoriteItem(BaseModel):
    """收藏穿搭"""
    id: int
    name: str
    scene: str
    score: float
    reason: str
    created_at: datetime
    top_id: Optional[int] = None
    pants_id: Optional[int] = None
    shoes_id: Optional[int] = None
    jacket_id: Optional[int] = None

    class Config:
        from_attributes = True


@router.get("/stats", response_model=ProfileStats)
async def get_profile_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户统计信息"""
    # 统计衣服数量
    clothes_count = db.query(func.count(Clothes.id)).filter(
        Clothes.user_id == current_user.id
    ).scalar()

    # 统计收藏数量（新收藏表 + 旧 Outfit 表的 is_favorite 标记）
    new_favorites_count = db.query(func.count(FavoriteOutfit.id)).filter(
        FavoriteOutfit.user_id == current_user.id
    ).scalar()
    
    old_favorites_count = db.query(func.count(Outfit.id)).filter(
        Outfit.user_id == current_user.id,
        Outfit.is_favorite == 1
    ).scalar()
    
    favorites_count = (new_favorites_count or 0) + (old_favorites_count or 0)

    return ProfileStats(
        clothes_count=clothes_count or 0,
        favorites_count=favorites_count or 0
    )


@router.get("/favorites", response_model=List[FavoriteItem])
async def get_favorites(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取收藏的穿搭列表"""
    query = db.query(Outfit).filter(
        Outfit.user_id == current_user.id,
        Outfit.is_favorite == 1
    ).order_by(Outfit.created_at.desc())

    total = query.count()
    offset = (page - 1) * page_size
    favorites = query.offset(offset).limit(page_size).all()

    return favorites


@router.post("/favorites/{outfit_id}", status_code=201)
async def add_favorite(
    outfit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加收藏"""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="穿搭不存在")

    outfit.is_favorite = 1
    db.commit()

    return {"success": True, "message": "收藏成功"}


@router.delete("/favorites/{outfit_id}", status_code=200)
async def remove_favorite(
    outfit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="穿搭不存在")

    outfit.is_favorite = 0
    db.commit()

    return {"success": True, "message": "已取消收藏"}


@router.post("/quick-favorite", response_model=dict)
async def quick_favorite_outfit(
    outfit_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    快速收藏穿搭推荐（不保存到数据库，只是标记收藏）
    返回一个临时的收藏ID
    """
    import uuid
    temp_id = str(uuid.uuid4())

    return {
        "success": True,
        "temp_id": temp_id,
        "message": "穿搭已收藏"
    }


@router.get("/favorite-clothes/{clothes_id}", response_model=Optional[dict])
async def get_clothes_for_favorite(
    clothes_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取衣服详情用于穿搭卡片展示"""
    clothes = db.query(Clothes).filter(
        Clothes.id == clothes_id,
        Clothes.user_id == current_user.id
    ).first()

    if not clothes:
        return None

    return {
        "id": clothes.id,
        "name": clothes.name or f"{clothes.color or ''}{clothes.type or ''}",
        "type": clothes.type or "",
        "color": clothes.color or "",
        "image_url": clothes.image_url or ""
    }
