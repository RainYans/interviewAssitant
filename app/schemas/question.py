class QuestionBase(BaseModel):
    content: str
    question_type: str
    difficulty_level: int  # 1-5
    evaluation_criteria: Dict[str, Any]
    reference_answer: Optional[str] = None
    tags: List[str] = []

class QuestionCreate(QuestionBase):
    position_id: int

class Question(QuestionBase):
    id: int
    position_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True