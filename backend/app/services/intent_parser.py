"""天气意图解析器 - 从用户消息中识别城市和天气查询"""
from typing import Optional, Tuple, Dict, Any


class WeatherIntentParser:
    """解析用户天气相关查询的意图"""

    # 支持的城市列表（中英文）
    SUPPORTED_CITIES = {
        # 中国城市
        "北京": ["北京", "beijing", "bj", "北"],
        "上海": ["上海", "shanghai", "sh", "沪"],
        "广州": ["广州", "guangzhou", "gz", "穗"],
        "深圳": ["深圳", "shenzhen", "sz", "深"],
        "成都": ["成都", "chengdu", "cd"],
        "杭州": ["杭州", "hangzhou", "hz", "杭"],
        "武汉": ["武汉", "wuhan", "wh"],
        "西安": ["西安", "xian", "xa", "西安", "Xi'an"],
        "重庆": ["重庆", "chongqing", "cq", "渝"],
        "南京": ["南京", "nanjing", "nj"],
        "天津": ["天津", "tianjin", "tj"],
        "苏州": ["苏州", "suzhou", "su"],
        "厦门": ["厦门", "xiamen", "xm"],
        "长沙": ["长沙", "changsha", "cs"],
        "青岛": ["青岛", "qingdao", "qd"],
        "大连": ["大连", "dalian", "dl"],
        "沈阳": ["沈阳", "shenyang", "sy"],
        "哈尔滨": ["哈尔滨", "harbin", "heb"],
        "长春": ["长春", "changchun", "cc"],
        "郑州": ["郑州", "zhengzhou", "zz"],
        "济南": ["济南", "jinan", "jn"],
        "福州": ["福州", "fuzhou", "fz"],
        "昆明": ["昆明", "kunming", "km"],
        "贵阳": ["贵阳", "guiyang", "gy"],
        "太原": ["太原", "taiyuan", "ty"],
        "石家庄": ["石家庄", "shijiazhuang", "sjz"],
        "兰州": ["兰州", "lanzhou", "lz"],
        "南宁": ["南宁", "nanning", "nn"],
        "海口": ["海口", "haikou", "hk"],
        "乌鲁木齐": ["乌鲁木齐", "urumqi", "wlmq"],
        "呼和浩特": ["呼和浩特", "hohhot", "hhht"],
        # 国际城市
        "东京": ["东京", "tokyo", "日本"],
        "纽约": ["纽约", "new york", "nyc", "美国纽约"],
        "伦敦": ["伦敦", "london", "英国"],
        "巴黎": ["巴黎", "paris", "法国"],
        "悉尼": ["悉尼", "sydney", "澳大利亚"],
        "首尔": ["首尔", "seoul", "韩国"],
        "新加坡": ["新加坡", "singapore"],
        "曼谷": ["曼谷", "bangkok", "泰国"],
        "洛杉矶": ["洛杉矶", "los angeles", "la", "美国洛杉矶"],
        "旧金山": ["旧金山", "san francisco", "sf", "美国旧金山"],
        "温哥华": ["温哥华", "vancouver", "加拿大"],
        "多伦多": ["多伦多", "toronto", "加拿大"],
        "柏林": ["柏林", "berlin", "德国"],
        "东京": ["东京", "tokyo", "日本"],
        "大阪": ["大阪", "osaka", "日本大阪"],
        "罗马": ["罗马", "rome", "意大利"],
        "米兰": ["米兰", "milan", "意大利"],
        "迪拜": ["迪拜", "dubai", "阿联酋"],
        "莫斯科": ["莫斯科", "moscow", "俄罗斯"],
    }

    def __init__(self):
        # 构建城市名到标准名称的映射
        self.city_aliases = {}
        for city, aliases in self.SUPPORTED_CITIES.items():
            for alias in aliases:
                self.city_aliases[alias.lower()] = city

    def extract_city(self, message: str) -> Optional[str]:
        """从消息中提取城市名称"""
        message_lower = message.lower()

        # 优先匹配更长的别名（避免"京"单独匹配导致误匹配）
        sorted_aliases = sorted(self.city_aliases.keys(), key=len, reverse=True)

        for alias in sorted_aliases:
            # 确保是完整匹配，而不是子串
            if alias in message_lower:
                # 检查是否是独立词（前后有空格、标点或开头/结尾）
                start = message_lower.find(alias)
                end = start + len(alias)

                is_word_boundary = (
                    (start == 0 or message_lower[start - 1] in ' \t\n,，.。!！?？、:：;；(') and
                    (end == len(message_lower) or message_lower[end] in ' \t\n,，.。!！?？、:：;；)')
                )

                if is_word_boundary or len(alias) >= 2:  # 长别名直接匹配
                    return self.city_aliases[alias]

        return None

    def detect_intent(self, message: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        检测用户意图
        返回: (intent_type, extracted_city, modified_message)
        intent_type: "weather" | "fashion" | "other"
        """
        message_lower = message.lower()

        # 天气相关关键词
        weather_keywords = ["天气", "温度", "气温", "下雨", "下雪", "晴天", "多云", "weather", "temp", "temperature"]
        # 穿搭相关关键词
        fashion_keywords = ["穿什么", "穿搭", "衣服", "搭配", "外套", "推荐", "outfit", "wear", "dress"]
        # 城市相关关键词
        city_related = ["去", "到", "来", "在", "去", "飞", "旅游", "出差", "旅行"]

        has_weather = any(k in message_lower for k in weather_keywords)
        has_fashion = any(k in message_lower for k in fashion_keywords)

        # 提取城市
        extracted_city = self.extract_city(message)

        # 判断意图
        if has_weather and has_fashion:
            return ("weather_and_fashion", extracted_city, message)
        elif has_weather:
            return ("weather", extracted_city, message)
        elif has_fashion:
            return ("fashion", extracted_city, message)
        elif extracted_city:
            # 提到了城市但没有明确关键词，推断为天气查询
            return ("weather", extracted_city, message)

        return ("other", None, message)

    def parse(self, message: str) -> Dict[str, Any]:
        """
        完整解析消息
        返回解析结果字典
        """
        intent_type, city, modified_message = self.detect_intent(message)

        return {
            "original_message": message,
            "intent_type": intent_type,
            "city": city,
            "need_weather": intent_type in ["weather", "weather_and_fashion"],
            "need_fashion": intent_type in ["fashion", "weather_and_fashion"],
        }


# 全局实例
weather_intent_parser = WeatherIntentParser()
