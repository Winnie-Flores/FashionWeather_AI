from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(500))  # 头像URL
    gender = Column(String(10))  # 性别
    style_preference = Column(String(50))  # 风格偏好
    bio = Column(Text)  # 个人简介
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系 - 使用字符串引用延迟加载
    clothes = relationship("Clothes", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    outfits = relationship("Outfit", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    
    def __repr__(self):
        return f"<User {self.username}>"
