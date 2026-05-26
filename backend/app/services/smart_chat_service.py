"""
智能聊天服务 - 基于 LLM 的真正 AI 对话系统
使用 DeepSeek API 提供自然、专业的穿搭天气助手体验
"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


# ============ 智能 Prompt 模板系统 ============

class ChatPromptEngine:
    """聊天 Prompt 引擎 - 构建智能、专业、自然的对话体验"""
    
    # 系统角色定义
    SYSTEM_PROMPT = """你是一个专业、友好的时尚穿搭与天气助手，叫 **FashionWeather AI**。

## 你的核心能力
1. 根据实时天气和温度，精准推荐穿搭
2. 结合用户的衣橱和偏好，给出个性化建议
3. 理解上下文，进行连续、自然的多轮对话
4. 分析颜色搭配、场景适合度
5. 主动提供实用的出行和穿衣建议

## 回答风格要求
- ✅ 使用自然、亲切的中文，像朋友聊天一样
- ✅ 回答简洁但专业，避免冗长
- ✅ 根据具体温度给出精准建议，不要泛泛而谈
- ✅ 结合用户已有衣服给出推荐，优先推荐衣橱里有的
- ✅ 必要时主动追问，了解用户的具体需求
- ✅ 适当使用表情或语气词，让对话更生动
- ❌ 不要输出 JSON 或代码块
- ❌ 不要机械地列清单，要有温度和解释

## 天气穿搭知识
- 30°C+：极热，穿轻薄透气的T恤、短裤
- 25-30°C：炎热，适合短袖、短裤、裙子
- 20-25°C：温暖舒适，长袖、薄外套即可
- 15-20°C：凉爽，需要外套、卫衣
- 10-15°C：微冷，毛衣、厚外套
- 5-10°C：寒冷，羽绒服、保暖内衣
- 5°C以下：严寒，全副武装的冬季装备

## 额外建议原则
- 下雨：带雨伞，穿防水鞋子，避免帆布鞋
- 大风：穿防风外套，避免过于宽松的衣服
- 紫外线强：涂抹防晒，戴帽子太阳镜
- 高湿度：穿透气衣物，避免棉质内衣
- 早晚温差大：建议叠穿，方便增减衣物"""

    @staticmethod
    def build_messages(
        user_message: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        """
        构建完整的消息列表，包含系统提示、上下文和历史
        
        Args:
            user_message: 用户当前消息
            context: 上下文信息（天气、衣橱等）
            history: 历史对话记录
        
        Returns:
            完整的消息列表，可直接传给 LLM
        """
        messages = []
        
        # 1. 系统提示
        messages.append({
            "role": "system",
            "content": ChatPromptEngine.SYSTEM_PROMPT
        })
        
        # 2. 构建上下文信息
        context_prompt = ChatPromptEngine._build_context_prompt(context)
        if context_prompt:
            messages.append({
                "role": "system",
                "content": f"<当前上下文>\n{context_prompt}\n</当前上下文>"
            })
        
        # 3. 历史对话（如果有）
        if history:
            for item in history[-10:]:  # 限制最近10轮
                if item.get("role") == "user":
                    messages.append({
                        "role": "user",
                        "content": item["content"]
                    })
                elif item.get("role") == "assistant":
                    messages.append({
                        "role": "assistant",
                        "content": item["content"]
                    })
        
        # 4. 当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    @staticmethod
    def _build_context_prompt(context: Dict[str, Any]) -> str:
        """构建上下文提示"""
        parts = []
        
        # 天气信息
        if context.get("weather") and context.get("temperature"):
            weather = context["weather"]
            temp = context["temperature"]
            city = context.get("city", "当前城市")
            humidity = context.get("humidity", 0)
            wind_speed = context.get("wind_speed", 0)
            feels_like = context.get("feels_like", temp)
            uv_index = context.get("uv_index", 0)
            
            weather_desc = f"""【当前天气】
📍 位置：{city}
🌡️ 温度：{temp}°C（体感 {feels_like}°C）
🌤️ 天气：{weather.get('weather', '未知')} {weather.get('icon', '')}
💧 湿度：{humidity}%
🌬️ 风速：{wind_speed} m/s"""
            
            if uv_index and uv_index > 0:
                weather_desc += f"\n☀️ 紫外线：{uv_index}"
            
            # 添加温度感受
            if temp >= 30:
                weather_desc += "\n💭 体感：非常炎热"
            elif temp >= 25:
                weather_desc += "\n💭 体感：炎热"
            elif temp >= 20:
                weather_desc += "\n💭 体感：温暖舒适"
            elif temp >= 15:
                weather_desc += "\n💭 体感：略微凉爽"
            elif temp >= 10:
                weather_desc += "\n💭 体感：较冷"
            else:
                weather_desc += "\n💭 体感：寒冷"
            
            parts.append(weather_desc)
        
        # 衣橱信息
        if context.get("wardrobe"):
            wardrobe = context["wardrobe"]
            if wardrobe:
                wardrobe_desc = "【用户衣橱】\n"
                
                # 按类型分组
                by_type = {}
                for item in wardrobe[:15]:  # 限制展示数量
                    item_type = item.get("type", "其他")
                    if item_type not in by_type:
                        by_type[item_type] = []
                    item_name = item.get("name") or f"{item.get('color', '')}{item_type}"
                    by_type[item_type].append(item_name)
                
                for item_type, items in by_type.items():
                    if items:
                        wardrobe_desc += f"- {item_type}：{', '.join(items)}\n"
                
                if len(wardrobe) > 15:
                    wardrobe_desc += f"\n...（还有 {len(wardrobe) - 15} 件其他衣服）"
                
                parts.append(wardrobe_desc)
        
        # 用户偏好
        if context.get("user_preference"):
            prefs = context["user_preference"]
            pref_desc = "【用户偏好】\n"
            if prefs.get("style"):
                pref_desc += f"- 风格偏好：{prefs['style']}\n"
            if prefs.get("favorite_colors"):
                colors = prefs["favorite_colors"]
                if isinstance(colors, list):
                    pref_desc += f"- 喜欢的颜色：{', '.join(colors)}\n"
                else:
                    pref_desc += f"- 喜欢的颜色：{colors}\n"
            if pref_desc != "【用户偏好】\n":
                parts.append(pref_desc)
        
        # 场景信息
        if context.get("scene"):
            parts.append(f"【当前场景】{context['scene']}")
        
        return "\n\n".join(parts)
    
    @staticmethod
    def generate_suggestions(intent_type: str, context: Dict[str, Any]) -> List[str]:
        """
        根据意图类型和上下文生成建议问题
        
        Args:
            intent_type: 意图类型
            context: 上下文信息
        
        Returns:
            建议问题列表
        """
        base_suggestions = {
            "greeting": [
                "今天天气怎么样？",
                "今天穿什么合适？",
                "帮我推荐一套穿搭"
            ],
            "weather": [
                "今天适合户外运动吗？",
                "明天会下雨吗？",
                "这周温度怎么样？"
            ],
            "fashion": [
                "有什么穿搭建议吗？",
                "约会穿什么好？",
                "上班怎么穿？"
            ],
            "general": [
                "今天穿什么好？",
                "帮我选一套衣服",
                "去约会穿什么？"
            ]
        }
        
        # 根据温度调整建议
        temp = context.get("temperature")
        if temp is not None:
            if temp >= 30:
                base_suggestions["fashion"] = [
                    "太热了，穿什么凉快？",
                    "推荐清凉穿搭",
                    "有什么轻薄的衣服推荐？"
                ]
            elif temp <= 10:
                base_suggestions["fashion"] = [
                    "太冷了，怎么穿暖和？",
                    "推荐保暖穿搭",
                    "有什么厚衣服推荐？"
                ]
        
        return base_suggestions.get(intent_type, base_suggestions["general"])


# ============ LLM API 调用 ============

class LLMProvider:
    """LLM API 提供商 - 支持 DeepSeek 和 OpenAI 兼容接口"""
    
    @staticmethod
    async def call_deepseek(
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        调用 DeepSeek API
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
        
        Returns:
            LLM 回复内容
        """
        api_key = settings.DEEPSEEK_API_KEY
        if not api_key:
            raise ValueError("DeepSeek API Key 未配置")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"DeepSeek API 错误: {response.status_code} - {error_detail}")
                raise Exception(f"DeepSeek API 调用失败: {response.status_code}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    @staticmethod
    async def call_openai_compatible(
        messages: List[Dict[str, str]],
        api_key: str,
        base_url: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        调用 OpenAI 兼容 API（阿里云通义千问等）
        
        Args:
            messages: 消息列表
            api_key: API Key
            base_url: API 基础 URL
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
        
        Returns:
            LLM 回复内容
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"OpenAI 兼容 API 错误: {response.status_code} - {error_detail}")
                raise Exception(f"API 调用失败: {response.status_code}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]


# ============ 意图识别 ============

class IntentRecognizer:
    """用户意图识别器"""
    
    # 意图关键词映射
    INTENT_PATTERNS = {
        "greeting": [
            "你好", "您好", "hi", "hello", "嗨", "嗨嗨", "早上好", "晚上好", "在吗"
        ],
        "weather": [
            "天气", "温度", "气温", "冷不冷", "热不热", "下雨", "下雪", "晴天", 
            "阴天", "紫外线", "风力", "会下雨吗", "会下雪吗", "适合出门吗"
        ],
        "fashion": [
            "穿什么", "穿搭", "衣服", "外套", "推荐", "搭配", "怎么穿", "穿什么好",
            "上班穿", "约会穿", "运动穿", "休闲穿", "正装", "裙子", "裤子",
            "T恤", "卫衣", "毛衣", "羽绒服", "鞋子", "靴子"
        ],
        "outfit_analysis": [
            "这件怎么样", "那个好看吗", "配不配", "颜色", "风格"
        ],
        "plan": [
            "明天", "后天", "下周", "周末", "出游", "旅行", "出差"
        ]
    }
    
    @classmethod
    def recognize(cls, message: str) -> str:
        """
        识别用户意图
        
        Args:
            message: 用户消息
        
        Returns:
            意图类型
        """
        message_lower = message.lower()
        
        # 优先检测问候
        for greeting in cls.INTENT_PATTERNS["greeting"]:
            if greeting in message_lower:
                return "greeting"
        
        # 检测穿搭相关
        for pattern in cls.INTENT_PATTERNS["fashion"]:
            if pattern in message_lower:
                return "fashion"
        
        # 检测天气相关
        for pattern in cls.INTENT_PATTERNS["weather"]:
            if pattern in message_lower:
                return "weather"
        
        # 检测穿搭分析
        for pattern in cls.INTENT_PATTERNS["outfit_analysis"]:
            if pattern in message_lower:
                return "outfit_analysis"
        
        # 检测计划相关
        for pattern in cls.INTENT_PATTERNS["plan"]:
            if pattern in message_lower:
                return "plan"
        
        return "general"
    
    @classmethod
    def extract_city(cls, message: str) -> Optional[str]:
        """从消息中提取城市名"""
        import re
        
        # 常见城市
        cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都", 
            "重庆", "西安", "天津", "苏州", "郑州", "长沙", "沈阳", "青岛",
            "济南", "大连", "哈尔滨", "长春", "昆明", "福州", "厦门", "宁波",
            "合肥", "石家庄", "南昌", "贵阳", "太原", "兰州", "乌鲁木齐"
        ]
        
        for city in cities:
            if city in message:
                return city
        
        # 尝试匹配 "去X" 模式
        match = re.search(r'去([^\s]+?)(?:的话|的话|天气|穿什么|带什么)', message)
        if match:
            potential_city = match.group(1)
            if len(potential_city) >= 2 and len(potential_city) <= 6:
                return potential_city
        
        return None


# ============ 主聊天服务 ============

class SmartChatService:
    """
    智能聊天服务
    
    使用 LLM 提供真正的 AI 对话体验，包括：
    - 自然语言理解
    - 多轮对话记忆
    - 个性化推荐
    - 上下文感知
    """
    
    def __init__(self):
        self.prompt_engine = ChatPromptEngine()
        self.intent_recognizer = IntentRecognizer()
        self.llm_provider = LLMProvider()
    
    async def chat(
        self,
        message: str,
        context: Dict[str, Any] = None,
        history: List[Dict[str, str]] = None
    ) -> tuple[str, List[str], str]:
        """
        处理用户消息并返回 AI 回复
        
        Args:
            message: 用户消息
            context: 上下文信息（天气、衣橱等）
            history: 历史对话记录
        
        Returns:
            (回复内容, 建议问题, 意图类型)
        """
        context = context or {}
        history = history or []
        
        # 1. 意图识别
        intent = self.intent_recognizer.recognize(message)
        
        # 2. 如果消息中提到城市，添加到上下文
        extracted_city = self.intent_recognizer.extract_city(message)
        if extracted_city:
            context["requested_city"] = extracted_city
        
        # 3. 检查是否有可用的 LLM API
        has_deepseek = bool(settings.DEEPSEEK_API_KEY)
        has_openai = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_BASE)
        
        if has_deepseek or has_openai:
            # 使用真正的 LLM
            return await self._chat_with_llm(message, context, history, intent)
        else:
            # 降级到规则引擎
            return self._chat_with_rules(message, context, history, intent)
    
    async def _chat_with_llm(
        self,
        message: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]],
        intent: str
    ) -> tuple[str, List[str], str]:
        """使用 LLM 进行对话"""
        try:
            # 构建消息
            messages = self.prompt_engine.build_messages(message, context, history)
            
            # 调用 LLM
            if settings.DEEPSEEK_API_KEY:
                response = await self.llm_provider.call_deepseek(
                    messages,
                    model="deepseek-chat",
                    temperature=0.7,
                    max_tokens=800
                )
            else:
                response = await self.llm_provider.call_openai_compatible(
                    messages,
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_API_BASE,
                    model="qwen-plus",  # 推荐使用 qwen-plus 或 qwen-max
                    temperature=0.7,
                    max_tokens=800
                )
            
            # 生成建议
            suggestions = self.prompt_engine.generate_suggestions(intent, context)
            
            return response, suggestions, intent
            
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            # 降级到规则引擎
            return self._chat_with_rules(message, context, [], intent)
    
    def _chat_with_rules(
        self,
        message: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]],
        intent: str
    ) -> tuple[str, List[str], str]:
        """使用规则引擎进行对话（降级方案）"""
        temp = context.get("temperature")
        weather = context.get("weather", {})
        weather_text = weather.get("weather", "") if weather else ""
        city = context.get("city", "本地")
        
        # 根据意图生成回复
        if intent == "greeting":
            response = f"你好呀！👋 我是你的时尚穿搭助手。\n\n"
            if temp is not None:
                response += f"今天{city} {temp}°C，{weather_text}，"
                if temp >= 25:
                    response += "天气挺热的，有什么穿搭问题随时问我～"
                elif temp >= 15:
                    response += "天气挺舒服的，穿搭选择很多哦～"
                else:
                    response += "天气有点凉，记得保暖！"
            else:
                response += "有什么穿搭问题可以问我哦～"
            
        elif intent == "weather":
            if temp is not None:
                response = f"今天{city}的天气情况：\n\n"
                response += f"🌡️ 温度：{temp}°C\n"
                response += f"🌤️ 天气：{weather_text}\n"
                
                if temp >= 30:
                    response += "\n今天很热，建议穿清凉一点～"
                elif temp >= 20:
                    response += "\n天气很舒服，穿什么都合适！"
                elif temp >= 10:
                    response += "\n有点凉，记得带件外套～"
                else:
                    response += "\n比较冷，要多穿点哦！"
                
                if "雨" in weather_text:
                    response += "\n🌧️ 今天有雨，出门记得带伞～"
            else:
                response = f"我现在没有{city}的天气数据，你可以告诉我你在哪个城市，或者让我帮你查询～"
        
        elif intent == "fashion":
            if temp is not None:
                if temp >= 30:
                    response = f"今天{city} {temp}°C，很热呢！建议：\n\n"
                    response += "👕 上衣：白色或浅色T恤，背心也行\n"
                    response += "👖 下装：短裤、薄长裤\n"
                    response += "👟 鞋子：凉鞋、透气运动鞋\n"
                    response += "\n材质要选透气的，会舒服很多～"
                    
                elif temp >= 20:
                    response = f"今天{city} {temp}°C，天气舒适！建议：\n\n"
                    response += "👕 上衣：长袖T恤、薄卫衣、衬衫\n"
                    response += "👖 下装：牛仔裤、休闲裤、裙子\n"
                    response += "👟 鞋子：运动鞋、帆布鞋都行\n"
                    response += "\n早晚温差大可以带件薄外套～"
                    
                elif temp >= 10:
                    response = f"今天{city} {temp}°C，有点凉哦！建议：\n\n"
                    response += "👕 上衣：毛衣、厚卫衣、加绒衫\n"
                    response += "👖 下装：加绒裤、厚牛仔裤\n"
                    response += "🧥 外套：风衣、夹克、薄毛衣\n"
                    response += "\n建议叠穿，方便随时增减衣物～"
                    
                else:
                    response = f"今天{city}只有{temp}°C，很冷！建议：\n\n"
                    response += "👕 上衣：保暖内衣+毛衣+厚卫衣\n"
                    response += "👖 下装：加绒裤、保暖裤\n"
                    response += "🧥 外套：羽绒服、厚棉服\n"
                    response += "🧣 其他：围巾、手套、帽子\n"
                    response += "\n全副武装出门，别冻着！"
                
                # 特殊天气提示
                if "雨" in weather_text:
                    response += "\n\n🌧️ 今天有雨，记得带伞，穿防水的鞋子哦～"
                elif "雪" in weather_text:
                    response += "\n\n❄️ 有雪！路面可能滑，穿防滑的鞋子～"
            else:
                response = "想帮你推荐穿搭，但需要知道你在哪里、温度多少～\n\n可以告诉我：\n1. 你在哪个城市？\n2. 或者今天有什么活动？"
        
        else:
            # 通用回复
            response = "我是你的时尚穿搭助手～\n\n"
            response += "可以帮你：\n"
            response += "• 根据天气推荐穿搭\n"
            response += "• 结合你的衣橱给建议\n"
            response += "• 解答穿搭相关问题\n\n"
            response += "有什么想问的尽管说～"
        
        suggestions = self.prompt_engine.generate_suggestions(intent, context)
        return response, suggestions, intent


# 单例实例
smart_chat_service = SmartChatService()
