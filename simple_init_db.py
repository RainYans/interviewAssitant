#!/usr/bin/env python3
"""
简化的数据库初始化脚本
在项目根目录运行: python simple_init_db.py
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    try:
        print("🔧 初始化数据库...")
        
        # 导入必要模块
        from app.db.database import engine, Base
        
        print("📦 导入模型...")
        # 导入所有模型以确保表被注册
        try:
            from app.models import user
            print("  ✅ 用户模型已导入")
        except ImportError as e:
            print(f"  ⚠️ 用户模型导入失败: {e}")
        
        try:
            from app.models import profile
            print("  ✅ 资料模型已导入")
        except ImportError as e:
            print(f"  ⚠️ 资料模型导入失败: {e}")
        
        # 创建所有表
        print("🗄️ 创建数据库表...")
        Base.metadata.create_all(bind=engine)
        
        # 检查创建的表
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"✅ 数据库初始化成功！创建了 {len(tables)} 个表:")
            for table in tables:
                print(f"  - {table}")
        else:
            print("⚠️ 没有创建任何表，请检查模型定义")
        
        # 创建测试用户
        create_test_user()
        
        print("\n🎉 数据库初始化完成！")
        print("现在可以启动服务器了：")
        print("  python -m uvicorn app.main:app --reload --port 8000")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        print("\n🔍 请检查以下问题:")
        print("  1. 是否安装了所有依赖: pip install pydantic-settings")
        print("  2. 是否在正确的目录运行脚本")
        print("  3. .env 文件是否正确配置")
        return False
    
    return True

def create_test_user():
    """创建测试用户"""
    try:
        print("\n👤 创建测试用户...")
        
        from app.db.database import SessionLocal
        from app.models.user import User
        from app.core.security import get_password_hash
        
        db = SessionLocal()
        
        # 检查测试用户是否已存在
        existing_user = db.query(User).filter(User.username == "test").first()
        if existing_user:
            print("  ✅ 测试用户 'test' 已存在")
            db.close()
            return
        
        # 创建测试用户
        hashed_password = get_password_hash("123456")
        test_user = User(
            username="test",
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        db.close()
        
        print("  ✅ 测试用户创建成功:")
        print("     用户名: test")
        print("     密码: 123456")
        print("     邮箱: test@example.com")
        
    except Exception as e:
        print(f"  ⚠️ 测试用户创建失败: {e}")
        print("     可以在启动后手动注册用户")

if __name__ == "__main__":
    main()