# app/models/__init__.py

# 这一步是关键，它让SQLAlchemy和Alembic知道这些模型类的存在
from .user import User
from .profile import UserProfile
from .resume import Resume
from .question import Question, QuestionCategory, UserQuestionProgress
from .interview import Interview, InterviewQuestion, InterviewStatistics, InterviewTrendData
from .position import Position