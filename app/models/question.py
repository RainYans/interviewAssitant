# app/models/question.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Question(Base):
    """面试题目数据库模型"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    title = Column(String(500), nullable=False, index=True)  # 题目标题
    description = Column(Text, nullable=True)  # 题目描述
    category = Column(String(100), nullable=False, index=True)  # 分类（前端开发、后端开发等）
    sub_category = Column(String(100), nullable=True)  # 子分类（Vue.js、React等）
    
    # 难度和标签
    difficulty = Column(String(20), nullable=False, default='中等')  # 简单、中等、困难
    tags = Column(Text, nullable=True)  # JSON格式存储标签列表
    
    # 内容
    answer = Column(Text, nullable=False)  # 参考答案（支持HTML格式）
    key_points = Column(Text, nullable=True)  # JSON格式存储答题要点
    related_topics = Column(Text, nullable=True)  # JSON格式存储相关知识点
    interviewer_perspective = Column(Text, nullable=True)  # 面试官视角
    
    # 统计信息
    views = Column(Integer, default=0)  # 浏览次数
    stars = Column(Integer, default=0)  # 收藏次数
    difficulty_votes = Column(Integer, default=0)  # 难度投票数
    
    # 状态
    is_active = Column(Boolean, default=True)  # 是否启用
    is_featured = Column(Boolean, default=False)  # 是否精选
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系（如果有用户表的话）
    # created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    # creator = relationship("User")

class QuestionCategory(Base):
    """题目分类数据库模型"""
    __tablename__ = "question_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # 分类名称
    description = Column(Text, nullable=True)  # 分类描述
    icon = Column(String(50), nullable=True)  # 图标名称
    sort_order = Column(Integer, default=0)  # 排序
    is_active = Column(Boolean, default=True)  # 是否启用
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserQuestionProgress(Base):
    """用户题目学习进度"""
    __tablename__ = "user_question_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # 学习状态
    is_viewed = Column(Boolean, default=False)  # 是否已查看
    is_collected = Column(Boolean, default=False)  # 是否已收藏
    is_mastered = Column(Boolean, default=False)  # 是否已掌握
    
    # 练习记录
    practice_count = Column(Integer, default=0)  # 练习次数
    last_practiced_at = Column(DateTime(timezone=True), nullable=True)  # 最后练习时间
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())