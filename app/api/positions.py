# app/api/positions.py - 最终修复版本
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

# 创建路由器
router = APIRouter(prefix="/positions", tags=["positions"])

# 临时的测试数据
MOCK_POSITIONS = [
    {
        "id": 1,
        "name": "AI算法工程师",
        "category": "技术岗",
        "industry": "人工智能",
        "description": "负责机器学习算法研发和优化",
        "required_skills": ["Python", "机器学习", "深度学习", "TensorFlow", "PyTorch"],
        "preferred_skills": ["数据挖掘", "计算机视觉", "自然语言处理"],
        "interview_duration": 45,
        "question_count": 12,
        "is_active": True
    },
    {
        "id": 2,
        "name": "大数据开发工程师",
        "category": "技术岗", 
        "industry": "大数据",
        "description": "负责大数据平台开发和数据处理",
        "required_skills": ["Java", "Spark", "Hadoop", "SQL", "Linux"],
        "preferred_skills": ["Kafka", "HBase", "Flink", "Python"],
        "interview_duration": 40,
        "question_count": 10,
        "is_active": True
    },
    {
        "id": 3,
        "name": "物联网产品经理",
        "category": "产品岗",
        "industry": "物联网",
        "description": "负责物联网产品规划和设计", 
        "required_skills": ["产品设计", "需求分析", "项目管理", "用户体验"],
        "preferred_skills": ["硬件知识", "通信协议", "数据分析"],
        "interview_duration": 35,
        "question_count": 8,
        "is_active": True
    }
]

# 使用 /api/ 前缀来避免与 /{id} 冲突

@router.get("/api/test")
def test_positions():
    """测试接口 - 验证API是否正常工作"""
    return {
        "status": "success",
        "message": "positions API is working perfectly",
        "total_positions": len(MOCK_POSITIONS),
        "endpoints": {
            "list": "GET /positions/",
            "detail": "GET /positions/{id}",
            "search": "GET /positions/api/search?keyword=xxx",
            "categories": "GET /positions/api/categories",
            "test": "GET /positions/api/test"
        },
        "test_time": "2025-06-18"
    }

@router.get("/api/search")
def search_positions(keyword: str = Query(..., min_length=1, description="搜索关键词")):
    """搜索岗位 - 在名称、描述、技能中搜索"""
    if not keyword or len(keyword.strip()) == 0:
        raise HTTPException(status_code=400, detail="关键词不能为空")
        
    keyword_lower = keyword.strip().lower()
    results = []
    
    for position in MOCK_POSITIONS:
        # 搜索逻辑
        name_match = keyword_lower in position["name"].lower()
        desc_match = keyword_lower in position["description"].lower() 
        skill_match = any(keyword_lower in skill.lower() for skill in position["required_skills"])
        
        if name_match or desc_match or skill_match:
            results.append(position)
    
    return {
        "status": "success",
        "keyword": keyword,
        "total": len(results),
        "positions": results
    }

@router.get("/api/categories")
def get_categories():
    """获取岗位类别和行业列表"""
    return {
        "status": "success",
        "data": {
            "categories": ["技术岗", "产品岗", "运维岗"],
            "industries": ["人工智能", "大数据", "物联网", "智能系统"]
        }
    }

@router.get("/")
def get_positions(
    industry: Optional[str] = Query(None, description="按行业筛选"),
    category: Optional[str] = Query(None, description="按类别筛选")
):
    """获取岗位列表 - 支持按行业和类别筛选"""
    positions = MOCK_POSITIONS.copy()
    
    # 按行业筛选
    if industry:
        positions = [p for p in positions if p["industry"] == industry]
    
    # 按类别筛选  
    if category:
        positions = [p for p in positions if p["category"] == category]
        
    return {
        "status": "success",
        "filters": {
            "industry": industry,
            "category": category
        },
        "total": len(positions),
        "positions": positions
    }

# 路径参数在最后，并且使用明确的整数验证
@router.get("/{position_id}")
def get_position(position_id: int):
    """获取单个岗位详情"""
    if position_id <= 0:
        raise HTTPException(status_code=400, detail="岗位ID必须是正整数")
        
    position = next((p for p in MOCK_POSITIONS if p["id"] == position_id), None)
    
    if not position:
        raise HTTPException(status_code=404, detail=f"ID为{position_id}的岗位不存在")
        
    return {
        "status": "success",
        "position": position
    }