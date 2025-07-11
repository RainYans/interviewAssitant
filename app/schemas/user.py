# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ================== 用户认证相关 ==================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str  # 登录时使用用户名，而不是邮箱
    password: str

class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"

# ================== 用户资料相关 ==================

class UserProfileUpdate(BaseModel):
    """用于更新用户资料的Schema，匹配前端表单"""
    age: Optional[int] = None
    graduation_year: Optional[str] = None
    education: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    major_category: Optional[str] = None
    target_position: Optional[List[str]] = None

class UserResponse(BaseModel):
    """统一的用户信息返回模型"""
    id: int
    username: str
    email: EmailStr
    
    # 个人资料字段 (可以为None)
    age: Optional[int] = None
    graduation_year: Optional[str] = None
    education: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    major_category: Optional[str] = None
    target_position: Optional[List[str]] = []
    
    # **关键字段**：告诉前端资料是否完善
    has_profile: bool

    class Config:
        from_attributes = True # 兼容 SQLAlchemy 模型