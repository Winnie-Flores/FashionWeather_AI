from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.clothes import Clothes
from app.schemas.clothes import ClothesCreate, ClothesUpdate, ClothesResponse, ClothesListResponse, ClothesAnalysis
from app.services.ai_service import ai_service
import os
import uuid
import aiofiles
import logging

router = APIRouter(prefix="/api/clothes", tags=["衣橱"])

# 配置日志
logger = logging.getLogger(__name__)

@router.get("", response_model=ClothesListResponse)
async def get_clothes_list(
    page: int = 1,
    page_size: int = 20,
    type: Optional[str] = None,
    color: Optional[str] = None,
    season: Optional[str] = None,
    style: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取衣服列表"""
    query = db.query(Clothes).filter(Clothes.user_id == current_user.id)
    
    # 筛选条件
    if type:
        query = query.filter(Clothes.type == type)
    if color:
        query = query.filter(Clothes.color == color)
    if season:
        query = query.filter(Clothes.season == season)
    if style:
        query = query.filter(Clothes.style == style)
    
    # 统计总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    clothes = query.order_by(Clothes.created_at.desc()).offset(offset).limit(page_size).all()
    
    return ClothesListResponse(
        items=[ClothesResponse.model_validate(c) for c in clothes],
        total=total,
        page=page,
        page_size=page_size
    )

@router.post("", response_model=ClothesResponse, status_code=201)
async def add_clothes(
    clothes_data: ClothesCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加衣服"""
    new_clothes = Clothes(
        user_id=current_user.id,
        **clothes_data.model_dump()
    )
    
    db.add(new_clothes)
    db.commit()
    db.refresh(new_clothes)
    
    return new_clothes

@router.post("/upload")
async def upload_clothes_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传衣服图片"""
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持 JPG、PNG、WebP 格式的图片")
    
    # 验证文件大小
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过10MB")
    
    # 生成唯一文件名
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    # 保存文件
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(contents)
    
    # 分析图片
    image_url = f"/uploads/{filename}"
    analysis = await ai_service.analyze_clothes(image_url)
    
    return {
        "image_url": image_url,
        "analysis": analysis.model_dump()
    }

@router.get("/{clothes_id}", response_model=ClothesResponse)
async def get_clothes(
    clothes_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取衣服详情"""
    clothes = db.query(Clothes).filter(
        Clothes.id == clothes_id,
        Clothes.user_id == current_user.id
    ).first()
    
    if not clothes:
        raise HTTPException(status_code=404, detail="衣服不存在")
    
    return clothes

@router.put("/{clothes_id}", response_model=ClothesResponse)
async def update_clothes(
    clothes_id: int,
    clothes_data: ClothesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新衣服信息"""
    clothes = db.query(Clothes).filter(
        Clothes.id == clothes_id,
        Clothes.user_id == current_user.id
    ).first()
    
    if not clothes:
        raise HTTPException(status_code=404, detail="衣服不存在")
    
    for key, value in clothes_data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(clothes, key, value)
    
    db.commit()
    db.refresh(clothes)
    
    return clothes

@router.delete("/{clothes_id}", status_code=204)
async def delete_clothes(
    clothes_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除衣服"""
    clothes = db.query(Clothes).filter(
        Clothes.id == clothes_id,
        Clothes.user_id == current_user.id
    ).first()
    
    if not clothes:
        raise HTTPException(status_code=404, detail="衣服不存在")
    
    # 删除图片文件 - 修复路径处理逻辑
    if clothes.image_url:
        try:
            # 获取图片文件名
            image_url = clothes.image_url.strip()
            
            # 处理路径：移除开头的 /uploads/ 或 uploads/
            if image_url.startswith('/uploads/'):
                filename = image_url[9:]  # 移除 /uploads/
            elif image_url.startswith('uploads/'):
                filename = image_url[8:]  # 移除 uploads/
            else:
                filename = image_url
            
            # 构建完整路径
            filepath = os.path.join(settings.UPLOAD_DIR, filename)
            
            # 确保路径安全，防止目录遍历攻击
            upload_dir = os.path.abspath(settings.UPLOAD_DIR)
            file_path_abs = os.path.abspath(filepath)
            
            if file_path_abs.startswith(upload_dir) and os.path.isfile(file_path_abs):
                os.remove(file_path_abs)
                logger.info(f"[删除衣服] 已删除图片文件: {filepath}")
                
                # 尝试删除空目录（如果文件夹为空）
                dir_path = os.path.dirname(file_path_abs)
                if os.path.isdir(dir_path) and not os.listdir(dir_path):
                    try:
                        os.rmdir(dir_path)
                        logger.info(f"[删除衣服] 已删除空目录: {dir_path}")
                    except OSError:
                        pass  # 目录非空或有其他文件，跳过
            else:
                logger.warning(f"[删除衣服] 文件不存在或路径不安全: {filepath}")
        except Exception as e:
            logger.error(f"[删除衣服] 删除图片文件失败: {str(e)}")
    
    db.delete(clothes)
    db.commit()
    
    return None

@router.post("/analyze", response_model=ClothesAnalysis)
async def analyze_clothes_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """分析衣服图片"""
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持 JPG、PNG、WebP 格式的图片")
    
    # 验证文件大小（必须检查，防止大文件导致的问题）
    contents = await file.read()
    file_size = len(contents)
    
    # 10MB 限制
    max_size = 10 * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(status_code=400, detail="图片大小不能超过10MB，请压缩后重试")
    
    # 500KB 以下警告（可能是缩略图或小图）
    min_size = 500 * 1024
    if file_size < min_size:
        logger.warning(f"[上传] 图片较小({file_size / 1024:.1f}KB)，识别效果可能受影响")
    
    logger.info(f"[上传] 待处理图片大小: {file_size / 1024:.2f} KB")
    
    # 保存临时文件
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"temp_{uuid.uuid4()}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(contents)
    
    # 分析图片
    image_url = f"/uploads/{filename}"
    analysis = await ai_service.analyze_clothes(image_url)
    
    # 删除临时文件
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            logger.info(f"[上传] 已清理临时文件: {filename}")
        except Exception as e:
            logger.warning(f"[上传] 清理临时文件失败: {e}")
    
    return analysis
