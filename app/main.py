from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi  # 新增导入
import time

from app.core.config import settings
from app.api import auth, users
# from app.api import positions, interviews  # 暂时注释掉，专注于auth和users

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
    allow_origins=settings.get_cors_origins(),  # 使用配置文件中的CORS设置
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

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

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["Users"]
)

# 暂时注释其他路由，专注于auth和users
# app.include_router(
#     positions.router,
#     prefix="/api/v1",
# )
# 
# app.include_router(
#     interviews.router,
#     prefix="/api/v1",
# )

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

# ===== 新增：健康检查接口 =====
@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    """
    健康检查接口
    GET /api/v1/health
    
    匹配前端测试: 用于验证前后端连接
    """
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
    """
    API信息接口
    GET /api/v1/info
    
    返回API的详细信息和可用端点
    """
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
    print(f"🌐 CORS允许域名: {settings.get_cors_origins()}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print(f"👋 {settings.PROJECT_NAME} 正在关闭")

    '''
# ===== 开发模式启动配置 =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",  # 指定应用路径
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,  # 开发模式自动重载
        log_level="info"
    )
    '''