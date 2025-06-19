class EvaluationCreate(BaseModel):
    interview_id: int
    professional_knowledge: int  # 0-100
    skill_matching: int
    language_expression: int
    logical_thinking: int
    innovation_ability: int
    stress_resistance: int
    
class AbilityScore(BaseModel):
    """能力评分"""
    professional_knowledge: int
    skill_matching: int  
    language_expression: int
    logical_thinking: int
    innovation_ability: int
    stress_resistance: int
    overall_score: int

class AnalysisResult(BaseModel):
    """分析结果"""
    voice_analysis: Dict[str, Any]  # 语音分析
    expression_analysis: Dict[str, Any]  # 表情分析
    content_analysis: Dict[str, Any]  # 内容分析

class FeedbackSuggestion(BaseModel):
    """反馈建议"""
    strengths: List[str]  # 优势点
    weaknesses: List[str]  # 待改进点
    suggestions: List[str]  # 具体建议
    learning_resources: List[Dict[str, str]]  # 学习资源

class InterviewEvaluation(BaseModel):
    id: int
    interview_id: int
    ability_scores: AbilityScore
    analysis_results: AnalysisResult
    feedback: FeedbackSuggestion
    created_at: datetime
    
    class Config:
        from_attributes = True

class EvaluationReport(BaseModel):
    """完整评估报告"""
    interview: Interview
    evaluation: InterviewEvaluation
    position_info: Position
    
    # 可视化数据
    radar_chart_data: Dict[str, int]  # 雷达图数据
    improvement_priority: List[str]   # 改进优先级