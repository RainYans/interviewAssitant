from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, TokenResponse
from app.services import auth_service

# 创建路由器
router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录API
    
    使用邮箱和密码登录，返回访问令牌
    """
    # 验证用户
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成令牌
    access_token = auth_service.create_user_token(user.id)
    
    # 返回令牌
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册API
    
    注册新用户，返回访问令牌
    """
    # 检查邮箱是否已存在
    db_user = auth_service.get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建用户
    user = auth_service.create_user(db, user_data)
    
    # 生成令牌
    access_token = auth_service.create_user_token(user.id)
    
    # 返回令牌
    return {"access_token": access_token, "token_type": "bearer"}