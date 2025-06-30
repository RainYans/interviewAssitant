try:
    # pydantic v2
    from pydantic_settings import BaseSettings
    from pydantic import Field
    PYDANTIC_V2 = True
except ImportError:
    try:
        # pydantic v1
        from pydantic import BaseSettings, Field
        PYDANTIC_V2 = False
    except ImportError:
        raise ImportError("请安装 pydantic-settings: pip install pydantic-settings")

import os
from typing import List
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    """应用设置类，从环境变量加载配置"""
    
    # === 基础配置 ===
    PROJECT_NAME: str = "Interview System API"
    API_V1_STR: str = "/api/v1"
    
    # === 服务器配置 ===
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # === 数据库设置 ===
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # === JWT设置 ===
    SECRET_KEY: str = "your_actual_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # === CORS配置 ===
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173"
    
    # === 文件上传配置 ===
    UPLOAD_FOLDER: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    def get_cors_origins(self) -> List[str]:
        """获取CORS域名列表"""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    # pydantic 配置
    if PYDANTIC_V2:
        # pydantic v2 配置
        model_config = {
            "env_file": ".env",
            "case_sensitive": True,
            "extra": "ignore"  # 忽略额外字段而不是报错
        }
    else:
        # pydantic v1 配置
        class Config:
            env_file = ".env"
            case_sensitive = True
            extra = "ignore"

# 创建设置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

# 创建设置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)