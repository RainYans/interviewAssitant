from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate,  UserProfileUpdate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    """通过邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """通过用户名获取用户"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """通过ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    """创建新用户"""
    # 创建新用户实例
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=True
    )
    
    # 添加到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user_id: int, user_update:  UserProfileUpdate):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # 更新字段
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "password":
            # 密码需要哈希处理
            user.hashed_password = get_password_hash(value)
        elif hasattr(user, field):
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user

def delete_user(db: Session, user_id: int):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """获取用户列表"""
    return db.query(User).offset(skip).limit(limit).all()

def activate_user(db: Session, user_id: int):
    """激活用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user
    return None

def deactivate_user(db: Session, user_id: int):
    """停用用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    return None