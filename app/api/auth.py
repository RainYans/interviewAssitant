from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.schemas.user import UserCreate, TokenResponse
from app.services import auth_service

# 创建路由器
router = APIRouter()

# ===== 新增：匹配前端的请求模型 =====
class LoginRequest(BaseModel):
    """登录请求模型 - 匹配前端service.js中的格式"""
    username: str
    password: str

class RegisterRequest(BaseModel):
    """注册请求模型 - 匹配前端service.js中的格式"""
    username: str
    password: str
    email: str

# ===== 修改：登录接口支持JSON格式 =====
@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录API - 修改为支持JSON格式
    
    匹配前端: apiService.auth.login({username, password})
    返回格式: {code, data: {token, user}, message}
    """
    try:
        # 验证用户 - 这里username实际上可能是邮箱
        user = auth_service.authenticate_user(db, login_data.username, login_data.password)
        if not user:
            # 返回统一格式的错误响应
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 生成令牌
        access_token = auth_service.create_user_token(user.id)
        
        # 返回前端期望的格式
        return {
            "code": 200,
            "data": {
                "token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            },
            "message": "登录成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

@router.post("/register")
@router.post("/register")
def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册API - 修改为支持前端格式
    
    匹配前端: apiService.auth.register({username, password, email})
    返回格式: {code, data, message}
    """
    try:
        # 检查用户名是否已存在
        existing_user_by_username = auth_service.get_user_by_username(db, register_data.username)
        if existing_user_by_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="用户名已被注册"
            )
        
        # 检查邮箱是否已存在
        existing_user_by_email = auth_service.get_user_by_email(db, register_data.email)
        if existing_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="邮箱已被注册"
            )
        
        # 转换为UserCreate格式
        user_create_data = UserCreate(
            username=register_data.username,
            email=register_data.email,
            password=register_data.password
        )
        
        # 创建用户
        user = auth_service.create_user(db, user_create_data)
        
        # 生成令牌
        access_token = auth_service.create_user_token(user.id)
        
        # 返回前端期望的格式
        return {
            "code": 200,
            "data": {
                "token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            },
            "message": "注册成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

# ===== 新增：刷新Token接口 =====
@router.post("/refresh")
def refresh_token(authorization: Optional[str] = Header(None)):
    """
    刷新Token
    POST /api/v1/auth/refresh
    
    匹配前端: apiService.auth.refreshToken()
    返回格式: {code, data: {token}, message}
    """
    try:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="缺少认证Token"
            )
        
        # 移除Bearer前缀
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        
        # 这里简化处理，实际应该验证旧token并生成新token
        # TODO: 实现真正的token刷新逻辑
        
        return {
            "code": 200,
            "data": {
                "token": f"refreshed-{token[-10:]}"  # 模拟新token
            },
            "message": "Token刷新成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token刷新失败: {str(e)}"
        )

# ===== 保留原有的OAuth2登录接口（可选） =====
@router.post("/login-form", response_model=TokenResponse)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    表单登录API（保留用于API文档测试）
    
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