from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 用户基础模式
class UserBase(BaseModel):
    email: EmailStr
    username: str

# 用户创建模式
class UserCreate(UserBase):
    password: str

# 用户更新模式
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

# 用户模式(响应)
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# 用户登录模式
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 令牌数据模式
class TokenData(BaseModel):
    user_id: Optional[int] = None

# 令牌响应模式
class TokenResponse(BaseModel):
    access_token: str
    token_type: str