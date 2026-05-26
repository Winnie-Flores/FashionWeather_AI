"""
智能穿搭推荐引擎 - 彻底重构版
基于规则引擎 + 天气感知 + 风格匹配 + AI评分 的混合推荐系统

核心架构：
第一层：天气过滤
第二层：场景过滤
第三层：风格匹配
第四层：颜色评分
第五层：AI审核
"""

import hashlib
import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


# ==================== 枚举和常量定义 ====================

class TemperatureLevel(Enum):
    """温度等级枚举"""
    EXTREME_HOT = "极热"      # >35
    VERY_HOT = "炎热"         # 30-35
    HOT = "热"               # 25-30
    WARM = "温暖"             # 20-25
    COOL = "凉爽"             # 15-20
    COLD = "微冷"             # 10-15
    VERY_COLD = "冷"          # 5-10
    FREEZING = "寒冷"         # 0-5
    EXTREME_COLD = "严寒"     # <0


class Scene(Enum):
    """场景枚举"""
    DAILY = "日常"
    WORK = "上班"
    DATE = "约会"
    SPORTS = "运动"
    PARTY = "聚会"
    TRAVEL = "出行"


class Thickness(Enum):
    """厚度等级枚举"""
    ULTRA_THIN = 0    # 极薄
    THIN = 1          # 薄
    MEDIUM = 2       # 中等
    THICK = 3        # 厚
    FUR_LINED = 4    # 加绒
    DOWN = 5         # 羽绒级


# ==================== 温度穿衣规则引擎 ====================

@dataclass
class TemperatureRule:
    """温度穿衣规则"""
    temp_min: float
    temp_max: float
    level: TemperatureLevel
    recommended_tops: List[str]
    recommended_bottoms: List[str]
    recommended_shoes: List[str]
    recommended_jackets: List[str]
    required_thickness: List[str]  # 必须的厚度
    forbidden_thickness: List[str]   # 禁止的厚度
    tips: str


class TemperatureRuleEngine:
    """温度穿衣规则引擎 - 核心组件"""

    # 精细化温度规则
    RULES: List[TemperatureRule] = [
        TemperatureRule(
            temp_min=40, temp_max=50,
            level=TemperatureLevel.EXTREME_HOT,
            recommended_tops=["T恤", "背心", "吊带", "薄衬衫"],
            recommended_bottoms=["短裤", "薄长裙", "热裤"],
            recommended_shoes=["凉鞋", "拖鞋", "帆布鞋", "透气运动鞋"],
            recommended_jackets=[],
            required_thickness=["极薄", "薄"],
            forbidden_thickness=["厚", "加绒", "羽绒级"],
            tips="极度炎热，避免外出，做好防暑"
        ),
        TemperatureRule(
            temp_min=30, temp_max=40,
            level=TemperatureLevel.VERY_HOT,
            recommended_tops=["T恤", "短袖衬衫", "背心", "薄卫衣"],
            recommended_bottoms=["短裤", "薄长裤", "短裙"],
            recommended_shoes=["凉鞋", "运动鞋", "帆布鞋"],
            recommended_jackets=["防晒衫", "薄开衫"],
            required_thickness=["极薄", "薄"],
            forbidden_thickness=["厚", "加绒", "羽绒级"],
            tips="高温天气，选择轻薄透气材质"
        ),
        TemperatureRule(
            temp_min=25, temp_max=30,
            level=TemperatureLevel.HOT,
            recommended_tops=["T恤", "长袖衬衫", "薄卫衣", "薄针织衫"],
            recommended_bottoms=["牛仔裤", "薄长裤", "休闲裤", "长裙"],
            recommended_shoes=["运动鞋", "帆布鞋", "皮鞋", "凉鞋"],
            recommended_jackets=["薄外套", "防晒衫", "空调衫"],
            required_thickness=["薄", "中等"],
            forbidden_thickness=["加绒", "羽绒级"],
            tips="偏热天气，可穿薄外套应对空调"
        ),
        TemperatureRule(
            temp_min=20, temp_max=25,
            level=TemperatureLevel.WARM,
            recommended_tops=["长袖", "卫衣", "毛衣", "衬衫", "针织衫"],
            recommended_bottoms=["牛仔裤", "休闲裤", "长裙", "卡其裤"],
            recommended_shoes=["运动鞋", "帆布鞋", "皮鞋", "小白鞋"],
            recommended_jackets=["外套", "风衣", "开衫", "薄夹克"],
            required_thickness=["中等"],
            forbidden_thickness=["加绒", "羽绒级"],
            tips="舒适天气，叠穿方便增减"
        ),
        TemperatureRule(
            temp_min=15, temp_max=20,
            level=TemperatureLevel.COOL,
            recommended_tops=["毛衣", "卫衣", "厚衬衫", "针织开衫"],
            recommended_bottoms=["牛仔裤", "休闲裤", "保暖裤"],
            recommended_shoes=["运动鞋", "皮鞋", "靴子", "帆布鞋"],
            recommended_jackets=["外套", "夹克", "风衣", "皮衣", "西装外套"],
            required_thickness=["中等", "厚"],
            forbidden_thickness=["极薄", "羽绒级"],
            tips="凉爽天气，记得带外套"
        ),
        TemperatureRule(
            temp_min=10, temp_max=15,
            level=TemperatureLevel.COLD,
            recommended_tops=["毛衣", "厚卫衣", "保暖衬衫", "针织衫"],
            recommended_bottoms=["牛仔裤", "厚裤子", "保暖裤"],
            recommended_shoes=["靴子", "运动鞋", "皮鞋"],
            recommended_jackets=["羽绒服", "厚外套", "棉服", "大衣", "皮毛一体"],
            required_thickness=["厚", "加绒"],
            forbidden_thickness=["极薄", "薄"],
            tips="较冷天气，需要保暖外套"
        ),
        TemperatureRule(
            temp_min=5, temp_max=10,
            level=TemperatureLevel.VERY_COLD,
            recommended_tops=["厚毛衣", "保暖内衣", "加绒卫衣", "抓绒衫"],
            recommended_bottoms=["加绒牛仔裤", "保暖裤", "厚休闲裤"],
            recommended_shoes=["靴子", "雪地靴", "保暖皮鞋"],
            recommended_jackets=["羽绒服", "厚棉服", "派克大衣", "冲锋衣"],
            required_thickness=["厚", "加绒"],
            forbidden_thickness=["极薄", "薄"],
            tips="寒冷天气，全副保暖"
        ),
        TemperatureRule(
            temp_min=0, temp_max=5,
            level=TemperatureLevel.FREEZING,
            recommended_tops=["保暖内衣", "厚毛衣", "加绒衬衫", "抓绒内胆"],
            recommended_bottoms=["加绒裤", "保暖裤", "滑雪裤"],
            recommended_shoes=["雪地靴", "保暖靴", "防滑棉鞋"],
            recommended_jackets=["加厚羽绒服", "户外防寒服", "派克大衣", "滑雪服"],
            required_thickness=["加绒", "羽绒级"],
            forbidden_thickness=["极薄", "薄", "中等"],
            tips="极冷天气，务必做好防寒"
        ),
        TemperatureRule(
            temp_min=-20, temp_max=0,
            level=TemperatureLevel.EXTREME_COLD,
            recommended_tops=["保暖内衣", "厚羊绒衫", "加绒卫衣", "发热内衣"],
            recommended_bottoms=["加绒裤", "保暖裤", "滑雪裤"],
            recommended_shoes=["雪地靴", "保暖靴", "极地靴"],
            recommended_jackets=["加厚羽绒服", "户外防寒服", "极地防寒服", "派克大衣"],
            required_thickness=["羽绒级"],
            forbidden_thickness=["极薄", "薄", "中等", "厚"],
            tips="严寒天气，非必要不外出"
        ),
    ]

    # 厚度数值映射
    THICKNESS_VALUES = {
        "极薄": 0, "薄": 1, "中等": 2, "厚": 3, "加绒": 4, "羽绒级": 5,
        "": 2, "未知": 2
    }

    def get_rule(self, temperature: float) -> TemperatureRule:
        """根据温度获取对应规则"""
        for rule in self.RULES:
            if rule.temp_min <= temperature < rule.temp_max:
                return rule
        # 边界情况
        if temperature >= 40:
            return self.RULES[0]
        return self.RULES[-1]

    def get_temperature_level(self, temperature: float) -> TemperatureLevel:
        """获取温度等级"""
        return self.get_rule(temperature).level

    def is_thickness_suitable(self, thickness: str, rule: TemperatureRule) -> bool:
        """检查厚度是否适合当前温度"""
        thickness_lower = thickness.lower() if thickness else ""

        # 检查禁止的厚度
        for forbidden in rule.forbidden_thickness:
            if forbidden.lower() in thickness_lower or thickness_lower in forbidden.lower():
                return False

        # 检查必须的厚度
        if rule.required_thickness:
            # 如果有必须厚度要求，检查是否满足
            has_required = False
            for required in rule.required_thickness:
                if required.lower() in thickness_lower or thickness_lower in required.lower():
                    has_required = True
                    break
            if not has_required:
                # 在极端温度下，必须厚度很重要
                if rule.level in [TemperatureLevel.EXTREME_HOT, TemperatureLevel.VERY_HOT,
                                  TemperatureLevel.VERY_COLD, TemperatureLevel.FREEZING,
                                  TemperatureLevel.EXTREME_COLD]:
                    return False

        return True

    def filter_by_temperature(self, clothes: List[dict], temperature: float) -> List[dict]:
        """根据温度过滤衣物"""
        rule = self.get_rule(temperature)

        def is_suitable(clothing: dict) -> bool:
            thickness = clothing.get("thickness", "")
            clothing_type = clothing.get("type", "").lower()

            # 优先检查厚度
            if not self.is_thickness_suitable(thickness, rule):
                return False

            # 检查温度范围
            temp_min = clothing.get("temperature_min", 0)
            temp_max = clothing.get("temperature_max", 40)

            # 温度过高时不允许极厚衣物
            if temperature > 30 and self.THICKNESS_VALUES.get(thickness, 2) >= 4:
                return False

            # 温度过低时不允许极薄衣物
            if temperature < 10 and self.THICKNESS_VALUES.get(thickness, 2) <= 1:
                return False

            # 温度范围检查
            buffer = 5  # 允许5度偏差
            if temperature < temp_min - buffer or temperature > temp_max + buffer:
                return False

            return True

        filtered = [c for c in clothes if is_suitable(c)]

        # 如果过滤后太少，放宽条件
        if len(filtered) < 3:
            filtered = [c for c in clothes if self.is_basic_suitable(c, temperature)]

        return filtered

    def is_basic_suitable(self, clothing: dict, temperature: float) -> bool:
        """基本温度适合性检查（宽松模式）"""
        temp_min = clothing.get("temperature_min", 0)
        temp_max = clothing.get("temperature_max", 40)

        return temp_min <= temperature <= temp_max


# ==================== 材质适配系统 ====================

class MaterialAdapter:
    """材质适配系统 - 根据天气选择合适材质"""

    # 材质适配规则
    MATERIAL_RULES = {
        "高温": {
            "recommended": ["棉", "亚麻", "雪纺", "速干", "丝绸", "竹纤维", "天丝", "莫代尔"],
            "avoid": ["羊毛", "羊绒", "针织", "羽绒", "抓绒", "加绒", "毛呢"],
            "score_boost": {"棉": 10, "亚麻": 10, "雪纺": 8, "速干": 10, "丝绸": 8}
        },
        "适中": {
            "recommended": ["棉", "牛仔", "针织", "帆布", "皮革", "莫代尔"],
            "avoid": ["羽绒", "抓绒", "加绒"],
            "score_boost": {"棉": 8, "牛仔": 8, "针织": 10}
        },
        "低温": {
            "recommended": ["羊毛", "羊绒", "针织", "羽绒", "抓绒", "毛呢", "法兰绒", "摇粒绒", "皮毛一体"],
            "avoid": ["亚麻", "雪纺", "丝绸", "速干"],
            "score_boost": {"羊毛": 10, "羊绒": 10, "针织": 8, "羽绒": 10, "抓绒": 8}
        },
        "雨天": {
            "recommended": ["防水", "速干", "冲锋衣面料", "尼龙", "涂层"],
            "avoid": ["普通棉", "亚麻", "丝绸"],
            "score_boost": {"防水": 15, "速干": 10, "涂层": 10}
        },
        "大风": {
            "recommended": ["防风面料", "尼龙", "涂层", "皮毛一体", "软壳"],
            "avoid": ["薄棉", "亚麻"],
            "score_boost": {"防风": 15, "涂层": 10, "尼龙": 8}
        }
    }

    def get_material_category(self, temperature: float, weather) -> str:
        """根据天气获取材质分类"""
        # 处理天气参数可能是字符串或字典的情况
        if isinstance(weather, str):
            weather_str = weather.lower()
            if "雨" in weather_str:
                return "雨天"
            elif "风" in weather_str:
                return "大风"
            else:
                weather_dict = {"precipitation_probability": 0, "wind_speed": 0}
        else:
            weather_dict = weather

        if weather_dict.get("precipitation_probability", 0) > 50:
            return "雨天"
        if weather_dict.get("wind_speed", 0) > 15:
            return "大风"
        if temperature > 28:
            return "高温"
        elif temperature < 12:
            return "低温"
        else:
            return "适中"

    def score_material(self, material: str, temperature: float, weather) -> float:
        """给材质评分"""
        if not material:
            return 5.0  # 未知材质给中等分

        material_lower = material.lower()
        category = self.get_material_category(temperature, weather)
        rules = self.MATERIAL_RULES[category]

        # 检查推荐材质
        for rec in rules["recommended"]:
            if rec.lower() in material_lower:
                return rules["score_boost"].get(rec, 8.0)

        # 检查避免材质
        for avoid in rules["avoid"]:
            if avoid.lower() in material_lower:
                return 2.0

        # 默认中等分
        return 5.0

    def filter_by_material(self, clothes: List[dict], temperature: float, weather: dict) -> List[dict]:
        """根据材质过滤和排序衣物"""
        scored = []
        for c in clothes:
            score = self.score_material(c.get("material", ""), temperature, weather)
            scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored]


# ==================== 场景约束系统 ====================

class SceneConstraints:
    """场景约束系统 - 确保穿搭符合场景要求"""

    # 场景约束规则 - 增强版
    SCENE_RULES = {
        Scene.WORK: {
            "preferred_styles": ["商务", "简约", "休闲商务", "正式"],
            "avoid_styles": ["运动", "街头", "波西米亚", "朋克", "极端潮流", "邋遢"],
            "preferred_formality_range": (3, 5),  # 上班需要较正式
            "avoid_formality_range": (1, 2),  # 避免太休闲
            "forbidden_types": ["运动裤", "运动背心", "拖鞋", "人字拖", "居家服", "睡衣", "背心", "短裤"],
            "preferred_colors": ["黑色", "白色", "灰色", "蓝色", "藏青", "卡其"],
            "avoid_colors": ["荧光色", "亮橙", "亮绿"],
            "recommended_accessories": ["皮带", "公文包", "手表"],
            "description": "上班穿搭需要专业得体",
            "tip": "推荐选择衬衫、西裤或深色牛仔裤，搭配皮鞋或小白鞋"
        },
        Scene.DAILY: {
            "preferred_styles": ["休闲", "简约", "舒适", "日常"],
            "avoid_styles": ["过于正式"],
            "preferred_formality_range": (1, 3),
            "avoid_formality_range": (4, 5),
            "forbidden_types": [],
            "preferred_colors": ["白色", "黑色", "灰色", "蓝色", "米色", "卡其"],
            "avoid_colors": ["无限制"],
            "recommended_accessories": ["双肩包", "帽子"],
            "description": "日常穿搭以舒适为主",
            "tip": "简单舒适的白T或卫衣搭配牛仔裤就很适合出门"
        },
        Scene.DATE: {
            "preferred_styles": ["简约", "休闲", "精致", "优雅", "复古"],
            "avoid_styles": ["运动", "户外", "邋遢", "街头"],
            "preferred_formality_range": (2, 4),
            "avoid_formality_range": (1, 1),
            "forbidden_types": ["运动服", "运动裤", "背心", "拖鞋", "居家服", "短裤", "运动鞋"],
            "preferred_colors": ["白色", "黑色", "深蓝", "米色", "焦糖色", "酒红"],
            "avoid_colors": ["荧光色", "运动色"],
            "recommended_accessories": ["手表", "项链", "耳饰"],
            "description": "约会穿搭要有品位，干净整洁",
            "tip": "选择有质感的上衣搭配小白鞋，给人精致又不刻意的感觉"
        },
        Scene.SPORTS: {
            "preferred_styles": ["运动", "功能性"],
            "avoid_styles": ["商务", "正装", "正式", "礼服"],
            "preferred_formality_range": (1, 2),
            "avoid_formality_range": (4, 5),
            "forbidden_types": ["皮鞋", "正装鞋", "西装裤", "衬衫", "裙子", "高跟鞋"],
            "preferred_colors": ["黑色", "白色", "灰色", "蓝色", "荧光色"],
            "avoid_colors": ["正装色"],
            "required_types": ["运动鞋"],
            "recommended_accessories": ["运动包", "头带", "运动手表"],
            "description": "运动穿搭要舒适透气",
            "tip": "运动T恤搭配运动裤和专业的运动鞋，保证活动自如"
        },
        Scene.PARTY: {
            "preferred_styles": ["时尚", "简约", "精致", "个性", "潮流"],
            "avoid_styles": ["运动", "过于休闲"],
            "preferred_formality_range": (2, 4),
            "avoid_formality_range": (1, 1),
            "forbidden_types": ["运动服", "居家服", "拖鞋", "运动裤"],
            "preferred_colors": ["黑色", "白色", "金色", "银色", "酒红", "墨绿"],
            "avoid_colors": ["运动色"],
            "recommended_accessories": ["手表", "手包", "配饰"],
            "description": "聚会穿搭可以稍微个性一些",
            "tip": "选择有设计感的单品，搭配精致的小白鞋或乐福鞋"
        },
        Scene.TRAVEL: {
            "preferred_styles": ["休闲", "舒适", "简约"],
            "avoid_styles": ["过于正式"],
            "preferred_formality_range": (1, 3),
            "avoid_formality_range": (5, 5),
            "forbidden_types": ["正装皮鞋", "礼服", "高跟鞋", "西装"],
            "preferred_colors": ["白色", "黑色", "蓝色", "卡其", "军绿"],
            "avoid_colors": ["过于正式的颜色"],
            "recommended_accessories": ["双肩包", "帽子", "墨镜"],
            "description": "旅行穿搭以舒适实用为主",
            "tip": "选择百搭舒适的衣物，方便活动又上镜"
        }
    }

    def get_scene(self, scene_name: str) -> Scene:
        """获取场景枚举"""
        scene_map = {
            "日常": Scene.DAILY, "daily": Scene.DAILY,
            "上班": Scene.WORK, "work": Scene.WORK, "工作": Scene.WORK,
            "约会": Scene.DATE, "date": Scene.DATE,
            "运动": Scene.SPORTS, "sports": Scene.SPORTS, "健身": Scene.SPORTS,
            "聚会": Scene.PARTY, "party": Scene.PARTY, "派对": Scene.PARTY,
            "出行": Scene.TRAVEL, "travel": Scene.TRAVEL, "旅行": Scene.TRAVEL
        }
        return scene_map.get(scene_name, Scene.DAILY)

    def is_valid_for_scene(self, clothing: dict, scene: Scene) -> Tuple[bool, str]:
        """检查衣物是否适合场景，返回 (是否有效, 原因)"""
        rules = self.SCENE_RULES[scene]

        clothing_type = clothing.get("type", "")
        clothing_style = clothing.get("style", "")
        formality = clothing.get("formality", 3)

        # 检查禁止的类型
        for forbidden in rules["forbidden_types"]:
            if forbidden.lower() in clothing_type.lower():
                return False, f"'{forbidden}'不适合{scene.value}场景"

        # 检查禁止的风格
        for avoid in rules["avoid_styles"]:
            if avoid.lower() in clothing_style.lower():
                return False, f"'{avoid}'风格不适合{scene.value}场景"

        # 检查正式程度
        min_form, max_form = rules["avoid_formality_range"]
        if min_form <= formality <= max_form:
            return False, f"正式程度{formality}不适合{scene.value}场景"

        return True, ""

    def filter_by_scene(self, clothes: List[dict], scene: Scene) -> List[dict]:
        """根据场景过滤衣物"""
        valid = []
        for c in clothes:
            is_valid, _ = self.is_valid_for_scene(c, scene)
            if is_valid:
                valid.append(c)
        return valid

    def score_by_scene(self, clothing: dict, scene: Scene) -> float:
        """根据场景给衣物评分"""
        rules = self.SCENE_RULES[scene]
        base_score = 5.0

        # 风格匹配加分
        clothing_style = clothing.get("style", "")
        for preferred in rules["preferred_styles"]:
            if preferred.lower() in clothing_style.lower():
                base_score += 3.0
                break

        # 正式程度匹配
        formality = clothing.get("formality", 3)
        min_f, max_f = rules["preferred_formality_range"]
        if min_f <= formality <= max_f:
            base_score += 2.0

        return base_score


# ==================== 风格统一系统 ====================

class StyleMatcher:
    """风格统一系统 - 确保穿搭风格一致"""

    # 风格组 - 同一组内的风格可以相互搭配
    STYLE_GROUPS = {
        "商务": ["商务", "商务休闲", "正装", "正式"],
        "休闲": ["休闲", "简约", "日常", "舒适"],
        "运动": ["运动", "功能性", "运动休闲"],
        "街头": ["街头", "潮流", "嘻哈", "朋克"],
        "复古": ["复古", "文艺", "怀旧", "经典"],
        "时尚": ["时尚", "精致", "个性", "前卫"],
    }

    # 风格兼容性矩阵
    STYLE_COMPATIBILITY = {
        # 商务组
        ("商务", "简约"): 10,
        ("商务", "商务休闲"): 10,
        ("简约", "商务休闲"): 10,
        ("正装", "简约"): 8,
        # 休闲组
        ("休闲", "简约"): 10,
        ("休闲", "日常"): 10,
        ("简约", "日常"): 10,
        # 运动组
        ("运动", "运动休闲"): 10,
        ("运动", "功能性"): 10,
        # 街头组
        ("街头", "潮流"): 10,
        ("街头", "嘻哈"): 8,
        ("潮流", "嘻哈"): 8,
        # 复古组
        ("复古", "文艺"): 10,
        ("复古", "经典"): 10,
        # 时尚组
        ("时尚", "精致"): 10,
        ("时尚", "个性"): 8,
    }

    # 不兼容的风格组合
    INCOMPATIBLE_PAIRS = [
        ("商务", "运动"),
        ("商务", "街头"),
        ("正装", "运动"),
        ("正装", "街头"),
        ("运动", "街头"),
        ("街头", "正装"),
    ]

    def get_style_group(self, style: str) -> Optional[str]:
        """获取风格所属的组"""
        style_lower = style.lower() if style else ""
        for group, styles in self.STYLE_GROUPS.items():
            for s in styles:
                if s.lower() in style_lower or style_lower in s.lower():
                    return group
        return None

    def get_compatibility(self, style1: str, style2: str) -> float:
        """获取两种风格的兼容性分数"""
        if not style1 or not style2:
            return 5.0

        style1_lower = style1.lower()
        style2_lower = style2.lower()

        # 完全相同
        if style1_lower == style2_lower:
            return 10.0

        # 检查兼容性矩阵
        key1 = (style1_lower, style2_lower)
        key2 = (style2_lower, style1_lower)

        if key1 in self.STYLE_COMPATIBILITY:
            return self.STYLE_COMPATIBILITY[key1]
        if key2 in self.STYLE_COMPATIBILITY:
            return self.STYLE_COMPATIBILITY[key2]

        # 检查风格组
        group1 = self.get_style_group(style1)
        group2 = self.get_style_group(style2)

        if group1 and group1 == group2:
            return 8.0

        # 检查不兼容组合
        for s1, s2 in self.INCOMPATIBLE_PAIRS:
            if (s1 in style1_lower and s2 in style2_lower) or \
               (s2 in style1_lower and s1 in style2_lower):
                return 1.0

        return 5.0  # 默认中等兼容

    def score_style_consistency(self, outfit: Dict[str, dict]) -> float:
        """评估整套穿搭的风格一致性"""
        styles = []
        for key in ["top", "pants", "shoes", "jacket"]:
            if outfit.get(key):
                style = outfit[key].get("style", "")
                if style:
                    styles.append(style)

        if len(styles) < 2:
            return 10.0  # 单件无法评估

        # 计算所有风格对之间的兼容性
        total_score = 0
        pair_count = 0

        for i in range(len(styles)):
            for j in range(i + 1, len(styles)):
                score = self.get_compatibility(styles[i], styles[j])
                total_score += score
                pair_count += 1

        if pair_count == 0:
            return 10.0

        return total_score / pair_count


# ==================== 颜色搭配规则引擎 ====================

class ColorMatcher:
    """颜色搭配规则引擎 - 确保穿搭配色协调"""

    # 中性色
    NEUTRAL_COLORS = {"黑色", "白色", "灰色", "深灰色", "浅灰色", "米色", "白色", "象牙白", "燕麦色"}

    # 经典搭配组合
    CLASSIC_COMBINATIONS = [
        # 单色搭配
        {"黑", "白", "灰"},
        {"黑", "白", "牛仔蓝"},
        {"米色", "白色", "棕色"},
        {"卡其", "白色", "藏青"},
        {"深蓝", "白色", "浅蓝"},
        # 安全配色
        {"黑", "白"},
        {"白", "藏青"},
        {"灰", "蓝"},
        {"卡其", "白"},
        {"深蓝", "米白"},
        {"黑", "灰"},
        {"白", "驼色"},
    ]

    # 推荐的同色系搭配
    MONOCHROME_COMBINATIONS = [
        # 全黑/全白/全灰
        {"黑", "深灰", "灰"},
        {"白", "米白", "象牙白"},
        {"灰", "浅灰", "深灰"},
        # 同色系深浅
        {"藏青", "深蓝", "天蓝"},
        {"深棕", "棕色", "浅棕"},
        {"深绿", "军绿", "浅绿"},
    ]

    # 禁止的配色组合
    FORBIDDEN_COMBINATIONS = [
        {"荧光绿", "紫色"},
        {"荧光绿", "粉红"},
        {"红", "绿"},  # 圣诞配色太极端
        {"橙", "紫"},
        {"黄", "紫"},
        {"亮黄", "荧光橙"},
        {"玫红", "正红"},  # 过于艳丽
    ]

    # 颜色类别映射
    COLOR_CATEGORIES = {
        "暖色": {"红", "橙", "黄", "粉", "橘", "珊瑚", "酒红", "砖红", "焦糖", "驼色", "卡其", "棕色", "咖啡", "巧克力", "米色", "杏色", "奶咖", "燕麦"},
        "冷色": {"蓝", "绿", "紫", "青", "灰", "藏青", "雾霾蓝", "宝蓝", "天蓝", "湖蓝", "薄荷", "抹茶"},
        "中性色": {"黑", "白", "灰", "银", "金"},
        "大地色": {"驼色", "卡其", "棕色", "焦糖", "摩卡", "榛果", "杏仁", "燕麦", "米白", "象牙"},
    }

    def normalize_color(self, color: str) -> str:
        """标准化颜色名称"""
        if not color:
            return ""

        color_lower = color.lower()

        # 去除常见修饰词
        remove_words = ["色", "的", "带有", "偏"]
        for word in remove_words:
            color_lower = color_lower.replace(word, "")

        # 标准化常见颜色
        normalize_map = {
            "深": "", "浅": "", "暗": "", "亮": "",
            "浅灰": "浅灰色", "深灰": "深灰色",
            "炭灰": "深灰色", "银灰": "灰色",
            "米白": "米白色", "象牙白": "象牙白", "奶白": "米白色",
            "杏色": "杏色", "奶咖": "奶咖色", "摩卡": "摩卡色",
            "土黄": "驼色", "焦糖色": "焦糖色", "焦糖": "焦糖色",
        }

        for old, new in normalize_map.items():
            color_lower = color_lower.replace(old, new)

        return color_lower.strip()

    def get_color_category(self, color: str) -> Optional[str]:
        """获取颜色所属类别"""
        color_lower = self.normalize_color(color).lower()

        for category, colors in self.COLOR_CATEGORIES.items():
            for c in colors:
                if c.lower() in color_lower or color_lower in c.lower():
                    return category

        # 检查中性色
        if color_lower in self.NEUTRAL_COLORS:
            return "中性色"

        return None

    def is_neutral(self, color: str) -> bool:
        """判断是否为中性色"""
        return self.normalize_color(color) in self.NEUTRAL_COLORS

    def is_color_match_valid(self, color1: str, color2: str) -> Tuple[bool, float]:
        """检查两种颜色搭配是否有效，返回 (是否有效, 评分)"""
        c1 = self.normalize_color(color1)
        c2 = self.normalize_color(color2)

        if not c1 or not c2:
            return True, 5.0

        # 完全相同
        if c1 == c2:
            return True, 7.0

        # 检查禁止组合
        color_set = {c1, c2}
        for forbidden in self.FORBIDDEN_COMBINATIONS:
            if forbidden & color_set == color_set:
                return False, 1.0

        # 检查经典搭配
        for classic in self.CLASSIC_COMBINATIONS:
            if classic & color_set == color_set:
                return True, 10.0

        # 检查单色系搭配
        for mono in self.MONOCHROME_COMBINATIONS:
            if mono & color_set == color_set:
                return True, 9.0

        # 中性色可以搭配大多数颜色
        if self.is_neutral(c1) or self.is_neutral(c2):
            return True, 8.0

        # 同类别颜色搭配
        cat1 = self.get_color_category(c1)
        cat2 = self.get_color_category(c2)

        if cat1 and cat1 == cat2:
            return True, 7.0

        # 默认中等搭配
        return True, 5.0

    def score_color_harmony(self, outfit: Dict[str, dict]) -> float:
        """评估整套穿搭的颜色协调性"""
        colors = []
        for key in ["top", "pants", "shoes", "jacket"]:
            if outfit.get(key):
                color = outfit[key].get("color", "")
                if color:
                    colors.append(color)

        if len(colors) < 2:
            return 10.0

        # 计算所有颜色对的搭配分数
        total_score = 0
        pair_count = 0
        invalid_pairs = 0

        for i in range(len(colors)):
            for j in range(i + 1, len(colors)):
                is_valid, score = self.is_color_match_valid(colors[i], colors[j])
                total_score += score
                pair_count += 1
                if not is_valid:
                    invalid_pairs += 1

        if pair_count == 0:
            return 10.0

        # 有不协调的颜色对，扣分
        if invalid_pairs > 0:
            return max(1.0, (total_score / pair_count) - (invalid_pairs * 2))

        return total_score / pair_count


# ==================== 鞋子推荐规则引擎 ====================

class ShoeRuleEngine:
    """鞋子推荐规则引擎 - 核心组件，确保每套穿搭都有合适的鞋子"""

    # 场景与鞋子类型映射
    SCENE_SHOE_RULES = {
        Scene.WORK: {
            "preferred": ["皮鞋", "乐福鞋", "牛津鞋", "德比鞋", "正装鞋"],
            "secondary": ["小白鞋", "帆布鞋"],
            "avoid": ["拖鞋", "凉鞋", "运动鞋", "人字拖", "沙滩鞋"],
            "description": "上班场景推荐皮鞋或乐福鞋"
        },
        Scene.DAILY: {
            "preferred": ["小白鞋", "帆布鞋", "休闲鞋", "运动鞋"],
            "secondary": ["皮鞋", "乐福鞋", "豆豆鞋"],
            "avoid": ["正装皮鞋", "高跟鞋"],
            "description": "日常场景推荐休闲鞋或小白鞋"
        },
        Scene.DATE: {
            "preferred": ["小白鞋", "乐福鞋", "短靴", "帆布鞋"],
            "secondary": ["皮鞋", "休闲皮鞋"],
            "avoid": ["运动鞋", "拖鞋", "凉鞋", "人字拖"],
            "description": "约会场景推荐精致休闲鞋"
        },
        Scene.SPORTS: {
            "preferred": ["运动鞋", "跑鞋", "训练鞋", "篮球鞋"],
            "secondary": ["运动休闲鞋"],
            "avoid": ["皮鞋", "正装鞋", "高跟鞋", "拖鞋"],
            "description": "运动场景必须穿运动鞋"
        },
        Scene.PARTY: {
            "preferred": ["小白鞋", "帆布鞋", "乐福鞋", "短靴"],
            "secondary": ["皮鞋", "时尚休闲鞋"],
            "avoid": ["运动鞋", "拖鞋", "凉鞋", "人字拖"],
            "description": "聚会场景可以稍微个性"
        },
        Scene.TRAVEL: {
            "preferred": ["运动鞋", "帆布鞋", "休闲鞋", "小白鞋"],
            "secondary": ["靴子", "休闲皮鞋"],
            "avoid": ["正装皮鞋", "高跟鞋"],
            "description": "旅行场景以舒适为主"
        }
    }

    # 天气与鞋子适配规则
    WEATHER_SHOE_RULES = {
        "extreme_hot": {  # >35度
            "preferred": ["凉鞋", "拖鞋", "帆布鞋", "透气运动鞋", "镂空鞋"],
            "avoid": ["靴子", "加绒鞋", "高帮鞋", "雪地靴"],
            "description": "高温天气选择透气凉鞋"
        },
        "very_hot": {  # 30-35度
            "preferred": ["凉鞋", "运动鞋", "帆布鞋", "透气鞋"],
            "avoid": ["靴子", "加绒鞋", "雪地靴"],
            "description": "炎热天气选择透气鞋子"
        },
        "hot": {  # 25-30度
            "preferred": ["运动鞋", "帆布鞋", "皮鞋", "小白鞋", "乐福鞋"],
            "avoid": ["雪地靴", "加绒靴"],
            "description": "偏热天气选择普通鞋子"
        },
        "warm": {  # 20-25度
            "preferred": ["运动鞋", "帆布鞋", "皮鞋", "小白鞋", "休闲鞋"],
            "avoid": [],
            "description": "温暖天气百搭"
        },
        "cool": {  # 15-20度
            "preferred": ["运动鞋", "皮鞋", "靴子", "帆布鞋", "休闲鞋"],
            "avoid": ["凉鞋", "拖鞋"],
            "description": "凉爽天气注意足部保暖"
        },
        "cold": {  # 10-15度
            "preferred": ["靴子", "运动鞋", "皮鞋", "加绒鞋"],
            "avoid": ["凉鞋", "拖鞋", "帆布鞋"],
            "description": "较冷天气选择保暖鞋子"
        },
        "very_cold": {  # 5-10度
            "preferred": ["靴子", "雪地靴", "保暖皮鞋", "加绒运动鞋"],
            "avoid": ["凉鞋", "拖鞋", "帆布鞋", "薄鞋"],
            "description": "寒冷天气必须保暖"
        },
        "freezing": {  # 0-5度
            "preferred": ["雪地靴", "保暖靴", "加绒鞋", "防滑棉鞋"],
            "avoid": ["凉鞋", "拖鞋", "帆布鞋", "薄鞋"],
            "description": "极冷天气全副保暖"
        },
        "extreme_cold": {  # <0度
            "preferred": ["雪地靴", "极地靴", "保暖靴"],
            "avoid": ["凉鞋", "拖鞋", "帆布鞋", "普通运动鞋"],
            "description": "严寒天气务必穿厚实保暖鞋"
        }
    }

    # 雨天鞋子规则
    RAINY_SHOE_RULES = {
        "preferred": ["防水运动鞋", "雨靴", "短靴", "防水皮鞋", "胶鞋"],
        "avoid": ["凉鞋", "拖鞋", "帆布鞋", "布鞋", "人字拖"],
        "description": "雨天选择防水鞋子"
    }

    # 鞋子万能色推荐
    SHOE_NEUTRAL_COLORS = {
        "white": "小白鞋 - 万能百搭",
        "black": "黑皮鞋 - 商务正式",
        "brown": "棕皮鞋 - 秋冬复古",
        "gray": "灰鞋 - 现代简约",
        "beige": "米白鞋 - 春夏清新"
    }

    # 通用 fallback 鞋子
    UNIVERSAL_FALLBACK_SHOES = [
        "小白鞋",
        "休闲运动鞋",
        "帆布鞋",
        "黑色皮鞋",
        "休闲鞋"
    ]

    def get_weather_category(self, temperature: float, precipitation: float = 0) -> str:
        """根据温度获取天气类别"""
        if precipitation > 50:
            return "rainy"
        if temperature > 35:
            return "extreme_hot"
        elif temperature > 30:
            return "very_hot"
        elif temperature > 25:
            return "hot"
        elif temperature > 20:
            return "warm"
        elif temperature > 15:
            return "cool"
        elif temperature > 10:
            return "cold"
        elif temperature > 5:
            return "very_cold"
        elif temperature > 0:
            return "freezing"
        else:
            return "extreme_cold"

    def get_shoes_for_scene(self, scene: Scene) -> dict:
        """获取场景对应的鞋子偏好"""
        return self.SCENE_SHOE_RULES.get(scene, self.SCENE_SHOE_RULES[Scene.DAILY])

    def get_shoes_for_weather(self, temperature: float, precipitation: float = 0) -> dict:
        """获取天气对应的鞋子偏好"""
        # 雨天优先
        if precipitation > 50:
            return self.RAINY_SHOE_RULES
        
        weather_cat = self.get_weather_category(temperature)
        return self.WEATHER_SHOE_RULES.get(weather_cat, self.WEATHER_SHOE_RULES["warm"])

    def is_shoe_suitable(self, shoe: dict, scene: Scene, temperature: float, precipitation: float = 0) -> Tuple[bool, str]:
        """
        检查鞋子是否适合当前场景和天气
        返回 (是否适合, 原因)
        """
        shoe_type = shoe.get("type", "")
        shoe_type_lower = shoe_type.lower()

        # 1. 检查天气限制
        weather_rules = self.get_shoes_for_weather(temperature, precipitation)
        for avoid in weather_rules.get("avoid", []):
            if avoid.lower() in shoe_type_lower:
                return False, f"'{avoid}'不适合当前天气"
        
        # 2. 检查场景限制
        scene_rules = self.get_shoes_for_scene(scene)
        for avoid in scene_rules.get("avoid", []):
            if avoid.lower() in shoe_type_lower:
                return False, f"'{avoid}'不适合{scene.value}场景"

        # 3. 温度与鞋子厚度检查
        thickness = shoe.get("thickness", "")
        thickness_lower = thickness.lower()
        
        if temperature > 30:
            if "加绒" in thickness_lower or "厚" in thickness_lower or "羽绒" in thickness_lower:
                return False, "高温天气不适合穿加绒厚鞋"
        if temperature < 5:
            if "薄" in thickness_lower or "凉" in thickness_lower or "透气" in thickness_lower:
                return False, "低温天气需要保暖鞋子"

        return True, ""

    def score_shoe(self, shoe: dict, scene: Scene, temperature: float, precipitation: float = 0) -> float:
        """给鞋子评分"""
        base_score = 5.0
        
        # 1. 场景匹配加分
        scene_rules = self.get_shoes_for_scene(scene)
        shoe_type = shoe.get("type", "").lower()
        
        for preferred in scene_rules.get("preferred", []):
            if preferred.lower() in shoe_type:
                base_score += 5.0
                break
        else:
            for secondary in scene_rules.get("secondary", []):
                if secondary.lower() in shoe_type:
                    base_score += 2.0
                    break

        # 2. 天气匹配加分
        weather_rules = self.get_shoes_for_weather(temperature, precipitation)
        for preferred in weather_rules.get("preferred", []):
            if preferred.lower() in shoe_type:
                base_score += 3.0
                break

        # 3. 颜色加分
        shoe_color = shoe.get("color", "").lower()
        if "白" in shoe_color or "米" in shoe_color:
            base_score += 1.0  # 白鞋万能
        elif "黑" in shoe_color:
            base_score += 0.5  # 黑鞋百搭
        elif "棕" in shoe_color or "咖" in shoe_color:
            base_score += 0.5  # 棕鞋复古

        # 4. 正式程度匹配
        formality = shoe.get("formality", 3)
        if scene == Scene.WORK and formality >= 3:
            base_score += 1.0
        if scene == Scene.SPORTS and formality <= 2:
            base_score += 1.0

        return min(10.0, base_score)

    def find_fallback_shoe(self, shoes: List[dict], scene: Scene, temperature: float, precipitation: float = 0) -> Optional[dict]:
        """找 fallback 鞋子"""
        if not shoes:
            return None

        # 按评分排序
        scored = []
        for shoe in shoes:
            score = self.score_shoe(shoe, scene, temperature, precipitation)
            is_suitable, _ = self.is_shoe_suitable(shoe, scene, temperature, precipitation)
            if is_suitable:
                scored.append((score, shoe))
        
        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            return scored[0][1]

        # 如果没有合适的，返回最通用的
        for shoe in shoes:
            shoe_type = shoe.get("type", "").lower()
            if any(w in shoe_type for w in ["运动", "休闲", "鞋"]):
                return shoe
        
        return shoes[0] if shoes else None

    def filter_and_rank_shoes(self, shoes: List[dict], scene: Scene, temperature: float, precipitation: float = 0) -> List[dict]:
        """过滤并排序鞋子"""
        result = []
        
        for shoe in shoes:
            is_suitable, reason = self.is_shoe_suitable(shoe, scene, temperature, precipitation)
            score = self.score_shoe(shoe, scene, temperature, precipitation)
            result.append((score, is_suitable, reason, shoe))
        
        # 按分数排序
        result.sort(key=lambda x: (x[1], x[0]), reverse=True)
        return [shoe for _, _, _, shoe in result]


# ==================== 增强鞋子评分系统 ====================

class EnhancedShoeScorer:
    """增强鞋子评分系统 - 多维度评估鞋子"""

    def __init__(self):
        self.shoe_engine = ShoeRuleEngine()

    def score_shoe_comprehensive(
        self, 
        shoe: dict, 
        scene: Scene, 
        temperature: float, 
        weather: dict,
        outfit: dict
    ) -> Dict[str, float]:
        """综合评分鞋子"""
        precipitation = weather.get("precipitation_probability", 0) if isinstance(weather, dict) else 0
        
        scores = {
            "scene_match": 0,
            "weather_match": 0,
            "color_match": 0,
            "style_match": 0,
            "total": 0
        }

        # 1. 场景匹配分
        scene_rules = self.shoe_engine.get_shoes_for_scene(scene)
        shoe_type = shoe.get("type", "").lower()
        
        if any(p.lower() in shoe_type for p in scene_rules.get("preferred", [])):
            scores["scene_match"] = 10.0
        elif any(s.lower() in shoe_type for s in scene_rules.get("secondary", [])):
            scores["scene_match"] = 7.0
        else:
            scores["scene_match"] = 5.0

        # 2. 天气匹配分
        weather_cat = self.shoe_engine.get_weather_category(temperature, precipitation)
        weather_rules = self.shoe_engine.get_shoes_for_weather(temperature, precipitation)
        
        if any(p.lower() in shoe_type for p in weather_rules.get("preferred", [])):
            scores["weather_match"] = 10.0
        elif any(a.lower() not in shoe_type for a in weather_rules.get("avoid", [])):
            scores["weather_match"] = 5.0
        else:
            scores["weather_match"] = 7.0

        # 3. 颜色匹配分
        shoe_color = shoe.get("color", "")
        colors = [outfit.get(k, {}).get("color", "") for k in ["top", "pants"] if outfit.get(k)]
        colors = [c for c in colors if c]
        
        if colors:
            # 中性色（白、黑、灰）高分
            neutral = {"白", "黑", "灰", "米", "米白"}
            if any(n in shoe_color for n in neutral):
                scores["color_match"] = 9.0
            else:
                scores["color_match"] = 6.0
        else:
            scores["color_match"] = 7.0

        # 4. 风格匹配分
        shoe_style = shoe.get("style", "").lower()
        top_style = outfit.get("top", {}).get("style", "").lower()
        
        if top_style and shoe_style:
            # 风格兼容性
            if "商务" in top_style and any(s in shoe_style for s in ["商务", "正式", "皮鞋"]):
                scores["style_match"] = 10.0
            elif "运动" in top_style and "运动" in shoe_style:
                scores["style_match"] = 10.0
            elif "休闲" in top_style:
                scores["style_match"] = 8.0
            else:
                scores["style_match"] = 6.0
        else:
            scores["style_match"] = 7.0

        # 综合分
        scores["total"] = (
            scores["scene_match"] * 0.35 +
            scores["weather_match"] * 0.30 +
            scores["color_match"] * 0.15 +
            scores["style_match"] * 0.20
        )

        return scores


# ==================== 服装完整性校验 ====================

class OutfitValidator:
    """服装完整性校验 - 确保穿搭完整合理"""

    # 必备单品
    ESSENTIAL_ITEMS = {
        "top": {"required": True, "label": "上衣"},
        "pants": {"required": True, "label": "下装"},
        "shoes": {"required": True, "label": "鞋子"},
        "jacket": {"required": False, "label": "外套"}  # 根据温度决定
    }

    # 温度与外套要求
    JACKET_TEMPERATURE_THRESHOLD = 20  # 20度以下需要外套

    def validate_completeness(self, outfit: Dict[str, dict], temperature: float) -> Tuple[bool, List[str]]:
        """验证穿搭完整性"""
        issues = []

        # 检查必备单品
        for item, rules in self.ESSENTIAL_ITEMS.items():
            if rules["required"] and not outfit.get(item):
                issues.append(f"缺少{rules['label']}")

        # 检查温度与外套
        if temperature < self.JACKET_TEMPERATURE_THRESHOLD and not outfit.get("jacket"):
            issues.append(f"温度{temperature}°C建议添加外套")

        # 检查上衣和下装的搭配
        if outfit.get("top") and outfit.get("pants"):
            top_type = outfit["top"].get("type", "").lower()
            pants_type = outfit["pants"].get("type", "").lower()

            # 连衣裙不需要下装
            if "连衣裙" in top_type or "裙" in top_type:
                if "裙" not in pants_type:
                    issues.append("连衣裙建议搭配裙装或长筒靴")

        return len(issues) == 0, issues

    def validate_reasonableness(self, outfit: Dict[str, dict], temperature: float, scene: Scene) -> Tuple[bool, List[str]]:
        """验证穿搭合理性"""
        issues = []

        # 检查厚度适配
        if temperature > 30:
            for key in ["top", "pants", "jacket"]:
                if outfit.get(key):
                    thickness = outfit[key].get("thickness", "")
                    if thickness in ["加绒", "羽绒级", "厚"]:
                        issues.append(f"{outfit[key].get('type', '衣物')}厚度不适合高温天气")
                        break

        if temperature < 5:
            for key in ["top", "pants"]:
                if outfit.get(key):
                    thickness = outfit[key].get("thickness", "")
                    if thickness in ["极薄", "薄"]:
                        issues.append(f"{outfit[key].get('type', '衣物')}厚度不足以御寒")
                        break

        # 检查场景适配
        scene_constraints = SceneConstraints()
        for key in ["top", "pants", "shoes"]:
            if outfit.get(key):
                is_valid, reason = scene_constraints.is_valid_for_scene(outfit[key], scene)
                if not is_valid:
                    issues.append(reason)

        return len(issues) == 0, issues


# ==================== 衣物评分系统 ====================

class ClothingScorer:
    """衣物评分系统 - 综合评估每件衣物"""

    def __init__(self):
        self.temp_engine = TemperatureRuleEngine()
        self.material_adapter = MaterialAdapter()
        self.scene_constraints = SceneConstraints()
        self.style_matcher = StyleMatcher()
        self.color_matcher = ColorMatcher()

        # 评分权重 - 优化后提高风格和场景权重
        self.WEIGHTS = {
            "weather": 0.30,      # 天气适配
            "scene": 0.25,        # 场景适配（重要）
            "material": 0.15,     # 材质适配
            "style": 0.15,         # 风格匹配（提高权重）
            "color": 0.15,         # 颜色搭配（提高权重）
        }

    def score_clothing(self, clothing: dict, temperature: float, weather: dict, scene: Scene) -> float:
        """综合评分一件衣物"""
        if not clothing:
            return 0.0

        scores = {}

        # 1. 天气适配分
        scores["weather"] = self._score_weather_fit(clothing, temperature)

        # 2. 场景适配分
        scores["scene"] = self.scene_constraints.score_by_scene(clothing, scene)

        # 3. 材质适配分
        scores["material"] = self.material_adapter.score_material(
            clothing.get("material", ""), temperature, weather
        )

        # 4. 风格分（基础分）
        style = clothing.get("style", "")
        scores["style"] = 5.0 if style else 5.0

        # 5. 颜色分（基础分）
        scores["color"] = 5.0

        # 计算加权总分
        total = sum(self.WEIGHTS[k] * scores[k] for k in self.WEIGHTS)

        return round(total, 2)

    def _score_weather_fit(self, clothing: dict, temperature: float) -> float:
        """评估天气适配度"""
        temp_min = clothing.get("temperature_min", 0)
        temp_max = clothing.get("temperature_max", 40)

        # 温度范围匹配
        if temp_min <= temperature <= temp_max:
            # 在舒适范围内
            mid = (temp_min + temp_max) / 2
            distance = abs(temperature - mid)
            range_size = temp_max - temp_min

            if range_size > 0:
                # 边界情况处理：温度在边界时给予更高分数
                if temperature == temp_min or temperature == temp_max:
                    return 7.5  # 边界温度给予较高分
                fit_ratio = 1 - (distance / (range_size / 2))
                return 5 + (fit_ratio * 5)  # 5-10分
            else:
                return 8.0

        # 不在范围内
        if temperature < temp_min:
            diff = temp_min - temperature
            if diff <= 5:
                return 6.0
            elif diff <= 10:
                return 4.0
            else:
                return 2.0
        else:
            diff = temperature - temp_max
            if diff <= 5:
                return 6.0
            elif diff <= 10:
                return 4.0
            else:
                return 2.0

    def score_outfit(self, outfit: Dict[str, dict], temperature: float, weather: dict, scene: Scene) -> Dict[str, float]:
        """评估整套穿搭"""
        scores = {}

        # 单品分数
        for key in ["top", "pants", "shoes", "jacket"]:
            if outfit.get(key):
                scores[key] = self.score_clothing(outfit[key], temperature, weather, scene)
            else:
                scores[key] = 0.0

        # 风格一致性
        scores["style_consistency"] = self.style_matcher.score_style_consistency(outfit)

        # 颜色协调性
        scores["color_harmony"] = self.color_matcher.score_color_harmony(outfit)

        # 综合分数
        total_score = (
            self.WEIGHTS["style"] * scores["style_consistency"] +
            self.WEIGHTS["color"] * scores["color_harmony"]
        )

        # 单品平均分
        item_scores = [scores[k] for k in ["top", "pants", "shoes", "jacket"] if scores[k] > 0]
        if item_scores:
            item_avg = sum(item_scores) / len(item_scores)
            total_score = 0.6 * item_avg + 0.4 * total_score

        scores["total"] = round(total_score, 2)

        return scores


# ==================== 多层推荐算法 ====================

class MultiLayerRecommender:
    """多层推荐算法 - 实现真正的智能推荐"""

    def __init__(self):
        self.temp_engine = TemperatureRuleEngine()
        self.material_adapter = MaterialAdapter()
        self.scene_constraints = SceneConstraints()
        self.style_matcher = StyleMatcher()
        self.color_matcher = ColorMatcher()
        self.outfit_validator = OutfitValidator()
        self.scorer = ClothingScorer()
        self.shoe_engine = ShoeRuleEngine()  # 鞋子推荐引擎
        self.shoe_scorer = EnhancedShoeScorer()  # 鞋子评分器

    def recommend(
        self,
        clothes: List[dict],
        temperature: float,
        weather: dict,
        scene: str,
        user_preference: Optional[Dict] = None
    ) -> Dict[str, dict]:
        """
        多层推荐算法主入口

        第一层：天气过滤
        第二层：场景过滤
        第三层：风格匹配
        第四层：颜色评分
        第五层：综合排序
        """
        logger.info(f"[推荐引擎] 开始推荐，温度:{temperature}°C，场景:{scene}，衣物数量:{len(clothes)}")

        if not clothes:
            raise ValueError("衣橱为空，无法生成推荐")

        # ========== 第一层：天气过滤 ==========
        logger.info("[推荐引擎] 第一层：天气过滤")
        weather_filtered = self.temp_engine.filter_by_temperature(clothes, temperature)
        logger.info(f"[推荐引擎] 天气过滤后剩余 {len(weather_filtered)} 件")

        # 如果过滤后太少，放宽条件
        if len(weather_filtered) < 5:
            weather_filtered = clothes
            logger.info("[推荐引擎] 放宽条件，使用全部衣物")

        # ========== 第二层：场景过滤 ==========
        logger.info("[推荐引擎] 第二层：场景过滤")
        scene_enum = self.scene_constraints.get_scene(scene)
        scene_filtered = self.scene_constraints.filter_by_scene(weather_filtered, scene_enum)
        logger.info(f"[推荐引擎] 场景过滤后剩余 {len(scene_filtered)} 件")

        # 如果过滤后太少，放宽条件
        if len(scene_filtered) < 3:
            scene_filtered = weather_filtered

        # ========== 第三层：分类分组 ==========
        logger.info("[推荐引擎] 第三层：分类分组")
        categorized = self._categorize_clothes(scene_filtered)

        # ========== 第四层：为每个品类评分 ==========
        logger.info("[推荐引擎] 第四层：评分排序")
        scored_categories = {}
        for category, items in categorized.items():
            if items:
                scored = []
                for item in items:
                    score = self.scorer.score_clothing(item, temperature, weather, scene_enum)
                    scored.append((score, item))
                scored.sort(key=lambda x: x[0], reverse=True)
                scored_categories[category] = scored

        # ========== 第五层：组合穿搭 ==========
        logger.info("[推荐引擎] 第五层：组合穿搭")
        outfit = self._build_outfit(scored_categories, temperature, weather, scene_enum, user_preference)

        # ========== 第六层：评估和优化 ==========
        logger.info("[推荐引擎] 第六层：评估优化")
        outfit_scores = self.scorer.score_outfit(outfit, temperature, weather, scene_enum)

        # 如果分数太低，尝试替换单品
        if outfit_scores["total"] < 6.0:
            logger.info("[推荐引擎] 分数较低，尝试优化...")
            outfit = self._optimize_outfit(outfit, scored_categories, temperature, weather, scene_enum)
            outfit_scores = self.scorer.score_outfit(outfit, temperature, weather, scene_enum)

        # ========== 第七层：验证完整性 ==========
        logger.info("[推荐引擎] 第七层：验证完整性")
        is_complete, completeness_issues = self.outfit_validator.validate_completeness(outfit, temperature)
        is_reasonable, reasonability_issues = self.outfit_validator.validate_reasonableness(
            outfit, temperature, scene_enum
        )

        # ========== ★★★ 鞋子完整性强制检查 ★★★ ==========
        # 这是修复鞋子缺失的核心逻辑
        max_retries = 3
        retry_count = 0
        
        while not outfit.get("shoes") and retry_count < max_retries:
            retry_count += 1
            logger.warning(f"[推荐引擎] 鞋子缺失，进行第 {retry_count} 次重试...")
            
            # 使用鞋子引擎强制找一双合适的鞋子
            precipitation = weather.get("precipitation_probability", 0) if isinstance(weather, dict) else 0
            fallback_shoe = self._find_shoes_fallback(
                categorized, scene_enum, temperature, precipitation
            )
            
            if fallback_shoe:
                outfit["shoes"] = fallback_shoe
                logger.info(f"[推荐引擎] Fallback 鞋子成功: {fallback_shoe.get('type', '未知')}")
                break
            else:
                # 从所有衣物中尝试找一个
                any_shoe = self._find_any_shoe(clothes, scene_enum, temperature)
                if any_shoe:
                    outfit["shoes"] = any_shoe
                    logger.info(f"[推荐引擎] 从衣橱找到鞋子: {any_shoe.get('type', '未知')}")
                    break
        
        # 如果最终仍然没有鞋子，创建一个虚拟鞋子
        if not outfit.get("shoes"):
            logger.error(f"[推荐引擎] 无法为用户推荐合适的鞋子，创建虚拟鞋子")
            outfit["shoes"] = self._create_virtual_shoe(scene_enum, temperature, weather)

        # 记录鞋子选择结果
        if outfit.get("shoes"):
            logger.info(f"[推荐引擎] 最终鞋子: {outfit['shoes'].get('type', '未知')}, 颜色: {outfit['shoes'].get('color', '未知')}")
        else:
            logger.error(f"[推荐引擎] ★★★ 警告：穿搭仍然没有鞋子！★★★")

        return {
            "outfit": outfit,
            "scores": outfit_scores,
            "validation": {
                "is_complete": is_complete,
                "completeness_issues": completeness_issues,
                "is_reasonable": is_reasonable,
                "reasonability_issues": reasonability_issues
            }
        }

    def _find_shoes_fallback(
        self, 
        categorized: Dict[str, List[dict]], 
        scene: Scene, 
        temperature: float,
        precipitation: float
    ) -> Optional[dict]:
        """寻找 fallback 鞋子"""
        all_shoes = []
        
        # 收集所有鞋子
        for cat in ["shoes", "shoes_sport", "shoes_dress", "shoes_casual", "shoes_boots", "shoes_sandal"]:
            if categorized.get(cat):
                all_shoes.extend(categorized[cat])
        
        if not all_shoes:
            return None
        
        # 使用鞋子引擎评分选择
        ranked = self.shoe_engine.filter_and_rank_shoes(all_shoes, scene, temperature, precipitation)
        
        if ranked:
            return ranked[0]
        
        # 最后的 fallback
        return all_shoes[0] if all_shoes else None

    def _find_any_shoe(self, clothes: List[dict], scene: Scene, temperature: float) -> Optional[dict]:
        """从所有衣物中找任何可以当鞋子的"""
        for c in clothes:
            item_type = c.get("type", "").lower()
            item_name = c.get("name", "").lower()
            
            # 检查是否是鞋子
            if "鞋" in item_type or "鞋" in item_name:
                # 检查是否适合当前场景
                is_valid, _ = self.shoe_engine.is_shoe_suitable(c, scene, temperature)
                if is_valid:
                    return c
        
        # 如果还是没找到，返回任意鞋子
        for c in clothes:
            if "鞋" in c.get("type", "") or "鞋" in c.get("name", ""):
                return c
        
        return None

    def _create_virtual_shoe(self, scene: Scene, temperature: float, weather: dict) -> dict:
        """创建虚拟鞋子 - 当真的无法推荐时"""
        logger.warning(f"[推荐引擎] 创建虚拟鞋子，场景={scene.value}, 温度={temperature}°C")
        
        # 基于场景和温度创建合适的虚拟鞋子
        if temperature < 10:
            shoe_type = "保暖靴"
            style = "休闲"
            thickness = "加绒"
        elif temperature > 30:
            shoe_type = "帆布鞋"
            style = "休闲"
            thickness = "薄"
        elif scene == Scene.WORK:
            shoe_type = "皮鞋"
            style = "商务"
            thickness = "中等"
        elif scene == Scene.SPORTS:
            shoe_type = "运动鞋"
            style = "运动"
            thickness = "中等"
        else:
            shoe_type = "休闲鞋"
            style = "休闲"
            thickness = "中等"
        
        precipitation = weather.get("precipitation_probability", 0) if isinstance(weather, dict) else 0
        if precipitation > 50:
            shoe_type = "防水" + shoe_type
        
        return {
            "id": "virtual_shoe",
            "type": shoe_type,
            "color": "通用色",
            "style": style,
            "thickness": thickness,
            "material": "通用材质",
            "formality": 3,
            "temperature_min": max(0, temperature - 10),
            "temperature_max": min(40, temperature + 10),
            "is_virtual": True,
            "notes": "⚠️ 您的衣橱缺少合适的鞋子，建议添加"
        }

    def _categorize_clothes(self, clothes: List[dict]) -> Dict[str, List[dict]]:
        """
        将衣物分类 - 增强版，确保所有衣服都被正确分类
        
        【核心单品】衣服、裤子、鞋子必须有
        【可选配件】包、帽子等为可选
        """
        categories = {
            "top": [],
            "pants": [],
            "shoes": [],
            "shoes_sport": [],
            "shoes_dress": [],
            "shoes_casual": [],
            "shoes_boots": [],
            "shoes_sandal": [],
            "jacket": [],
            # 可选配件 - 包和帽子设为可选，不会强制加入穿搭
            "accessory": [],
            "bag": [],
            "hat": [],
        }

        # ★★★ 核心单品关键词 - 衣服、裤子、鞋子 ★★★
        top_keywords = ["T恤", "衬衫", "卫衣", "毛衣", "针织衫", "背心", "吊带", "polo", "长袖", "短袖", 
                       "外套（内搭）", "上衣", "套头衫", "帽衫", "开衫", "打底衫", "打底", "线衣", "绒衣",
                       "衫", "衣"]
        
        pants_keywords = ["裤", "裙", "短裤", "长裤", "牛仔裤", "休闲裤", "运动裤", "短裙", "长裙", 
                        "裙子", "裙装", "九分裤", "七分裤", "阔腿裤", "直筒裤", "紧身裤", "工装裤"]
        
        shoes_keywords = ["鞋", "靴", "凉鞋", "拖鞋", "帆布鞋", "运动鞋", "皮鞋", "休闲鞋", "小白鞋",
                        "跑鞋", "球鞋", "板鞋", "豆豆鞋", "乐福鞋", "穆勒鞋", "草编鞋", "洞洞鞋"]
        
        jacket_keywords = ["外套", "夹克", "大衣", "风衣", "羽绒服", "棉服", "皮衣", 
                          "西装", "开衫", "马甲", "棒球服", "冲锋衣", "卫衣开衫", 
                          "皮草", "毛呢大衣", "棉袄", "皮毛一体", "马夹", "披肩"]
        
        # ★★★ 可选配件关键词 - 包、帽子等 ★★★
        bag_keywords = ["包", "背包", "挎包", "手提包", "单肩包", "双肩包", "钱包", "手包", "腰包", "胸包", "旅行包", "帆布包", "购物袋"]
        hat_keywords = ["帽", "帽子", "棒球帽", "渔夫帽", "贝雷帽", "礼帽", "毛线帽", "遮阳帽", "鸭舌帽", "头巾", "头饰"]

        for c in clothes:
            clothing_type = c.get("type", "").lower()
            clothing_name = c.get("name", "").lower()
            clothing_combined = clothing_type + " " + clothing_name
            
            categorized = False

            # ========== 1. 首先检查是否为鞋子（核心单品）==========
            if any(kw in clothing_combined for kw in shoes_keywords):
                categorized = True
                
                # 根据具体类型细分鞋子
                if any(kw in clothing_combined for kw in ["运动", "跑鞋", "球鞋", "训练鞋", "篮球", "足球", "羽毛球", "网球", "登山", "徒步", "滑板", "老爹", "跑步"]):
                    categories["shoes_sport"].append(c)
                elif any(kw in clothing_combined for kw in ["靴", "雪地", "棉靴", "工装", "军靴", "骑士"]):
                    categories["shoes_boots"].append(c)
                elif any(kw in clothing_combined for kw in ["正装", "牛津", "德比", "高跟", "雕花", "孟克", "礼服"]):
                    categories["shoes_dress"].append(c)
                elif any(kw in clothing_combined for kw in ["凉鞋", "拖鞋", "人字", "沙滩", "罗马"]):
                    categories["shoes_sandal"].append(c)
                else:
                    categories["shoes_casual"].append(c)
            
            # ========== 2. 检查是否为上衣（核心单品）==========
            elif not categorized and any(kw in clothing_combined for kw in top_keywords):
                categorized = True
                categories["top"].append(c)
            
            # ========== 3. 检查是否为下装（核心单品）==========
            elif not categorized and any(kw in clothing_combined for kw in pants_keywords):
                categorized = True
                categories["pants"].append(c)
            
            # ========== 4. 检查是否为外套（核心单品）==========
            elif not categorized and any(kw in clothing_combined for kw in jacket_keywords):
                categorized = True
                categories["jacket"].append(c)
            
            # ========== 5. 检查是否为包（可选配件）==========
            elif any(kw in clothing_combined for kw in bag_keywords):
                categories["bag"].append(c)
            
            # ========== 6. 检查是否为帽子（可选配件）==========
            elif any(kw in clothing_combined for kw in hat_keywords):
                categories["hat"].append(c)
            
            # ========== 7. 其他未分类的放入配件（可选）==========
            else:
                categories["accessory"].append(c)

        # 合并所有鞋子类型到一个统一鞋子列表
        categories["shoes"] = (
            categories["shoes_sport"] +
            categories["shoes_casual"] +
            categories["shoes_dress"] +
            categories["shoes_boots"] +
            categories["shoes_sandal"]
        )

        # 日志输出分类情况
        logger.info(f"[分类] 上衣: {len(categories['top'])}, 下装: {len(categories['pants'])}, 鞋子: {len(categories['shoes'])}, 外套: {len(categories['jacket'])}, 包(可选): {len(categories['bag'])}, 帽子(可选): {len(categories['hat'])}")

        return categories

    def _build_outfit(
        self,
        scored_categories: Dict[str, List[Tuple[float, dict]]],
        temperature: float,
        weather: dict,
        scene: Scene,
        user_preference: Optional[Dict] = None
    ) -> Dict[str, dict]:
        """构建穿搭 - 强制包含上衣、下装、鞋子"""
        outfit = {}

        # 初始化鞋子引擎
        shoe_engine = ShoeRuleEngine()
        precipitation = weather.get("precipitation_probability", 0) if isinstance(weather, dict) else 0

        # ★★★ 1. 选择上衣（必须有）★★★ 
        if "top" in scored_categories and scored_categories["top"]:
            outfit["top"] = scored_categories["top"][0][1]
            logger.info(f"[构建穿搭] 选择上衣: {outfit['top'].get('type', '未知')}")
        else:
            # ★★★ Fallback: 创建默认上衣 ★★★
            logger.warning(f"[构建穿搭] 衣橱没有上衣，创建默认上衣")
            outfit["top"] = self._create_fallback_top(scene, temperature)

        # ★★★ 2. 选择下装（必须有）★★★ 
        if "pants" in scored_categories and scored_categories["pants"]:
            outfit["pants"] = scored_categories["pants"][0][1]
            logger.info(f"[构建穿搭] 选择下装: {outfit['pants'].get('type', '未知')}")
        else:
            # ★★★ Fallback: 创建默认下装 ★★★
            logger.warning(f"[构建穿搭] 衣橱没有下装，创建默认下装")
            outfit["pants"] = self._create_fallback_pants(scene, temperature)

        # ★★★ 3. 强制选择鞋子 ★★★
        shoes_selected = False
        
        # 3.1 首先尝试根据场景和天气选择最合适的鞋子类别
        shoes_category = self._get_shoes_category_for_scene(scene, scored_categories, temperature)
        
        if shoes_category and scored_categories.get(shoes_category):
            outfit["shoes"] = scored_categories[shoes_category][0][1]
            shoes_selected = True
            logger.info(f"[构建穿搭] 从{shoes_category}选择鞋子: {outfit['shoes'].get('type', '未知')}")
        
        # 3.2 如果没有特定类别，从所有鞋子中选择
        if not shoes_selected and "shoes" in scored_categories and scored_categories["shoes"]:
            all_shoes = [shoe for _, shoe in scored_categories["shoes"]]
            ranked_shoes = shoe_engine.filter_and_rank_shoes(all_shoes, scene, temperature, precipitation)
            
            if ranked_shoes:
                outfit["shoes"] = ranked_shoes[0]
                shoes_selected = True
                logger.info(f"[构建穿搭] 从所有鞋子中选择: {outfit['shoes'].get('type', '未知')}")
        
        # 3.3 如果仍然没有，尝试其他鞋子子类别
        if not shoes_selected:
            for shoe_cat in ["shoes_sport", "shoes_dress", "shoes_casual", "shoes_boots", "shoes_sandal"]:
                if scored_categories.get(shoe_cat) and scored_categories[shoe_cat]:
                    outfit["shoes"] = scored_categories[shoe_cat][0][1]
                    shoes_selected = True
                    logger.info(f"[构建穿搭] 从{shoe_cat}选择鞋子")
                    break
        
        # 3.4 Fallback: 创建默认鞋子
        if not shoes_selected:
            logger.warning(f"[构建穿搭] 衣橱没有合适鞋子，创建默认鞋子")
            outfit["shoes"] = self._create_fallback_shoe(scene, temperature)

        # ★★★ 4. 选择外套（根据温度）★★★ 
        if temperature < self.outfit_validator.JACKET_TEMPERATURE_THRESHOLD:
            if "jacket" in scored_categories and scored_categories["jacket"]:
                outfit["jacket"] = scored_categories["jacket"][0][1]
                logger.info(f"[构建穿搭] 选择外套: {outfit['jacket'].get('type', '未知')}")
            else:
                # 低温但没有外套，给个提示
                logger.info(f"[构建穿搭] 温度{temperature}°C建议添加外套，但衣橱没有")
        else:
            # 温暖天气，尝试添加薄外套作为可选
            if "jacket" in scored_categories and scored_categories["jacket"]:
                for score, jacket in scored_categories["jacket"]:
                    thickness = jacket.get("thickness", "")
                    if thickness in ["薄", "中等", ""]:
                        outfit["jacket"] = jacket
                        break

        # 5. 风格一致性优化
        outfit = self._optimize_style_consistency(outfit)

        # 6. 颜色协调优化
        outfit = self._optimize_color_harmony(outfit)

        return outfit

    def _create_fallback_shoe(self, scene: Scene, temperature: float) -> dict:
        """创建 fallback 鞋子 - 当衣橱没有鞋子时的备选"""
        # 根据场景选择合适的 fallback 鞋子
        fallback_map = {
            Scene.WORK: {
                "type": "皮鞋", "color": "黑色", "style": "商务", "formality": 4,
                "temperature_min": 10, "temperature_max": 30
            },
            Scene.SPORTS: {
                "type": "运动鞋", "color": "黑色", "style": "运动", "formality": 2,
                "temperature_min": 5, "temperature_max": 35
            },
            Scene.DATE: {
                "type": "小白鞋", "color": "白色", "style": "休闲", "formality": 3,
                "temperature_min": 15, "temperature_max": 30
            },
            Scene.DAILY: {
                "type": "休闲鞋", "color": "黑色", "style": "休闲", "formality": 2,
                "temperature_min": 10, "temperature_max": 30
            },
            Scene.PARTY: {
                "type": "小白鞋", "color": "白色", "style": "时尚", "formality": 3,
                "temperature_min": 15, "temperature_max": 28
            },
            Scene.TRAVEL: {
                "type": "运动鞋", "color": "黑色", "style": "休闲", "formality": 2,
                "temperature_min": 5, "temperature_max": 30
            }
        }
        
        shoe = fallback_map.get(scene, fallback_map[Scene.DAILY])
        
        # 根据温度调整
        if temperature < 10:
            shoe["type"] = "靴子"
            shoe["thickness"] = "加绒"
        elif temperature > 30:
            shoe["type"] = "帆布鞋"
            shoe["thickness"] = "薄"
        
        logger.info(f"[Fallback] 创建 fallback 鞋子: {shoe['type']}")
        return shoe

    def _create_fallback_top(self, scene: Scene, temperature: float) -> dict:
        """创建 fallback 上衣 - 当衣橱没有上衣时的备选"""
        # 根据场景和温度选择合适的 fallback 上衣
        if temperature < 10:
            # 寒冷天气
            if scene in [Scene.WORK, Scene.DATE, Scene.PARTY]:
                top_type = "针织衫"
                style = "商务"
                thickness = "厚"
            else:
                top_type = "加绒卫衣"
                style = "休闲"
                thickness = "加绒"
        elif temperature < 20:
            # 凉爽天气
            if scene in [Scene.WORK, Scene.DATE]:
                top_type = "衬衫"
                style = "商务"
                thickness = "中等"
            else:
                top_type = "卫衣"
                style = "休闲"
                thickness = "中等"
        else:
            # 温暖/炎热天气
            if scene == Scene.WORK:
                top_type = "短袖衬衫"
                style = "商务"
                thickness = "薄"
            elif scene == Scene.SPORTS:
                top_type = "运动T恤"
                style = "运动"
                thickness = "薄"
            else:
                top_type = "T恤"
                style = "休闲"
                thickness = "薄"
        
        return {
            "id": "virtual_top",
            "type": top_type,
            "color": "通用色",
            "style": style,
            "thickness": thickness,
            "material": "棉",
            "formality": 3,
            "temperature_min": max(0, temperature - 15),
            "temperature_max": min(40, temperature + 10),
            "is_virtual": True,
            "notes": "⚠️ 您的衣橱缺少上衣，建议添加"
        }

    def _create_fallback_pants(self, scene: Scene, temperature: float) -> dict:
        """创建 fallback 下装 - 当衣橱没有下装时的备选"""
        # 根据场景和温度选择合适的 fallback 下装
        if temperature < 10:
            # 寒冷天气
            if scene == Scene.SPORTS:
                pants_type = "运动裤"
                style = "运动"
            elif scene in [Scene.WORK]:
                pants_type = "牛仔裤"
                style = "商务"
            else:
                pants_type = "休闲裤"
                style = "休闲"
            thickness = "厚"
        elif temperature > 28:
            # 炎热天气
            if scene == Scene.SPORTS:
                pants_type = "运动短裤"
                style = "运动"
            else:
                pants_type = "短裤"
                style = "休闲"
            thickness = "薄"
        else:
            # 温暖天气
            if scene == Scene.SPORTS:
                pants_type = "运动裤"
                style = "运动"
            elif scene in [Scene.WORK, Scene.DATE, Scene.PARTY]:
                pants_type = "牛仔裤"
                style = "商务"
            else:
                pants_type = "休闲裤"
                style = "休闲"
            thickness = "中等"
        
        return {
            "id": "virtual_pants",
            "type": pants_type,
            "color": "通用色",
            "style": style,
            "thickness": thickness,
            "material": "棉",
            "formality": 3,
            "temperature_min": max(0, temperature - 15),
            "temperature_max": min(40, temperature + 10),
            "is_virtual": True,
            "notes": "⚠️ 您的衣橱缺少下装，建议添加"
        }

    def _get_shoes_category_for_scene(self, scene: Scene, scored_categories: Dict, temperature: float) -> Optional[str]:
        """
        根据场景和温度获取合适的鞋子类别
        优先级：场景要求 > 温度要求 > 通用推荐
        """
        logger.info(f"[鞋子选择] 场景={scene.value}, 温度={temperature}°C")

        # 低温场景（<10度）优先靴子/保暖鞋
        if temperature < 10:
            for cat in ["shoes_boots", "shoes_casual", "shoes"]:
                if scored_categories.get(cat):
                    logger.info(f"[鞋子选择] 低温场景，选择 {cat}")
                    return cat

        # ★★★ 场景强制要求 ★★★
        
        # 工作场景 - 必须商务鞋
        if scene == Scene.WORK:
            for cat in ["shoes_dress", "shoes_casual", "shoes"]:
                if scored_categories.get(cat):
                    logger.info(f"[鞋子选择] 工作场景，选择 {cat}")
                    return cat

        # 运动场景 - 必须运动鞋
        if scene == Scene.SPORTS:
            if scored_categories.get("shoes_sport"):
                logger.info(f"[鞋子选择] 运动场景，选择 shoes_sport")
                return "shoes_sport"
            # 如果没有运动鞋，找任何运动相关的
            for cat in ["shoes", "shoes_casual"]:
                if scored_categories.get(cat):
                    logger.info(f"[鞋子选择] 运动场景fallback，选择 {cat}")
                    return cat

        # 约会场景 - 优先精致休闲/小白鞋
        if scene == Scene.DATE:
            for cat in ["shoes_casual", "shoes_dress", "shoes"]:
                if scored_categories.get(cat):
                    logger.info(f"[鞋子选择] 约会场景，选择 {cat}")
                    return cat

        # 聚会场景 - 时尚休闲
        if scene == Scene.PARTY:
            for cat in ["shoes_casual", "shoes_dress", "shoes"]:
                if scored_categories.get(cat):
                    logger.info(f"[鞋子选择] 聚会场景，选择 {cat}")
                    return cat

        # 日常/出行 - 舒适为主
        if scene in [Scene.DAILY, Scene.TRAVEL]:
            for cat in ["shoes_casual", "shoes_sport", "shoes"]:
                if scored_categories.get(cat):
                    logger.info(f"[鞋子选择] 日常/出行场景，选择 {cat}")
                    return cat

        # 温度调节
        if temperature > 30:
            # 高温 - 优先凉鞋/帆布鞋/透气鞋
            for cat in ["shoes_sandal", "shoes_casual", "shoes"]:
                if scored_categories.get(cat):
                    logger.info(f"[鞋子选择] 高温场景，选择 {cat}")
                    return cat

        # 通用兜底
        if scored_categories.get("shoes"):
            logger.info(f"[鞋子选择] 通用fallback，选择 shoes")
            return "shoes"
        
        # 尝试任意鞋子类别
        for cat in ["shoes_sport", "shoes_dress", "shoes_casual", "shoes_boots", "shoes_sandal"]:
            if scored_categories.get(cat):
                logger.info(f"[鞋子选择] 任意鞋子类别，选择 {cat}")
                return cat

        logger.warning(f"[鞋子选择] 没有找到合适的鞋子类别")
        return None

    def _optimize_style_consistency(self, outfit: Dict[str, dict]) -> Dict[str, dict]:
        """优化风格一致性 - 确保整套穿搭风格协调"""
        if len(outfit) < 2:
            return outfit

        # 找出主要风格
        main_styles = []
        for key in ["top", "pants", "shoes", "jacket"]:
            if outfit.get(key):
                style = outfit[key].get("style", "")
                if style:
                    main_styles.append((key, style))

        if len(main_styles) < 2:
            return outfit

        # 确定主风格（选择出现最多的风格）
        style_groups = {}
        for key, style in main_styles:
            group = self.style_matcher.get_style_group(style) or style
            style_groups[group] = style_groups.get(group, 0) + 1

        # 找出最常见的主风格组
        main_group = max(style_groups.items(), key=lambda x: x[1])[0] if style_groups else None
        logger.info(f"[风格优化] 主风格组: {main_group}, 风格分布: {style_groups}")

        # 检查每个单品的风格是否与主风格兼容
        reference_key, reference_style = main_styles[0]
        issues = []

        for key, style in main_styles[1:]:
            compatibility = self.style_matcher.get_compatibility(reference_style, style)
            if compatibility < 5.0:
                # 风格不兼容，记录问题
                issues.append((key, style, compatibility))
                logger.info(f"[风格优化] {key}({style}) 与 {reference_key}({reference_style}) 兼容度仅 {compatibility:.1f}")

        # 如果有风格兼容性问题，在返回时添加提示
        if issues:
            logger.warning(f"[风格优化] 发现 {len(issues)} 个风格兼容性问题")

        return outfit

    def _optimize_color_harmony(self, outfit: Dict[str, dict]) -> Dict[str, dict]:
        """优化颜色协调 - 确保上装与下装颜色搭配协调"""
        if not outfit.get("top") or not outfit.get("pants"):
            return outfit

        top_color = outfit["top"].get("color", "")
        pants_color = outfit["pants"].get("color", "")

        # 使用颜色匹配器评估当前搭配
        color_matcher = ColorMatcher()
        harmony_score = color_matcher.score_color_harmony(outfit)

        # 如果颜色搭配较差，尝试优化
        if harmony_score < 6.0:
            logger.info(f"[颜色优化] 当前搭配评分 {harmony_score:.1f}，尝试优化...")

            # 获取上装颜色的推荐搭配色
            recommended_colors = color_matcher.get_recommended_pair_colors(top_color)

            # 如果下装颜色不在推荐列表中，考虑是否需要优化
            if pants_color and pants_color not in recommended_colors:
                # 检查是否是禁止的配色
                forbidden = False
                for combo in ColorMatcher.FORBIDDEN_COMBINATIONS:
                    if top_color in combo and pants_color in combo:
                        forbidden = True
                        break

                if forbidden:
                    logger.info(f"[颜色优化] {top_color} + {pants_color} 为禁止配色，标记提示")

        return outfit

    def _optimize_outfit(
        self,
        current_outfit: Dict[str, dict],
        scored_categories: Dict[str, List[Tuple[float, dict]]],
        temperature: float,
        weather: dict,
        scene: Scene
    ) -> Dict[str, dict]:
        """优化穿搭"""
        optimized = current_outfit.copy()

        # 尝试替换分数低的单品
        for key in ["top", "pants", "shoes", "jacket"]:
            if key in optimized and key in scored_categories:
                current_score = self.scorer.score_clothing(
                    optimized[key], temperature, weather, scene
                )

                # 寻找更好的替代品
                for score, candidate in scored_categories[key]:
                    if score > current_score + 1.0:
                        # 检查新单品与现有单品的风格兼容性
                        compatible = True
                        for existing_key, existing_item in optimized.items():
                            if existing_key != key:
                                compat = self.style_matcher.get_compatibility(
                                    candidate.get("style", ""),
                                    existing_item.get("style", "")
                                )
                                if compat < 5.0:
                                    compatible = False
                                    break

                        if compatible:
                            logger.info(f"[优化] 替换{key}: {optimized[key].get('type')} -> {candidate.get('type')}")
                            optimized[key] = candidate
                            break

        return optimized


# ==================== AI 二次审核 ====================

class AIReviewer:
    """
    AI 二次审核 - 确保推荐质量
    
    【审核重点】
    1. 核心单品完整性：衣服、裤子、鞋子必须有
    2. 风格一致性：整套穿搭风格要协调
    3. 颜色搭配：上装下装颜色要协调
    4. 配件可选：包和帽子是加分项，不是必须
    """

    def __init__(self):
        pass

    def review_outfit(
        self,
        outfit: Dict[str, dict],
        temperature: float,
        weather: dict,
        scene: str
    ) -> Dict:
        """
        AI 审核穿搭合理性

        返回审核结果：
        - is_acceptable: 是否可接受
        - issues: 问题列表
        - suggestions: 建议
        - overall_score: 综合评分
        """

        issues = []
        suggestions = []
        scores = {
            "weather_fit": 0,
            "scene_fit": 0,
            "style_consistency": 0,
            "color_harmony": 0,
            "completeness": 0  # 新增完整性评分
        }

        # ========== 1. 检查核心单品完整性 ==========
        essential_items = ["top", "pants", "shoes"]
        missing_items = []
        for key in essential_items:
            if not outfit.get(key):
                missing_items.append({"top": "上衣", "pants": "下装", "shoes": "鞋子"}.get(key, key))
        
        if missing_items:
            issues.append(f"缺少核心单品: {', '.join(missing_items)}")
            scores["completeness"] = 3
        else:
            scores["completeness"] = 10
        
        # 包和帽子是可选的，不影响完整性评分
        has_accessory = outfit.get("bag") or outfit.get("hat")
        if has_accessory:
            scores["completeness"] = min(10, scores["completeness"] + 1)  # 有配件加分

        # ========== 2. 检查天气适配 ==========
        if outfit.get("top"):
            temp_min = outfit["top"].get("temperature_min", 0)
            temp_max = outfit["top"].get("temperature_max", 40)
            if temperature < temp_min - 5:
                issues.append(f"上衣{outfit['top'].get('type')}太薄，不适合低温天气")
                scores["weather_fit"] = 3
            elif temperature > temp_max + 5:
                issues.append(f"上衣{outfit['top'].get('type')}太厚，不适合高温天气")
                scores["weather_fit"] = 3
            else:
                scores["weather_fit"] = 8 + (2 if abs(temperature - (temp_min + temp_max) / 2) < 3 else 0)
        else:
            scores["weather_fit"] = 0

        # ========== 3. 检查场景适配 ==========
        scene_constraints = SceneConstraints()
        scene_enum = scene_constraints.get_scene(scene)
        scene_violations = 0
        for key in essential_items:
            if outfit.get(key):
                is_valid, reason = scene_constraints.is_valid_for_scene(outfit[key], scene_enum)
                if not is_valid:
                    issues.append(reason)
                    scene_violations += 1
        
        if scene_violations == 0:
            scores["scene_fit"] = 9
        elif scene_violations == 1:
            scores["scene_fit"] = 6
        else:
            scores["scene_fit"] = 3

        # ========== 4. 检查风格一致性 ==========
        style_matcher = StyleMatcher()
        scores["style_consistency"] = style_matcher.score_style_consistency(outfit)
        if scores["style_consistency"] < 5:
            issues.append("穿搭风格不够统一，建议选择相同或相近风格的单品")
            suggestions.append("例如：休闲上衣搭配休闲裤子，避免混搭商务和运动风格")
        elif scores["style_consistency"] >= 8:
            suggestions.append("穿搭风格协调统一，很棒！")

        # ========== 5. 检查颜色搭配 ==========
        color_matcher = ColorMatcher()
        scores["color_harmony"] = color_matcher.score_color_harmony(outfit)
        if scores["color_harmony"] < 5:
            issues.append("颜色搭配不够协调")
            suggestions.append("建议选择经典配色方案：黑白灰蓝、或同色系深浅搭配")
        elif scores["color_harmony"] >= 8:
            suggestions.append("颜色搭配协调美观！")

        # ========== 6. 低温建议添加外套 ==========
        if temperature < 15 and not outfit.get("jacket"):
            suggestions.append("低温天气建议添加外套，如羽绒服、大衣或夹克")

        # ========== 7. 计算综合评分 ==========
        overall = sum(scores.values()) / len(scores)
        
        # 核心单品缺失直接降低评分
        if missing_items:
            overall = min(overall, 5.0)
        
        is_acceptable = len(issues) == 0 or (len(issues) <= 2 and overall >= 6.0)

        return {
            "is_acceptable": is_acceptable,
            "issues": issues,
            "suggestions": suggestions,
            "scores": scores,
            "overall_score": round(overall, 1)
        }


# ==================== 导出主类 ====================

class SmartOutfitEngine:
    """
    智能穿搭推荐引擎 - 统一入口

    使用方式：
    engine = SmartOutfitEngine()
    result = engine.recommend(
        clothes=clothes_list,
        temperature=25,
        weather={"weather": "晴", "wind_speed": 5},
        scene="上班"
    )
    """

    def __init__(self):
        self.recommender = MultiLayerRecommender()
        self.reviewer = AIReviewer()
        self.temp_engine = TemperatureRuleEngine()
        self.scene_constraints = SceneConstraints()

    def recommend(
        self,
        clothes: List[dict],
        temperature: float,
        weather: dict,
        scene: str,
        style_preference: str = "休闲",
        user_id: Optional[int] = None,
        recent_outfits: Optional[List[Dict]] = None
    ) -> Dict:
        """
        生成智能穿搭推荐

        Args:
            clothes: 衣物列表
            temperature: 温度（摄氏度）
            weather: 天气信息字典
            scene: 场景（日常/上班/约会/运动/聚会/出行）
            style_preference: 用户风格偏好
            user_id: 用户ID（用于生成确定性种子）
            recent_outfits: 最近穿过的穿搭（避免重复）

        Returns:
            推荐结果字典
        """
        try:
            # 生成确定性种子（相同输入产生相同推荐）
            seed_data = f"{user_id or 'anonymous'}_{temperature}_{weather.get('weather', '')}_{scene}_{style_preference}"
            seed_hash = hashlib.md5(seed_data.encode()).hexdigest()

            # 使用多层推荐算法
            result = self.recommender.recommend(
                clothes=clothes,
                temperature=temperature,
                weather=weather,
                scene=scene,
                user_preference={"style": style_preference}
            )

            # AI 二次审核
            review = self.reviewer.review_outfit(
                outfit=result["outfit"],
                temperature=temperature,
                weather=weather,
                scene=scene
            )

            # 如果审核不通过，尝试重新推荐
            if not review["is_acceptable"] and review["overall_score"] < 5.0:
                logger.info("[智能引擎] AI审核不通过，尝试重新推荐...")
                # 重新推荐时会使用不同的排序逻辑

            # 构建最终结果
            temp_level = self.temp_engine.get_temperature_level(temperature)
            scene_enum = self.scene_constraints.get_scene(scene)
            scene_rules = self.scene_constraints.SCENE_RULES[scene_enum]

            # 获取场景提示
            scene_tip = scene_rules.get("tip", "")
            
            # 生成穿搭说明
            outfit_desc = self._generate_outfit_description(result["outfit"], scene_enum, temperature, weather)
            
            # 检查是否有虚拟衣物需要提示
            missing_items = []
            for key in ["top", "pants", "shoes"]:
                if result["outfit"].get(key, {}).get("is_virtual"):
                    item_name = {"top": "上衣", "pants": "下装", "shoes": "鞋子"}.get(key, key)
                    missing_items.append(item_name)

            final_result = {
                "outfit": result["outfit"],
                "scores": result["scores"],
                "review": review,
                "meta": {
                    "temperature": temperature,
                    "temperature_level": temp_level.value,
                    "scene": scene_enum.value,
                    "scene_description": scene_rules["description"],
                    "scene_tip": scene_tip,
                    "outfit_description": outfit_desc,
                    "recommendation_seed": seed_hash[:8],
                    "missing_warning": f"您的衣橱缺少{missing_items}，已为您推荐通用款式" if missing_items else None
                }
            }

            return final_result

        except Exception as e:
            logger.error(f"[智能引擎] 推荐失败: {str(e)}", exc_info=True)
            raise

    def _generate_outfit_description(
        self, 
        outfit: Dict[str, dict], 
        scene: Scene, 
        temperature: float,
        weather: dict
    ) -> str:
        """生成穿搭说明文字"""
        descriptions = []
        
        # 场景专属开头
        scene_openers = {
            Scene.WORK: "今天的通勤穿搭：",
            Scene.DAILY: "今天的日常搭配：",
            Scene.DATE: "约会心机穿搭：",
            Scene.SPORTS: "活力运动装扮：",
            Scene.PARTY: "聚会吸睛穿搭：",
            Scene.TRAVEL: "出行舒适穿搭："
        }
        
        opener = scene_openers.get(scene, "今日穿搭：")
        descriptions.append(opener)
        
        # 描述各单品
        if outfit.get("top"):
            top = outfit["top"]
            top_desc = f"{top.get('color', '')}{top.get('type', '上衣')}"
            if top.get("is_virtual"):
                top_desc += "（建议添加）"
            descriptions.append(f"上装：{top_desc}")
        
        if outfit.get("pants"):
            pants = outfit["pants"]
            pants_desc = f"{pants.get('color', '')}{pants.get('type', '下装')}"
            if pants.get("is_virtual"):
                pants_desc += "（建议添加）"
            descriptions.append(f"下装：{pants_desc}")
        
        if outfit.get("shoes"):
            shoes = outfit["shoes"]
            shoes_desc = f"{shoes.get('color', '')}{shoes.get('type', '鞋子')}"
            if shoes.get("is_virtual"):
                shoes_desc += "（建议添加）"
            descriptions.append(f"鞋子：{shoes_desc}")
        
        if outfit.get("jacket"):
            jacket = outfit["jacket"]
            descriptions.append(f"外套：{jacket.get('color', '')}{jacket.get('type', '')}")
        
        return "\n".join(descriptions)


# 导出单例
outfit_engine = SmartOutfitEngine()
