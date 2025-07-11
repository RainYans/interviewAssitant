# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import database
from app.db.repositories import user_repo # 确保你已经创建了这个repo文件
from app.core.config import settings
from app.models.user import User


# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 方案，它会告诉FastAPI从哪里获取token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码和哈希密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码的哈希值"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# --- 修改开始 ---
# 将 get_current_user 修改为 get_current_active_user 并增加逻辑
def get_current_active_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(database.get_db)
) -> User:
    """
    通过Token获取当前激活的用户。
    Token的'sub'字段现在应该包含 user_id。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # --- 修改点: 将 "sub" 解析为整数类型的 user_id ---
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # 将 sub 从字符串转换为整数
        token_data_id = int(user_id)
    except (JWTError, ValueError): # 增加ValueError以捕获int转换失败
        raise credentials_exception
    
    # --- 修改点: 使用 user_id 从数据库获取用户 ---
    user = user_repo.get_user_by_id(db, user_id=token_data_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
        
    return user
# --- 修改结束 ---