# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import user as user_schema # 从schemas统一导入模型
from app.services import auth_service, user_service # 导入需要的服务
from app.core import security
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=user_schema.UserResponse, status_code=status.HTTP_201_CREATED, summary="用户注册")
def register(user_in: user_schema.UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户，并返回不含密码的用户信息。
    """
    # 检查用户名是否已存在
    if auth_service.get_user_by_username(db, username=user_in.username):
        raise HTTPException(status_code=400, detail="该用户名已被注册")
        
    # 检查邮箱是否已存在
    if auth_service.get_user_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="该邮箱已被注册")
    
    # 创建用户
    user = auth_service.create_user(db, user_in=user_in)
    
    # 构造不含敏感信息的返回数据
    # 新注册用户一定没有个人资料
    return user_schema.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        has_profile=False 
    )


@router.post("/login", summary="用户登录")
def login(
    # 将参数从 form_data 修改为接收 JSON 格式的 user_credentials
    # FastAPI 会自动用 UserLogin 模型来验证请求体
    user_credentials: user_schema.UserLogin, 
    db: Session = Depends(get_db)
):
    """通过用户名和密码登录 (接收JSON)"""
    # 使用 Pydantic 模型中的字段进行验证
    user = auth_service.authenticate_user(
        db, username=user_credentials.username, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户profile是否完善
    user_data = user_service.get_user_profile_data(db, user)

    # 创建Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # 返回统一的、包含所有需要信息的响应体
    return {
        "token": access_token,
        "token_type": "bearer",
        "user": user_data # user_data 中已经包含了 has_profile 字段
    }
