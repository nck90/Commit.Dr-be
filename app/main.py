from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import diagnose
from app.core.database import init_db, close_db

app = FastAPI(
    title="CommitCure API",
    description="GitHub 커밋 분석 및 처방 서비스 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(diagnose.router, prefix="/api", tags=["diagnose"])

@app.on_event("startup")
async def startup_db_client():
    await init_db()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_db()

@app.get("/")
async def root():
    return {"message": "Welcome to CommitCure API"} 