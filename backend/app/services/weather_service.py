"""
WeatherService - 天气服务（兼容层）
内部使用 QWeatherService 实现
"""
from app.services.qweather_service import qweather_service

# 为了兼容现有代码，导出 qweather_service 的方法
# 实际逻辑在 qweather_service.py 中实现

weather_service = qweather_service
