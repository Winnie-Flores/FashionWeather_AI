from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatMessage
from app.models.clothes import Clothes
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.smart_chat_service import smart_chat_service
from app.services.qweather_service import qweather_service
from app.services.intent_parser import weather_intent_parser

router = APIRouter(prefix="/api/chat", tags=["聊天"])

# 对话历史内存缓存（生产环境应使用 Redis）
conversation_cache = {}  # {user_id: [{"role": "user/assistant", "content": "..."}]}


def get_conversation_history(user_id: int, limit: int = 10) -> List[dict]:
    """获取用户的对话历史"""
    if user_id not in conversation_cache:
        conversation_cache[user_id] = []
    return conversation_cache[user_id][-limit:]


def add_to_history(user_id: int, role: str, content: str):
    """添加对话到历史"""
    if user_id not in conversation_cache:
        conversation_cache[user_id] = []
    conversation_cache[user_id].append({
        "role": role,
        "content": content
    })
    # 限制历史长度
    if len(conversation_cache[user_id]) > 20:
        conversation_cache[user_id] = conversation_cache[user_id][-20:]


@router.get("/history")
async def get_chat_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取聊天历史"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

    return [
        {
            "id": m.id,
            "message": m.message,
            "response": m.response,
            "message_type": m.message_type,
            "created_at": m.created_at.isoformat()
        }
        for m in reversed(messages)
    ]


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发送消息 - 智能聊天接口
    
    特性：
    - 基于 LLM 的真正 AI 对话
    - 支持多轮对话记忆
    - 自动获取天气数据
    - 结合用户衣橱数据
    """
    # 解析用户消息意图
    intent_result = weather_intent_parser.parse(request.message)

    # 准备上下文
    context = request.context or {}
    context["user_id"] = current_user.id
    
    # 1. 获取天气数据
    target_city = intent_result.get("city") or context.get("city")
    
    # 尝试从用户资料或请求中获取城市
    if not target_city and request.message:
        # 从消息中提取城市
        import re
        cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都", 
                  "重庆", "西安", "天津", "苏州", "郑州", "长沙", "沈阳", "青岛"]
        for city in cities:
            if city in request.message:
                target_city = city
                break
    
    # 如果还是没有，尝试从用户资料获取
    if not target_city and current_user and hasattr(current_user, 'city'):
        target_city = getattr(current_user, 'city', None) or "北京"
    else:
        target_city = target_city or "北京"
    
    # 获取天气（如果需要）
    if intent_result.get("need_weather") or _should_fetch_weather(request.message):
        try:
            weather = await qweather_service.get_weather(target_city, db)
            context["weather"] = weather
            context["temperature"] = weather.get("temperature")
            context["city"] = target_city
            context["weather_text"] = weather.get("weather", "")
            context["humidity"] = weather.get("humidity", 0)
            context["wind_speed"] = weather.get("wind_speed", 0)
            context["feels_like"] = weather.get("feels_like", weather.get("temperature"))
            context["uv_index"] = weather.get("uv_index", 0)
            context["aqi"] = weather.get("aqi", 0)
        except Exception as e:
            # 天气获取失败不影响对话
            context["weather_error"] = str(e)
    
    # 2. 获取用户衣橱数据
    try:
        user_clothes = db.query(Clothes).filter(
            Clothes.user_id == current_user.id
        ).limit(20).all()
        
        if user_clothes:
            wardrobe_data = []
            for cloth in user_clothes:
                wardrobe_data.append({
                    "id": cloth.id,
                    "name": cloth.name,
                    "type": cloth.type,
                    "color": cloth.color,
                    "style": getattr(cloth, 'style', None),
                    "season": getattr(cloth, 'season', None)
                })
            context["wardrobe"] = wardrobe_data
            context["wardrobe_count"] = len(user_clothes)
    except Exception as e:
        context["wardrobe_error"] = str(e)
    
    # 3. 获取对话历史
    history = get_conversation_history(current_user.id)
    
    # 4. 调用智能聊天服务
    try:
        response_text, suggestions, intent = await smart_chat_service.chat(
            message=request.message,
            context=context,
            history=history
        )
    except Exception as e:
        # 聊天服务异常
        response_text = f"抱歉，服务遇到了一点问题，请稍后再试～"
        suggestions = ["稍后再试", "换个问题"]
        intent = "error"
    
    # 5. 保存聊天记录到数据库
    try:
        chat_message = ChatMessage(
            user_id=current_user.id,
            message=request.message,
            response=response_text,
            context=str(context) if context else None,
            message_type="text"
        )
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        message_id = chat_message.id
    except Exception as e:
        message_id = 0
    
    # 6. 添加到内存历史缓存
    add_to_history(current_user.id, "user", request.message)
    add_to_history(current_user.id, "assistant", response_text)

    return ChatResponse(
        response=response_text,
        message_id=message_id,
        suggestions=suggestions,
        intent=intent
    )


def _should_fetch_weather(message: str) -> bool:
    """判断是否需要获取天气数据"""
    weather_keywords = [
        "天气", "温度", "气温", "冷", "热", "下雨", "下雪", "晴天",
        "穿", "外套", "衣服", "穿搭", "出门", "户外", "今天", "明天",
        "后天", "这周", "带什么", "适合"
    ]
    return any(keyword in message for keyword in weather_keywords)

@router.delete("/history", status_code=204)
async def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空聊天历史"""
    # 清空数据库记录
    db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id
    ).delete()
    db.commit()
    
    # 清空内存缓存
    if current_user.id in conversation_cache:
        del conversation_cache[current_user.id]
    
    return None

@router.get("/suggestions")
async def get_suggestions():
    """
    获取聊天建议 - 根据时间动态生成
    
    生成逻辑：
    - 早上：推荐早餐、天气相关
    - 白天：推荐穿搭、活动相关
    - 晚上：推荐第二天的准备
    """
    from datetime import datetime
    
    hour = datetime.now().hour
    
    # 早上建议（6-11点）
    morning_suggestions = [
        "今天天气怎么样？",
        "今天上班穿什么？",
        "适合户外运动吗？",
        "明天去杭州出差带什么？"
    ]
    
    # 下午建议（11-18点）
    afternoon_suggestions = [
        "今天穿什么合适？",
        "约会穿什么好？",
        "天气会影响穿搭吗？",
        "帮我推荐一套穿搭"
    ]
    
    # 晚上建议（18-24点）
    evening_suggestions = [
        "明天天气怎么样？",
        "明天穿什么？",
        "周末去北京带什么衣服？",
        "下周出差怎么穿搭？"
    ]
    
    if 6 <= hour < 11:
        suggestions = morning_suggestions
    elif 11 <= hour < 18:
        suggestions = afternoon_suggestions
    else:
        suggestions = evening_suggestions
    
    return suggestions
