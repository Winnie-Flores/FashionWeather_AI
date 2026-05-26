from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessageBase(BaseModel):
    """聊天消息基础模型"""
    message: str
    message_type: Optional[str] = "text"

class ChatMessageCreate(ChatMessageBase):
    """聊天消息创建模型"""
    context: Optional[str] = None

class ChatMessageResponse(ChatMessageBase):
    """聊天消息响应模型"""
    id: int
    user_id: int
    response: Optional[str] = None
    context: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    message_id: int
    suggestions: List[str] = []
    intent: Optional[str] = None  # 意图类型
