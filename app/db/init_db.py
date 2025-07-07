# app/db/init_db.py (更新版本)
from app.db.database import engine, Base
# 确保导入所有模型
from app.models import user, profile, resume, question, interview  # 新增interview

def create_tables():
    """创建所有数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    print("新增的面试相关表：")
    print("- interviews (面试记录)")
    print("- interview_questions (面试题目)")
    print("- interview_statistics (用户统计)")
    print("- interview_trend_data (趋势数据)")

def drop_tables():
    """删除所有数据库表（谨慎使用）"""
    print("正在删除数据库表...")
    Base.metadata.drop_all(bind=engine)
    print("数据库表删除完成！")

def reset_database():
    """重置数据库（删除并重新创建表）"""
    print("正在重置数据库...")
    drop_tables()
    create_tables()
    print("数据库重置完成！")

if __name__ == "__main__":
    # 运行此脚本来初始化数据库
    create_tables()