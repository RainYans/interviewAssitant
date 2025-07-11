from datetime import timedelta
from sqlalchemy.orm import Session
from app.db.repositories import user_repo
from app.core import security
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.schemas.user import UserCreate

def authenticate_user(db: Session, username: str, password: str):
    """
    验证用户并返回用户对象。
    支持用户名或邮箱登录。
    参数名已从 username_or_email 修改为 username 以匹配API层的调用。
    """
    user = None
    
    # 首先尝试作为邮箱查找
    if "@" in username:
        user = user_repo.get_user_by_email(db, email=username)
    
    # 如果邮箱查找失败，或者输入不包含@，尝试作为用户名查找
    if not user:
        user = user_repo.get_user_by_username(db, username=username)
    
    # 验证密码
    if not user or not security.verify_password(password, user.hashed_password):
        return None
        
    # 检查用户是否激活
    if not user.is_active:
        return None
        
    return user

def create_user_token(user_id: int):
    """为用户创建访问令牌"""
    # 设置令牌过期时间
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 创建令牌
    return create_access_token(
        data={"sub": str(user_id)}, 
        expires_delta=access_token_expires
    )

def get_user_by_email(db: Session, email: str):
    """通过邮箱获取用户"""
    return user_repo.get_user_by_email(db, email)

def get_user_by_username(db: Session, username: str):
    """通过用户名获取用户"""
    return user_repo.get_user_by_username(db, username)

def create_user(db: Session, user_in: UserCreate):
    """
    创建新用户。
    我们将参数名从 user_data 修改为 user_in，与 auth.py 中的调用保持一致。
    """
    # 这里的参数名也相应修改
    return user_repo.create_user(db, user=user_in) 

def check_user_exists(db: Session, username: str = None, email: str = None):
    """
    检查用户是否已存在
    返回 (username_exists, email_exists)
    """
    username_exists = False
    email_exists = False
    
    if username:
        existing_user = user_repo.get_user_by_username(db, username)
        username_exists = existing_user is not None
    
    if email:
        existing_user = user_repo.get_user_by_email(db, email)
        email_exists = existing_user is not None
    
    return username_exists, email_exists

def validate_user_data(db: Session, user_data: UserCreate):
    """
    验证用户注册数据
    返回 (is_valid, error_message)
    """
    # 检查用户名和邮箱是否已存在
    username_exists, email_exists = check_user_exists(
        db, 
        username=user_data.username, 
        email=user_data.email
    )
    
    if username_exists:
        return False, "用户名已存在"
    
    if email_exists:
        return False, "邮箱已被注册"
    
    # 其他验证逻辑可以在这里添加
    if len(user_data.password) < 6:
        return False, "密码长度至少6位"
    
    if len(user_data.username) < 3:
        return False, "用户名长度至少3位"
    
    return True, "验证通过"