# app/services/user_service.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import UserProfile
from app.core.security import get_password_hash
from app.schemas.user import UserUpdate

def get_user_by_email(db: Session, email: str):
    """通过邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """通过用户名获取用户"""
    return db.query(User).filter(User.username == username).first()

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    """更新用户基本信息"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # 更新字段
    if user_update.email:
        user.email = user_update.email
    if user_update.username:
        user.username = user_update.username
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(user)
    
    return user

def get_user_profile(db: Session, user_id: int):
    """获取用户资料"""
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

def update_user_profile(db: Session, user_id: int, profile_data: dict):
    """更新或创建用户资料"""
    # 查找现有资料
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if profile:
        # 更新现有资料
        for key, value in profile_data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
    else:
        # 创建新资料
        profile = UserProfile(user_id=user_id, **profile_data)
        db.add(profile)
    
    # ===== 修复：这三行应该在这里！ =====
    db.commit()
    db.refresh(profile)
    return profile

def check_profile_complete(profile):
    """
    检查用户资料是否完整
    返回 True/False
    """
    if not profile:
        return False
    
    # 定义必需字段（与前端Profile.vue中的必填项对应）
    required_fields = [
        'age',           # 年龄
        'graduation_year', # 毕业年份
        'education',     # 学历
        'school',        # 院校
        'major_category', # 专业类别
        'major',         # 具体专业
        'target_position' # 意向岗位
    ]
    
    for field in required_fields:
        value = getattr(profile, field, None)
        
        # 检查字段是否为空
        if not value or value == '' or value == 'null':
            return False
            
        # 特殊处理target_position（JSON字符串）
        if field == 'target_position':
            try:
                import json
                if isinstance(value, str):
                    parsed_value = json.loads(value)
                    if not parsed_value or len(parsed_value) == 0:
                        return False
                elif isinstance(value, list):
                    if len(value) == 0:
                        return False
            except:
                return False
    
    return True