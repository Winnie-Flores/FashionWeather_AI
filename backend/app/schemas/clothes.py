from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ClothesBase(BaseModel):
    """衣服基础模型"""
    name: Optional[str] = None
    type: str
    color: Optional[str] = None
    material: Optional[str] = None
    thickness: Optional[str] = None
    style: Optional[str] = None
    season: Optional[str] = None
    formality: Optional[int] = Field(default=3, ge=1, le=5)  # 正式程度 1-5
    gender: Optional[str] = "中性"  # 适用性别
    temperature_min: Optional[int] = None  # 适合最低温度
    temperature_max: Optional[int] = None  # 适合最高温度
    tags: Optional[str] = None
    description: Optional[str] = None

class ClothesCreate(ClothesBase):
    """衣服创建模型"""
    image_url: Optional[str] = None

class ClothesUpdate(BaseModel):
    """衣服更新模型"""
    name: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    thickness: Optional[str] = None
    style: Optional[str] = None
    season: Optional[str] = None
    formality: Optional[int] = Field(default=None, ge=1, le=5)
    gender: Optional[str] = None
    temperature_min: Optional[int] = None
    temperature_max: Optional[int] = None
    tags: Optional[str] = None
    description: Optional[str] = None

class ClothesResponse(ClothesBase):
    """衣服响应模型"""
    id: int
    user_id: int
    image_url: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ClothesListResponse(BaseModel):
    """衣服列表响应模型"""
    items: List[ClothesResponse]
    total: int
    page: int
    page_size: int

class ClothesAnalysis(BaseModel):
    """
    衣服分析结果模型 - 增强版
    包含详细的衣物属性，用于精准推荐
    """
    type: str = Field(description="衣物类型")
    color: str = Field(description="主色调（中文）")
    material: str = Field(description="主要材质")
    thickness: str = Field(description="厚度等级：极薄/薄/中等/厚/加绒/羽绒级")
    style: str = Field(description="风格：休闲/商务/运动/街头/简约/复古等")
    
    # 新增字段
    season: str = Field(default="四季通用", description="适合季节")
    formality: int = Field(default=3, ge=1, le=5, description="正式程度 1-5")
    gender: str = Field(default="中性", description="适用性别")
    temperature_min: int = Field(default=10, description="适合的最低温度(°C)")
    temperature_max: int = Field(default=25, description="适合的最高温度(°C)")
    confidence: float = Field(ge=0, le=1, description="识别置信度 0-1")
    notes: str = Field(default="", description="补充说明")
