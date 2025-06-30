from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, users
from app.api import positions,interviews

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 在生产环境中应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
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

app.include_router(
    positions.router,
    prefix="/api/v1",
    )

app.include_router(
    interviews.router,
    prefix="/api/v1",
    )



# 首页路由
@app.get("/")
def root():
    return {
        "message": "Welcome to Interview System API",
        "version": "0.1.0",
        "docs": f"{settings.API_V1_STR}/docs"
    }


