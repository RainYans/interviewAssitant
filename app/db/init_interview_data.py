# scripts/init_interview_data.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.interview import Interview, InterviewQuestion, InterviewStatistics, InterviewTrendData
from app.models.user import User
from app.models.profile import UserProfile
from datetime import datetime, timedelta
import random
import json

def create_mock_interviews(db: Session, user_id: int, count: int = 10):
    """为用户创建模拟面试记录"""
    positions = ["前端开发", "后端开发", "产品经理", "UI设计师", "数据分析"]
    types = ["practice", "simulation"]
    
    interviews = []
    
    for i in range(count):
        # 创建面试记录
        interview_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        interview = Interview(
            user_id=user_id,
            type=random.choice(types),
            position=random.choice(positions),
            difficulty=random.choice(["junior", "medium", "senior"]),
            planned_duration=random.choice([30, 45, 60]),
            question_types=["behavioral", "technical"],
            status="completed",
            actual_duration=random.randint(25, 65),
            total_questions=5,
            answered_questions=random.randint(4, 5),
            overall_score=random.uniform(70, 95),
            professional_score=random.uniform(75, 95),
            expression_score=random.uniform(70, 90),
            logic_score=random.uniform(75, 92),
            adaptability_score=random.uniform(65, 88),
            professionalism_score=random.uniform(80, 95),
            started_at=interview_date,
            finished_at=interview_date + timedelta(minutes=random.randint(25, 65))
        )
        
        db.add(interview)
        db.flush()  # 获取interview.id
        
        # 创建面试题目
        questions_data = [
            {
                "text": "请做一下自我介绍，包括您的教育背景、工作经验和技能特长。",
                "type": "behavioral",
                "answer": "我毕业于XX大学计算机专业，有3年前端开发经验，熟悉Vue、React等框架..."
            },
            {
                "text": f"说说您对{interview.position}的理解，以及您认为一个优秀的工程师应该具备哪些能力？",
                "type": "technical",
                "answer": "我认为前端开发需要掌握扎实的基础知识，包括HTML、CSS、JavaScript..."
            },
            {
                "text": "请介绍一个您最有成就感的项目，包括项目背景、您的角色和贡献。",
                "type": "project",
                "answer": "我参与开发了一个电商平台的前端项目，负责商品详情页的开发..."
            },
            {
                "text": "当您与团队成员意见不一致时，您会如何处理？",
                "type": "situational",
                "answer": "我会首先倾听对方的观点，理解分歧的原因，然后通过数据和事实..."
            },
            {
                "text": "您有什么想问我的吗？",
                "type": "behavioral",
                "answer": "我想了解一下公司的技术栈和团队文化..."
            }
        ]
        
        for j, q_data in enumerate(questions_data):
            question = InterviewQuestion(
                interview_id=interview.id,
                question_text=q_data["text"],
                question_type=q_data["type"],
                difficulty=interview.difficulty,
                order_index=j + 1,
                answer_text=q_data["answer"],
                answer_duration=random.randint(60, 180),  # 1-3分钟
                score=random.uniform(3.0, 4.5),
                ai_feedback=json.dumps({
                    "score": random.uniform(3.0, 4.5),
                    "pros": "回答结构清晰，表达流畅，重点突出。",
                    "cons": "可以增加一些具体的案例来支撑观点。",
                    "reference": "参考答案：建议从具体背景开始...",
                    "keyword_match": random.uniform(0.7, 0.9),
                    "fluency_score": random.uniform(0.8, 0.95)
                }),
                keyword_match=random.uniform(0.7, 0.9),
                fluency_score=random.uniform(0.8, 0.95),
                asked_at=interview_date + timedelta(minutes=j * 8),
                answered_at=interview_date + timedelta(minutes=j * 8 + 3)
            )
            db.add(question)
        
        interviews.append(interview)
    
    return interviews

def create_user_statistics(db: Session, user_id: int, interviews: list):
    """创建用户统计数据"""
    # 计算统计数据
    total_interviews = len(interviews)
    total_practice = len([i for i in interviews if i.type == "practice"])
    total_simulation = len([i for i in interviews if i.type == "simulation"])
    total_time = sum([i.actual_duration for i in interviews if i.actual_duration])
    
    # 计算平均分数
    scores = [i.overall_score for i in interviews if i.overall_score]
    avg_overall = sum(scores) / len(scores) if scores else 0
    
    professional_scores = [i.professional_score for i in interviews if i.professional_score]
    avg_professional = sum(professional_scores) / len(professional_scores) if professional_scores else 0
    
    expression_scores = [i.expression_score for i in interviews if i.expression_score]
    avg_expression = sum(expression_scores) / len(expression_scores) if expression_scores else 0
    
    logic_scores = [i.logic_score for i in interviews if i.logic_score]
    avg_logic = sum(logic_scores) / len(logic_scores) if logic_scores else 0
    
    adaptability_scores = [i.adaptability_score for i in interviews if i.adaptability_score]
    avg_adaptability = sum(adaptability_scores) / len(adaptability_scores) if adaptability_scores else 0
    
    professionalism_scores = [i.professionalism_score for i in interviews if i.professionalism_score]
    avg_professionalism = sum(professionalism_scores) / len(professionalism_scores) if professionalism_scores else 0
    
    # 创建统计记录
    stats = InterviewStatistics(
        user_id=user_id,
        total_interviews=total_interviews,
        total_practice=total_practice,
        total_simulation=total_simulation,
        total_time_minutes=total_time,
        avg_overall_score=avg_overall,
        avg_professional_score=avg_professional,
        avg_expression_score=avg_expression,
        avg_logic_score=avg_logic,
        avg_adaptability_score=avg_adaptability,
        avg_professionalism_score=avg_professionalism,
        score_improvement=random.uniform(8, 15),
        better_than_percent=min(95, 60 + total_interviews * 2),
        last_interview_date=max([i.finished_at for i in interviews if i.finished_at])
    )
    
    db.add(stats)
    return stats

def create_trend_data(db: Session, user_id: int, days: int = 30):
    """创建趋势数据"""
    base_score = 75
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - i)
        
        # 模拟分数逐渐提升的趋势
        daily_score = base_score + random.uniform(-3, 5)
        base_score = min(95, base_score + 0.3)  # 每天微小提升
        
        trend = InterviewTrendData(
            user_id=user_id,
            record_date=date,
            daily_score=daily_score,
            interviews_count=random.choice([0, 0, 0, 1, 1, 2]),  # 大部分天数没有面试
            cumulative_avg_score=daily_score,
            professional_score=daily_score + random.uniform(-3, 3),
            expression_score=daily_score + random.uniform(-2, 2),
            logic_score=daily_score + random.uniform(-4, 4),
            adaptability_score=daily_score + random.uniform(-5, 5),
            professionalism_score=daily_score + random.uniform(-2, 2)
        )
        
        db.add(trend)

def init_mock_data_for_user(db: Session, username: str):
    """为指定用户初始化模拟数据"""
    # 查找用户
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"❌ 用户 {username} 不存在")
        return False
    
    print(f"📊 开始为用户 {username} (ID: {user.id}) 创建模拟数据...")
    
    # 检查是否已有数据
    existing_interviews = db.query(Interview).filter(Interview.user_id == user.id).count()
    if existing_interviews > 0:
        print(f"⚠️  用户已有 {existing_interviews} 条面试记录，是否清除并重新创建？(y/n)")
        choice = input().lower()
        if choice == 'y':
            # 删除现有数据
            db.query(InterviewTrendData).filter(InterviewTrendData.user_id == user.id).delete()
            db.query(InterviewStatistics).filter(InterviewStatistics.user_id == user.id).delete()
            db.query(InterviewQuestion).filter(
                InterviewQuestion.interview_id.in_(
                    db.query(Interview.id).filter(Interview.user_id == user.id)
                )
            ).delete(synchronize_session=False)
            db.query(Interview).filter(Interview.user_id == user.id).delete()
            print("🗑️  已清除现有数据")
        else:
            print("❌ 取消操作")
            return False
    
    try:
        # 1. 创建面试记录
        print("1️⃣  创建面试记录...")
        interviews = create_mock_interviews(db, user.id, 15)  # 创建15次面试
        
        # 2. 创建统计数据
        print("2️⃣  生成统计数据...")
        stats = create_user_statistics(db, user.id, interviews)
        
        # 3. 创建趋势数据
        print("3️⃣  生成趋势数据...")
        create_trend_data(db, user.id, 30)  # 30天的趋势
        
        db.commit()
        
        print("✅ 模拟数据创建完成！")
        print(f"📈 总计创建：")
        print(f"   - 面试记录：{len(interviews)} 条")
        print(f"   - 面试题目：{len(interviews) * 5} 道")
        print(f"   - 趋势数据：30 天")
        print(f"   - 平均评分：{stats.avg_overall_score:.1f}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建模拟数据失败: {e}")
        return False

def main():
    """主函数"""
    db = SessionLocal()
    try:
        print("🎯 面试模拟数据生成器")
        print("=" * 50)
        
        # 列出所有用户
        users = db.query(User).all()
        if not users:
            print("❌ 数据库中没有用户，请先创建用户账号")
            return
        
        print("📋 现有用户列表：")
        for i, user in enumerate(users, 1):
            interview_count = db.query(Interview).filter(Interview.user_id == user.id).count()
            print(f"   {i}. {user.username} (ID: {user.id}) - 已有{interview_count}条面试记录")
        
        print("\n请选择操作：")
        print("1. 为特定用户创建模拟数据")
        print("2. 为所有用户创建模拟数据")
        print("3. 退出")
        
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == "1":
            username = input("请输入用户名: ").strip()
            init_mock_data_for_user(db, username)
            
        elif choice == "2":
            for user in users:
                print(f"\n🔄 处理用户: {user.username}")
                init_mock_data_for_user(db, user.username)
                
        elif choice == "3":
            print("👋 退出程序")
            
        else:
            print("❌ 无效选择")
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()