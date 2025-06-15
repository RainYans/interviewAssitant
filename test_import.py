import sys
import os
print(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    from app.db.database import Base
    print("成功导入 Base!")
    
    from app.models.user import User
    print("成功导入 User!")
    
    from app.core.config import settings
    print("成功导入 settings!")
    print(f"数据库URL: {settings.DATABASE_URL}")
except ImportError as e:
    print(f"导入失败: {e}")