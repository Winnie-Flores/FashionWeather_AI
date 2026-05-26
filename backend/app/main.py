from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import get_db, init_db
from app.core.security import get_password_hash
from app.api import auth, weather, clothes, ai, chat, profile, favorites
# 导入所有模型以确保 SQLAlchemy 关系配置正确
from app.models.user import User
from app.models.clothes import Clothes
from app.models.outfit import Outfit
from app.models.favorite import FavoriteOutfit
from app.models.chat import ChatMessage
from app.models.weather import WeatherRecord
import os
import logging

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FashionWeather AI - 智能天气穿搭助手 API",
    docs_url="/docs",
    redoc_url="/redoc"
)

def create_test_user():
    """创建测试账号"""
    db = next(get_db())
    try:
        # 检查测试账号是否已存在
        existing_user = db.query(User).filter(User.username == "test").first()
        if not existing_user:
            test_user = User(
                username="test",
                email="test@example.com",
                password_hash=get_password_hash("test123"),
                gender="male",
                style_preference="casual",
                bio="这是测试账号"
            )
            db.add(test_user)
            db.commit()
            print("✅ 测试账号已创建: test / test123")
        else:
            print("ℹ️  测试账号已存在: test / test123")
    except Exception as e:
        print(f"⚠️  创建测试账号时出错: {e}")
    finally:
        db.close()

# 配置CORS - 注意：当 allow_credentials=True 时，不能使用通配符 "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth.router)
app.include_router(weather.router)
app.include_router(clothes.router)
app.include_router(ai.router)
app.include_router(chat.router)
app.include_router(profile.router)
app.include_router(favorites.router)

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    create_test_user()

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "智能天气穿搭助手 API",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
