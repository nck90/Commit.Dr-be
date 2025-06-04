from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import get_settings

settings = get_settings()

# 비동기 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# 비동기 세션 생성
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base 클래스 생성
Base = declarative_base()

async def get_session() -> AsyncSession:
    """데이터베이스 세션을 가져옵니다."""
    async with async_session() as session:
        yield session

async def init_db():
    """데이터베이스 테이블을 생성합니다."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """데이터베이스 연결을 종료합니다."""
    await engine.dispose() 