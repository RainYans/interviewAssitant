from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class InterviewMode(str, Enum):
    PRACTICE = "practice"
    SIMULATION = "simulation"

class InterviewStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EVALUATED = "evaluated"

class InterviewCreate(BaseModel):
    position_id: int
    mode: InterviewMode = InterviewMode.PRACTICE

class InterviewAnswer(BaseModel):
    question_id: int
    question_content: str
    answer_text: Optional[str] = None
    answer_duration: Optional[int] = None  # 回答时长(秒)
    confidence_level: Optional[int] = None  # 自信度评分

class InterviewUpdate(BaseModel):
    status: Optional[InterviewStatus] = None
    answers: Optional[List[InterviewAnswer]] = None
    video_path: Optional[str] = None
    audio_path: Optional[str] = None

class Interview(BaseModel):
    id: int
    user_id: int
    position_id: int
    mode: InterviewMode
    status: InterviewStatus
    questions: Optional[List[Dict[str, Any]]] = None
    answers: Optional[List[Dict[str, Any]]] = None
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True