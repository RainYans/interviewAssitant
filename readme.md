面试系统后端项目结构详解


interview_system_backend/
├── app/
│   ├── init.py
│   ├── main.py
│   ├── api/
│   │   ├── init.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── resumes.py        # 新增简历API
│   │   ├── interviews.py
│   │   ├── positions.py
│   │   ├── knowledge.py      # 新增知识库API
│   │   └── recommendations.py # 新增推荐API
│   ├── core/
│   │   ├── init.py
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── init.py
│   │   ├── database.py
│   │   ├── init_db.py
│   │   └── repositories/     # 新增数据访问层
│   │       ├── init.py
│   │       ├── user_repo.py
│   │       ├── resume_repo.py
│   │       └── ...
│   ├── models/
│   │   ├── init.py
│   │   ├── user.py
│   │   ├── profile.py        # 新增个人资料模型
│   │   ├── resume.py         # 新增简历模型
│   │   ├── interview.py
│   │   ├── position.py
│   │   └── knowledge.py      # 新增知识模型
│   ├── schemas/
│   │   ├── init.py
│   │   ├── user.py
│   │   ├── profile.py        # 新增个人资料模式
│   │   ├── resume.py         # 新增简历模式
│   │   ├── interview.py
│   │   ├── position.py
│   │   └── knowledge.py      # 新增知识模式
│   └── services/
│       ├── init.py
│       ├── auth_service.py
│       ├── user_service.py   # 新增用户服务
│       ├── resume_service.py # 新增简历服务
│       ├── interview_service.py
│       ├── knowledge_service.py # 新增知识服务
│       └── iflytek_service.py
├── alembic/                  # 新增数据库迁移目录
│   ├── versions/
│   └── ...
├── uploads/
├── requirements.txt
├── .env
└── README.md

requirements.txt: 列出项目所有Python依赖包及版本
.env: 环境变量配置文件，存储敏感信息（数据库URL、API密钥等）
README.md: 项目文档，包含安装说明和使用指南

app/（主应用目录）

init.py: 将app目录标记为Python包
main.py: 应用入口点，包含FastAPI实例创建、中间件配置、路由注册和启动事件

app/api/（API路由层）
API路由层定义了所有HTTP端点，负责接收请求和返回响应：

auth.py: 处理用户认证（登录、注册、令牌刷新）
users.py: 用户管理功能（获取/更新用户信息）
resumes.py: 简历管理（上传、查看、更新、删除简历）
interviews.py: 面试相关（创建面试、获取结果、面试反馈）
positions.py: 岗位管理（查询岗位、岗位详情）
knowledge.py: 知识库管理（获取学习资料）
recommendations.py: 个性化推荐功能

app/core/（核心配置）
核心配置层包含应用级别的设置和工具：

config.py: 集中管理应用配置，从环境变量加载设置
security.py: 安全相关功能（JWT生成/验证、密码加密/验证）

app/db/（数据库层）
数据库层管理数据库连接和底层数据访问：

database.py: 数据库连接配置，包含SQLAlchemy设置
init_db.py: 数据库初始化脚本，创建表和加载初始数据
repositories/: 数据访问层，封装数据库操作

user_repo.py: 用户数据访问逻辑
resume_repo.py: 简历数据访问逻辑
其他仓库模块: 各实体的数据访问实现



app/models/（数据模型）
定义数据库表结构的SQLAlchemy ORM模型：

user.py: 用户表模型（账号信息）
profile.py: 个人资料表模型（详细个人信息）
resume.py: 简历表模型（简历内容和元数据）
interview.py: 面试表模型（面试记录、评分）
position.py: 岗位表模型（岗位描述和要求）
knowledge.py: 知识库表模型（学习资料）

app/schemas/（数据验证模式）
使用Pydantic定义的数据验证和序列化模式：

user.py: 用户数据验证模式（创建、更新、响应）
profile.py: 个人资料验证模式
resume.py: 简历数据验证模式
interview.py: 面试数据验证模式
position.py: 岗位数据验证模式
knowledge.py: 知识库数据验证模式

app/services/（业务逻辑层）
封装核心业务逻辑，协调多个组件实现功能：

auth_service.py: 认证业务逻辑（验证用户、生成令牌）
user_service.py: 用户管理业务逻辑
resume_service.py: 简历处理业务逻辑（包括优化功能）
interview_service.py: 面试流程业务逻辑（面试模拟、评分）
knowledge_service.py: 知识管理业务逻辑
iflytek_service.py: 讯飞API集成（语音识别、NLP功能）

alembic/（数据库迁移）
管理数据库结构变更的迁移工具：

versions/: 存储数据库迁移脚本
其他配置文件: Alembic配置

uploads/（文件存储）
用于存储用户上传的文件：

简历文件（PDF、DOCX等）
面试录音/录像
其他用户上传的内容

各层之间的协作流程

请求流程：HTTP请求 → API路由 → 服务层 → 数据仓库 → 数据库
响应流程：数据库 → ORM模型 → Pydantic模式 → API响应







使用3.10 python版本
安装rust
venv310\Scripts\activate 
使用这个环境