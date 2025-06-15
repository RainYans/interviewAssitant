from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
# 如果使用SQLite，添加check_same_thread=False参数
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类，所有模型将继承此类
Base = declarative_base()

# 依赖函数，用于获取数据库会话
def get_db():
    """FastAPI依赖，提供数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()