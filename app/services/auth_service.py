from datetime import timedelta
from sqlalchemy.orm import Session
from app.db.repositories import user_repo
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.schemas.user import UserCreate

def authenticate_user(db: Session, email: str, password: str):
    """验证用户并返回用户对象"""
    # 获取用户
    user = user_repo.get_user_by_email(db, email)
    
    # 验证密码
    if not user or not verify_password(password, user.hashed_password):
        return None
        
    return user

def create_user_token(user_id: int):
    """为用户创建访问令牌"""
    # 设置令牌过期时间
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 创建令牌
    return create_access_token(
        data={"sub": str(user_id)}, 
        expires_delta=access_token_expires
    )

def get_user_by_email(db: Session, email: str):
    """通过邮箱获取用户"""
    return user_repo.get_user_by_email(db, email)

def create_user(db: Session, user_data: UserCreate):
    """创建新用户"""
    return user_repo.create_user(db, user_data)