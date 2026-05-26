"""
QWeatherService - 和风天气服务
正确实现：城市名 -> LocationID -> 天气数据
"""
import httpx
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.geo_service import geo_service


class QWeatherService:
    """和风天气服务 - 必须先获取LocationID才能查询天气"""
    
    # 和风天气 API 配置 - 使用正确的API Host
    WEATHER_API_HOST = "https://pu3qqt4yxn.re.qweatherapi.com"
    API_KEY = None
    
    def __init__(self):
        self.api_key = getattr(settings, 'WEATHER_API_KEY', None) or getattr(settings, 'HEFENG_API_KEY', None)
        self.API_KEY = self.api_key
    
    async def _get_location_id(self, city: str) -> Optional[str]:
        """获取城市的 LocationID"""
        return await geo_service.get_location_id(city)
    
    async def get_weather(self, city: str, db: Session) -> dict:
        """
        获取当前天气 - 正确流程：
        1. 调用 GeoService 获取 LocationID
        2. 使用 LocationID 查询天气
        """
        if not self.api_key:
            raise ValueError("未配置和风天气 API Key，请检查 .env 文件中的 WEATHER_API_KEY")
        
        # 第一步：获取 LocationID
        location_id = await self._get_location_id(city)
        if not location_id:
            raise ValueError(f"无法获取城市 {city} 的 LocationID，请确认城市名称正确")
        
        print(f"[QWeatherService] 使用 LocationID: {location_id} 查询天气")
        
        # 第二步：使用 LocationID 查询天气
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                url = f"{self.WEATHER_API_HOST}/v7/weather/now"
                params = {
                    "location": location_id,
                    "key": self.api_key
                }
                
                response = await client.get(url, params=params)
                data = response.json()
                
                print(f"[QWeatherService] API返回: {data}")
                
                if data.get("code") != "200":
                    raise ValueError(f"天气API错误: {data.get('code')} - {data.get('message', '未知错误')}")
                
                now = data.get("now", {})
                
                weather_data = {
                    "city": city,
                    "location_id": location_id,
                    "temperature": int(float(now.get("temp", 0))),
                    "feels_like": int(float(now.get("feelsLike", 0))),
                    "humidity": int(float(now.get("humidity", 0))),
                    "wind_speed": float(now.get("windSpeed", 0)),
                    "wind_dir": now.get("windDir", ""),
                    "weather": now.get("text", ""),
                    "weather_code": int(now.get("icon", 100)),
                    "description": now.get("text", ""),
                    "aqi": int(float(now.get("airScore", 50))),
                    "uv_index": 5.0,
                    "precipitation_probability": int(float(now.get("precip", 0))),
                    "visibility": float(now.get("vis", 10)),
                    "pressure": float(now.get("pressure", 1013)),
                    "update_time": data.get("updateTime", ""),
                }
                
                return weather_data
                
        except httpx.TimeoutException:
            raise ValueError("天气API请求超时，请检查网络连接")
        except httpx.RequestError as e:
            raise ValueError(f"天气API请求失败: {str(e)}")
    
    async def get_forecast(self, city: str, days: int = 7) -> List[dict]:
        """
        获取天气预报 - 正确流程
        """
        if not self.api_key:
            raise ValueError("未配置和风天气 API Key")
        
        location_id = await self._get_location_id(city)
        if not location_id:
            raise ValueError(f"无法获取城市 {city} 的 LocationID")
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                url = f"{self.WEATHER_API_HOST}/v7/weather/7d"
                params = {
                    "location": location_id,
                    "key": self.api_key
                }
                
                print(f"[QWeatherService] 预报查询: {city} ({location_id})")
                response = await client.get(url, params=params)
                data = response.json()
                
                if data.get("code") != "200":
                    raise ValueError(f"预报API错误: {data.get('code')}")
                
                forecasts = []
                for day in data.get("daily", []):
                    forecasts.append({
                        "date": day.get("fxDate", ""),
                        "temperature_max": int(day.get("tempMax", 0)),
                        "temperature_min": int(day.get("tempMin", 0)),
                        "weather": day.get("textDay", ""),
                        "weather_night": day.get("textNight", ""),
                        "weather_code": int(day.get("iconDay", 100)),
                        "weather_code_night": int(day.get("iconNight", 100)),
                        "precipitation_probability": int(day.get("pop", 0)),
                        "humidity": int(day.get("humidity", 50)),
                        "wind_speed": float(day.get("windSpeedDay", 0)),
                        "wind_dir": day.get("windDirDay", ""),
                        "sunrise": day.get("sunrise", ""),
                        "sunset": day.get("sunset", ""),
                        "moonrise": day.get("moonrise", ""),
                        "moonset": day.get("moonset", ""),
                        "moon_phase": day.get("moonPhase", ""),
                    })
                
                return forecasts[:days]
                
        except Exception as e:
            print(f"[QWeatherService] 预报查询异常: {e}")
            raise
    
    async def get_hourly_forecast(self, city: str, hours: int = 24) -> List[dict]:
        """获取逐小时预报 - 正确流程"""
        if not self.api_key:
            raise ValueError("未配置和风天气 API Key")
        
        location_id = await self._get_location_id(city)
        if not location_id:
            raise ValueError(f"无法获取城市 {city} 的 LocationID")
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                url = f"{self.WEATHER_API_HOST}/v7/weather/24h"
                params = {
                    "location": location_id,
                    "key": self.api_key
                }
                
                response = await client.get(url, params=params)
                data = response.json()
                
                if data.get("code") != "200":
                    raise ValueError(f"逐时API错误: {data.get('code')}")
                
                hourly = []
                for hour in data.get("hourly", []):
                    fx_time = hour.get("fxTime", "")
                    hourly.append({
                        "hour": fx_time[11:16] if fx_time else "00:00",
                        "full_time": fx_time,
                        "temperature": int(hour.get("temp", 0)),
                        "feels_like": int(hour.get("feelsLike", 0)),
                        "weather": hour.get("text", ""),
                        "weather_code": int(hour.get("icon", 100)),
                        "precipitation_probability": int(hour.get("pop", 0)),
                        "humidity": int(hour.get("humidity", 50)),
                        "wind_speed": float(hour.get("windSpeed", 0)),
                        "wind_dir": hour.get("windDir", ""),
                    })
                
                return hourly[:hours]
                
        except Exception as e:
            print(f"[QWeatherService] 逐时查询异常: {e}")
            raise
    
    async def get_air_quality(self, city: str) -> dict:
        """获取空气质量 - 正确流程"""
        if not self.api_key:
            raise ValueError("未配置和风天气 API Key")
        
        location_id = await self._get_location_id(city)
        if not location_id:
            raise ValueError(f"无法获取城市 {city} 的 LocationID")
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                url = f"{self.WEATHER_API_HOST}/v7/air/now"
                params = {
                    "location": location_id,
                    "key": self.api_key
                }
                
                response = await client.get(url, params=params)
                data = response.json()
                
                if data.get("code") != "200":
                    return {
                        "aqi": 50,
                        "level": "良",
                        "pm2_5": 0,
                        "pm10": 0,
                        "so2": 0,
                        "no2": 0,
                        "co": 0,
                        "o3": 0,
                    }
                
                now = data.get("now", {})
                aqi = int(now.get("aqi", 50))
                
                return {
                    "aqi": aqi,
                    "level": self._get_aqi_level(aqi),
                    "pm2_5": float(now.get("pm2p5", 0)),
                    "pm10": float(now.get("pm10", 0)),
                    "so2": float(now.get("so2", 0)),
                    "no2": float(now.get("no2", 0)),
                    "co": float(now.get("co", 0)),
                    "o3": float(now.get("o3", 0)),
                    "main_pollutant": now.get("category", ""),
                }
                
        except Exception as e:
            print(f"[QWeatherService] AQI查询异常: {e}")
            return {"aqi": 50, "level": "良"}
    
    def _get_aqi_level(self, aqi: int) -> str:
        """AQI等级"""
        if aqi <= 50:
            return "优"
        elif aqi <= 100:
            return "良"
        elif aqi <= 150:
            return "轻度污染"
        elif aqi <= 200:
            return "中度污染"
        elif aqi <= 300:
            return "重度污染"
        else:
            return "严重污染"
    
    def get_aqi_info(self, aqi: int) -> dict:
        """获取空气质量详细信息"""
        if aqi <= 50:
            return {
                "level": "优",
                "description": "空气质量令人满意，基本无空气污染",
                "main_pollutant": "—",
                "advice": "各类人群可正常活动"
            }
        elif aqi <= 100:
            return {
                "level": "良",
                "description": "空气质量可接受，某些污染物可能对极少数异常敏感人群健康有较弱影响",
                "main_pollutant": "PM2.5",
                "advice": "极少数异常敏感人群应减少户外活动"
            }
        elif aqi <= 150:
            return {
                "level": "轻度污染",
                "description": "易感人群症状有轻度加剧，健康人群出现刺激症状",
                "main_pollutant": "PM2.5",
                "advice": "儿童、老年人及心脏病、呼吸系统疾病患者应减少长时间、高强度的户外锻炼"
            }
        elif aqi <= 200:
            return {
                "level": "中度污染",
                "description": "进一步加剧易感人群症状，可能对心脏、呼吸系统有影响",
                "main_pollutant": "PM2.5",
                "advice": "儿童、老年人及心脏病、呼吸系统疾病患者应避免长时间、高强度的户外锻炼"
            }
        else:
            return {
                "level": "重度污染",
                "description": "心脏病和肺病患者症状显著加剧，运动耐受力降低，健康人群普遍出现症状",
                "main_pollutant": "PM2.5",
                "advice": "儿童、老年人和病人应停留在室内，避免体力消耗，一般人群应避免户外活动"
            }


# 全局实例
qweather_service = QWeatherService()
