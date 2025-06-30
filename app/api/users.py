from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.db.repositories import user_repo
from app.core.security import get_current_user
from app.schemas.user import User, UserUpdate
from app.services.user_service import get_user_profile, update_user_profile

# 创建路由器
router = APIRouter()

# ===== 新增：用户资料更新模型 =====
class UserProfileUpdate(BaseModel):
    """用户资料更新模型 - 匹配前端期望"""
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

# ===== 修改：获取用户资料接口 =====
@router.get("/profile")
def get_user_profile_api(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户资料 - 修改路径匹配前端期望
    GET /api/v1/users/profile
    
    匹配前端: apiService.user.getProfile()
    返回格式: {code, data: {用户资料}, message}
    """
    try:
        # 获取用户基本信息
        user_data = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "phone": "",
            "real_name": "",
            "bio": "",
            "avatar_url": ""
        }
        
        # 尝试获取扩展资料
        try:
            profile = get_user_profile(db, current_user.id)
            if profile:
                # 如果有扩展资料，合并数据
                if hasattr(profile, 'age'):
                    user_data.update({
                        "age": profile.age,
                        "graduation_year": profile.graduation_year,
                        "education": profile.education,
                        "school": profile.school,
                        "major_category": profile.major_category,
                        "major": profile.major,
                        "target_position": profile.target_position
                    })
        except Exception as e:
            # 如果获取扩展资料失败，使用基本信息
            print(f"获取扩展资料失败: {e}")
        
        return {
            "code": 200,
            "data": user_data,
            "message": "获取用户资料成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户资料失败: {str(e)}"
        )

# ===== 修改：更新用户资料接口 =====
@router.put("/profile")
def update_user_profile_api(
    profile_data: UserProfileUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户资料 - 修改为匹配前端期望
    PUT /api/v1/users/profile
    
    匹配前端: apiService.user.updateProfile(profile)
    返回格式: {code, data: {更新后的资料}, message}
    """
    try:
        # 检查邮箱冲突
        if profile_data.email and profile_data.email != current_user.email:
            existing_user = user_repo.get_user_by_email(db, profile_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被使用"
                )
        
        # 更新用户基本信息
        user_update_data = UserUpdate()
        if profile_data.email:
            user_update_data.email = profile_data.email
        if profile_data.username:
            user_update_data.username = profile_data.username
            
        if user_update_data.email or user_update_data.username:
            updated_user = user_repo.update_user(db, current_user.id, user_update_data)
        else:
            updated_user = current_user
        
        # 更新扩展资料
        profile_dict = {}
        for field, value in profile_data.dict(exclude_unset=True).items():
            if field not in ['email', 'username'] and value is not None:
                profile_dict[field] = value
        
        if profile_dict:
            try:
                update_user_profile(db, current_user.id, profile_dict)
            except Exception as e:
                print(f"更新扩展资料失败: {e}")
        
        # 返回更新后的资料
        response_data = {
            "id": updated_user.id,
            "username": updated_user.username,
            "email": updated_user.email,
            "phone": profile_data.phone or "",
            "real_name": profile_data.real_name or "",
            "bio": profile_data.bio or "",
            "avatar_url": profile_data.avatar_url or ""
        }
        
        return {
            "code": 200,
            "data": response_data,
            "message": "更新用户资料成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户资料失败: {str(e)}"
        )

# ===== 保留原有接口（用于兼容） =====
@router.get("/me", response_model=User)
def get_current_user_info(current_user = Depends(get_current_user)):
    """获取当前用户信息API（保留用于兼容）
    
    返回当前登录用户的详细信息
    """
    return current_user

@router.put("/me", response_model=User)
def update_user_info(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户信息API（保留用于兼容）
    
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

# ===== 新增：检查用户名和邮箱可用性 =====
@router.post("/check-username")
def check_username_availability(username_data: dict, db: Session = Depends(get_db)):
    """
    检查用户名是否可用
    POST /api/v1/users/check-username
    """
    try:
        username = username_data.get("username")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名不能为空"
            )
        
        existing_user = user_repo.get_user_by_username(db, username)
        available = existing_user is None
        
        return {
            "code": 200,
            "data": {
                "available": available,
                "username": username
            },
            "message": "用户名可用" if available else "用户名已存在"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查用户名失败: {str(e)}"
        )

@router.post("/check-email")
def check_email_availability(email_data: dict, db: Session = Depends(get_db)):
    """
    检查邮箱是否可用
    POST /api/v1/users/check-email
    """
    try:
        email = email_data.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱不能为空"
            )
        
        existing_user = user_repo.get_user_by_email(db, email)
        available = existing_user is None
        
        return {
            "code": 200,
            "data": {
                "available": available,
                "email": email
            },
            "message": "邮箱可用" if available else "邮箱已存在"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查邮箱失败: {str(e)}"
        )