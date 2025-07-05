# app/api/positions.py
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

# 创建路由器
router = APIRouter()

# 岗位数据 - 与前端保持一致的完整数据
POSITION_DATA = {
    "it": {
        "title": "互联网IT岗位",
        "description": "涵盖前端、后端、算法等技术岗位的详细信息",
        "salary": "15k-30k",
        "trend": "需求持续增长",
        "jobCount": "10000+",
        "education": "本科及以上",
        "coreSkills": [
            {
                "name": "编程能力",
                "level": "必备",
                "importance": 95,
                "description": "扎实的编程基础，熟练掌握至少一门编程语言"
            },
            {
                "name": "数据结构与算法",
                "level": "重要",
                "importance": 85,
                "description": "理解常用数据结构，能够分析算法复杂度"
            },
            {
                "name": "计算机网络",
                "level": "重要",
                "importance": 80,
                "description": "了解TCP/IP协议栈，HTTP协议等网络基础"
            },
            {
                "name": "数据库",
                "level": "必备",
                "importance": 88,
                "description": "熟悉关系型数据库，了解NoSQL数据库"
            }
        ],
        "softSkills": ["学习能力强", "团队协作", "沟通表达", "逻辑思维", "抗压能力"],
        "experience": "应届生或1-3年经验，根据具体岗位要求",
        "careerPath": [
            {
                "level": 1,
                "title": "初级工程师",
                "years": "0-2年",
                "salary": "10k-18k",
                "keySkills": ["基础开发", "代码规范", "Bug修复"],
                "isCurrent": True
            },
            {
                "level": 2,
                "title": "中级工程师",
                "years": "2-5年",
                "salary": "18k-30k",
                "keySkills": ["独立开发", "技术选型", "性能优化"]
            },
            {
                "level": 3,
                "title": "高级工程师",
                "years": "5-8年",
                "salary": "30k-50k",
                "keySkills": ["架构设计", "技术攻关", "团队指导"]
            },
            {
                "level": 4,
                "title": "技术专家",
                "years": "8年+",
                "salary": "50k+",
                "keySkills": ["技术规划", "跨团队协作", "技术布道"]
            }
        ],
        "dailyWork": [
            "参与产品需求评审，提供技术方案",
            "编写高质量代码，进行代码审查",
            "解决技术难题，优化系统性能",
            "编写技术文档，分享技术经验",
            "与产品、设计、测试等团队协作"
        ],
        "projectExamples": [
            {
                "name": "电商平台开发",
                "description": "负责商品详情页、购物车、订单系统等核心模块开发",
                "technologies": ["Vue.js", "Node.js", "MySQL", "Redis"]
            },
            {
                "name": "后台管理系统",
                "description": "搭建企业级后台管理系统，包括权限管理、数据统计等",
                "technologies": ["React", "TypeScript", "Ant Design", "ECharts"]
            }
        ],
        "techStack": [
            {
                "name": "前端技术",
                "items": ["HTML/CSS", "JavaScript", "Vue.js", "React", "TypeScript"]
            },
            {
                "name": "后端技术",
                "items": ["Node.js", "Java", "Python", "Go", "PHP"]
            },
            {
                "name": "数据库",
                "items": ["MySQL", "PostgreSQL", "MongoDB", "Redis"]
            },
            {
                "name": "工具链",
                "items": ["Git", "Webpack", "Docker", "CI/CD", "Linux"]
            }
        ],
        "preparationTips": {
            "knowledge": [
                "复习计算机基础知识：数据结构、算法、网络、操作系统",
                "深入理解所使用技术栈的原理和最佳实践",
                "了解最新的技术趋势和行业动态"
            ],
            "project": [
                "准备2-3个核心项目的详细介绍",
                "梳理项目中的技术难点和解决方案",
                "量化项目成果，准备具体数据支撑"
            ],
            "questions": [
                "准备常见技术面试题的回答",
                "准备行为面试题（STAR法则）",
                "准备向面试官提问的问题"
            ]
        },
        "resources": [
            {
                "id": 1,
                "icon": "Link",
                "color": "#409eff",
                "title": "LeetCode算法练习",
                "description": "提升算法能力的最佳平台"
            },
            {
                "id": 2,
                "icon": "Document",
                "color": "#67c23a",
                "title": "前端面试宝典",
                "description": "系统整理的前端面试知识点"
            },
            {
                "id": 3,
                "icon": "Collection",
                "color": "#e6a23c",
                "title": "技术博客推荐",
                "description": "优质技术博客和学习资源"
            }
        ]
    },
    "finance": {
        "title": "金融行业岗位",
        "description": "包括投资分析、风险控制、数据分析等金融相关岗位",
        "salary": "20k-40k",
        "trend": "稳定需求",
        "jobCount": "5000+",
        "education": "本科及以上，金融相关专业优先",
        "coreSkills": [
            {
                "name": "金融知识",
                "level": "必备",
                "importance": 90,
                "description": "扎实的金融理论基础，了解金融市场和产品"
            },
            {
                "name": "数据分析",
                "level": "必备",
                "importance": 92,
                "description": "熟练使用Excel、Python等工具进行数据分析"
            },
            {
                "name": "风险意识",
                "level": "重要",
                "importance": 88,
                "description": "具备风险识别和评估能力"
            },
            {
                "name": "财务建模",
                "level": "重要",
                "importance": 85,
                "description": "能够建立财务模型，进行估值分析"
            }
        ],
        "softSkills": ["严谨细致", "抗压能力", "商业敏感", "团队合作", "持续学习"],
        "experience": "1-3年金融行业经验优先，优秀应届生亦可",
        "careerPath": [
            {
                "level": 1,
                "title": "分析师",
                "years": "0-3年",
                "salary": "15k-25k",
                "keySkills": ["数据分析", "报告撰写", "市场研究"],
                "isCurrent": True
            },
            {
                "level": 2,
                "title": "高级分析师",
                "years": "3-5年",
                "salary": "25k-40k",
                "keySkills": ["独立研究", "客户沟通", "项目管理"]
            },
            {
                "level": 3,
                "title": "经理/总监",
                "years": "5-10年",
                "salary": "40k-80k",
                "keySkills": ["团队管理", "战略规划", "业务拓展"]
            },
            {
                "level": 4,
                "title": "合伙人/VP",
                "years": "10年+",
                "salary": "80k+",
                "keySkills": ["决策制定", "资源整合", "行业影响力"]
            }
        ],
        "dailyWork": [
            "市场研究和行业分析",
            "财务数据分析和建模",
            "投资项目评估和尽职调查",
            "撰写研究报告和投资建议",
            "客户沟通和关系维护"
        ],
        "projectExamples": [
            {
                "name": "IPO项目",
                "description": "参与企业上市辅导，进行财务分析和估值",
                "technologies": ["Excel建模", "Wind数据库", "Python分析"]
            },
            {
                "name": "并购重组",
                "description": "负责目标公司尽职调查，评估并购方案",
                "technologies": ["财务分析", "法律合规", "估值模型"]
            }
        ],
        "techStack": [
            {
                "name": "分析工具",
                "items": ["Excel", "Python", "R", "SAS", "MATLAB"]
            },
            {
                "name": "数据库",
                "items": ["Wind", "Bloomberg", "Reuters", "CEIC"]
            },
            {
                "name": "专业软件",
                "items": ["估值模型", "风控系统", "CRM", "ERP"]
            }
        ],
        "preparationTips": {
            "knowledge": [
                "复习金融基础知识：公司金融、投资学、衍生品等",
                "了解最新的金融市场动态和监管政策",
                "准备相关的资格证书：CPA、CFA、FRM等"
            ],
            "project": [
                "准备具体的项目案例和分析框架",
                "整理自己的研究报告或分析作品",
                "准备展示数据分析和建模能力"
            ],
            "questions": [
                "准备估值、财务分析等专业问题",
                "准备市场观点和投资理念阐述",
                "准备职业规划和发展目标"
            ]
        },
        "resources": [
            {
                "id": 1,
                "icon": "Link",
                "color": "#409eff",
                "title": "CFA学习资料",
                "description": "金融分析师必备认证"
            },
            {
                "id": 2,
                "icon": "Document",
                "color": "#67c23a",
                "title": "金融建模指南",
                "description": "Excel和Python金融建模教程"
            }
        ]
    },
    "education": {
        "title": "教育行业岗位",
        "description": "包括教师、教研、教育产品运营等教育相关岗位",
        "salary": "8k-20k",
        "trend": "在线教育蓬勃发展",
        "jobCount": "8000+",
        "education": "本科及以上，师范类或相关专业优先",
        "coreSkills": [
            {
                "name": "学科知识",
                "level": "必备",
                "importance": 95,
                "description": "扎实的学科专业知识，持续更新知识体系"
            },
            {
                "name": "教学能力",
                "level": "必备",
                "importance": 93,
                "description": "能够设计课程，运用多种教学方法"
            },
            {
                "name": "沟通能力",
                "level": "重要",
                "importance": 90,
                "description": "与学生、家长、同事的有效沟通"
            },
            {
                "name": "教育技术",
                "level": "重要",
                "importance": 82,
                "description": "熟悉在线教育工具和平台"
            }
        ],
        "softSkills": ["耐心细致", "责任心强", "创新思维", "亲和力", "持续学习"],
        "experience": "有教学经验优先，优秀应届生可培养",
        "careerPath": [
            {
                "level": 1,
                "title": "初级教师",
                "years": "0-2年",
                "salary": "6k-10k",
                "keySkills": ["基础教学", "班级管理", "作业批改"],
                "isCurrent": True
            },
            {
                "level": 2,
                "title": "骨干教师",
                "years": "3-5年",
                "salary": "10k-15k",
                "keySkills": ["教学创新", "教研活动", "竞赛辅导"]
            },
            {
                "level": 3,
                "title": "学科带头人",
                "years": "5-10年",
                "salary": "15k-25k",
                "keySkills": ["课程设计", "教师培训", "教学研究"]
            },
            {
                "level": 4,
                "title": "教学总监",
                "years": "10年+",
                "salary": "25k+",
                "keySkills": ["教学管理", "课程体系", "团队建设"]
            }
        ],
        "dailyWork": [
            "备课和教案设计",
            "课堂教学和辅导答疑",
            "作业批改和学情分析",
            "家校沟通和家长会",
            "教研活动和培训学习"
        ],
        "projectExamples": [
            {
                "name": "在线课程开发",
                "description": "设计和录制系列在线课程，服务数千名学生",
                "technologies": ["课程设计", "视频录制", "互动教学"]
            },
            {
                "name": "教学创新项目",
                "description": "运用新技术改进教学方法，提升学习效果",
                "technologies": ["智能题库", "AI助教", "数据分析"]
            }
        ],
        "techStack": [
            {
                "name": "教学工具",
                "items": ["PPT", "Keynote", "希沃白板", "钉钉"]
            },
            {
                "name": "在线平台",
                "items": ["腾讯会议", "ClassIn", "Zoom", "学习通"]
            },
            {
                "name": "教学软件",
                "items": ["几何画板", "GeoGebra", "Scratch", "Python"]
            }
        ],
        "preparationTips": {
            "knowledge": [
                "深入复习学科知识，关注教材变化",
                "了解教育理论和教学方法",
                "关注教育政策和行业趋势"
            ],
            "project": [
                "准备试讲内容和教学设计",
                "整理教学成果和学生反馈",
                "准备创新教学案例"
            ],
            "questions": [
                "准备教育理念和教学方法问题",
                "准备班级管理和师生关系处理",
                "准备对教育行业的理解和展望"
            ]
        },
        "resources": [
            {
                "id": 1,
                "icon": "Link",
                "color": "#409eff",
                "title": "教师资格证备考",
                "description": "教师必备职业资格"
            },
            {
                "id": 2,
                "icon": "Collection",
                "color": "#67c23a",
                "title": "优秀教案分享",
                "description": "各学科优秀教学设计"
            }
        ]
    }
}

@router.get("/positions/{position_type}")
def get_position_info(position_type: str):
    """
    获取岗位信息
    GET /api/v1/positions/{position_type}
    
    参数:
        position_type: 岗位类型 (it, finance, education)
    
    返回:
        岗位详细信息，包括技能要求、职业发展路径等
    """
    try:
        # 验证岗位类型
        if position_type not in POSITION_DATA:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"不支持的岗位类型: {position_type}。支持的类型: {', '.join(POSITION_DATA.keys())}"
            )
        
        position_info = POSITION_DATA[position_type]
        
        print(f"✅ 获取岗位信息成功: {position_type}")
        
        return {
            "code": 200,
            "data": position_info,
            "message": "获取岗位信息成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 获取岗位信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取岗位信息失败: {str(e)}"
        )

@router.get("/positions")
def get_all_positions():
    """
    获取所有岗位类型列表
    GET /api/v1/positions
    
    返回:
        所有支持的岗位类型及基本信息
    """
    try:
        position_list = []
        
        for position_type, data in POSITION_DATA.items():
            position_summary = {
                "type": position_type,
                "title": data["title"],
                "description": data["description"],
                "salary": data["salary"],
                "trend": data["trend"],
                "jobCount": data["jobCount"],
                "education": data["education"]
            }
            position_list.append(position_summary)
        
        return {
            "code": 200,
            "data": position_list,
            "message": "获取岗位列表成功"
        }
        
    except Exception as e:
        print(f"❌ 获取岗位列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取岗位列表失败: {str(e)}"
        )