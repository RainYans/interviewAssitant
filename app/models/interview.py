# app/models/interview.py (修复版)
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Interview(Base):
    """面试记录主表"""
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 面试基本信息
    type = Column(String(20), nullable=False)  # 'practice' 或 'simulation'
    position = Column(String(100), nullable=False)  # 面试岗位
    company_type = Column(String(50), nullable=True)  # 公司类型（仅模拟模式）
    difficulty = Column(String(20), nullable=True)  # 难度等级
    
    # 面试配置
    planned_duration = Column(Integer, nullable=False, default=30)  # 计划时长（分钟）
    question_types = Column(JSON, nullable=True)  # 题目类型列表
    
    # 面试状态
    status = Column(String(20), nullable=False, default='ongoing')  # ongoing, completed, cancelled
    
    # 面试结果
    actual_duration = Column(Integer, nullable=True)  # 实际时长（分钟）
    total_questions = Column(Integer, nullable=False, default=0)  # 总题目数
    answered_questions = Column(Integer, nullable=False, default=0)  # 已回答题目数
    
    # 综合评分
    overall_score = Column(Float, nullable=True)  # 综合评分 0-100
    professional_score = Column(Float, nullable=True)  # 专业知识
    expression_score = Column(Float, nullable=True)  # 表达能力
    logic_score = Column(Float, nullable=True)  # 逻辑思维
    adaptability_score = Column(Float, nullable=True)  # 应变能力
    professionalism_score = Column(Float, nullable=True)  # 职业素养
    
    # 时间戳
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan")

class InterviewQuestion(Base):
    """面试题目记录表"""
    __tablename__ = "interview_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    # 🔥 修复：暂时移除对questions表的外键约束，避免依赖问题
    question_id = Column(Integer, nullable=True)  # 关联知识库题目（不设外键）
    
    # 题目信息
    question_text = Column(Text, nullable=False)  # 题目内容
    question_type = Column(String(50), nullable=True)  # 题目类型
    difficulty = Column(String(20), nullable=True)  # 题目难度
    order_index = Column(Integer, nullable=False)  # 题目顺序
    
    # 回答信息
    answer_text = Column(Text, nullable=True)  # 用户回答内容
    answer_duration = Column(Integer, nullable=True)  # 回答时长（秒）
    audio_file_path = Column(String(500), nullable=True)  # 录音文件路径
    video_file_path = Column(String(500), nullable=True)  # 录像文件路径
    
    # 评分信息
    score = Column(Float, nullable=True)  # 单题得分 0-100
    ai_feedback = Column(Text, nullable=True)  # AI反馈（JSON格式）
    keyword_match = Column(Float, nullable=True)  # 关键词匹配度
    fluency_score = Column(Float, nullable=True)  # 流畅度评分
    
    # 状态
    is_skipped = Column(Boolean, default=False)  # 是否跳过
    hint_used = Column(Boolean, default=False)  # 是否使用提示
    
    # 时间戳
    asked_at = Column(DateTime(timezone=True), server_default=func.now())
    answered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    interview = relationship("Interview", back_populates="questions")

class InterviewStatistics(Base):
    """用户面试统计表"""
    __tablename__ = "interview_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # 基础统计
    total_interviews = Column(Integer, default=0)  # 总面试次数
    total_practice = Column(Integer, default=0)  # 练习次数
    total_simulation = Column(Integer, default=0)  # 模拟次数
    total_time_minutes = Column(Integer, default=0)  # 总时长（分钟）
    
    # 平均分数
    avg_overall_score = Column(Float, nullable=True)  # 平均综合评分
    avg_professional_score = Column(Float, nullable=True)  # 平均专业知识
    avg_expression_score = Column(Float, nullable=True)  # 平均表达能力
    avg_logic_score = Column(Float, nullable=True)  # 平均逻辑思维
    avg_adaptability_score = Column(Float, nullable=True)  # 平均应变能力
    avg_professionalism_score = Column(Float, nullable=True)  # 平均职业素养
    
    # 进步数据（与上月对比）
    score_improvement = Column(Float, default=0.0)  # 评分提升百分比
    
    # 排名数据
    better_than_percent = Column(Float, default=0.0)  # 超过多少用户
    
    # 时间戳
    last_interview_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class InterviewTrendData(Base):
    """面试趋势数据表（用于生成趋势图）"""
    __tablename__ = "interview_trend_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 记录日期
    record_date = Column(DateTime(timezone=True), nullable=False)
    
    # 当日数据
    daily_score = Column(Float, nullable=True)  # 当日平均分
    interviews_count = Column(Integer, default=0)  # 当日面试次数
    
    # 累计数据
    cumulative_avg_score = Column(Float, nullable=True)  # 累计平均分
    
    # 分项数据
    professional_score = Column(Float, nullable=True)
    expression_score = Column(Float, nullable=True)
    logic_score = Column(Float, nullable=True)
    adaptability_score = Column(Float, nullable=True)
    professionalism_score = Column(Float, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())