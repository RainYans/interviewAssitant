# app/core/config.py

import os
from typing import List
from dotenv import load_dotenv

# 确保在最开始加载.env文件
load_dotenv()

try:
    # 兼容 pydantic v2
    from pydantic_settings import BaseSettings
except ImportError:
    # 兼容 pydantic v1
    from pydantic import BaseSettings

class Settings(BaseSettings):
    """应用设置类，从环境变量或.env文件加载配置"""
    
    # === 基础配置 ===
    PROJECT_NAME: str = "AI面试智能体 API"
    API_V1_STR: str = "/api/v1"
    
    # === 服务器配置 ===
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # === 数据库设置 ===
    # 默认使用SQLite，如果需要使用PostgreSQL等，可以在.env文件中覆盖此项
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # === JWT设置 ===
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a-super-secret-key-that-you-must-change")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # Token有效期为7天
    
    # === CORS配置 ===
    # 允许的前端源列表，用逗号分隔
    BACKEND_CORS_ORIGINS: str = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    
    def get_cors_origins(self) -> List[str]:
        """获取CORS域名列表"""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    # === 文件上传配置 ===
    UPLOAD_FOLDER: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

# 创建全局唯一的设置实例
settings = Settings()

# 确保上传目录在应用启动时存在
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)