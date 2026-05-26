from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Union
from app.core.database import get_db
from app.services.qweather_service import qweather_service
from app.services.geo_service import geo_service
from app.schemas.weather import WeatherResponse, WeatherForecastResponse, HourlyWeatherResponse, AQIResponse

router = APIRouter(prefix="/api/weather", tags=["天气"])

@router.get("")
async def get_weather(
    city: str = Query("北京", description="城市名称，支持中英文"),
    db: Session = Depends(get_db)
):
    """获取当前天气 - 必须通过LocationID查询"""
    try:
        weather = await qweather_service.get_weather(city, db)
        return weather
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取天气失败: {str(e)}")

@router.get("/forecast")
async def get_forecast(
    city: str = Query("北京", description="城市名称"),
    days: int = Query(7, ge=1, le=15, description="预报天数")
):
    """获取天气预报"""
    try:
        forecast = await qweather_service.get_forecast(city, days)
        return {"city": city, "forecast": forecast}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预报失败: {str(e)}")

@router.get("/hourly")
async def get_hourly_weather(
    city: str = Query("北京", description="城市名称"),
    hours: int = Query(24, ge=1, le=48, description="小时数")
):
    """获取逐时天气"""
    try:
        hourly = await qweather_service.get_hourly_forecast(city, hours)
        return {"city": city, "hourly": hourly}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取逐时天气失败: {str(e)}")

@router.get("/aqi")
async def get_aqi_info(aqi: int = Query(..., ge=0, le=500)):
    """获取空气质量信息"""
    info = qweather_service.get_aqi_info(aqi)
    return {"aqi": aqi, **info}

@router.get("/air")
async def get_air_quality(city: str = Query("北京", description="城市名称")):
    """获取空气质量（通过真实API）"""
    try:
        air = await qweather_service.get_air_quality(city)
        return {"city": city, **air}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取空气质量失败: {str(e)}")

@router.get("/location/search")
async def search_location(q: str = Query(..., description="搜索关键词")):
    """搜索城市位置"""
    try:
        results = await geo_service.search_cities(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/location/by-coords")
async def get_location_by_coords(
    longitude: float = Query(..., description="经度"),
    latitude: float = Query(..., description="纬度")
):
    """根据坐标获取位置"""
    try:
        result = await geo_service.get_location_by_coords(longitude, latitude)
        if not result:
            raise HTTPException(status_code=404, detail="未找到该位置")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@router.get("/advice")
async def get_dressing_advice(
    city: str = Query("北京", description="城市名称"),
    temperature: Optional[float] = Query(None, description="温度（可选，如不提供则自动获取）"),
    humidity: Optional[int] = Query(None, description="湿度（可选）"),
    weather_type: Optional[str] = Query(None, description="天气类型（可选）"),
    wind_speed: Optional[float] = Query(None, description="风速（可选）"),
    uv_index: Optional[int] = Query(None, description="紫外线指数（可选）"),
    db: Session = Depends(get_db)
):
    """获取穿衣建议 - 优化：如果调用方已获取天气数据，直接传入参数避免重复请求"""
    try:
        # 如果没有传入天气数据，才需要获取（向后兼容）
        if temperature is None:
            weather = await qweather_service.get_weather(city, db)
            temperature = weather["temperature"]
            humidity = weather.get("humidity", 50)
            weather_type = weather["weather"]
            wind_speed = weather.get("wind_speed", 0)
            uv_index = weather.get("uv_index", 5)
        else:
            # 使用传入的参数，避免重复请求
            humidity = humidity or 50
            weather_type = weather_type or ""
            wind_speed = wind_speed or 0
            uv_index = uv_index or 5
        
        advice = []
        
        # 温度建议
        if temperature < 5:
            advice.append({
                "type": "cold",
                "level": "寒冷",
                "suggestion": "建议穿着厚羽绒服、棉衣、保暖内衣等，外出请戴帽子、手套，注意防寒保暖。"
            })
        elif temperature < 15:
            advice.append({
                "type": "cool",
                "level": "较凉",
                "suggestion": "建议穿着毛衣、夹克、风衣等，早晚温差大时可加件外套。"
            })
        elif temperature < 25:
            advice.append({
                "type": "comfortable",
                "level": "舒适",
                "suggestion": "气温适宜，穿着轻薄外套或长袖即可。"
            })
        else:
            advice.append({
                "type": "hot",
                "level": "炎热",
                "suggestion": "建议穿着短袖、短裤等轻薄衣物，注意防晒和补充水分。"
            })
        
        # 天气状况建议
        if "雨" in weather_type:
            advice.append({
                "type": "rain",
                "level": "雨天",
                "suggestion": "记得携带雨具，建议穿防水的鞋子和外套。"
            })
        elif "雪" in weather_type:
            advice.append({
                "type": "snow",
                "level": "雪天",
                "suggestion": "穿防滑保暖的鞋子，外出注意安全。"
            })
        
        # 风力建议
        if wind_speed > 10:
            advice.append({
                "type": "windy",
                "level": "大风",
                "suggestion": "风速较大，建议穿着防风衣物，避免穿过于宽松的外套。"
            })
        
        # 紫外线建议
        if uv_index >= 8:
            advice.append({
                "type": "uv",
                "level": "强紫外线",
                "suggestion": "紫外线强度很高，建议涂抹防晒霜，佩戴太阳镜和遮阳帽。"
            })
        elif uv_index >= 5:
            advice.append({
                "type": "uv",
                "level": "中等紫外线",
                "suggestion": "紫外线较强，建议涂抹防晒霜。"
            })
        
        # 湿度建议
        if humidity > 80:
            advice.append({
                "type": "humid",
                "level": "高湿度",
                "suggestion": "空气较潮湿，建议选择透气性好的衣物，避免棉质内衣。"
            })
        elif humidity < 30:
            advice.append({
                "type": "dry",
                "level": "干燥",
                "suggestion": "空气干燥，注意补充水分，可以穿保湿性好的衣物。"
            })
        
        return {
            "city": city,
            "temperature": temperature,
            "weather": weather_type,
            "advice": advice
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取建议失败: {str(e)}")
