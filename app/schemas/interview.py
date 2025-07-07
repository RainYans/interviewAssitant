# app/schemas/interview.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# ===== 面试配置和创建 =====
class InterviewConfig(BaseModel):
    """面试配置"""
    position: str
    difficulty: str = "medium"  # junior, medium, senior
    duration: int = 30  # 分钟
    question_types: List[str] = ["behavioral", "technical"]
    company_type: Optional[str] = None  # 仅模拟模式需要

class InterviewCreate(BaseModel):
    """创建面试请求"""
    type: str  # 'practice' 或 'simulation'
    config: InterviewConfig

class InterviewStart(BaseModel):
    """开始面试响应"""
    interview_id: int
    first_question: "QuestionData"
    total_questions: int
    
class QuestionData(BaseModel):
    """题目数据"""
    id: int
    text: str
    type: str
    difficulty: str
    hint: Optional[str] = None
    order_index: int

# ===== 面试进行中 =====
class AnswerSubmit(BaseModel):
    """提交答案"""
    question_id: int
    answer_text: Optional[str] = None
    answer_duration: Optional[int] = None  # 秒
    is_skipped: bool = False
    hint_used: bool = False
    audio_file: Optional[str] = None  # 音频文件路径

class QuestionFeedback(BaseModel):
    """题目反馈"""
    score: float
    pros: str  # 优点
    cons: str  # 建议
    reference: str  # 参考答案
    keyword_match: Optional[float] = None
    fluency_score: Optional[float] = None

class NextQuestionResponse(BaseModel):
    """下一题响应"""
    has_next: bool
    question: Optional[QuestionData] = None
    current_progress: int
    total_questions: int

# ===== 面试结束 =====
class InterviewComplete(BaseModel):
    """完成面试请求"""
    interview_id: int
    reason: str = "completed"  # completed, cancelled, timeout

class InterviewResult(BaseModel):
    """面试结果"""
    interview_id: int
    overall_score: float
    duration_minutes: int
    scores: Dict[str, float]  # 各项评分
    total_questions: int
    answered_questions: int
    performance_summary: str

# ===== 面试历史和统计 =====
class InterviewHistory(BaseModel):
    """面试历史记录"""
    id: int
    type: str
    position: str
    date: str
    duration: str
    score: float
    status: str

class InterviewStatisticsData(BaseModel):
    """面试统计数据"""
    studied: int  # 已学习题目数
    mastered: int  # 已掌握题目数
    collected: int  # 已收藏题目数
    hours: float  # 学习时长
    accuracy: float  # 正确率
    total_practice: int  # 总练习次数

class AbilityScores(BaseModel):
    """能力评分"""
    professional: float  # 专业知识
    expression: float  # 表达能力
    logic: float  # 逻辑思维
    adaptability: float  # 应变能力
    professionalism: float  # 职业素养

class PerformanceData(BaseModel):
    """面试表现数据"""
    overall_score: int
    score_level: str
    score_comment: str
    better_than: int  # 超过百分比
    improvement: float  # 提升百分比
    ability_scores: AbilityScores
    recent_records: List[InterviewHistory]

class TrendPoint(BaseModel):
    """趋势数据点"""
    date: str
    score: float

class TrendData(BaseModel):
    """趋势数据"""
    dates: List[str]
    scores: List[float]
    dimension: str  # overall, professional, expression, logic

# ===== 个性化建议 =====
class PersonalAdvice(BaseModel):
    """个性化建议"""
    type: str  # success, warning, info
    title: str
    content: str
    action: Optional[str] = None
    action_text: Optional[str] = None

class PerformanceAnalysis(BaseModel):
    """面试表现分析完整数据"""
    performance: PerformanceData
    trend_data: TrendData
    advice_list: List[PersonalAdvice]
    radar_data: Dict[str, Any]  # 雷达图数据

# ===== 响应格式 =====
class InterviewResponse(BaseModel):
    """统一响应格式"""
    code: int = 200
    data: Any
    message: str

# 更新QuestionData的前向引用
#InterviewStart.model_rebuild()