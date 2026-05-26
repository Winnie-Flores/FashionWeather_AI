from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from app.core.database import Base


class FavoriteOutfit(Base):
    """收藏穿搭模型"""
    __tablename__ = "favorite_outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    outfit_id = Column(String(100), nullable=False, index=True)  # UUID 字符串
    outfit_data = Column(JSON, nullable=False)  # 完整穿搭数据
    scene = Column(String(50))  # 场景
    weather = Column(String(100))  # 天气
    temperature = Column(String(20))  # 温度
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FavoriteOutfit {self.outfit_id}>"
