from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class Position(Base):
    """岗位模型"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="岗位名称")
    category = Column(String(50), nullable=False, comment="岗位类别: 技术岗/产品岗/运维岗")
    industry = Column(String(50), nullable=False, comment="技术领域: AI/大数据/物联网/智能系统")
    description = Column(Text, comment="岗位描述")
    required_skills = Column(JSON, comment="必需技能列表")
    preferred_skills = Column(JSON, comment="优选技能列表")
    
    # 面试配置
    interview_duration = Column(Integer, default=30, comment="面试时长(分钟)")
    question_count = Column(Integer, default=10, comment="题目数量")
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
