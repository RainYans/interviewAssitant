# app/api/interviews.py - 完整的面试管理API
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

router = APIRouter(prefix="/interviews", tags=["interviews"])

# 面试状态枚举
INTERVIEW_STATUS = {
    "PENDING": "pending",         # 等待开始
    "IN_PROGRESS": "in_progress", # 进行中
    "PAUSED": "paused",          # 暂停（仅练习模式）
    "COMPLETED": "completed",     # 已完成
    "EVALUATED": "evaluated"      # 已评估
}

# 面试模式枚举
INTERVIEW_MODE = {
    "PRACTICE": "practice",       # 练习模式
    "SIMULATION": "simulation"    # 模拟模式
}

# 模拟面试数据存储
MOCK_INTERVIEWS = {}  # 使用字典存储，key为interview_id
INTERVIEW_ID_COUNTER = 1

# 面试题库 - 按岗位分类
QUESTION_BANK = {
    1: {  # AI算法工程师
        "basic": [
            {
                "id": 1,
                "content": "请简单介绍一下机器学习的基本概念和分类",
                "type": "基础知识",
                "time_limit": 180,  # 3分钟
                "difficulty": 1
            },
            {
                "id": 2,
                "content": "解释一下监督学习和无监督学习的区别",
                "type": "基础知识",
                "time_limit": 150,
                "difficulty": 1
            }
        ],
        "technical": [
            {
                "id": 3,
                "content": "如何处理机器学习中的过拟合问题？请举出几种方法",
                "type": "技术深度",
                "time_limit": 300,  # 5分钟
                "difficulty": 3
            },
            {
                "id": 4,
                "content": "请描述一个你实际参与过的机器学习项目，包括数据处理、模型选择和优化过程",
                "type": "项目经验",
                "time_limit": 480,  # 8分钟
                "difficulty": 4
            }
        ],
        "scenario": [
            {
                "id": 5,
                "content": "假设你需要为一个电商推荐系统设计算法，请说明你的思路和技术选型",
                "type": "场景应用",
                "time_limit": 420,  # 7分钟
                "difficulty": 4
            }
        ],
        "stress": [
            {
                "id": 6,
                "content": "如果产品经理要求你在一周内完成一个复杂的深度学习模型，但你评估需要一个月，你会如何处理？",
                "type": "压力应对",
                "time_limit": 240,
                "difficulty": 3
            }
        ]
    },
    2: {  # 大数据开发工程师
        "basic": [
            {
                "id": 7,
                "content": "请介绍Hadoop生态系统的主要组件",
                "type": "基础知识",
                "time_limit": 180,
                "difficulty": 1
            }
        ],
        "technical": [
            {
                "id": 8,
                "content": "Spark和MapReduce的区别是什么？在什么场景下选择Spark？",
                "type": "技术深度",
                "time_limit": 300,
                "difficulty": 3
            }
        ]
    },
    3: {  # 物联网产品经理
        "basic": [
            {
                "id": 9,
                "content": "请介绍物联网的基本架构和关键技术",
                "type": "基础知识",
                "time_limit": 180,
                "difficulty": 1
            }
        ],
        "scenario": [
            {
                "id": 10,
                "content": "如何设计一个智能家居产品的用户体验？请详细说明你的产品规划思路",
                "type": "产品设计",
                "time_limit": 420,
                "difficulty": 4
            }
        ]
    }
}

# 1. 创建面试会话
@router.post("/")
def create_interview(
    position_id: int,
    mode: str = "practice",  # practice 或 simulation
    question_types: List[str] = ["basic", "technical"]  # 题目类型
):
    """创建新的面试会话"""
    global INTERVIEW_ID_COUNTER
    
    # 验证岗位是否存在
    if position_id not in QUESTION_BANK:
        raise HTTPException(status_code=404, detail="岗位不存在或暂无题库")
    
    # 验证面试模式
    if mode not in ["practice", "simulation"]:
        raise HTTPException(status_code=400, detail="面试模式必须是practice或simulation")
    
    # 生成面试题目
    questions = []
    for question_type in question_types:
        if question_type in QUESTION_BANK[position_id]:
            questions.extend(QUESTION_BANK[position_id][question_type])
    
    if not questions:
        raise HTTPException(status_code=400, detail="该岗位暂无相关类型题目")
    
    # 创建面试记录
    interview_id = INTERVIEW_ID_COUNTER
    INTERVIEW_ID_COUNTER += 1
    
    interview = {
        "id": interview_id,
        "position_id": position_id,
        "mode": mode,
        "status": INTERVIEW_STATUS["PENDING"],
        "questions": questions,
        "current_question_index": 0,
        "answers": [],
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
        "total_time": 0,
        "video_path": None,
        "audio_path": None,
        "metadata": {
            "question_types": question_types,
            "total_questions": len(questions)
        }
    }
    
    MOCK_INTERVIEWS[interview_id] = interview
    
    return {
        "status": "success",
        "message": "面试会话创建成功",
        "interview": interview
    }

# 2. 开始面试
@router.post("/{interview_id}/start")
def start_interview(interview_id: int):
    """开始面试"""
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    if interview["status"] != INTERVIEW_STATUS["PENDING"]:
        raise HTTPException(status_code=400, detail="面试已经开始或已结束")
    
    # 更新状态
    interview["status"] = INTERVIEW_STATUS["IN_PROGRESS"]
    interview["started_at"] = datetime.now().isoformat()
    
    # 返回第一个问题
    current_question = interview["questions"][0] if interview["questions"] else None
    
    return {
        "status": "success",
        "message": "面试开始",
        "interview_id": interview_id,
        "current_question": current_question,
        "progress": {
            "current": 1,
            "total": len(interview["questions"])
        }
    }

# 3. 获取当前问题
@router.get("/{interview_id}/current-question")
def get_current_question(interview_id: int):
    """获取当前面试问题"""
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    
    interview = MOCK_INTERVIEWS[interview_id]
    current_index = interview["current_question_index"]
    
    if current_index >= len(interview["questions"]):
        return {
            "status": "completed",
            "message": "所有问题已完成",
            "current_question": None
        }
    
    current_question = interview["questions"][current_index]
    
    return {
        "status": "success",
        "current_question": current_question,
        "progress": {
            "current": current_index + 1,
            "total": len(interview["questions"])
        },
        "interview_mode": interview["mode"]
    }

# 4. 提交答案
@router.post("/{interview_id}/submit-answer")
def submit_answer(
    interview_id: int,
    question_id: int,
    answer_text: Optional[str] = None,
    answer_duration: Optional[int] = None,  # 回答时长(秒)
    confidence_level: Optional[int] = None  # 自信度 1-5
):
    """提交问题答案"""
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    if interview["status"] != INTERVIEW_STATUS["IN_PROGRESS"]:
        raise HTTPException(status_code=400, detail="面试未在进行中")
    
    # 记录答案
    answer = {
        "question_id": question_id,
        "answer_text": answer_text,
        "answer_duration": answer_duration,
        "confidence_level": confidence_level,
        "answered_at": datetime.now().isoformat()
    }
    
    interview["answers"].append(answer)
    
    # 移动到下一题
    interview["current_question_index"] += 1
    
    # 检查是否完成所有题目
    if interview["current_question_index"] >= len(interview["questions"]):
        interview["status"] = INTERVIEW_STATUS["COMPLETED"]
        interview["completed_at"] = datetime.now().isoformat()
        
        return {
            "status": "interview_completed",
            "message": "面试已完成",
            "next_question": None,
            "total_answered": len(interview["answers"])
        }
    
    # 返回下一题
    next_question = interview["questions"][interview["current_question_index"]]
    
    return {
        "status": "success",
        "message": "答案已提交",
        "next_question": next_question,
        "progress": {
            "current": interview["current_question_index"] + 1,
            "total": len(interview["questions"])
        }
    }

# 5. 暂停面试（仅练习模式）
@router.post("/{interview_id}/pause")
def pause_interview(interview_id: int):
    """暂停面试（仅练习模式）"""
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    if interview["mode"] != "practice":
        raise HTTPException(status_code=400, detail="只有练习模式才能暂停")
    
    if interview["status"] != INTERVIEW_STATUS["IN_PROGRESS"]:
        raise HTTPException(status_code=400, detail="面试未在进行中")
    
    interview["status"] = INTERVIEW_STATUS["PAUSED"]
    
    return {
        "status": "success",
        "message": "面试已暂停",
        "can_resume": True
    }

# 6. 恢复面试
@router.post("/{interview_id}/resume")
def resume_interview(interview_id: int):
    """恢复面试"""
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    if interview["status"] != INTERVIEW_STATUS["PAUSED"]:
        raise HTTPException(status_code=400, detail="面试未处于暂停状态")
    
    interview["status"] = INTERVIEW_STATUS["IN_PROGRESS"]
    
    # 返回当前问题
    current_question = interview["questions"][interview["current_question_index"]]
    
    return {
        "status": "success",
        "message": "面试已恢复",
        "current_question": current_question
    }

# 7. 获取AI建议（仅练习模式）
@router.get("/{interview_id}/ai-suggestion")
def get_ai_suggestion(interview_id: int, question_id: int):
    """获取AI答题建议（仅练习模式）"""
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    if interview["mode"] != "practice":
        raise HTTPException(status_code=400, detail="只有练习模式才能获取AI建议")
    
    # 模拟AI建议（后期接入讯飞星火大模型）
    suggestions = {
        1: "建议从机器学习的定义开始，然后分别介绍监督学习、无监督学习和强化学习的特点和应用场景。",
        2: "可以从数据标注的角度来区分，监督学习有标注数据，无监督学习没有标注数据。举例说明会更好。",
        3: "可以从正则化、交叉验证、增加数据量、特征选择等多个角度来回答，建议结合具体算法举例。"
    }
    
    suggestion = suggestions.get(question_id, "建议仔细思考问题的核心要点，结构化地组织答案，可以使用STAR模型来回答。")
    
    return {
        "status": "success",
        "question_id": question_id,
        "ai_suggestion": suggestion,
        "tips": [
            "保持自信的语调",
            "注意眼神交流",
            "回答要有逻辑层次",
            "可以结合具体例子说明"
        ]
    }

# 8. 文件上传
@router.post("/{interview_id}/upload")
async def upload_interview_file(
    interview_id: int,
    file_type: str = Form(...),  # "video" 或 "audio"
    file: UploadFile = File(...)
):
    """上传面试视频或音频文件"""
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    # 验证文件类型
    if file_type not in ["video", "audio"]:
        raise HTTPException(status_code=400, detail="文件类型必须是video或audio")
    
    # 创建上传目录
    upload_dir = Path("uploads") / "interviews" / str(interview_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "mp4"
    filename = f"{file_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
    file_path = upload_dir / filename
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 更新面试记录
    if file_type == "video":
        interview["video_path"] = str(file_path)
    else:
        interview["audio_path"] = str(file_path)
    
    return {
        "status": "success",
        "message": f"{file_type}文件上传成功",
        "file_path": str(file_path),
        "file_size": len(content)
    }

# 9. 获取面试详情
@router.get("/{interview_id}")
def get_interview_detail(interview_id: int):
    """获取面试详情"""
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    # 计算统计信息
    answered_count = len(interview["answers"])
    total_questions = len(interview["questions"])
    completion_rate = (answered_count / total_questions) * 100 if total_questions > 0 else 0
    
    return {
        "status": "success",
        "interview": interview,
        "statistics": {
            "answered_count": answered_count,
            "total_questions": total_questions,
            "completion_rate": round(completion_rate, 1),
            "average_confidence": round(
                sum(a.get("confidence_level", 0) for a in interview["answers"]) / max(answered_count, 1), 1
            ) if answered_count > 0 else 0
        }
    }

# 10. 获取用户面试历史
@router.get("/user/{user_id}/history")
def get_user_interviews(
    user_id: int,
    status: Optional[str] = None,
    limit: int = 10
):
    """获取用户面试历史记录"""
    # 模拟用户面试记录筛选
    user_interviews = []
    for interview in MOCK_INTERVIEWS.values():
        # 这里应该根据interview中的user_id筛选，暂时返回所有
        if status is None or interview["status"] == status:
            user_interviews.append(interview)
    
    # 按创建时间倒序排列
    user_interviews.sort(key=lambda x: x["created_at"], reverse=True)
    user_interviews = user_interviews[:limit]
    
    return {
        "status": "success",
        "total": len(user_interviews),
        "interviews": user_interviews
    }

# 11. 删除面试记录
@router.delete("/{interview_id}")
def delete_interview(interview_id: int):
    """删除面试记录"""
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    
    del MOCK_INTERVIEWS[interview_id]
    
    return {
        "status": "success",
        "message": "面试记录已删除"
    }

# 12. 测试接口
@router.get("/api/test")
def test_interviews():
    """测试面试API"""
    return {
        "status": "success",
        "message": "Interview API is working",
        "available_endpoints": {
            "create": "POST /interviews/",
            "start": "POST /interviews/{id}/start",
            "current_question": "GET /interviews/{id}/current-question", 
            "submit_answer": "POST /interviews/{id}/submit-answer",
            "pause": "POST /interviews/{id}/pause",
            "resume": "POST /interviews/{id}/resume",
            "ai_suggestion": "GET /interviews/{id}/ai-suggestion",
            "upload": "POST /interviews/{id}/upload",
            "detail": "GET /interviews/{id}",
            "history": "GET /interviews/user/{user_id}/history",
            "delete": "DELETE /interviews/{id}"
        },
        "features": {
            "modes": ["practice", "simulation"],
            "question_types": ["basic", "technical", "scenario", "stress"],
            "file_upload": ["video", "audio"],
            "ai_assistance": "practice mode only"
        }
    }