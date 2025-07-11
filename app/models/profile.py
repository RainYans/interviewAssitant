# app/models/profile.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class UserProfile(Base):
    """用户基本资料数据库模型"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # 与前端 BasicInfo.vue 和 Profile.vue 表单对应的字段
    age = Column(Integer, nullable=True)
    graduation_year = Column(String, nullable=True)
    education = Column(String, nullable=True)
    school = Column(String, nullable=True)
    major = Column(String, nullable=True)
    major_category = Column(String, nullable=True) # Profile.vue 中需要
    
    # 意向岗位是个列表，用JSON类型存储
    target_position = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 与User模型建立反向关系
    user = relationship("User", back_populates="profile")