# app/services/user_service.py
from sqlalchemy.orm import Session
from typing import Optional 
import json
from app.models.user import User
from app.models.profile import UserProfile

def get_user_profile(db: Session, user_id: int) -> Optional[UserProfile]:
    """获取用户的Profile记录"""
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

def check_profile_complete(profile: Optional[UserProfile]) -> bool:
    """检查用户资料是否完整"""
    if not profile:
        print("❌ 检查失败: Profile记录在数据库中不存在。")
        return False
    # 定义所有必填的资料字段
    required_fields = ['age', 'graduation_year', 'education', 'school', 'major', 'target_position']
    for field in required_fields:
        value = getattr(profile, field, None)
        # 任何一个字段是None或空字符串都算不完整
        if value is None or value == '':
            print(f"❌ 检查失败: 字段 '{field}' 是空的。")
            return False
                # 专门检查列表类型是否为空
        if isinstance(value, list) and not value:
            print(f"❌ 检查失败: 字段 '{field}' 是一个空列表。")
            return False
            
        # 专门检查从数据库取出的JSON字符串是否是代表空列表的 "[]"
        if isinstance(value, str) and value.strip() == '[]':
            print(f"❌ 检查失败: 字段 '{field}' 是一个空的JSON列表字符串 '[]'。")
            return False
        # 对列表/JSON字段，需要判断是否为空列表
        if field == 'target_position':
            # 数据库里存的是JSON字符串或原生JSON
            if isinstance(value, str):
                try:
                    parsed_list = json.loads(value)
                    if not parsed_list: return False
                except json.JSONDecodeError:
                    return False
            elif isinstance(value, list) and not value:
                return False
    print("✅ 检查通过: 所有必填字段都已填写。")
    return True

def get_user_profile_data(db: Session, user: User) -> dict:
    """获取完整的用户资料和完成状态"""
    profile = get_user_profile(db, user.id)
    is_complete = check_profile_complete(profile)
    
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "has_profile": is_complete,
    }
    
    if profile:
        # 将profile的所有字段合并到返回数据中
        profile_dict = {c.name: getattr(profile, c.name) for c in profile.__table__.columns if c.name not in ['id', 'user_id', 'created_at', 'updated_at']}
        # 特殊处理JSON字段的解码
        if 'target_position' in profile_dict and isinstance(profile_dict['target_position'], str):
            try:
                profile_dict['target_position'] = json.loads(profile_dict['target_position'])
            except json.JSONDecodeError:
                profile_dict['target_position'] = []
        user_data.update(profile_dict)
    
    return user_data

def update_or_create_user_profile(db: Session, user_id: int, profile_data: dict):
    """更新或创建用户资料"""
    profile = get_user_profile(db, user_id)
    
    if 'target_position' in profile_data and isinstance(profile_data['target_position'], list):
        profile_data['target_position'] = json.dumps(profile_data['target_position'], ensure_ascii=False)

    if profile:
        for key, value in profile_data.items():
            setattr(profile, key, value)
    else:
        profile = UserProfile(user_id=user_id, **profile_data)
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    return profile