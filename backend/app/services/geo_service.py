"""
GeoService - 地理编码服务
功能：城市名称 -> LocationID 转换
支持：中文城市名、英文城市名、坐标查询
"""
import httpx
from typing import Optional, List, Dict, Any
from app.core.config import settings


class GeoService:
    """地理编码服务 - 处理城市名与LocationID之间的转换"""
    
    # 和风天气 API 配置 - 使用正确的API Host
    GEO_API_HOST = "https://pu3qqt4yxn.re.qweatherapi.com"
    API_KEY = None
    
    # 常用城市缓存（避免重复请求API）
    _city_cache: Dict[str, str] = {}
    
    def __init__(self):
        self.api_key = getattr(settings, 'WEATHER_API_KEY', None) or getattr(settings, 'HEFENG_API_KEY', None)
        self.API_KEY = self.api_key
        
    async def get_location_id(self, location: str) -> Optional[str]:
        """
        根据城市名称获取 LocationID
        
        Args:
            location: 城市名称（支持中英文）
            
        Returns:
            LocationID 字符串，如 "101010100"，失败返回 None
        """
        if not self.api_key:
            print(f"[GeoService] 错误：未配置 API Key")
            return None
            
        # 检查缓存
        cache_key = location.lower().strip()
        if cache_key in self._city_cache:
            print(f"[GeoService] 缓存命中: {location} -> {self._city_cache[cache_key]}")
            return self._city_cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 正确的API路径：/geo/v2/city/lookup
                url = f"{self.GEO_API_HOST}/geo/v2/city/lookup"
                params = {
                    "location": location,
                    "key": self.api_key
                }
                
                print(f"[GeoService] 请求: {location}")
                response = await client.get(url, params=params)
                data = response.json()
                
                if data.get("code") != "200":
                    print(f"[GeoService] API错误: {data}")
                    return None
                
                locations = data.get("location", [])
                if not locations:
                    print(f"[GeoService] 未找到城市: {location}")
                    return None
                
                # 返回第一个匹配结果
                location_id = locations[0].get("id")
                city_name = locations[0].get("name")
                
                # 缓存结果
                self._city_cache[cache_key] = location_id
                # 同时缓存标准城市名
                self._city_cache[city_name.lower()] = location_id
                
                print(f"[GeoService] 成功: {location} -> {city_name} ({location_id})")
                return location_id
                
        except Exception as e:
            print(f"[GeoService] 异常: {e}")
            return None
    
    async def get_location_by_coords(self, longitude: float, latitude: float) -> Optional[Dict[str, Any]]:
        """
        根据坐标获取位置信息
        
        Args:
            longitude: 经度
            latitude: 纬度
            
        Returns:
            包含 id, name 等信息 dict，失败返回 None
        """
        if not self.api_key:
            print(f"[GeoService] 错误：未配置 API Key")
            return None
            
        try:
            # 和风天气要求：经度,纬度
            location = f"{longitude},{latitude}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 正确的API路径：/geo/v2/city/lookup
                url = f"{self.GEO_API_HOST}/geo/v2/city/lookup"
                params = {
                    "location": location,
                    "key": self.api_key
                }
                
                print(f"[GeoService] 坐标查询: {location}")
                response = await client.get(url, params=params)
                data = response.json()
                
                if data.get("code") != "200":
                    print(f"[GeoService] API错误: {data}")
                    return None
                
                locations = data.get("location", [])
                if not locations:
                    return None
                
                result = locations[0]
                print(f"[GeoService] 坐标结果: {result.get('name')} ({result.get('id')})")
                return result
                
        except Exception as e:
            print(f"[GeoService] 坐标查询异常: {e}")
            return None
    
    async def search_cities(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索城市列表
        
        Args:
            query: 搜索关键词
            
        Returns:
            城市列表
        """
        if not self.api_key:
            return []
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 正确的API路径：/geo/v2/city/lookup
                url = f"{self.GEO_API_HOST}/geo/v2/city/lookup"
                params = {
                    "location": query,
                    "key": self.api_key,
                    "range": "world"  # 支持全球搜索
                }
                
                response = await client.get(url, params=params)
                data = response.json()
                
                if data.get("code") != "200":
                    return []
                
                return data.get("location", [])
                
        except Exception as e:
            print(f"[GeoService] 搜索异常: {e}")
            return []
    
    def clear_cache(self):
        """清除缓存"""
        self._city_cache.clear()
        print("[GeoService] 缓存已清除")


# 全局实例
geo_service = GeoService()
