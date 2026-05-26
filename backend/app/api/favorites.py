from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.favorite import FavoriteOutfit
from app.schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteListItem
import logging

router = APIRouter(prefix="/api/favorites", tags=["收藏"])
logger = logging.getLogger(__name__)


@router.post("", response_model=dict, status_code=201)
async def add_favorite(
    data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    收藏穿搭推荐（新建独立收藏接口）
    
    直接接收完整穿搭数据，无需先创建历史记录
    """
    try:
        # 检查是否已收藏
        existing = db.query(FavoriteOutfit).filter(
            FavoriteOutfit.user_id == current_user.id,
            FavoriteOutfit.outfit_id == data.outfit_id
        ).first()

        if existing:
            logger.info(f"[收藏] 用户 {current_user.id} 已收藏过 {data.outfit_id}")
            return {"success": True, "message": "已收藏", "favorite_id": existing.id, "is_new": False}

        # 创建新收藏
        favorite = FavoriteOutfit(
            user_id=current_user.id,
            outfit_id=data.outfit_id,
            outfit_data=data.outfit_data,
            scene=data.scene or "",
            weather=data.weather or "",
            temperature=str(data.temperature) if data.temperature else None
        )

        db.add(favorite)
        db.commit()
        db.refresh(favorite)

        logger.info(f"[收藏] 用户 {current_user.id} 成功收藏 {data.outfit_id}")
        return {"success": True, "message": "收藏成功", "favorite_id": favorite.id, "is_new": True}

    except Exception as e:
        db.rollback()
        logger.error(f"[收藏] 收藏失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"收藏失败: {str(e)}")


@router.get("", response_model=List[FavoriteListItem])
async def get_favorites(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取收藏列表"""
    query = db.query(FavoriteOutfit).filter(
        FavoriteOutfit.user_id == current_user.id
    ).order_by(FavoriteOutfit.created_at.desc())

    total = query.count()
    offset = (page - 1) * page_size
    favorites = query.offset(offset).limit(page_size).all()

    # 添加总数到响应头
    return favorites


@router.delete("/{outfit_id}", response_model=dict)
async def remove_favorite(
    outfit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    favorite = db.query(FavoriteOutfit).filter(
        FavoriteOutfit.user_id == current_user.id,
        FavoriteOutfit.outfit_id == outfit_id
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="收藏不存在")

    db.delete(favorite)
    db.commit()

    logger.info(f"[收藏] 用户 {current_user.id} 取消收藏 {outfit_id}")
    return {"success": True, "message": "已取消收藏"}


@router.get("/check/{outfit_id}", response_model=dict)
async def check_favorite(
    outfit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """检查是否已收藏"""
    favorite = db.query(FavoriteOutfit).filter(
        FavoriteOutfit.user_id == current_user.id,
        FavoriteOutfit.outfit_id == outfit_id
    ).first()

    return {"is_favorited": favorite is not None}


@router.get("/stats/count", response_model=dict)
async def get_favorites_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取收藏数量"""
    count = db.query(func.count(FavoriteOutfit.id)).filter(
        FavoriteOutfit.user_id == current_user.id
    ).scalar()

    return {"count": count or 0}
