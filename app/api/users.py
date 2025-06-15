from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.repositories import user_repo
from app.core.security import get_current_user
from app.schemas.user import User, UserUpdate

# 创建路由器
router = APIRouter()

@router.get("/me", response_model=User)
def get_current_user_info(current_user = Depends(get_current_user)):
    """获取当前用户信息API
    
    返回当前登录用户的详细信息
    """
    return current_user

@router.put("/me", response_model=User)
def update_user_info(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户信息API
    
    更新当前登录用户的个人信息
    """
    # 如果要更新邮箱，检查是否已被使用
    if user_update.email and user_update.email != current_user.email:
        existing_user = user_repo.get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # 更新用户信息
    updated_user = user_repo.update_user(db, current_user.id, user_update)
    
    return updated_user