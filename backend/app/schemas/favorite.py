from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class FavoriteBase(BaseModel):
    """收藏基础模型"""
    pass


class FavoriteCreate(BaseModel):
    """创建收藏请求"""
    outfit_id: str  # 字符串类型的 UUID
    outfit_data: Dict  # 完整穿搭数据
    weather: Optional[str] = None
    scene: Optional[str] = None
    temperature: Optional[float] = None


class FavoriteResponse(BaseModel):
    """收藏响应模型"""
    id: int
    user_id: int
    outfit_id: str
    outfit_data: Dict
    scene: str
    weather: str
    temperature: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteListItem(BaseModel):
    """收藏列表项"""
    id: int
    outfit_id: str
    outfit_data: Dict
    scene: str
    weather: Optional[str] = None
    temperature: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
