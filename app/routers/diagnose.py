from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, Any
from app.services.github_service import GitHubService
from app.services.sentiment_service import SentimentService
from app.services.prescription_service import PrescriptionService
from app.core.database import get_session
from app.models.analysis import AnalysisResult
from datetime import datetime, timedelta

router = APIRouter()
github_service = GitHubService()
sentiment_service = SentimentService()
prescription_service = PrescriptionService()

class DiagnoseRequest(BaseModel):
    github_id: str

@router.post("/diagnose")
async def diagnose(
    request: DiagnoseRequest,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    try:
        # 1. GitHub 커밋 데이터 수집
        commits = await github_service.get_user_commits(request.github_id)
        
        if not commits:
            raise HTTPException(status_code=404, detail="커밋 데이터를 찾을 수 없습니다.")
        
        # 2. 감정 분석
        sentiment_results = []
        total_profanity = 0
        
        for commit in commits:
            sentiment = sentiment_service.analyze_sentiment(commit["message"])
            sentiment_results.append(sentiment)
            total_profanity += sentiment["profanity_count"]
        
        # 3. 시간 패턴 분석
        time_patterns = analyze_time_patterns(commits)
        
        # 4. 진단 유형 결정
        diagnosis_type = determine_diagnosis_type(sentiment_results, time_patterns)
        
        # 5. 처방전 생성
        analysis_data = {
            "diagnosis_type": diagnosis_type,
            "total_commits_90d": len(commits),
            "time_pattern_summary": time_patterns,
            "sentiment_summary": {
                "positive_ratio": sum(1 for s in sentiment_results if s["sentiment"] == "positive") / len(sentiment_results),
                "negative_ratio": sum(1 for s in sentiment_results if s["sentiment"] == "negative") / len(sentiment_results),
                "neutral_ratio": sum(1 for s in sentiment_results if s["sentiment"] == "neutral") / len(sentiment_results)
            },
            "profanity_count": total_profanity
        }
        
        prescription = await prescription_service.generate_prescription(analysis_data)
        
        # 6. 결과 저장
        result = AnalysisResult(
            github_id=request.github_id,
            diagnosis_type=diagnosis_type,
            total_commits_90d=len(commits),
            time_pattern_summary=time_patterns,
            sentiment_summary=analysis_data["sentiment_summary"],
            profanity_count=total_profanity,
            prescription_text=prescription
        )
        
        session.add(result)
        await session.commit()
        await session.refresh(result)
        
        return {
            "status": "success",
            "data": {
                "github_id": result.github_id,
                "created_at": result.created_at,
                "diagnosis_type": result.diagnosis_type,
                "total_commits_90d": result.total_commits_90d,
                "time_pattern_summary": result.time_pattern_summary,
                "sentiment_summary": result.sentiment_summary,
                "profanity_count": result.profanity_count,
                "prescription_text": result.prescription_text
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def analyze_time_patterns(commits: list) -> Dict[str, Any]:
    """커밋 시간 패턴을 분석합니다."""
    timestamps = [datetime.fromisoformat(c["timestamp"].replace("Z", "+00:00")) for c in commits]
    
    # 시간대별 커밋 수 계산
    hour_counts = [0] * 24
    for ts in timestamps:
        hour_counts[ts.hour] += 1
    
    # 야간 커밋 비율 (새벽 2-5시)
    night_commits = sum(hour_counts[2:6])
    night_ratio = night_commits / len(commits) if commits else 0
    
    # 주말 커밋 비율
    weekend_commits = sum(1 for ts in timestamps if ts.weekday() >= 5)
    weekend_ratio = weekend_commits / len(commits) if commits else 0
    
    # 일일 평균 커밋 수
    days = (max(timestamps) - min(timestamps)).days + 1
    avg_daily_commits = len(commits) / days if days > 0 else 0
    
    return {
        "avg_daily_commits": round(avg_daily_commits, 2),
        "max_daily_commits": max(hour_counts),
        "night_commit_ratio": round(night_ratio, 2),
        "weekend_commit_ratio": round(weekend_ratio, 2)
    }

def determine_diagnosis_type(sentiment_results: list, time_patterns: Dict[str, Any]) -> str:
    """커밋 패턴을 분석하여 진단 유형을 결정합니다."""
    if time_patterns["avg_daily_commits"] > 30:
        return "커밋 중독자형"
    elif time_patterns["night_commit_ratio"] > 0.5:
        return "야근 요정형"
    elif sum(1 for s in sentiment_results if s["profanity_count"] > 0) / len(sentiment_results) > 0.3:
        return "분노 디버깅형"
    elif time_patterns["weekend_commit_ratio"] < 0.1:
        return "사라진 코더형"
    else:
        return "멘탈 안정형" 