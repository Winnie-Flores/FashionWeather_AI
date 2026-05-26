from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import logging
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.clothes import Clothes
from app.schemas.outfit import OutfitRecommendation, RecommendationRequest
from app.schemas.clothes import ClothesAnalysis
from app.services.ai_service import ai_service, normalize_clothing_id
from app.services.weather_service import weather_service

router = APIRouter(prefix="/api/ai", tags=["AI"])
logger = logging.getLogger(__name__)


@router.post("/recommend")
async def get_outfit_recommendation(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取穿搭推荐"""
    try:
        # 获取天气信息
        city = request.city or "北京"
        weather = await weather_service.get_weather(city, db)
        
        # 获取用户衣服
        clothes_list = db.query(Clothes).filter(
            Clothes.user_id == current_user.id
        ).all()
        
        # 转换衣服数据，统一 id 为字符串
        clothes_data = [
            normalize_clothing_id({
                "id": c.id,
                "name": c.name or f"{c.color or ''}{c.type or ''}",
                "type": c.type or "",
                "color": c.color or "",
                "material": c.material or "",
                "thickness": c.thickness or "",
                "style": c.style or "",
                "season": c.season or "",
                "image_url": c.image_url or ""
            }, i)
            for i, c in enumerate(clothes_list)
        ]
        
        if not clothes_list:
            # 如果用户没有衣服，返回基于天气的推荐
            recommendation = await ai_service.generate_outfit_recommendation(
                weather=weather,
                clothes=[],
                scene=request.scene or "日常",
                style_preference=request.style_preference or current_user.style_preference or "休闲"
            )
            recommendation.reason = "您的衣橱还没有衣服！这是一套基于当前天气的推荐穿搭：\n" + recommendation.reason
            return {"success": True, "data": recommendation}
        
        # 生成推荐
        logger.info(f"[API] 获取推荐，用户 {current_user.id}，城市 {city}，衣服数量 {len(clothes_data)}")
        recommendation = await ai_service.generate_outfit_recommendation(
            weather=weather,
            clothes=clothes_data,
            scene=request.scene or "日常",
            style_preference=request.style_preference or current_user.style_preference or "休闲",
            user_id=current_user.id  # 传递用户ID用于确定性推荐
        )
        
        return {"success": True, "data": recommendation}
    except Exception as e:
        logger.error(f"[API] 推荐生成失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"推荐生成失败: {str(e)}")

@router.get("/recommend/today")
async def get_today_recommendation(
    city: str = "北京",
    scene: str = "日常",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取今日推荐"""
    try:
        # 获取天气
        weather = await weather_service.get_weather(city, db)
        
        # 获取用户衣服
        clothes_list = db.query(Clothes).filter(
            Clothes.user_id == current_user.id
        ).all()
        
        # 转换衣服数据，统一 id 为字符串
        clothes_data = [
            normalize_clothing_id({
                "id": c.id,
                "name": c.name or f"{c.color or ''}{c.type or ''}",
                "type": c.type or "",
                "color": c.color or "",
                "material": c.material or "",
                "thickness": c.thickness or "",
                "style": c.style or "",
                "season": c.season or "",
                "image_url": c.image_url or ""
            }, i)
            for i, c in enumerate(clothes_list)
        ]
        
        logger.info(f"[API] 今日推荐，用户 {current_user.id}，城市 {city}，衣服数量 {len(clothes_data)}")

        recommendation = await ai_service.generate_outfit_recommendation(
            weather=weather,
            clothes=clothes_data,
            scene=scene,
            style_preference=current_user.style_preference or "休闲",
            user_id=current_user.id  # 传递用户ID用于确定性推荐
        )
        
        # 添加今日日期到推荐
        from datetime import datetime
        recommendation_dict = recommendation.model_dump()
        recommendation_dict["date"] = datetime.now().strftime("%Y年%m月%d日")
        recommendation_dict["weather"] = weather
        
        return {"success": True, "data": OutfitRecommendation(**recommendation_dict)}
    except Exception as e:
        logger.error(f"[API] 今日推荐失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"推荐生成失败: {str(e)}")

@router.get("/recommend/scenes")
async def get_scene_options():
    """获取可选场景"""
    return [
        {"value": "daily", "label": "日常", "icon": "🏠"},
        {"value": "work", "label": "上班", "icon": "💼"},
        {"value": "date", "label": "约会", "icon": "💕"},
        {"value": "sports", "label": "运动", "icon": "🏃"},
        {"value": "party", "label": "聚会", "icon": "🎉"},
        {"value": "travel", "label": "出行", "icon": "✈️"},
    ]

@router.get("/recommend/styles")
async def get_style_options():
    """获取可选风格"""
    return [
        {"value": "casual", "label": "休闲", "description": "轻松舒适的日常风格"},
        {"value": "business", "label": "商务", "description": "正式专业的职场风格"},
        {"value": "sports", "label": "运动", "description": "活力四射的运动风格"},
        {"value": "street", "label": "街头", "description": "个性十足的街头风格"},
        {"value": "minimalist", "label": "简约", "description": "简洁大方的极简风格"},
        {"value": "vintage", "label": "复古", "description": "怀旧经典的复古风格"},
    ]
