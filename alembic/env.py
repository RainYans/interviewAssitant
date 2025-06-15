from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys
from dotenv import load_dotenv

# 更精确的路径添加方式
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 加载环境变量
load_dotenv()

# 先导入配置
from app.core.config import settings

# Alembic 配置对象
config = context.config

# 设置数据库 URL - 提前设置到正确位置
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 配置日志
fileConfig(config.config_file_name)

# 导入数据库和模型
from app.db.database import Base
# 导入所有模型，确保它们注册到 Base.metadata
from app.models.user import User

# 设置目标元数据 - 删除之前设置为 None 的那行
target_metadata = Base.metadata

def run_migrations_offline():
    """离线模式运行迁移"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """在线模式运行迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()