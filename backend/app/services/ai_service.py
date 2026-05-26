import json
import random
import hashlib
import logging
import uuid
import os
from typing import Optional, List, Dict

# 必须在导入 PIL 之前设置，处理截断/损坏的图片
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from app.schemas.clothes import ClothesAnalysis
from app.schemas.outfit import OutfitRecommendation, OutfitItem
from app.services.outfit_engine import outfit_engine, SmartOutfitEngine

logger = logging.getLogger(__name__)


def normalize_clothing_id(clothing: dict, index: int) -> dict:
    """统一将 clothing 的 id 转换为字符串，避免类型不一致导致的错误"""
    if "id" in clothing:
        clothing["id"] = str(clothing["id"])
    else:
        clothing["id"] = str(index)
    return clothing


class OutfitRecommendationEngine:
    """基于规则的穿搭推荐引擎 - 使用确定性算法"""

    # 温度等级定义
    TEMP_LEVELS = [
        (35, "极热"),
        (30, "炎热"),
        (25, "热"),
        (20, "温暖"),
        (15, "凉爽"),
        (10, "微冷"),
        (5, "冷"),
        (0, "寒冷"),
        (-999, "严寒"),
    ]

    # 温度到衣服类型的映射
    TEMP_CLOTHING_RULES = {
        "极热": {
            "top": ["T恤", "背心"],
            "bottom": ["短裤", "薄长裤"],
            "shoes": ["凉鞋", "运动鞋"],
        },
        "炎热": {
            "top": ["T恤", "短袖衬衫"],
            "bottom": ["短裤", "薄长裤", "裙子"],
            "shoes": ["凉鞋", "运动鞋", "帆布鞋"],
        },
        "热": {
            "top": ["T恤", "长袖", "薄衬衫"],
            "bottom": ["薄长裤", "牛仔裤", "裙子"],
            "shoes": ["运动鞋", "帆布鞋", "皮鞋"],
            "jacket": ["薄外套"],
        },
        "温暖": {
            "top": ["长袖", "卫衣", "毛衣", "衬衫"],
            "bottom": ["牛仔裤", "休闲裤", "长裙"],
            "shoes": ["运动鞋", "帆布鞋", "皮鞋"],
            "jacket": ["外套", "风衣", "开衫"],
        },
        "凉爽": {
            "top": ["毛衣", "卫衣", "厚衬衫"],
            "bottom": ["牛仔裤", "休闲裤", "保暖长裤"],
            "shoes": ["运动鞋", "皮鞋", "靴子"],
            "jacket": ["外套", "夹克", "风衣", "皮衣"],
        },
        "微冷": {
            "top": ["毛衣", "厚卫衣", "保暖衬衫"],
            "bottom": ["牛仔裤", "厚裤子", "保暖裤"],
            "shoes": ["靴子", "运动鞋", "皮鞋"],
            "jacket": ["羽绒服", "厚外套", "棉服", "大衣"],
        },
        "冷": {
            "top": ["厚毛衣", "保暖内衣", "加绒卫衣"],
            "bottom": ["加绒牛仔裤", "保暖裤", "厚休闲裤"],
            "shoes": ["靴子", "雪地靴"],
            "jacket": ["羽绒服", "厚棉服", "派克大衣"],
        },
        "严寒": {
            "top": ["保暖内衣", "厚毛衣", "加绒衬衫"],
            "bottom": ["加绒裤", "保暖裤"],
            "shoes": ["雪地靴", "保暖靴"],
            "jacket": ["加厚羽绒服", "户外防寒服", "派克大衣"],
        },
    }

    # 场景风格权重
    SCENE_STYLES = {
        "日常": {"preferred": ["休闲", "简约"], "avoid": ["太正式"]},
        "上班": {"preferred": ["商务", "简约", "休闲"], "avoid": ["运动", "街头"]},
        "约会": {"preferred": ["简约", "休闲", "复古"], "avoid": ["运动", "邋遢"]},
        "运动": {"preferred": ["运动"], "avoid": ["商务", "正装"]},
        "派对": {"preferred": ["简约", "复古", "时尚"], "avoid": ["运动"]},
    }

    def get_temp_level(self, temperature: float) -> str:
        """根据温度获取温度等级"""
        for threshold, level in self.TEMP_LEVELS:
            if temperature >= threshold:
                return level
        return "严寒"

    def select_items_deterministic(
        self,
        clothes: List[dict],
        preferred_types: List[str],
        preferred_styles: List[str] = None,
        temperature: float = None,
        current_season: str = None
    ) -> Optional[dict]:
        """
        确定性选择：使用哈希确保相同输入产生相同输出
        增强版：根据温度和季节优先选择合适的衣物
        """
        if not clothes:
            return None

        # 统一 id 类型为字符串，避免 TypeError
        clothes = [normalize_clothing_id(c, i) for i, c in enumerate(clothes)]

        # 过滤符合条件的衣服
        candidates = [
            c for c in clothes
            if c.get("type") in preferred_types
        ]

        if not candidates:
            # 如果没有精确匹配，尝试模糊匹配
            type_mapping = {
                "T恤": ["T恤", "卫衣", "衬衫"],
                "短裤": ["短裤", "休闲裤"],
                "凉鞋": ["凉鞋", "运动鞋", "帆布鞋"],
                "外套": ["外套", "羽绒服", "夹克", "风衣"],
                "牛仔裤": ["牛仔裤", "休闲裤"],
            }
            for exact_type in preferred_types:
                fallback_types = type_mapping.get(exact_type, [exact_type])
                candidates = [c for c in clothes if c.get("type") in fallback_types]
                if candidates:
                    break

        if not candidates:
            return None

        # 增强：根据温度和季节排序候选衣物
        if temperature is not None:
            candidates = self._score_by_temperature(candidates, temperature)
        
        if current_season:
            candidates = self._score_by_season(candidates, current_season)

        # 使用确定性选择：基于候选列表和输入条件生成稳定索引
        # 确保 id 已经是字符串类型
        candidate_ids = [str(c.get("id", c.get("name", str(i)))) for i, c in enumerate(candidates)]
        candidate_key = "".join(sorted(candidate_ids))
        hash_input = f"{candidate_key}_{len(clothes)}_{temperature}_{current_season}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        selected_index = hash_value % len(candidates)

        return candidates[selected_index]

    def _score_by_temperature(self, clothes: List[dict], temperature: float) -> List[dict]:
        """根据温度对衣物进行评分和排序"""
        scored = []
        for c in clothes:
            score = 0
            temp_min = c.get("temperature_min", 0)
            temp_max = c.get("temperature_max", 30)
            
            # 检查温度是否在衣物适合范围内
            if temp_min <= temperature <= temp_max:
                score = 10
            elif temperature < temp_min:
                # 温度太低，衣物不够保暖
                diff = temp_min - temperature
                score = max(0, 10 - diff)
            else:
                # 温度太高，衣物太厚
                diff = temperature - temp_max
                score = max(0, 10 - diff)
            
            # 厚度加成
            thickness = c.get("thickness", "中等")
            thickness_scores = {
                "极薄": -5, "薄": -2, "中等": 0, "厚": 3, "加绒": 5, "羽绒级": 7
            }
            score += thickness_scores.get(thickness, 0)
            
            scored.append((score, c))
        
        # 按分数降序排序
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored]

    def _score_by_season(self, clothes: List[dict], current_season: str) -> List[dict]:
        """根据季节对衣物进行评分和排序"""
        season_map = {"春": ["春", "春夏", "四季通用"], "夏": ["夏", "春夏", "四季通用"], 
                      "秋": ["秋", "秋冬", "四季通用"], "冬": ["冬", "秋冬", "四季通用"]}
        preferred_seasons = season_map.get(current_season, ["四季通用"])
        
        scored = []
        for c in clothes:
            season = c.get("season", "")
            if season in preferred_seasons:
                score = 10
            elif season == "" or season == "四季通用":
                score = 5
            else:
                score = 0
            scored.append((score, c))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored]

    def build_context_hash(self, weather: dict, scene: str, style: str) -> str:
        """生成上下文哈希，用于确定性推荐"""
        temp = weather.get("temperature", 20)
        weather_type = weather.get("weather", "晴")
        humidity = weather.get("humidity", 50)
        return f"{temp}_{weather_type}_{humidity}_{scene}_{style}"


class AIService:
    """AI服务 - 统一管理AI能力"""

    def __init__(self):
        from app.core.config import settings
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_api_base = settings.OPENAI_API_BASE
        self.deepseek_api_key = settings.DEEPSEEK_API_KEY
        self.recommendation_engine = OutfitRecommendationEngine()

    async def analyze_clothes(self, image_url: str) -> ClothesAnalysis:
        """
        分析衣服图片 - 使用 GPT-4o Vision 或 阿里云通义千问
        真正的多模态AI识别，返回详细的衣物属性
        """
        from app.core.config import settings
        from openai import OpenAI
        import json
        import base64
        import os
        import io
        from PIL import Image
        
        logger.info(f"[AI识别] 开始分析图片: {image_url}")
        
        # 获取完整图片路径
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        if image_url.startswith('/'):
            full_path = os.path.join(os.path.dirname(__file__), '..', '..', image_url.lstrip('/'))
            full_path = os.path.normpath(full_path)
        else:
            full_path = image_url
        
        logger.info(f"[AI识别] 图片路径: {full_path}")
        
        # 图片预处理：压缩和标准化
        processed_image_path = self._preprocess_image(full_path)
        
        # 提取主色调（用于辅助AI识别）
        dominant_colors = self._extract_dominant_colors(processed_image_path)
        logger.info(f"[AI识别] 提取的主色调: {dominant_colors}")
        
        # 专业的服装分析 Prompt - 增强版
        prompt = f"""你是一名专业服装造型师与服装识别AI。请仔细分析这张衣服图片。

图片中识别到的主色调参考（帮助你更准确判断颜色）：
{dominant_colors}

请以JSON格式返回分析结果，必须包含以下字段：
{{
    "type": "衣物类型，如：T恤、衬衫、卫衣、毛衣、外套、牛仔裤、休闲裤、裙子、连衣裙、运动鞋、皮鞋、靴子、帽子、包等",
    "color": "主色调，使用中文描述，如：黑色、白色、深蓝色、浅灰色、酒红色、卡其色、雾霾蓝、米白色、燕麦色、奶油白、藏青色等",
    "secondary_color": "次要颜色，如：白色拼色、灰色镶边等，没有则填null",
    "material": "主要材质，结合光泽、纹理、褶皱特征判断，如：棉质、羊毛、羊绒、涤纶、牛仔布、皮革、PU皮、针织、丝绸、羽绒、帆布、亚麻、雪纺等",
    "thickness": "厚度等级：极薄（雪纺/蕾丝）、薄（T恤/衬衫面料）、中等（牛仔裤/休闲裤面料）、厚（卫衣/毛衣面料）、加绒（内里加绒）、羽绒级（羽绒服）",
    "style": "风格，如：休闲、商务、运动、街头、简约、复古、正式、甜美、帅气、工装、文艺、国潮等",
    "season": "适合季节，如：春、夏、秋、冬、四季通用",
    "formality": "正式程度1-5，1=非常休闲（睡衣、运动服、家居服）、2=休闲（T恤、牛仔裤）、3=普通（衬衫、卫衣）、4=商务休闲（西装外套、修身裤）、5=正式（西装、礼服、正装衬衫）",
    "gender": "适用性别：男、女、中性",
    "temperature_min": "适合的最低温度（摄氏度），纯数字",
    "temperature_max": "适合的最高温度（摄氏度），纯数字",
    "confidence": "识别置信度0-1，如果图片模糊、背景复杂、无法确定，请降低置信度",
    "notes": "补充说明，如：特殊设计元素、搭配建议、需要注意的洗涤方式等"
}}

重要要求：
1. 必须仔细观察图片中的实际衣物，基于视觉特征判断，不要凭空猜测
2. 颜色识别要考虑光线影响，优先使用主色调参考列表中的颜色名称
3. 材质识别要结合光泽（丝绸有光泽vs棉质无光泽）、纹理（针织有纹路vs平滑）、褶皱特征
4. 厚度判断要结合材质和视觉厚度感
5. 如果图片中有多个物品或背景干扰，请只分析最主要的衣物主体
6. 如果图片模糊、质量低或无法识别，请将confidence设为低于0.6并说明原因
7. 所有描述必须使用中文
8. temperature_min和temperature_max必须是整数
9. 必须返回纯JSON格式，不要包含任何markdown代码块标记
"""
        
        # 清理临时文件的函数
        def _cleanup_temp_files():
            if processed_image_path != full_path and os.path.exists(processed_image_path):
                try:
                    os.remove(processed_image_path)
                    logger.info("[AI识别] 已清理临时文件")
                except Exception as e:
                    logger.warning(f"[AI识别] 清理临时文件失败: {e}")
        
        try:
            # 检查是否配置了 API Key
            if self.openai_api_key:
                # 关键修复：必须同时传递 api_key 和 base_url！
                # 否则默认请求 api.openai.com 而不是阿里云 DashScope
                client = OpenAI(
                    api_key=self.openai_api_key,
                    base_url=self.openai_api_base,  # 阿里云 DashScope endpoint
                    timeout=60.0  # 60秒超时，防止API卡住
                )
                
                # 检查是否配置了自定义 base_url（阿里云通义千问）
                custom_base_url = self.openai_api_base
                
                if custom_base_url and "aliyuncs" in custom_base_url.lower():
                    # 使用阿里云通义千问 API - 需要使用 base64 编码图片
                    logger.info("[AI识别] 使用阿里云通义千问 API (qwen-vl-max)")
                    
                    # 读取并编码图片
                    with open(processed_image_path, 'rb') as img_file:
                        img_data = img_file.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                    
                    base64_size = len(img_base64)
                    logger.info(f"[AI识别] Base64 编码后大小: {base64_size / 1024:.2f} KB")
                    
                    # 阿里云 20MB 限制检测，如果超限则进一步压缩
                    if base64_size > 18 * 1024 * 1024:  # 接近20MB时
                        logger.warning("[AI识别] Base64 过大，进行二次压缩...")
                        img = Image.open(processed_image_path)
                        # 强制压缩到更小尺寸
                        img.thumbnail((512, 512), Image.Resampling.LANCZOS)
                        temp_path = processed_image_path.replace('.jpg', '_small.jpg')
                        img.save(temp_path, 'JPEG', quality=50, optimize=True)
                        
                        with open(temp_path, 'rb') as f:
                            img_base64 = base64.b64encode(f.read()).decode('utf-8')
                        os.remove(temp_path)
                        logger.info(f"[AI识别] 二次压缩后 Base64 大小: {len(img_base64) / 1024:.2f} KB")
                    
                    # 阿里云 API 格式
                    response = client.chat.completions.create(
                        model="qwen-vl-max",  # 升级为 qwen-vl-max 效果更好
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{img_base64}"
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": prompt
                                    }
                                ]
                            }
                        ],
                        max_tokens=1500,
                        temperature=0.3
                    )
                else:
                    # 使用 OpenAI GPT-4o - 支持 image_url
                    logger.info("[AI识别] 使用 OpenAI GPT-4o API")
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {"type": "image_url", "image_url": {"url": f"{base_url}{image_url}" if image_url.startswith('/') else image_url}}
                                ]
                            }
                        ],
                        max_tokens=1500,
                        temperature=0.3
                    )
                
                result_text = response.choices[0].message.content
                logger.info(f"[AI识别] AI原始响应: {result_text[:500]}...")
                logger.info(f"[AI识别] 视觉模型返回内容:\n{result_text}")
                
                # 提取 JSON - 更robust的解析
                json_str = self._extract_json(result_text)
                
                result = json.loads(json_str)
                
                logger.info(f"[AI识别] 解析结果: type={result.get('type')}, color={result.get('color')}, confidence={result.get('confidence')}")
                
                # 清理临时处理后的图片
                _cleanup_temp_files()
                
                return ClothesAnalysis(
                    type=result.get("type", "未知"),
                    color=result.get("color", "未知"),
                    material=result.get("material", "未知"),
                    thickness=result.get("thickness", "中等"),
                    style=result.get("style", "休闲"),
                    season=result.get("season", "四季通用"),
                    formality=result.get("formality", 3),
                    gender=result.get("gender", "中性"),
                    temperature_min=result.get("temperature_min", 10),
                    temperature_max=result.get("temperature_max", 25),
                    confidence=result.get("confidence", 0.7),
                    notes=result.get("notes", "")
                )
            else:
                # 没有 API Key，返回低置信度提示
                logger.warning("[AI识别] 未配置 OPENAI_API_KEY，返回模拟数据")
                _cleanup_temp_files()
                return ClothesAnalysis(
                    type="T恤",
                    color="蓝色",
                    material="棉质",
                    thickness="中等",
                    style="休闲",
                    season="春夏",
                    formality=2,
                    gender="中性",
                    temperature_min=15,
                    temperature_max=28,
                    confidence=0.3,
                    notes="未配置AI API，请配置OPENAI_API_KEY以获得准确识别"
                )
                
        except json.JSONDecodeError as e:
            logger.error(f"[AI识别] JSON解析失败: {str(e)}", exc_info=True)
            _cleanup_temp_files()
            return ClothesAnalysis(
                type="未知",
                color="未知",
                material="未知",
                thickness="中等",
                style="休闲",
                season="四季通用",
                formality=3,
                gender="中性",
                temperature_min=10,
                temperature_max=25,
                confidence=0.1,
                notes=f"AI响应格式错误，请手动填写属性"
            )
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[AI识别] AI视觉识别服务异常: {error_msg}", exc_info=True)
            
            # 清理临时文件
            _cleanup_temp_files()
            
            # 根据错误类型提供更明确的提示
            if "401" in error_msg or "Incorrect API key" in error_msg:
                notes = "API认证失败，请检查 API Key 是否正确配置"
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                notes = "API访问被拒绝，请检查账户权限或余额"
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                notes = "API请求过于频繁，请稍后重试"
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                notes = "AI识别超时，请上传更小或更清晰的图片后重试"
            elif "connection" in error_msg.lower() or "ConnectionError" in error_msg:
                notes = "网络连接异常，请检查网络后重试"
            elif "truncated" in error_msg.lower() or "image file is truncated" in error_msg.lower():
                notes = "图片文件可能已损坏，请尝试重新上传"
            elif "max bytes" in error_msg.lower() or "20971520" in error_msg:
                notes = "图片过大，请上传10MB以内的图片"
            else:
                notes = f"AI视觉识别服务异常，请尝试上传更小或更清晰的图片"
            
            return ClothesAnalysis(
                type="未知",
                color="未知",
                material="未知",
                thickness="中等",
                style="休闲",
                season="四季通用",
                formality=3,
                gender="中性",
                temperature_min=10,
                temperature_max=25,
                confidence=0.1,
                notes=notes
            )

    def _preprocess_image(self, image_path: str) -> str:
        """
        图片预处理：完整性校验、压缩、标准化
        返回处理后的图片路径
        
        处理步骤：
        1. 图片完整性校验
        2. EXIF 方向纠正
        3. RGB 转换
        4. 智能压缩
        5. 临时文件清理
        """
        from PIL import Image, ImageOps
        
        original_size = 0
        try:
            if not os.path.exists(image_path):
                logger.warning(f"[AI识别] 图片不存在: {image_path}")
                return image_path
            
            # 获取原始文件大小
            original_size = os.path.getsize(image_path)
            logger.info(f"[AI识别] 原始图片大小: {original_size / 1024:.2f} KB")
            
            # ========== 第一步：图片完整性校验 ==========
            try:
                with open(image_path, 'rb') as f:
                    img_check = Image.open(f)
                    img_check.verify()  # 验证图片完整性
                logger.info("[AI识别] 图片完整性校验通过")
            except Exception as verify_error:
                logger.error(f"[AI识别] 图片完整性校验失败: {verify_error}")
                raise Exception(f"图片文件损坏或格式错误: {verify_error}")
            
            # ========== 第二步：打开并处理图片 ==========
            img = Image.open(image_path)
            
            # EXIF 方向纠正（修复手机拍照方向问题）
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass  # EXIF 错误不影响继续处理
            
            # 转换为 RGB（处理 RGBA、PNG 等格式）
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # ========== 第三步：智能压缩 ==========
            # 最大边限制：1024px（平衡清晰度和文件大小）
            max_size = 1024
            ratio = min(max_size / img.width, max_size / img.height) if img.width > max_size or img.height > max_size else 1
            
            if ratio < 1:
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"[AI识别] 图片已缩放: {img.width}x{img.height}")
            
            # 根据原始大小调整压缩质量
            # 原始 > 5MB: quality=60
            # 原始 > 2MB: quality=70
            # 原始 > 1MB: quality=80
            # 其他: quality=85
            if original_size > 5 * 1024 * 1024:
                quality = 60
            elif original_size > 2 * 1024 * 1024:
                quality = 70
            elif original_size > 1 * 1024 * 1024:
                quality = 80
            else:
                quality = 85
            
            # ========== 第四步：保存压缩后的图片 ==========
            output_path = image_path.replace('.', '_processed.')
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            # 记录压缩结果
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            logger.info(f"[AI识别] 压缩完成: {compressed_size / 1024:.2f} KB (节省 {compression_ratio:.1f}%)")
            
            return output_path
            
        except Exception as e:
            logger.warning(f"[AI识别] 图片预处理失败: {str(e)}")
            return image_path

    def _extract_dominant_colors(self, image_path: str, num_colors: int = 5) -> List[str]:
        """
        提取主色调 - 使用 K-means 颜色聚类
        返回中文颜色名称列表
        
        增强容错：
        - 图片文件不存在
        - 图片格式错误
        - 图片损坏
        - sklearn 未安装
        """
        try:
            from PIL import Image
            import numpy as np
            
            if not os.path.exists(image_path):
                logger.warning(f"[AI识别] 颜色提取：图片不存在 {image_path}")
                return []
            
            try:
                img = Image.open(image_path)
                # 转换为 RGB 避免 PNG 透明通道问题
                if img.mode != 'RGB':
                    img = img.convert('RGB')
            except Exception as img_error:
                logger.warning(f"[AI识别] 颜色提取：无法打开图片 {img_error}")
                return []
            
            # 缩小图片以加快处理
            try:
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
            except Exception:
                # 如果 resize 失败，尝试更小的尺寸
                try:
                    img = img.resize((50, 50), Image.Resampling.LANCZOS)
                except Exception:
                    logger.warning("[AI识别] 颜色提取：图片尺寸调整失败")
                    return []
            
            # 转换为 numpy 数组
            try:
                img_array = np.array(img)
            except Exception as array_error:
                logger.warning(f"[AI识别] 颜色提取：图片转数组失败 {array_error}")
                return []
            
            # 将图片重塑为一维数组
            try:
                pixels = img_array.reshape(-1, 3)
            except Exception as reshape_error:
                logger.warning(f"[AI识别] 颜色提取：像素重塑失败 {reshape_error}")
                return []
            
            # 检查像素数量是否足够
            if len(pixels) < num_colors:
                num_colors = max(1, len(pixels))
            
            # 使用 K-means 聚类
            try:
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
                kmeans.fit(pixels)
                colors = kmeans.cluster_centers_
            except ImportError:
                logger.warning("[AI识别] sklearn 未安装，使用简单颜色提取")
                # 如果 sklearn 不可用，使用简单的颜色采样
                return self._simple_color_extraction(img_array)
            except Exception as kmeans_error:
                logger.warning(f"[AI识别] K-means 聚类失败: {kmeans_error}")
                return self._simple_color_extraction(img_array)
            
            # 将 RGB 转换为中文颜色名称
            color_names = []
            for rgb in colors:
                r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
                color_name = self._rgb_to_color_name(r, g, b)
                if color_name not in color_names:  # 去重
                    color_names.append(color_name)
            
            logger.info(f"[AI识别] 提取的颜色: {color_names}")
            return color_names
            
        except Exception as e:
            logger.warning(f"[AI识别] 颜色提取失败: {str(e)}")
            return []

    def _simple_color_extraction(self, img_array) -> List[str]:
        """
        简单的颜色提取（当 sklearn 不可用时使用）
        """
        try:
            import numpy as np
            # 计算平均颜色
            avg_color = np.mean(img_array.reshape(-1, 3), axis=0)
            r, g, b = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
            return [self._rgb_to_color_name(r, g, b)]
        except Exception:
            return []

    def _rgb_to_color_name(self, r: int, g: int, b: int) -> str:
        """将 RGB 转换为中文颜色名称"""
        # 基础颜色映射
        color_ranges = [
            {"name": "黑色", "rgb": (0, 0, 0), "threshold": 30},
            {"name": "白色", "rgb": (255, 255, 255), "threshold": 30},
            {"name": "灰色", "rgb": (128, 128, 128), "threshold": 40},
            {"name": "深灰色", "rgb": (80, 80, 80), "threshold": 40},
            {"name": "浅灰色", "rgb": (180, 180, 180), "threshold": 40},
            {"name": "红色", "rgb": (255, 0, 0), "threshold": 60},
            {"name": "酒红色", "rgb": (128, 0, 32), "threshold": 50},
            {"name": "深红色", "rgb": (139, 0, 0), "threshold": 50},
            {"name": "粉红色", "rgb": (255, 192, 203), "threshold": 60},
            {"name": "橙色", "rgb": (255, 165, 0), "threshold": 60},
            {"name": "黄色", "rgb": (255, 255, 0), "threshold": 60},
            {"name": "米黄色", "rgb": (255, 246, 220), "threshold": 50},
            {"name": "卡其色", "rgb": (195, 176, 145), "threshold": 50},
            {"name": "棕色", "rgb": (139, 69, 19), "threshold": 50},
            {"name": "咖啡色", "rgb": (111, 78, 55), "threshold": 50},
            {"name": "深棕色", "rgb": (101, 67, 33), "threshold": 50},
            {"name": "燕麦色", "rgb": (235, 224, 204), "threshold": 50},
            {"name": "奶油色", "rgb": (255, 253, 208), "threshold": 50},
            {"name": "绿色", "rgb": (0, 128, 0), "threshold": 60},
            {"name": "深绿色", "rgb": (0, 100, 0), "threshold": 50},
            {"name": "军绿色", "rgb": (75, 83, 32), "threshold": 50},
            {"name": "浅绿色", "rgb": (144, 238, 144), "threshold": 60},
            {"name": "青色", "rgb": (0, 128, 128), "threshold": 60},
            {"name": "蓝色", "rgb": (0, 0, 255), "threshold": 60},
            {"name": "深蓝色", "rgb": (0, 0, 139), "threshold": 50},
            {"name": "天蓝色", "rgb": (135, 206, 235), "threshold": 60},
            {"name": "浅蓝色", "rgb": (173, 216, 230), "threshold": 60},
            {"name": "藏青色", "rgb": (0, 51, 102), "threshold": 50},
            {"name": "雾霾蓝", "rgb": (101, 133, 154), "threshold": 50},
            {"name": "宝蓝色", "rgb": (0, 112, 221), "threshold": 50},
            {"name": "紫色", "rgb": (128, 0, 128), "threshold": 60},
            {"name": "紫红色", "rgb": (199, 21, 133), "threshold": 50},
        ]
        
        # 计算与每个颜色的距离
        min_distance = float('inf')
        closest_name = "未知"
        
        for color in color_ranges:
            distance = ((r - color["rgb"][0]) ** 2 + 
                       (g - color["rgb"][1]) ** 2 + 
                       (b - color["rgb"][2]) ** 2) ** 0.5
            
            if distance < min_distance and distance < color["threshold"]:
                min_distance = distance
                closest_name = color["name"]
        
        return closest_name

    def _extract_json(self, text: str) -> str:
        """
        从文本中提取 JSON 字符串
        支持多种格式：```json...```、```...```、直接JSON
        """
        import re
        
        # 尝试提取 ```json...```
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if json_match:
            return json_match.group(1).strip()
        
        # 尝试提取 ```...```
        code_match = re.search(r'```\s*([\s\S]*?)\s*```', text)
        if code_match:
            potential_json = code_match.group(1).strip()
            if potential_json.startswith('{'):
                return potential_json
        
        # 尝试直接解析（假设整个文本就是JSON）
        if text.strip().startswith('{'):
            return text.strip()
        
        # 最后尝试查找第一个 { 到最后一个 } 之间的内容
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return text[first_brace:last_brace + 1]
        
        raise ValueError("无法从文本中提取JSON")

    async def generate_outfit_recommendation(
        self,
        weather: dict,
        clothes: List[dict],
        scene: str = "日常",
        style_preference: str = "休闲",
        user_id: Optional[int] = None
    ) -> OutfitRecommendation:
        """
        生成穿搭推荐 - 智能推荐引擎版

        使用多层次推荐算法：
        第一层：天气过滤
        第二层：场景过滤
        第三层：风格匹配
        第四层：颜色评分
        第五层：AI审核

        真正使用衣物的厚度、材质、季节、温度范围等属性
        """
        try:
            temperature = weather.get("temperature", 20)
            weather_type = weather.get("weather", "晴")
            wind_speed = weather.get("wind_speed", 0)
            precipitation = weather.get("precipitation_probability", 0)

            # 统一衣服 id 为字符串类型
            clothes = [normalize_clothing_id(c, i) for i, c in enumerate(clothes)]
            logger.info(f"[AIService] 使用智能引擎处理 {len(clothes)} 件衣服，温度 {temperature}°C")

            # 构建天气信息
            weather_info = {
                "weather": weather_type,
                "wind_speed": wind_speed,
                "precipitation_probability": precipitation,
                "uv_index": weather.get("uv_index", 0),
                "humidity": weather.get("humidity", 50)
            }

            # 使用新的智能推荐引擎
            smart_engine = SmartOutfitEngine()
            result = smart_engine.recommend(
                clothes=clothes,
                temperature=temperature,
                weather=weather_info,
                scene=scene,
                style_preference=style_preference,
                user_id=user_id
            )

            outfit = result["outfit"]
            scores = result["scores"]
            review = result["review"]
            meta = result["meta"]

            # 构建 OutfitItem
            top_item = OutfitItem(**outfit["top"]) if outfit.get("top") else None
            pants_item = OutfitItem(**outfit["pants"]) if outfit.get("pants") else None
            shoes_item = OutfitItem(**outfit["shoes"]) if outfit.get("shoes") else None
            jacket_item = OutfitItem(**outfit["jacket"]) if outfit.get("jacket") else None

            # 生成推荐理由
            reason = self._generate_smart_reason(
                temperature=temperature,
                weather=weather_type,
                scene=scene,
                outfit=outfit,
                review=review,
                meta=meta
            )

            # 生成穿搭建议
            tips = self._generate_smart_tips(
                weather=weather_info,
                temperature=temperature,
                outfit=outfit,
                scores=scores
            )

            # 综合评分
            final_score = (scores.get("total", 7.0) + review.get("overall_score", 7.0)) / 2

            logger.info(f"[AIService] 推荐完成，综合评分: {final_score:.1f}")

            # 生成唯一 ID 用于收藏识别
            recommendation_id = str(uuid.uuid4())

            return OutfitRecommendation(
                id=recommendation_id,
                top=top_item,
                pants=pants_item,
                shoes=shoes_item,
                jacket=jacket_item,
                accessories=[],
                reason=reason,
                score=round(final_score, 1),
                scene=scene,
                tips=tips
            )

        except Exception as e:
            logger.error(f"[AIService] 智能推荐失败: {str(e)}", exc_info=True)
            # 回退到原来的推荐逻辑
            return await self._fallback_recommendation(weather, clothes, scene, style_preference)

    async def _fallback_recommendation(
        self,
        weather: dict,
        clothes: List[dict],
        scene: str,
        style_preference: str
    ) -> OutfitRecommendation:
        """降级推荐：当智能引擎失败时使用"""
        try:
            temperature = weather.get("temperature", 20)
            weather_type = weather.get("weather", "晴")

            # 统一衣服 id 为字符串类型
            clothes = [normalize_clothing_id(c, i) for i, c in enumerate(clothes)]

            # 获取温度等级
            temp_level = self.recommendation_engine.get_temp_level(temperature)

            # 根据月份判断当前季节
            from datetime import datetime
            month = datetime.now().month
            current_season = "春" if month in [3, 4, 5] else "夏" if month in [6, 7, 8] else "秋" if month in [9, 10, 11] else "冬"

            # 获取该温度等级的衣服类型
            clothing_rules = self.recommendation_engine.TEMP_CLOTHING_RULES.get(
                temp_level,
                self.recommendation_engine.TEMP_CLOTHING_RULES["温暖"]
            )

            # 确定性选择单品
            top = self.recommendation_engine.select_items_deterministic(
                clothes,
                clothing_rules.get("top", ["T恤"]),
                temperature=temperature,
                current_season=current_season
            )

            pants = self.recommendation_engine.select_items_deterministic(
                clothes,
                clothing_rules.get("bottom", ["牛仔裤"]),
                temperature=temperature,
                current_season=current_season
            )

            shoes = self.recommendation_engine.select_items_deterministic(
                clothes,
                clothing_rules.get("shoes", ["运动鞋"]),
                temperature=temperature,
                current_season=current_season
            )

            jacket = self.recommendation_engine.select_items_deterministic(
                clothes,
                clothing_rules.get("jacket", []),
                temperature=temperature,
                current_season=current_season
            ) if clothing_rules.get("jacket") else None

            reason = self._generate_enhanced_reason(temperature, weather_type, scene, temp_level, top, pants, jacket)
            tips = self._generate_enhanced_tips(weather, temperature, top, pants, jacket)

            base_score = 7.0
            if temp_level in ["极热", "严寒"]:
                base_score -= 1.0
            if scene in ["上班", "约会"]:
                base_score += 1.5
            if top and pants:
                base_score += 0.5
            if top:
                top_temp_min = top.get("temperature_min", 10)
                top_temp_max = top.get("temperature_max", 25)
                if top_temp_min <= temperature <= top_temp_max:
                    base_score += 1.0

            score = min(10.0, max(6.0, base_score))

            # 生成唯一 ID 用于收藏识别
            recommendation_id = str(uuid.uuid4())

            return OutfitRecommendation(
                id=recommendation_id,
                top=OutfitItem(**top) if top else None,
                pants=OutfitItem(**pants) if pants else None,
                shoes=OutfitItem(**shoes) if shoes else None,
                jacket=OutfitItem(**jacket) if jacket else None,
                accessories=[],
                reason=reason,
                score=round(score, 1),
                scene=scene,
                tips=tips
            )
        except Exception as e:
            logger.error(f"[AIService] 降级推荐也失败: {str(e)}", exc_info=True)
            return OutfitRecommendation(
                id=str(uuid.uuid4()),
                top=None,
                pants=None,
                shoes=None,
                jacket=None,
                accessories=[],
                reason=f"推荐生成遇到问题: {str(e)}",
                score=0.0,
                scene=scene,
                tips=["请稍后重试或联系客服"]
            )

    def _generate_smart_reason(
        self,
        temperature: float,
        weather: str,
        scene: str,
        outfit: dict,
        review: dict,
        meta: dict
    ) -> str:
        """生成智能推荐理由"""
        temp_level = meta.get("temperature_level", "舒适")
        scene_desc = meta.get("scene_description", "")

        # 基础描述
        weather_desc = {
            "晴": "阳光明媚",
            "多云": "多云",
            "阴": "阴天",
            "小雨": "有小雨",
            "中雨": "有雨",
            "大雨": "大雨",
            "雪": "下雪",
            "雾": "有雾",
            "霾": "有霾",
        }.get(weather, weather)

        base_reason = f"今天{temp_level}（{temperature}°C），{weather_desc}，适合{scene}。{scene_desc}"

        # 添加衣物详情
        outfit_details = []
        if outfit.get("top"):
            top = outfit["top"]
            details = f"上衣：{top.get('color', '')}{top.get('type', '')}"
            if top.get("material"):
                details += f"（{top.get('material')}）"
            if top.get("thickness") and top.get("thickness") not in ["", "中等"]:
                details += f"[{top.get('thickness')}]"
            outfit_details.append(details)

        if outfit.get("pants"):
            pants = outfit["pants"]
            details = f"下装：{pants.get('color', '')}{pants.get('type', '')}"
            outfit_details.append(details)

        if outfit.get("jacket"):
            jacket = outfit["jacket"]
            details = f"外套：{jacket.get('color', '')}{jacket.get('type', '')}"
            outfit_details.append(details)

        if outfit.get("shoes"):
            shoes = outfit["shoes"]
            details = f"鞋子：{shoes.get('color', '')}{shoes.get('type', '')}"
            outfit_details.append(details)

        # AI 审核反馈
        if review.get("issues"):
            base_reason += "\n\n⚠️ AI审核建议："
            for issue in review["issues"][:2]:  # 最多显示2个问题
                base_reason += f"\n• {issue}"

        if outfit_details:
            base_reason += "\n\n📋 推荐搭配：\n" + "\n".join(outfit_details)

        return base_reason

    def _generate_smart_tips(
        self,
        weather: dict,
        temperature: float,
        outfit: dict,
        scores: dict
    ) -> List[str]:
        """生成智能穿搭建议"""
        tips = []

        # 温度相关建议
        if temperature < 5:
            tips.append("极度寒冷，建议穿保暖内衣+厚毛衣+羽绒服，全副武装保暖")
        elif temperature < 15:
            tips.append("气温较低，建议穿外套或风衣，早晚温差大请注意")
        elif temperature > 30:
            tips.append("高温天气，选择轻薄透气的棉麻材质，注意防暑")
        else:
            tips.append("今日气温舒适，适合轻装出行")

        # 天气相关建议
        if weather.get("precipitation_probability", 0) > 50:
            tips.append("降雨概率较高，建议带伞或穿防水鞋")
        if weather.get("wind_speed", 0) > 15:
            tips.append("今天风较大，建议选择防风外套")
        if weather.get("uv_index", 0) > 7:
            tips.append("紫外线较强，外出做好防晒")

        # 材质建议
        materials = set()
        for key in ["top", "pants", "jacket"]:
            if outfit.get(key):
                material = outfit[key].get("material", "")
                if material:
                    materials.add(material)

        if "羊毛" in materials or "羊绒" in materials:
            tips.append("含有羊毛/羊绒材质，注意避免摩擦起球")
        if "皮革" in materials:
            tips.append("皮革材质注意防潮，定期保养")

        # 评分反馈
        if scores.get("style_consistency", 0) < 6:
            tips.append("建议保持整体风格统一")
        if scores.get("color_harmony", 0) < 6:
            tips.append("可以尝试经典配色，如黑白灰蓝")

        if not tips:
            tips.append("今日宜出行，尽情享受穿搭的乐趣！")

        return tips[:5]  # 最多5条建议

    def _generate_reason(self, temperature: float, weather: str, scene: str, temp_level: str) -> str:
        """生成推荐理由"""
        weather_descriptions = {
            "晴": "阳光明媚",
            "多云": "多云",
            "阴": "阴天",
            "小雨": "有小雨",
            "中雨": "有雨",
            "大雨": "大雨",
            "雪": "下雪",
            "雾": "有雾",
            "霾": "有霾",
        }
        weather_desc = weather_descriptions.get(weather, weather)

        temp_advice = {
            "极热": "气温极高，建议选择轻薄透气的衣物",
            "炎热": "气温较高，建议选择清凉舒适的衣物",
            "热": "气温偏热，建议选择轻薄衣物",
            "温暖": "气温舒适，是穿搭的好时节",
            "凉爽": "气温转凉，建议适当增添衣物",
            "微冷": "气温较冷，建议穿厚实一些",
            "冷": "气温较低，需要注意保暖",
            "寒冷": "气温很低，保暖是第一要务",
            "严寒": "极寒天气，务必做好防寒措施",
        }

        return f"今天{temp_level}（{temperature}°C），{weather_desc}，适合{scene}。{temp_advice.get(temp_level, '请根据实际情况选择衣物')}。"

    def _generate_enhanced_reason(
        self, 
        temperature: float, 
        weather: str, 
        scene: str, 
        temp_level: str,
        top: dict = None,
        pants: dict = None,
        jacket: dict = None
    ) -> str:
        """生成增强的推荐理由，结合实际选中的衣物属性"""
        weather_descriptions = {
            "晴": "阳光明媚",
            "多云": "多云",
            "阴": "阴天",
            "小雨": "有小雨",
            "中雨": "有雨",
            "大雨": "大雨",
            "雪": "下雪",
            "雾": "有雾",
            "霾": "有霾",
        }
        weather_desc = weather_descriptions.get(weather, weather)

        temp_advice = {
            "极热": "气温极高，建议选择轻薄透气的衣物",
            "炎热": "气温较高，建议选择清凉舒适的衣物",
            "热": "气温偏热，建议选择轻薄衣物",
            "温暖": "气温舒适，是穿搭的好时节",
            "凉爽": "气温转凉，建议适当增添衣物",
            "微冷": "气温较冷，建议穿厚实一些",
            "冷": "气温较低，需要注意保暖",
            "寒冷": "气温很低，保暖是第一要务",
            "严寒": "极寒天气，务必做好防寒措施",
        }

        base_reason = f"今天{temp_level}（{temperature}°C），{weather_desc}，适合{scene}。{temp_advice.get(temp_level, '请根据实际情况选择衣物')}"

        # 添加衣物详情
        outfit_details = []
        if top:
            color = top.get("color", "")
            material = top.get("material", "")
            thickness = top.get("thickness", "")
            outfit_details.append(f"上衣：{color}{top.get('type', '')}（{material}，{thickness}）")
        if pants:
            color = pants.get("color", "")
            outfit_details.append(f"下装：{color}{pants.get('type', '')}")
        if jacket:
            color = jacket.get("color", "")
            outfit_details.append(f"外套：{color}{jacket.get('type', '')}")

        if outfit_details:
            base_reason += "\n\n" + "，".join(outfit_details)

        return base_reason

    def _generate_enhanced_tips(
        self, 
        weather: dict, 
        temperature: float,
        top: dict = None,
        pants: dict = None,
        jacket: dict = None
    ) -> List[str]:
        """生成增强的穿搭建议，结合衣物的实际属性"""
        tips = []

        # 温度相关建议
        if temperature < 5:
            tips.append("天气寒冷，建议穿加绒或厚实材质的衣物，注意手脚保暖")
        elif temperature < 15:
            tips.append("早晚温差较大，建议携带外套方便增减")
        elif temperature > 30:
            tips.append("高温天气，建议选择轻薄透气的棉麻材质，避免中暑")

        # 降雨相关建议
        if weather.get("precipitation_probability", 0) > 50:
            tips.append("降雨概率较高，记得带伞或穿防水鞋")

        # 紫外线相关建议
        if weather.get("uv_index", 0) > 7:
            tips.append("紫外线较强，外出记得做好防晒措施")

        # 风速相关建议
        if weather.get("wind_speed", 0) > 15:
            tips.append("今天风较大，建议选择防风材质的外套")

        # 衣物材质建议
        if top and top.get("material") in ["羊毛", "羊绒", "针织"]:
            tips.append(f"这件{top.get('type')}是{top.get('material')}材质，注意避免摩擦起球")

        # 搭配建议
        if top and pants:
            top_color = top.get("color", "")
            pants_color = pants.get("color", "")
            # 基础颜色搭配建议
            neutral_colors = ["黑色", "白色", "灰色", "深蓝色"]
            if top_color in neutral_colors or pants_color in neutral_colors:
                tips.append("经典配色，永不出错")

        if not tips:
            tips.append("今日天气宜人，尽情享受穿搭的乐趣吧！")

        return tips

    def _generate_tips(self, weather: dict) -> List[str]:
        """生成穿搭建议"""
        tips = []
        
        temp = weather.get("temperature", 20)
        if temp < 10:
            tips.append("建议穿上厚外套，注意保暖")
        elif temp < 20:
            tips.append("建议携带一件外套，早晚温差较大")
        
        if weather.get("precipitation_probability", 0) > 50:
            tips.append("降雨概率较高，建议携带雨伞")
        
        if weather.get("uv_index", 0) > 7:
            tips.append("紫外线较强，建议做好防晒措施")
        
        if weather.get("wind_speed", 0) > 10:
            tips.append("风速较大，建议选择防风衣物")
        
        if not tips:
            tips.append("今日天气适宜，尽情享受美好时光吧")
        
        return tips
    
    async def chat(
        self,
        message: str,
        context: Optional[Dict] = None
    ) -> tuple[str, List[str]]:
        """
        AI聊天
        返回: (回复内容, 建议问题列表)
        """
        message_lower = message.lower()
        
        # 意图识别
        if "穿什么" in message or "推荐" in message or "搭配" in message:
            response = self._get_fashion_advice(context)
            suggestions = ["今天适合户外运动吗？", "下周去北京应该带什么衣服？", "帮我推荐一套约会穿搭"]
        elif "天气" in message:
            response = self._get_weather_advice(context)
            suggestions = ["明天会下雨吗？", "这周温度怎么样？", "紫外线强吗？"]
        elif "衣橱" in message or "衣服" in message:
            response = "您可以在衣橱页面管理您的衣服。上传图片后，AI会自动识别衣服的属性，包括颜色、材质、风格等。\n\n您的数字衣橱会根据季节和天气智能推荐穿搭方案哦！"
            suggestions = ["如何上传衣服？", "AI怎么识别衣服？", "查看我的衣橱"]
        else:
            response = self._get_general_advice(message)
            suggestions = ["今天应该穿什么？", "北京现在天气怎么样？", "帮我选一套衣服"]
        
        return response, suggestions
    
    def _get_fashion_advice(self, context: Optional[Dict]) -> str:
        """获取穿搭建议"""
        city = context.get("city", "北京") if context else "北京"
        city_from_intent = context.get("city_from_intent") if context else None

        if context and context.get("temperature"):
            temp = context["temperature"]
            weather = context.get("weather", "")
            weather_desc = context.get("description", "")

            # 根据温度生成穿搭建议
            if temp < 0:
                advice = f"{city}今天严寒（{temp}°C），{weather_desc}。建议穿羽绒服、保暖内衣、厚毛衣，加绒裤子，雪地靴，围巾手套帽子全副武装。"
            elif temp < 10:
                advice = f"{city}今天很冷（{temp}°C），{weather_desc}。建议穿厚外套、毛衣或卫衣，搭配保暖裤和靴子。早晚温差大，建议带备用保暖衣物。"
            elif temp < 20:
                advice = f"{city}今天凉爽（{temp}°C），{weather_desc}。建议穿外套、卫衣或薄毛衣，搭配长裤。可以考虑叠穿，方便增减衣物。"
            elif temp < 28:
                advice = f"{city}今天温暖舒适（{temp}°C），{weather_desc}。建议穿长袖、薄外套或卫衣，搭配休闲裤或牛仔裤。"
            else:
                advice = f"{city}今天炎热（{temp}°C），{weather_desc}。建议穿轻薄透气的T恤、短裤，注意防晒和补充水分。"

            # 添加天气相关的额外建议
            if weather and "雨" in weather:
                advice += "另外，今天有雨，记得带雨伞或穿防水的鞋子。"
            elif weather and "雪" in weather:
                advice += "有雪！路面可能湿滑，请穿防滑的鞋子。"

            return advice

        # 如果只知道城市但不知道温度
        if city_from_intent:
            return f"我已经为您查询了{city}的天气，但温度信息似乎没有返回。您可以换个方式再问一下，或者告诉我您想了解的具体穿搭场景。"

        return "告诉我您所在的地区和当前天气，我可以为您推荐合适的穿搭哦！"

    def _get_weather_advice(self, context: Optional[Dict]) -> str:
        """获取天气建议"""
        city = context.get("city", "北京") if context else "北京"
        city_from_intent = context.get("city_from_intent") if context else None

        if context and context.get("weather"):
            weather = context.get("weather", "")
            temp = context.get("temperature", 0)
            humidity = context.get("humidity", 0)
            wind_speed = context.get("wind_speed", 0)
            description = context.get("description", "")

            # 构建详细的天气描述
            advice = f"{city}今天天气{weather}，气温{ temp}°C。"

            # 添加温度感受
            if temp < 5:
                advice += "天气寒冷，建议减少外出，做好防寒保暖措施。"
            elif temp < 15:
                advice += "天气较凉，早晚温差大，外出建议加件外套。"
            elif temp < 25:
                advice += "天气舒适，适合各种户外活动。"
            elif temp < 35:
                advice += "天气较热，户外活动请注意防暑降温。"
            else:
                advice += "高温预警！请尽量避免在高温时段外出，注意防暑。"

            # 添加其他天气信息
            if humidity > 80:
                advice += f"另外湿度较高（{humidity}%），可能会感觉闷热。"
            if wind_speed > 10:
                advice += f"今天风速较大（{wind_speed}级），请注意防风。"

            # 添加活动建议
            if "雨" in weather:
                advice += "不太适合户外活动，建议带雨具或安排室内活动。"
            elif "雪" in weather:
                advice += "路面可能结冰，外出请注意安全，减速慢行。"
            else:
                advice += "整体来说适合外出活动。"

            return advice

        # 如果只知道城市但没有天气数据
        if city_from_intent:
            return f"我识别到您在询问{city}的天气，但获取天气信息时遇到了一些问题。您可以稍后再试，或者换个方式描述您的问题。"

        return "我可以根据您的位置和天气情况提供穿搭建议。请问您想了解哪里的天气呢？"
    
    def _get_general_advice(self, message: str) -> str:
        """获取通用建议"""
        greetings = ["你好", "hi", "hello", "嗨"]
        if any(g in message.lower() for g in greetings):
            return "您好！我是FashionWeather AI您的智能穿搭助手。\n\n我可以帮您：\n• 根据天气推荐穿搭\n• 分析您的衣橱\n• 解答穿搭相关问题\n\n请问有什么可以帮助您的？"
        
        return "我对时尚和天气穿搭颇有研究。您可以问我：\n• \"今天应该穿什么？\"\n• \"这周天气怎么样？\"\n• \"帮我推荐一套约会穿搭\"\n\n我会根据您的需求给出专业建议！"

ai_service = AIService()
