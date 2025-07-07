from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles  # 新增：用于提供静态文件服务
import time
import os  # 新增

from app.core.config import settings
from app.api import auth, users, resumes, positions, questions, interview  # 🔥 添加 resumes 导入

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="面试系统后端API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="面试系统后端API",
        routes=app.routes,
    )
    
    # 添加OAuth2密码流配置
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": f"{settings.API_V1_STR}/auth/login-form",
                    "scopes": {}
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ===== CORS中间件配置 =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ===== 静态文件服务配置 =====
# 创建上传目录（如果不存在）
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)
os.makedirs(os.path.join(upload_dir, "resumes"), exist_ok=True)

# 提供静态文件访问（用于简历预览等）
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ===== 全局异常处理 =====
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "data": {},
            "message": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "data": {},
            "message": "服务器内部错误"
        }
    )

# ===== 注册路由 =====
# 认证路由
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"]
)

# 用户路由
app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["Users"]
)

app.include_router(
    resumes.router,
    prefix=f"{settings.API_V1_STR}/resumes",
    tags=["Resumes"]
)

app.include_router(
    positions.router,
    prefix=f"{settings.API_V1_STR}",
    tags=["Positions"]
)

app.include_router(
    questions.router,
    prefix=f"{settings.API_V1_STR}/questions",
    tags=["Questions"]
)

app.include_router(
    interview.router, 
    prefix="/api/v1/interviews", 
    tags=["interview"]
)

# ===== 基础路由 =====
@app.get("/")
def root():
    """根路径 - API信息"""
    return {
        "code": 200,
        "data": {
            "message": "Welcome to Interview System API",
            "version": "1.0.0",
            "docs": f"{settings.API_V1_STR}/docs",
            "timestamp": int(time.time())
        },
        "message": "API服务运行正常"
    }

@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    """健康检查接口"""
    return {
        "code": 200,
        "data": {
            "status": "ok",
            "service": "Interview System API",
            "version": "1.0.0",
            "timestamp": int(time.time()),
            "api_prefix": settings.API_V1_STR
        },
        "message": "服务运行正常"
    }

@app.get(f"{settings.API_V1_STR}/info")
def api_info():
    """API信息接口"""
    return {
        "code": 200,
        "data": {
            "name": settings.PROJECT_NAME,
            "version": "1.0.0",
            "endpoints": {
                "auth": {
                    "login": "POST /api/v1/auth/login",
                    "register": "POST /api/v1/auth/register",
                    "refresh": "POST /api/v1/auth/refresh",
                    "login_form": "POST /api/v1/auth/login-form"
                },
                "users": {
                    "profile": "GET /api/v1/users/profile",
                    "update_profile": "PUT /api/v1/users/profile",
                    "me": "GET /api/v1/users/me",
                    "update_me": "PUT /api/v1/users/me",
                    "check_username": "POST /api/v1/users/check-username",
                    "check_email": "POST /api/v1/users/check-email"
                },
                # 🔥 新增：简历相关接口文档
                "resumes": {
                    "upload": "POST /api/v1/resumes",
                    "list": "GET /api/v1/resumes",
                    "delete": "DELETE /api/v1/resumes/{resume_id}",
                    "set_active": "PUT /api/v1/resumes/{resume_id}/activate"
                }
            },
            "documentation": f"{settings.API_V1_STR}/docs",
            "cors_origins": settings.get_cors_origins()
        },
        "message": "API信息获取成功"
    }

# ===== 启动事件 =====
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print(f"🚀 {settings.PROJECT_NAME} 启动成功")
    print(f"📖 API文档: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}{settings.API_V1_STR}/docs")
    print(f"🔗 健康检查: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}{settings.API_V1_STR}/health")
    print(f"📁 上传目录: {os.path.abspath('uploads')}")
    print(f"🌐 CORS允许域名: {settings.get_cors_origins()}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print(f"👋 {settings.PROJECT_NAME} 正在关闭")