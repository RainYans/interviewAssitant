from pydantic import BaseSettings
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    """应用设置类，从环境变量加载配置"""
    
    # === 基础配置 ===
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Interview System API")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")  # 关键修改！
    
    # === 服务器配置 ===
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    
    # === 数据库设置 ===
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # === JWT设置 ===
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_actual_secret_key_here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # === CORS配置 - 简化处理 ===
    def get_cors_origins(self):
        """获取CORS域名列表"""
        cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        return [origin.strip() for origin in cors_origins.split(",")]
    
    # === 文件上传配置 ===
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB

# 创建设置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)