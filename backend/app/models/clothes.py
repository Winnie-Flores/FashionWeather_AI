from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Clothes(Base):
    """衣服模型 - 增强版"""
    __tablename__ = "clothes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_url = Column(String(500), nullable=False)  # 图片URL
    name = Column(String(100))  # 衣服名称
    type = Column(String(50), nullable=False)  # 类型：T恤、衬衫、卫衣、外套、牛仔裤等
    color = Column(String(50))  # 颜色
    material = Column(String(50))  # 材质
    thickness = Column(String(20))  # 厚度：极薄、薄、中等、厚、加绒、羽绒级
    style = Column(String(50))  # 风格
    season = Column(String(50))  # 季节
    formality = Column(Integer, default=3)  # 正式程度 1-5
    gender = Column(String(20), default="中性")  # 适用性别
    temperature_min = Column(Integer, default=10)  # 适合最低温度
    temperature_max = Column(Integer, default=25)  # 适合最高温度
    tags = Column(Text)  # 自定义标签，JSON格式
    description = Column(Text)  # 描述
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="clothes")
    
    def __repr__(self):
        return f"<Clothes {self.name} - {self.type}>"
