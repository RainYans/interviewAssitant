from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    """通过邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """通过ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    """创建新用户"""
    # 生成密码哈希
    hashed_password = get_password_hash(user.password)
    
    # 创建用户对象
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    
    # 添加到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate):
    """更新用户信息"""
    # 获取用户
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # 准备更新数据
    update_data = user.dict(exclude_unset=True)
    
    # 如果包含密码，更新密码哈希
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # 更新属性
    for field, value in update_data.items():
        if hasattr(db_user, field) and value is not None:
            setattr(db_user, field, value)
    
    # 提交更改
    db.commit()
    db.refresh(db_user)
    
    return db_user