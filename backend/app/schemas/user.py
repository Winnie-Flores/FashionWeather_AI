from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: Optional[EmailStr] = None
    gender: Optional[str] = None
    style_preference: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    """用户创建模型"""
    password: str

class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    style_preference: Optional[str] = None
    bio: Optional[str] = None

class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    avatar: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str

class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[int] = None
