# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_active_user
from app.schemas import user as user_schema
from app.services import user_service
from app.db.repositories import user_repo # 引入 repo 以支持可用性检查

router = APIRouter()

# ================== 用户资料管理接口 (精简后) ==================

@router.get("/me", response_model=user_schema.UserResponse, summary="获取当前用户资料")
def get_current_user_profile(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户的完整资料，包括基本信息和个人资料。
    - **has_profile**: 布尔值，指示用户的个人资料是否已填写完整。
    """
    user_data = user_service.get_user_profile_data(db, user=current_user)
    return user_data

@router.put("/me", response_model=user_schema.UserResponse, summary="更新当前用户资料")
def update_current_user_profile(
    profile_update: user_schema.UserProfileUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新当前登录用户的基本资料。
    前端只需传入需要修改的字段。
    """
    # 将Pydantic模型转为字典，并排除未设置的字段
    profile_dict = profile_update.dict(exclude_unset=True)
    print(f"✅ [API层] 收到的数据: {profile_dict}")
    if not profile_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供任何需要更新的数据"
        )

    user_service.update_or_create_user_profile(db, user_id=current_user.id, profile_data=profile_dict)
    
    # 返回更新后的完整用户数据
    updated_user_data = user_service.get_user_profile_data(db, user=current_user)
    return updated_user_data

# ================== 可用性检查接口 (保留并优化) ==================

@router.post("/check-username", summary="检查用户名可用性")
def check_username_availability(data: dict, db: Session = Depends(get_db)):
    """检查用户名是否已被注册"""
    username = data.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能为空"
        )
    
    existing_user = user_repo.get_user_by_username(db, username)
    return {"available": existing_user is None}

@router.post("/check-email", summary="检查邮箱可用性")
def check_email_availability(data: dict, db: Session = Depends(get_db)):
    """检查邮箱是否已被注册"""
    email = data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱不能为空"
        )
    
    existing_user = user_repo.get_user_by_email(db, email)
    return {"available": existing_user is None}