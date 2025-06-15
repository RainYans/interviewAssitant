from pydantic import BaseSettings
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    """应用设置类，从环境变量加载配置"""
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Interview System API")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api")
    
    # 数据库设置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # JWT设置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 创建设置实例
settings = Settings()