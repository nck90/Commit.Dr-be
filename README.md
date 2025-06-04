# CommitCure Backend

GitHub 커밋을 분석하여 개발자의 심리 상태와 개발 성향을 진단하고 처방하는 서비스의 백엔드입니다.

## 기술 스택

- FastAPI
- MongoDB
- Huggingface Transformers
- Google Gemini API
- GitHub API

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/your-username/commitcure-backend.git
cd commitcure-backend
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 프로젝트 루트에 생성하고 다음 변수들을 설정합니다:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=commitcure
GITHUB_API_TOKEN=your_github_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## 실행 방법

1. MongoDB 실행
```bash
mongod
```

2. 서버 실행
```bash
uvicorn app.main:app --reload
```

## API 엔드포인트

### 진단 요청
- **URL**: `/api/diagnose`
- **Method**: `POST`
- **Request Body**:
```json
{
    "github_id": "사용자GitHubID"
}
```

## 라이선스

MIT 