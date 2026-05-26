from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OutfitBase(BaseModel):
    """穿搭基础模型"""
    name: Optional[str] = None
    scene: Optional[str] = None
    weather_condition: Optional[str] = None
    score: Optional[float] = None
    reason: Optional[str] = None

class OutfitCreate(OutfitBase):
    """穿搭创建模型"""
    top_id: Optional[int] = None
    pants_id: Optional[int] = None
    shoes_id: Optional[int] = None
    jacket_id: Optional[int] = None
    accessory_ids: Optional[str] = None

class OutfitResponse(OutfitBase):
    """穿搭响应模型"""
    id: int
    user_id: int
    top_id: Optional[int] = None
    pants_id: Optional[int] = None
    shoes_id: Optional[int] = None
    jacket_id: Optional[int] = None
    accessory_ids: Optional[str] = None
    is_favorite: int
    times_worn: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class OutfitItem(BaseModel):
    """穿搭单品模型"""
    id: int
    name: str
    type: str
    color: str
    image_url: str

class OutfitRecommendation(BaseModel):
    """穿搭推荐模型"""
    id: Optional[str] = None  # UUID 字符串，用于收藏识别
    top: Optional[OutfitItem] = None
    pants: Optional[OutfitItem] = None
    shoes: Optional[OutfitItem] = None
    jacket: Optional[OutfitItem] = None
    accessories: List[OutfitItem] = []
    reason: str
    score: float
    scene: str
    tips: List[str] = []

class RecommendationRequest(BaseModel):
    """推荐请求模型"""
    city: Optional[str] = None
    temperature: Optional[float] = None
    weather: Optional[str] = None
    scene: Optional[str] = None
    style_preference: Optional[str] = None
