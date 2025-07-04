from app.db.database import engine, Base
from app.models import user, profile, resume # 导入所有模型


def create_tables():
    """创建所有数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")

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