from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.api import auth, servers, scripts, users, alerts, tasks
from app.services.scheduler_service import scheduler_service

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(servers.router, prefix="/api")
app.include_router(scripts.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    """应用启动时执行"""
    # 初始化数据库
    init_db()
    
    # 创建默认管理员用户
    db = next(get_db())
    admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
    if not admin:
        admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True
        )
        db.add(admin)
        db.commit()
        print(f"Created admin user: {settings.ADMIN_USERNAME}")
    
    # 加载定时任务
    scheduler_service.load_tasks()


@app.on_event("shutdown")
def on_shutdown():
    """应用关闭时执行"""
    scheduler_service.shutdown()


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "欢迎使用运维自动化平台",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

