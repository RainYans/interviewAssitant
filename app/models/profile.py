# app/models/profile.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class UserProfile(Base):
    """用户资料数据库模型"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # 基本信息
    age = Column(Integer, nullable=True)
    graduation_year = Column(String(4), nullable=True)  # 毕业年份，如 "2024"
    
    # 教育背景
    education = Column(String(50), nullable=True)  # 专科/本科/硕士/博士
    school = Column(String(255), nullable=True)    # 院校名称
    
    # 专业信息
    major_category = Column(String(50), nullable=True)  # 专业类别
    major = Column(String(255), nullable=True)          # 具体专业
    target_position = Column(Text, nullable=True)       # JSON格式存储意向岗位列表
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="profile")