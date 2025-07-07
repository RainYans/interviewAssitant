# scripts/check_tables.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect
from app.db.database import engine

def check_tables():
    """检查数据库中存在哪些表"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("🔍 当前数据库中的表：")
        print("=" * 30)
        
        expected_tables = [
            'users', 'user_profiles', 'resumes',
            'questions', 'question_categories', 'user_question_progress',
            'interviews', 'interview_questions', 'interview_statistics', 'interview_trend_data'
        ]
        
        for table in expected_tables:
            if table in tables:
                print(f"✅ {table}")
            else:
                print(f"❌ {table} (缺失)")
        
        print(f"\n📊 总计：{len(tables)} 个表存在")
        print(f"📊 需要：{len(expected_tables)} 个表")
        
        if 'questions' not in tables:
            print("\n💡 建议：先运行 python scripts/init_questions_data.py")
        
        return 'questions' in tables
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    check_tables()