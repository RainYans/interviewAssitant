# app/models/resume.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Resume(Base):
    """简历数据库模型"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 文件信息
    filename = Column(String(255), nullable=False)  # 原始文件名
    stored_filename = Column(String(255), nullable=False)  # 存储的文件名
    file_path = Column(String(500), nullable=False)  # 文件路径
    file_size = Column(BigInteger, nullable=False)  # 文件大小（字节）
    file_type = Column(String(50), nullable=False)  # 文件类型 (pdf, doc, docx)
    
    # 状态信息
    is_active = Column(Boolean, default=False)  # 是否为默认简历
    is_parsed = Column(Boolean, default=False)  # 是否已解析
    
    # 解析后的信息
    parsed_content = Column(Text, nullable=True)  # 解析后的文本内容
    parsed_data = Column(Text, nullable=True)  # JSON格式的结构化数据
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    #user = relationship("User", back_populates="resumes")
    user = relationship("User")


