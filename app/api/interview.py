# app/api/interview.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import json
import random

from app.db.database import get_db
# 👇 --- 修改点 1: 导入新的、更安全的函数 ---
from app.core.security import get_current_active_user
from app.models.user import User # 确保导入User模型以在依赖中使用
from app.models.interview import Interview, InterviewQuestion, InterviewStatistics, InterviewTrendData
from app.models.question import Question
from app.schemas.interview import *

router = APIRouter()

# ===== 面试管理接口 =====

@router.post("/start")
def start_interview(
    interview_data: InterviewCreate,
    # 👇 --- 修改点 2: 使用新的依赖 ---
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    开始面试
    POST /api/v1/interviews/start
    """
    try:
        config = interview_data.config
        
        # 创建面试记录
        interview = Interview(
            user_id=current_user.id,
            type=interview_data.type,
            position=config.position,
            company_type=config.company_type,
            difficulty=config.difficulty,
            planned_duration=config.duration,
            question_types=config.question_types,
            status="ongoing"
        )
        
        db.add(interview)
        db.flush()  # 获取interview.id
        
        # 生成面试题目
        questions = generate_interview_questions(db, config, interview.id)
        interview.total_questions = len(questions)
        
        db.commit()
        db.refresh(interview)
        
        # 返回第一题
        first_question = questions[0] if questions else None
        
        return {
            "code": 200,
            "data": {
                "interview_id": interview.id,
                "first_question": {
                    "id": first_question.id,
                    "text": first_question.question_text,
                    "type": first_question.question_type or "behavioral",
                    "difficulty": first_question.difficulty or "medium",
                    "hint": get_question_hint(first_question.question_text),
                    "order_index": first_question.order_index
                } if first_question else None,
                "total_questions": len(questions)
            },
            "message": "面试开始成功"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"开始面试失败: {str(e)}"
        )

@router.post("/questions/{question_id}/answer")
def submit_answer(
    question_id: int,
    answer_data: AnswerSubmit,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    提交答案
    POST /api/v1/interviews/questions/{question_id}/answer
    """
    try:
        # 查找题目
        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.id == question_id
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题目不存在"
            )
        
        # 验证用户权限
        interview = db.query(Interview).filter(
            Interview.id == question.interview_id,
            Interview.user_id == current_user.id
        ).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此面试"
            )
        
        # 更新答案
        question.answer_text = answer_data.answer_text
        question.answer_duration = answer_data.answer_duration
        question.is_skipped = answer_data.is_skipped
        question.hint_used = answer_data.hint_used
        question.answered_at = datetime.utcnow()
        
        # 生成AI评分和反馈
        if not answer_data.is_skipped and answer_data.answer_text:
            feedback = generate_ai_feedback(question.question_text, answer_data.answer_text)
            question.score = feedback["score"]
            question.ai_feedback = json.dumps(feedback)
            question.keyword_match = feedback.get("keyword_match", 0.8)
            question.fluency_score = feedback.get("fluency_score", 0.85)
        
        # 更新面试进度
        interview.answered_questions += 1
        
        db.commit()
        
        # 返回反馈
        if answer_data.is_skipped:
            feedback_response = {
                "score": 0,
                "pros": "已跳过此题",
                "cons": "建议完整回答以获得更好的评估",
                "reference": get_reference_answer(question.question_text)
            }
        else:
            feedback_response = json.loads(question.ai_feedback) if question.ai_feedback else {
                "score": 3.5,
                "pros": "回答基本完整",
                "cons": "可以更加详细一些",
                "reference": get_reference_answer(question.question_text)
            }
        
        return {
            "code": 200,
            "data": feedback_response,
            "message": "答案提交成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交答案失败: {str(e)}"
        )

@router.get("/questions/{question_id}/next")
def get_next_question(
    question_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取下一题
    GET /api/v1/interviews/questions/{question_id}/next
    """
    try:
        # 找当前题目
        current_question = db.query(InterviewQuestion).filter(
            InterviewQuestion.id == question_id
        ).first()
        
        if not current_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="当前题目不存在"
            )
        
        # 验证权限
        interview = db.query(Interview).filter(
            Interview.id == current_question.interview_id,
            Interview.user_id == current_user.id
        ).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此面试"
            )
        
        # 查找下一题
        next_question = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == current_question.interview_id,
            InterviewQuestion.order_index > current_question.order_index
        ).order_by(InterviewQuestion.order_index).first()
        
        if next_question:
            return {
                "code": 200,
                "data": {
                    "has_next": True,
                    "question": {
                        "id": next_question.id,
                        "text": next_question.question_text,
                        "type": next_question.question_type or "behavioral",
                        "difficulty": next_question.difficulty or "medium",
                        "hint": get_question_hint(next_question.question_text),
                        "order_index": next_question.order_index
                    },
                    "current_progress": next_question.order_index,
                    "total_questions": interview.total_questions
                },
                "message": "获取下一题成功"
            }
        else:
            return {
                "code": 200,
                "data": {
                    "has_next": False,
                    "question": None,
                    "current_progress": interview.total_questions,
                    "total_questions": interview.total_questions
                },
                "message": "已完成所有题目"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取下一题失败: {str(e)}"
        )

@router.post("/{interview_id}/complete")
def complete_interview(
    interview_id: int,
    complete_data: InterviewComplete,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    完成面试
    POST /api/v1/interviews/{interview_id}/complete
    """
    try:
        # 查找面试
        interview = db.query(Interview).filter(
            Interview.id == interview_id,
            Interview.user_id == current_user.id
        ).first()
        
        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试不存在"
            )
        
        # 计算面试结果
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview_id
        ).all()
        
        scores = calculate_interview_scores(questions)
        
        # 更新面试记录
        interview.status = "completed"
        interview.finished_at = datetime.utcnow()
        interview.actual_duration = int((datetime.utcnow() - interview.started_at).total_seconds() / 60)
        interview.overall_score = scores["overall"]
        interview.professional_score = scores["professional"]
        interview.expression_score = scores["expression"]
        interview.logic_score = scores["logic"]
        interview.adaptability_score = scores["adaptability"]
        interview.professionalism_score = scores["professionalism"]
        
        # 更新用户统计
        update_user_statistics(db, current_user.id, interview)
        
        # 更新趋势数据
        update_trend_data(db, current_user.id, scores["overall"])
        
        db.commit()
        
        return {
            "code": 200,
            "data": {
                "interview_id": interview.id,
                "overall_score": scores["overall"],
                "duration_minutes": interview.actual_duration,
                "scores": scores,
                "total_questions": interview.total_questions,
                "answered_questions": interview.answered_questions,
                "performance_summary": generate_performance_summary(scores)
            },
            "message": "面试完成"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"完成面试失败: {str(e)}"
        )

# ===== 面试数据查询接口 =====

@router.get("/performance")
def get_interview_performance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取面试表现数据
    GET /api/v1/interviews/performance
    
    匹配前端 InterviewPerformance.vue 的数据需求
    """
    try:
        # 获取用户统计
        stats = db.query(InterviewStatistics).filter(
            InterviewStatistics.user_id == current_user.id
        ).first()
        
        if not stats:
            # 如果没有统计数据，创建默认数据
            stats = create_default_statistics(db, current_user.id)
        
        # 获取最近面试记录
        recent_interviews = db.query(Interview).filter(
            Interview.user_id == current_user.id,
            Interview.status == "completed"
        ).order_by(desc(Interview.finished_at)).limit(10).all()
        
        # 格式化历史记录
        recent_records = []
        for interview in recent_interviews:
            recent_records.append({
                "id": interview.id,
                "date": interview.finished_at.strftime("%Y-%m-%d") if interview.finished_at else "",
                "type": interview.type,
                "position": interview.position,
                "duration": f"{interview.actual_duration}分钟" if interview.actual_duration else "未知",
                "score": round(interview.overall_score or 0)
            })
        
        # 构造能力评分
        ability_scores = {
            "professional": round(stats.avg_professional_score or 0),
            "expression": round(stats.avg_expression_score or 0),
            "logic": round(stats.avg_logic_score or 0),
            "adaptability": round(stats.avg_adaptability_score or 0),
            "professionalism": round(stats.avg_professionalism_score or 0)
        }
        
        # 综合评分
        overall_score = round(stats.avg_overall_score or 0)
        
        performance_data = {
            "overall_score": overall_score,
            "score_level": get_score_level(overall_score),
            "score_comment": get_score_comment(overall_score),
            "better_than": round(stats.better_than_percent or 0),
            "improvement": round(stats.score_improvement or 0),
            "ability_scores": ability_scores,
            "recent_records": recent_records
        }
        
        return {
            "code": 200,
            "data": performance_data,
            "message": "获取面试表现成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取面试表现失败: {str(e)}"
        )

@router.get("/trend")
def get_trend_data(
    dimension: str = "overall",
    period: str = "month",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取趋势数据
    GET /api/v1/interviews/trend?dimension=overall&period=month
    """
    try:
        # 计算时间范围
        end_date = datetime.utcnow()
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=90)
        
        # 查询趋势数据
        trend_records = db.query(InterviewTrendData).filter(
            InterviewTrendData.user_id == current_user.id,
            InterviewTrendData.record_date >= start_date
        ).order_by(InterviewTrendData.record_date).all()
        
        # 如果没有数据，生成模拟数据
        if not trend_records:
            trend_records = generate_mock_trend_data(current_user.id, start_date, end_date)
        
        # 提取数据
        dates = []
        scores = []
        
        for record in trend_records:
            dates.append(record.record_date.strftime("%m-%d"))
            
            if dimension == "overall":
                scores.append(round(record.cumulative_avg_score or 0))
            elif dimension == "professional":
                scores.append(round(record.professional_score or 0))
            elif dimension == "expression":
                scores.append(round(record.expression_score or 0))
            elif dimension == "logic":
                scores.append(round(record.logic_score or 0))
            else:
                scores.append(round(record.cumulative_avg_score or 0))
        
        return {
            "code": 200,
            "data": {
                "dates": dates,
                "scores": scores,
                "dimension": dimension
            },
            "message": "获取趋势数据成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取趋势数据失败: {str(e)}"
        )

@router.get("/history")
def get_interview_history(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取面试历史
    GET /api/v1/interviews/history?page=1&page_size=10
    """
    try:
        offset = (page - 1) * page_size
        
        # 查询面试历史
        interviews = db.query(Interview).filter(
            Interview.user_id == current_user.id
        ).order_by(desc(Interview.started_at)).offset(offset).limit(page_size).all()
        
        total = db.query(Interview).filter(
            Interview.user_id == current_user.id
        ).count()
        
        # 格式化数据
        history_list = []
        for interview in interviews:
            history_list.append({
                "id": interview.id,
                "type": interview.type,
                "position": interview.position,
                "date": interview.started_at.strftime("%Y-%m-%d %H:%M"),
                "duration": f"{interview.actual_duration or interview.planned_duration}分钟",
                "score": round(interview.overall_score or 0),
                "status": interview.status
            })
        
        return {
            "code": 200,
            "data": {
                "list": history_list,
                "total": total,
                "page": page,
                "page_size": page_size
            },
            "message": "获取面试历史成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取面试历史失败: {str(e)}"
        )

# ===== 辅助函数 =====

def generate_interview_questions(db: Session, config: InterviewConfig, interview_id: int):
    """生成面试题目"""
    questions = []
    
    # 从知识库获取题目
    query = db.query(Question).filter(Question.is_active == True)
    
    # 根据岗位筛选
    if config.position == "frontend":
        query = query.filter(Question.category.in_(["前端开发", "算法数据结构"]))
    elif config.position == "backend":
        query = query.filter(Question.category.in_(["后端开发", "算法数据结构"]))
    
    available_questions = query.all()
    
    # 随机选择题目（简化版）
    selected_questions = random.sample(available_questions, min(5, len(available_questions)))
    
    # 添加通用问题
    common_questions = [
        "请做一下自我介绍",
        "介绍一个你负责的项目",
        "你的职业规划是什么？"
    ]
    
    # 创建面试题目记录
    for i, q in enumerate(selected_questions[:3]):
        interview_question = InterviewQuestion(
            interview_id=interview_id,
            question_id=q.id,
            question_text=q.title,
            question_type=q.category,
            difficulty=q.difficulty,
            order_index=i + 1
        )
        questions.append(interview_question)
    
    # 添加通用问题
    for i, q_text in enumerate(common_questions[:2]):
        interview_question = InterviewQuestion(
            interview_id=interview_id,
            question_text=q_text,
            question_type="behavioral",
            difficulty="medium",
            order_index=len(questions) + i + 1
        )
        questions.append(interview_question)
    
    # 批量保存
    for q in questions:
        db.add(q)
    
    return questions

def generate_ai_feedback(question: str, answer: str):
    """生成AI反馈（模拟）"""
    # 这里是简化版本，实际应该调用AI接口
    base_score = random.uniform(3.0, 4.5)
    
    feedback = {
        "score": round(base_score, 1),
        "pros": "回答结构清晰，表达流畅，重点突出。",
        "cons": "可以增加一些具体的案例来支撑观点，让回答更有说服力。",
        "reference": "参考答案：建议从具体背景开始，然后介绍解决方案和结果。",
        "keyword_match": random.uniform(0.7, 0.9),
        "fluency_score": random.uniform(0.8, 0.95)
    }
    
    return feedback

def calculate_interview_scores(questions):
    """计算面试各项评分"""
    total_score = 0
    count = 0
    
    for q in questions:
        if q.score is not None:
            total_score += q.score
            count += 1
    
    overall = (total_score / count * 20) if count > 0 else 75  # 转换为100分制
    
    # 生成各项评分（基于整体评分的波动）
    scores = {
        "overall": round(overall, 1),
        "professional": round(overall + random.uniform(-5, 5), 1),
        "expression": round(overall + random.uniform(-3, 3), 1),
        "logic": round(overall + random.uniform(-4, 4), 1),
        "adaptability": round(overall + random.uniform(-6, 6), 1),
        "professionalism": round(overall + random.uniform(-2, 2), 1)
    }
    
    # 确保评分在合理范围内
    for key in scores:
        scores[key] = max(0, min(100, scores[key]))
    
    return scores

def update_user_statistics(db: Session, user_id: int, interview: Interview):
    """更新用户统计数据"""
    stats = db.query(InterviewStatistics).filter(
        InterviewStatistics.user_id == user_id
    ).first()
    
    if not stats:
        stats = InterviewStatistics(user_id=user_id)
        db.add(stats)
    
    # 更新统计
    stats.total_interviews += 1
    if interview.type == "practice":
        stats.total_practice += 1
    else:
        stats.total_simulation += 1
    
    stats.total_time_minutes += interview.actual_duration or 0
    
    # 更新平均分数（简化版）
    if interview.overall_score:
        current_avg = stats.avg_overall_score or 0
        total_interviews = stats.total_interviews
        stats.avg_overall_score = (current_avg * (total_interviews - 1) + interview.overall_score) / total_interviews
        
        # 更新其他平均分
        stats.avg_professional_score = interview.professional_score
        stats.avg_expression_score = interview.expression_score
        stats.avg_logic_score = interview.logic_score
        stats.avg_adaptability_score = interview.adaptability_score
        stats.avg_professionalism_score = interview.professionalism_score
    
    # 更新排名（模拟）
    stats.better_than_percent = min(95, 60 + stats.total_interviews * 2)
    stats.score_improvement = random.uniform(8, 15)
    
    stats.last_interview_date = datetime.utcnow()

def update_trend_data(db: Session, user_id: int, score: float):
    """更新趋势数据"""
    today = datetime.utcnow().date()
    
    trend = db.query(InterviewTrendData).filter(
        InterviewTrendData.user_id == user_id,
        func.date(InterviewTrendData.record_date) == today
    ).first()
    
    if not trend:
        trend = InterviewTrendData(
            user_id=user_id,
            record_date=datetime.utcnow(),
            daily_score=score,
            interviews_count=1,
            cumulative_avg_score=score
        )
        db.add(trend)
    else:
        # 更新当日数据
        trend.interviews_count += 1
        trend.daily_score = (trend.daily_score * (trend.interviews_count - 1) + score) / trend.interviews_count
        trend.cumulative_avg_score = score  # 简化处理

# 其他辅助函数...
def get_question_hint(question_text: str) -> str:
    """获取题目提示"""
    hints = {
        "自我介绍": "建议按照'个人信息-教育背景-项目经验-技能特长-职业规划'的结构来组织回答。",
        "项目": "使用STAR法则：Situation（情境）、Task（任务）、Action（行动）、Result（结果）。",
        "Vue": "可以从技术特点、使用场景、性能优化等角度来回答。"
    }
    
    for key, hint in hints.items():
        if key in question_text:
            return hint
    
    return "建议结构化表达，逻辑清晰，结合具体例子。"

def get_reference_answer(question_text: str) -> str:
    """获取参考答案"""
    return "参考答案：建议从背景介绍开始，然后详细说明解决方案和最终结果，展现个人能力和成长。"

def get_score_level(score: int) -> str:
    """获取评分等级"""
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "中等"
    elif score >= 60:
        return "及格"
    else:
        return "待提升"

def get_score_comment(score: int) -> str:
    """获取评分评语"""
    if score >= 90:
        return "您的面试表现非常出色，保持这个状态！"
    elif score >= 80:
        return "表现良好，还有一些细节可以优化"
    elif score >= 70:
        return "基础扎实，需要加强某些方面的训练"
    else:
        return "建议多加练习，重点提升薄弱环节"

def create_default_statistics(db: Session, user_id: int):
    """创建默认统计数据"""
    stats = InterviewStatistics(
        user_id=user_id,
        total_interviews=0,
        avg_overall_score=0,
        better_than_percent=0,
        score_improvement=0
    )
    db.add(stats)
    db.commit()
    return stats

def generate_mock_trend_data(user_id: int, start_date: datetime, end_date: datetime):
    """生成模拟趋势数据"""
    data = []
    current_date = start_date
    base_score = 75
    
    while current_date <= end_date:
        score = base_score + random.uniform(-5, 10)
        base_score = min(95, base_score + 0.2)  # 逐渐提升
        
        data.append(type('MockTrendData', (), {
            'record_date': current_date,
            'cumulative_avg_score': score,
            'professional_score': score + random.uniform(-3, 3),
            'expression_score': score + random.uniform(-2, 2),
            'logic_score': score + random.uniform(-4, 4)
        }))
        
        current_date += timedelta(days=1)
    
    return data

def generate_performance_summary(scores: dict) -> str:
    """生成表现总结"""
    overall = scores["overall"]
    if overall >= 85:
        return "整体表现优秀，各项能力均衡发展，继续保持！"
    elif overall >= 75:
        return "表现良好，在某些方面还有提升空间。"
    else:
        return "基础扎实，建议加强练习提升面试技巧。"