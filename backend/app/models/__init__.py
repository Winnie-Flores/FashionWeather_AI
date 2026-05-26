# 导入所有模型，确保它们在关系配置前已注册
# 导入顺序很重要：先导入有外键依赖的模型

from app.models.user import User
from app.models.clothes import Clothes
from app.models.outfit import Outfit
from app.models.favorite import FavoriteOutfit
from app.models.chat import ChatMessage
from app.models.weather import WeatherRecord

# 导出所有模型
__all__ = ["User", "Clothes", "Outfit", "FavoriteOutfit", "ChatMessage", "WeatherRecord"]
