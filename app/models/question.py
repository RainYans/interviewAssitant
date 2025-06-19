class Question(Base):
    """面试题库模型"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    
    # 题目内容
    content = Column(Text, nullable=False, comment="题目内容")
    question_type = Column(String(50), comment="题目类型: 基础知识/场景应用/压力题等")
    difficulty_level = Column(Integer, comment="难度等级 1-5")
    
    # 评估标准
    evaluation_criteria = Column(JSON, comment="评分标准")
    reference_answer = Column(Text, comment="参考答案")
    
    # 标签
    tags = Column(JSON, comment="题目标签")
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)