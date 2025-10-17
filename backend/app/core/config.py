from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./devops.db"
    
    # JWT配置
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 管理员配置
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_EMAIL: str = "admin@example.com"
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    
    # 项目信息
    PROJECT_NAME: str = "运维自动化平台"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "基于FastAPI的运维自动化管理平台"
    
    # SMTP邮件配置（用于告警通知）
    SMTP_ENABLED: bool = False  # 是否启用邮件通知
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # 发件人邮箱
    SMTP_PASSWORD: str = ""  # 邮箱密码或应用专用密码
    SMTP_FROM_NAME: str = "运维自动化平台"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

