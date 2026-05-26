from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from app.core.database import Base

class WeatherRecord(Base):
    """天气记录模型"""
    __tablename__ = "weather_records"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False, index=True)  # 城市
    temperature = Column(Float)  # 温度
    feels_like = Column(Float)  # 体感温度
    humidity = Column(Integer)  # 湿度
    wind_speed = Column(Float)  # 风速
    weather = Column(String(50))  # 天气状况
    weather_code = Column(Integer)  # 天气代码
    description = Column(String(100))  # 天气描述
    aqi = Column(Integer)  # 空气质量指数
    uv_index = Column(Float)  # 紫外线指数
    precipitation_probability = Column(Integer)  # 降雨概率
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<WeatherRecord {self.city} - {self.temperature}°C>"
