from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WeatherBase(BaseModel):
    """天气基础模型"""
    city: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    weather: str
    weather_code: int
    description: str
    aqi: int
    uv_index: float
    precipitation_probability: int

class WeatherResponse(WeatherBase):
    """天气响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WeatherForecast(BaseModel):
    """天气预报模型"""
    date: str
    temperature_max: float
    temperature_min: float
    weather: str
    weather_code: int
    precipitation_probability: int
    humidity: int
    wind_speed: float

class WeatherForecastResponse(BaseModel):
    """天气预报列表响应"""
    city: str
    forecast: List[WeatherForecast]

class HourlyWeather(BaseModel):
    """逐时天气模型"""
    hour: str
    temperature: float
    weather: str
    weather_code: int
    precipitation_probability: int

class HourlyWeatherResponse(BaseModel):
    """逐时天气列表响应"""
    city: str
    hourly: List[HourlyWeather]

class AQIResponse(BaseModel):
    """空气质量响应模型"""
    aqi: int
    level: str
    description: str
    main_pollutant: str
    advice: str
