from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Outfit(Base):
    """穿搭记录模型"""
    __tablename__ = "outfits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100))  # 穿搭名称
    top_id = Column(Integer, ForeignKey("clothes.id"))  # 上衣ID
    pants_id = Column(Integer, ForeignKey("clothes.id"))  # 裤子ID
    shoes_id = Column(Integer, ForeignKey("clothes.id"))  # 鞋子ID
    jacket_id = Column(Integer, ForeignKey("clothes.id"))  # 外套ID
    accessory_ids = Column(Text)  # 配饰ID列表，JSON格式
    scene = Column(String(50))  # 场景
    weather_condition = Column(String(100))  # 天气条件
    score = Column(Float, default=0.0)  # 评分
    reason = Column(Text)  # 推荐理由
    is_favorite = Column(Integer, default=0)  # 是否收藏
    times_worn = Column(Integer, default=0)  # 穿着次数
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="outfits")
    
    def __repr__(self):
        return f"<Outfit {self.name}>"
