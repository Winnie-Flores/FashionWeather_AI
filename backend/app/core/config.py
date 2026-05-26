from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """系统配置"""
    # 应用配置
    APP_NAME: str = "FashionWeather AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./weatherai.db"
    
    # JWT配置
    SECRET_KEY: str = "fashion-weather-ai-secret-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # AI API配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None  # 阿里云通义千问等兼容API的base_url
    DEEPSEEK_API_KEY: Optional[str] = None
    
    # 天气API配置
    WEATHER_API_KEY: Optional[str] = None
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
