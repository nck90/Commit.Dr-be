from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # DATABASE_URL을 환경 변수에서 직접 읽어옴
    DATABASE_URL_ENV: str | None = os.getenv("DATABASE_URL")

    # PostgreSQL 설정 (DATABASE_URL_ENV가 없을 경우 폴백으로 사용)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "commitcure"
    
    # GitHub API 설정
    GITHUB_API_TOKEN: str = ""
    
    # Gemini API 설정
    GEMINI_API_KEY: str = ""
    
    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_ENV:
            return self.DATABASE_URL_ENV
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"
        # .env 파일이 없어도 오류 발생하지 않도록 설정 (선택 사항)
        # env_file_encoding = 'utf-8' 
        # extra = 'ignore' 

@lru_cache()
def get_settings():
    return Settings() 