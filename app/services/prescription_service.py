import google.generativeai as genai
from typing import Dict, Any
from ..core.config import get_settings

settings = get_settings()

class PrescriptionService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    async def generate_prescription(self, analysis_data: Dict[str, Any]) -> str:
        """분석 데이터를 바탕으로 처방전을 생성합니다."""
        prompt = self._create_prompt(analysis_data)
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _create_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """Gemini API에 전달할 프롬프트를 생성합니다."""
        return f"""
당신은 개발자의 GitHub 커밋을 분석하여 재미있고 유머러스한 처방전을 작성하는 의사입니다.
다음 분석 데이터를 바탕으로 재미있고 유머러스한 처방전을 작성해주세요:

진단 유형: {analysis_data['diagnosis_type']}
커밋 통계:
- 총 커밋 수: {analysis_data['total_commits_90d']}
- 평균 일일 커밋: {analysis_data['time_pattern_summary']['avg_daily_commits']}
- 야간 커밋 비율: {analysis_data['time_pattern_summary']['night_commit_ratio']}
- 주말 커밋 비율: {analysis_data['time_pattern_summary']['weekend_commit_ratio']}

감정 분석:
- 긍정적 커밋 비율: {analysis_data['sentiment_summary']['positive_ratio']}
- 부정적 커밋 비율: {analysis_data['sentiment_summary']['negative_ratio']}
- 욕설 사용 횟수: {analysis_data['profanity_count']}

처방전은 다음 형식을 따라주세요:
1. 환자 상태 요약 (재미있게)
2. 진단 내용 (유머러스하게)
3. 처방 내용 (실질적인 조언 포함)
4. 마무리 멘트 (격려하는 내용)

전체적으로 재미있고 유머러스한 톤을 유지하면서도, 실질적인 조언을 포함해주세요.
""" 