# test_add_question.py
import sys
import os
sys.path.append('.')

from app.db.database import SessionLocal
from app.models.question import Question, QuestionCategory
import json

def add_test_data():
    db = SessionLocal()
    try:
        # 添加一个分类
        category = QuestionCategory(
            name="前端开发",
            description="前端技术相关题目",
            icon="Monitor"
        )
        db.add(category)
        
        # 添加一道题目
        question = Question(
            title="Vue3 相比 Vue2 有哪些重要更新？",
            description="考察Vue框架知识",
            category="前端开发",
            difficulty="中等",
            tags=json.dumps(["Vue.js", "前端框架"]),
            answer="Vue3的主要更新包括Composition API、性能提升等...",
            key_points=json.dumps(["性能优化", "Composition API"]),
            related_topics=json.dumps(["响应式原理", "虚拟DOM"]),
            interviewer_perspective="考察对框架发展的了解",
            views=100,
            stars=10
        )
        db.add(question)
        
        db.commit()
        print("✅ 测试数据添加成功")
        
    except Exception as e:
        print(f"❌ 添加失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_data()