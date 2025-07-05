# app/api/questions.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import json

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.question import Question, QuestionCategory, UserQuestionProgress

# 创建路由器
router = APIRouter()

@router.get("/")
def get_questions(
    category: Optional[str] = Query(None, description="分类筛选"),
    difficulty: Optional[str] = Query(None, description="难度筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    tags: Optional[str] = Query(None, description="标签筛选，逗号分隔"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取题目列表
    GET /api/v1/questions
    """
    try:
        # 构建查询
        query = db.query(Question).filter(Question.is_active == True)
        
        # 分类筛选
        if category:
            query = query.filter(Question.category == category)
        
        # 难度筛选
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        # 搜索 - SQLite兼容的不区分大小写搜索
        if search:
            from sqlalchemy import func
            
            # 转换为小写进行不区分大小写搜索
            search_lower = f'%{search.lower()}%'
            
            # 使用 func.lower() 确保不区分大小写
            search_filter = or_(
                func.lower(Question.title).like(search_lower),
                func.lower(Question.description).like(search_lower),
                func.lower(Question.answer).like(search_lower),
                func.lower(Question.tags).like(search_lower),
                func.lower(Question.category).like(search_lower),
                func.lower(Question.sub_category).like(search_lower),
                func.lower(Question.key_points).like(search_lower),
                func.lower(Question.related_topics).like(search_lower)
            )
            query = query.filter(search_filter)
        
        # 标签筛选
        if tags:
            tag_list = tags.split(',')
            for tag in tag_list:
                query = query.filter(Question.tags.contains(tag.strip()))
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        questions = query.offset(offset).limit(page_size).all()
        
        # 转换数据格式
        question_list = []
        for q in questions:
            question_data = {
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "category": q.category,
                "sub_category": q.sub_category,
                "difficulty": q.difficulty,
                "tags": json.loads(q.tags) if q.tags else [],
                "views": q.views,
                "stars": q.stars,
                "is_featured": q.is_featured,
                "created_at": q.created_at.strftime("%Y-%m-%d %H:%M:%S") if q.created_at else None
            }
            question_list.append(question_data)
        
        return {
            "code": 200,
            "data": {
                "list": question_list,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            },
            "message": "获取题目列表成功"
        }
        
    except Exception as e:
        print(f"❌ 获取题目列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取题目列表失败: {str(e)}"
        )

@router.get("/{question_id}")
def get_question_detail(
    question_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取题目详情
    GET /api/v1/questions/{question_id}
    """
    try:
        # 查找题目
        question = db.query(Question).filter(
            Question.id == question_id,
            Question.is_active == True
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题目不存在"
            )
        
        # 增加浏览次数
        question.views += 1
        
        # 查找用户学习进度
        progress = db.query(UserQuestionProgress).filter(
            UserQuestionProgress.user_id == current_user.id,
            UserQuestionProgress.question_id == question_id
        ).first()
        
        if not progress:
            # 创建新的学习进度记录
            progress = UserQuestionProgress(
                user_id=current_user.id,
                question_id=question_id,
                is_viewed=True
            )
            db.add(progress)
        else:
            # 更新查看状态
            progress.is_viewed = True
        
        db.commit()
        
        # 返回题目详情
        question_detail = {
            "id": question.id,
            "title": question.title,
            "description": question.description,
            "category": question.category,
            "sub_category": question.sub_category,
            "difficulty": question.difficulty,
            "tags": json.loads(question.tags) if question.tags else [],
            "answer": question.answer,
            "keyPoints": json.loads(question.key_points) if question.key_points else [],
            "relatedTopics": json.loads(question.related_topics) if question.related_topics else [],
            "interviewerPerspective": question.interviewer_perspective,
            "views": question.views,
            "stars": question.stars,
            "collected": progress.is_collected if progress else False,
            "mastered": progress.is_mastered if progress else False
        }
        
        return {
            "code": 200,
            "data": question_detail,
            "message": "获取题目详情成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 获取题目详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取题目详情失败: {str(e)}"
        )

@router.post("/{question_id}/collect")
def toggle_collect_question(
    question_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    收藏/取消收藏题目
    POST /api/v1/questions/{question_id}/collect
    """
    try:
        # 检查题目是否存在
        question = db.query(Question).filter(
            Question.id == question_id,
            Question.is_active == True
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题目不存在"
            )
        
        # 查找或创建学习进度
        progress = db.query(UserQuestionProgress).filter(
            UserQuestionProgress.user_id == current_user.id,
            UserQuestionProgress.question_id == question_id
        ).first()
        
        if not progress:
            progress = UserQuestionProgress(
                user_id=current_user.id,
                question_id=question_id,
                is_collected=True
            )
            db.add(progress)
            is_collected = True
            # 增加收藏数
            question.stars += 1
        else:
            # 切换收藏状态
            progress.is_collected = not progress.is_collected
            is_collected = progress.is_collected
            
            if is_collected:
                question.stars += 1
            else:
                question.stars = max(0, question.stars - 1)
        
        db.commit()
        
        return {
            "code": 200,
            "data": {
                "collected": is_collected,
                "stars": question.stars
            },
            "message": "收藏成功" if is_collected else "已取消收藏"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 收藏题目失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"收藏题目失败: {str(e)}"
        )

@router.get("/categories/list")
def get_question_categories(db: Session = Depends(get_db)):
    """
    获取题目分类列表
    GET /api/v1/questions/categories/list
    """
    try:
        categories = db.query(QuestionCategory).filter(
            QuestionCategory.is_active == True
        ).order_by(QuestionCategory.sort_order).all()
        
        category_list = []
        for category in categories:
            # 统计该分类下的题目数量
            question_count = db.query(Question).filter(
                Question.category == category.name,
                Question.is_active == True
            ).count()
            
            category_data = {
                "id": category.name.lower(),
                "name": category.name,
                "description": category.description,
                "icon": category.icon or "Document",
                "count": question_count
            }
            category_list.append(category_data)
        
        return {
            "code": 200,
            "data": category_list,
            "message": "获取分类列表成功"
        }
        
    except Exception as e:
        print(f"❌ 获取分类列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类列表失败: {str(e)}"
        )

@router.get("/stats/user")
def get_user_study_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户学习统计
    GET /api/v1/questions/stats/user
    """
    try:
        # 统计学习数据
        total_progress = db.query(UserQuestionProgress).filter(
            UserQuestionProgress.user_id == current_user.id
        )
        
        studied = total_progress.filter(UserQuestionProgress.is_viewed == True).count()
        mastered = total_progress.filter(UserQuestionProgress.is_mastered == True).count()
        collected = total_progress.filter(UserQuestionProgress.is_collected == True).count()
        
        # 计算总练习次数
        total_practice = db.query(
            db.func.sum(UserQuestionProgress.practice_count)
        ).filter(
            UserQuestionProgress.user_id == current_user.id
        ).scalar() or 0
        
        # 模拟学习时长和正确率（这里可以根据实际业务逻辑调整）
        hours = round(total_practice * 0.5, 1)  # 假设每次练习0.5小时
        accuracy = min(95, 60 + (mastered * 2))  # 根据掌握题目数计算正确率
        
        stats = {
            "studied": studied,
            "mastered": mastered,
            "collected": collected,
            "hours": hours,
            "accuracy": accuracy,
            "total_practice": total_practice
        }
        
        return {
            "code": 200,
            "data": stats,
            "message": "获取学习统计成功"
        }
        
    except Exception as e:
        print(f"❌ 获取学习统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习统计失败: {str(e)}"
        )