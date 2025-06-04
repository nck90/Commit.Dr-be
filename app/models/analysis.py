from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 분석 결과
    diagnosis_type = Column(String)
    total_commits_90d = Column(Integer)
    
    # 시간 패턴 요약
    time_pattern_summary = Column(JSON)
    
    # 감정 분석 요약
    sentiment_summary = Column(JSON)
    
    # 욕설 카운트
    profanity_count = Column(Integer)
    
    # 처방전
    prescription_text = Column(String) 