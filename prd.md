## 📝 CommitCure 백엔드 PRD (Product Requirements Document) - Gemini 기반

---

훌륭한 아이디어네요! "커밋치료제(CommitCure)" 프로젝트의 백엔드 PRD(Product Requirements Document)를 작성해 드릴게요. 특히 **Gemini**를 활용할 수 있도록 관련 내용을 업데이트했습니다. 명확하고 기능적인 요구사항을 중심으로 구성했습니다.

---

## 1. 개요

**CommitCure**는 개발자의 GitHub 커밋 로그를 분석하여 심리 상태, 감정 상태, 개발 성향을 진단하고, 이에 대한 의사 같은 처방 리포트를 제공하는 서비스입니다. 사용자는 GitHub ID만 입력하여 자신의 커밋 데이터를 기반으로 한 재미있는 진단과 처방을 받을 수 있으며, 이를 SNS에 공유할 수 있습니다.

본 문서는 CommitCure 백엔드 시스템 개발을 위한 핵심 기능, 데이터 흐름, 기술 스택 및 API 명세를 정의합니다.

---

## 2. 목표

* **GitHub 커밋 데이터 수집 및 분석 자동화:** 사용자의 GitHub ID를 기반으로 커밋 데이터를 정확하고 효율적으로 수집합니다.
* **다차원적 커밋 분석 로직 구현:** 커밋 메시지의 감정 분석, 시간 패턴 분석, 커밋 성향 프로파일링을 위한 견고한 분석 로직을 개발합니다.
* **Gemini 기반 맞춤형 처방전 생성:** 분석 결과를 바탕으로 사용자에게 개인화된 처방전을 생성하는 **Gemini 연동 기능**을 구현합니다.
* **확장성 및 안정성 확보:** 향후 기능 확장 및 사용자 증가에 대비하여 유연하고 안정적인 시스템 아키텍처를 구축합니다.
* **프론트엔드 연동 지원:** 프론트엔드에서 필요한 모든 데이터를 효율적으로 제공하는 RESTful API를 제공합니다.

---

## 3. 핵심 기능 (MVP 기준)

### 3.1. 사용자 GitHub 커밋 데이터 수집

* **기능 ID:** BCK-001
* **설명:** 사용자로부터 GitHub ID를 입력받아, 해당 ID의 **최근 90일간의 공개 커밋 데이터**를 GitHub REST API를 통해 수집합니다.
* **세부 사항:**
    * GitHub API Rate Limit을 고려하여 요청을 관리합니다.
    * 필수 수집 항목: 커밋 메시지, 커밋 시간(타임스탬프), 커밋어 정보 (ID).
    * 커밋 수가 매우 많을 경우, 성능을 위해 페이지네이션 및 비동기 처리를 고려합니다.
* **입력:** `github_id` (문자열)
* **출력:** 수집된 커밋 데이터 (내부 저장 및 분석용)

### 3.2. 커밋 메시지 감정 분석

* **기능 ID:** BCK-002
* **설명:** 수집된 각 커밋 메시지에 대해 NLP(자연어 처리) 기반 감정 분석을 수행합니다. 긍정, 부정, 중립 감정 및 특정 감정어(예: 욕설, 분노, 좌절 관련 단어)를 식별합니다.
* **세부 사항:**
    * **Huggingface의 사전 학습된 한국어 감정 분석 모델** (예: KoELECTRA, KoBERT 기반)을 활용합니다.
    * 추가적인 텍스트 패턴(욕설, 특정 부정어/긍정어 리스트)을 정의하여 감정 분석 결과를 보강합니다.
    * **욕설/부정어 카운트:** 특정 단어(예: fuck, pls 등)의 출현 빈도를 기록합니다.
* **입력:** 각 커밋의 `message` (문자열)
* **출력:** 커밋 메시지별 `sentiment` (긍정/부정/중립), `keywords` (식별된 감정어/욕설/특정 단어 리스트), `profanity_count` (욕설 개수)

### 3.3. 커밋 시간 패턴 분석

* **기능 ID:** BCK-003
* **설명:** 수집된 커밋 데이터의 시간 정보를 분석하여 사용자의 개발 리듬 및 습관을 파악합니다.
* **세부 사항:**
    * **커밋 시간대 분포:** 24시간 중 어느 시간대에 커밋이 집중되는지 분석합니다. (예: 새벽 2-5시 커밋 비율)
    * **요일별 커밋 분포:** 주중/주말 커밋 비율 및 특정 요일의 특징을 분석합니다.
    * **커밋 빈도:** 하루 평균 커밋 수, 최대 커밋 수, 일주일 이상 커밋 없음 기간 등을 계산합니다.
    * **폭주 커밋 감지:** 단기간 내 비정상적으로 많은 커밋이 발생한 패턴을 감지합니다.
* **입력:** 각 커밋의 `timestamp`
* **출력:** `daily_avg_commits`, `max_daily_commits`, `night_commit_ratio`, `weekend_commit_ratio`, `longest_inactive_period_days`, `burst_commit_detected` (부울) 등

### 3.4. 커밋 성향 프로파일링 및 진단 유형 분류

* **기능 ID:** BCK-004
* **설명:** 감정 분석, 시간 패턴 분석 결과를 종합하여 사용자의 커밋 성향을 5가지 유형 중 하나로 진단합니다.
* **세부 사항:**
    * 미리 정의된 5가지 진단 유형(커밋 중독자형, 사라진 코더형, 분노 디버깅형, 야근 요정형, 멘탈 안정형)에 대한 로직을 구현합니다. 각 유형의 기준은 MVP 기능 구성 및 진단 유형 예시를 참고합니다.
    * 예: `daily_avg_commits` > 30 이고 `burst_commit_detected` 가 True이면 "커밋 중독자형".
    * 가장 적합한 유형을 하나만 선택하도록 로직을 구성합니다.
* **입력:** BCK-002, BCK-003의 분석 결과 데이터
* **출력:** `diagnosis_type` (유형 이름), `diagnosis_description` (유형 설명)

### 3.5. Gemini 기반 처방전 생성

* **기능 ID:** BCK-005
* **설명:** 진단 결과와 분석 데이터를 바탕으로 사용자에게 맞춤형 처방전 텍스트를 생성합니다. **Google Gemini API**를 활용합니다.
* **세부 사항:**
    * **Gemini API**에 진단 유형, 감정 분석 요약, 시간 패턴 요약 등을 프롬프트로 전달하여 처방전 텍스트를 생성합니다.
    * 처방전은 긍정적이고 유머러스하며, 때로는 실질적인 조언을 포함하도록 **프롬프트를 정교하게 구성**합니다. (예: 시스템 프롬프트, 사용자 프롬프트 예시 등)
    * 생성된 처방전 텍스트를 기반으로 **카드형 이미지 생성 요청**을 위한 데이터를 준비합니다. (텍스트, 진단 유형, 주요 통계 등)
* **입력:** `diagnosis_type`, `sentiment_summary`, `time_pattern_summary`, `profanity_count` 등
* **출력:** `prescription_text` (생성된 처방전 내용)

### 3.6. 공유 카드 이미지 생성 (외부 모듈 또는 API 연동)

* **기능 ID:** BCK-006
* **설명:** 생성된 처방전 텍스트, 진단 유형, 주요 통계 등을 포함한 카드형 이미지를 생성합니다.
* **세부 사항:**
    * `puppeteer` 또는 외부 이미지 생성 서비스(예: Cloudinary)를 활용하여 서버 사이드에서 이미지 렌더링을 구현합니다.
    * 생성된 이미지는 저장소에 저장하고, 접근 가능한 URL을 프론트엔드에 제공합니다.
    * **공유 카드 내용:** CommitCure 로고, 진단 유형 (아이콘 포함), 간략한 처방 문구, 주요 통계 (예: "총 커밋 n개"), 프로젝트 URL 등.
* **입력:** `diagnosis_type`, `prescription_text` (요약), `summary_stats` (총 커밋 수, 특정 지표)
* **출력:** `share_card_image_url`

### 3.7. "이주의 정신승리 커밋" 선정 로직 (재미 요소)

* **기능 ID:** BCK-007
* **설명:** 모든 사용자 커밋 중 특정 키워드(idk how, yolo 등)를 포함하거나, 특이한 패턴을 보이는 커밋 메시지를 "이주의 정신승리 커밋"으로 선정합니다. (MVP에서는 간단한 키워드 매칭)
* **세부 사항:**
    * 내부적으로 수집된 커밋 메시지들을 대상으로 주기적으로 또는 요청 시 분석합니다.
    * 선정 기준은 향후 고도화될 수 있습니다. (예: 감정 점수와 결합)
* **입력:** 모든 사용자 커밋 메시지
* **출력:** `spirit_win_commit_message`, `spirit_win_commit_author`

### 3.8. Hidden Easter Egg 로직

* **기능 ID:** BCK-008
* **설명:** 특정 단어(LGTM, fuck, pls 등)가 감지될 경우, 진단 결과에 포함될 "이스터 에그" 메시지를 반환합니다.
* **세부 사항:**
    * 감정 분석 과정에서 특정 키워드의 출현 빈도를 카운트하고, 이 값이 특정 임계치를 넘을 경우 이스터 에그 트리거로 사용합니다.
    * 이스터 에그 메시지는 재미있고 유머러스하게 구성합니다.
* **입력:** `profanity_count`, `specific_keyword_counts`
* **출력:** `easter_egg_message` (옵션, 해당 시에만 포함)

---

## 4. API 명세 (RESTful API)

### 4.1. 진단 요청

* **엔드포인트:** `/api/diagnose`
* **메서드:** `POST`
* **요청 바디 (JSON):**
    ```json
    {
        "github_id": "사용자GitHubID"
    }
    ```
* **응답 바디 (JSON):**
    ```json
    {
        "status": "success",
        "data": {
            "github_id": "사용자GitHubID",
            "total_commits_90d": 123,
            "sentiment_summary": {
                "positive_ratio": 0.60,
                "negative_ratio": 0.15,
                "neutral_ratio": 0.25,
                "most_frequent_negative_words": ["버그", "실패"],
                "most_frequent_positive_words": ["완료", "개선"]
            },
            "time_pattern_summary": {
                "avg_daily_commits": 5.2,
                "max_daily_commits": 35,
                "night_commit_ratio": 0.20, // 새벽 2-5시 커밋 비율
                "weekend_commit_ratio": 0.30,
                "longest_inactive_period_days": 10,
                "burst_commit_detected": true
            },
            "diagnosis_type": "야근 요정형",
            "diagnosis_description": "새벽 2~5시 커밋 집중",
            "prescription_text": "이번 주는 커밋 쉬는 날을 추가하고 충분한 휴식을 취하세요. 규칙적인 생활 패턴은 개발 생산성 향상에 큰 도움이 됩니다.",
            "share_card_image_url": "https://commitcure.com/images/report/githubid_timestamp.png",
            "profanity_count": 7, // 욕설 카운트
            "easter_egg_message": "어라...? 'fuck' 단어가 너무 많아요! 당신은 '분노 뿜뿜형'이군요!" // 이스터 에그가 트리거될 경우에만 포함
        }
    }
    ```
* **에러 응답:**
    ```json
    {
        "status": "error",
        "message": "GitHub ID를 찾을 수 없습니다."
    }
    ```
    ```json
    {
        "status": "error",
        "message": "GitHub API 호출 중 오류가 발생했습니다."
    }
    ```

### 4.2. 이주의 정신승리 커밋 조회

* **엔드포인트:** `/api/spirit-win-commit`
* **메서드:** `GET`
* **응답 바디 (JSON):**
    ```json
    {
        "status": "success",
        "data": {
            "message": "fix everything idk how",
            "author": "CommitMaster",
            "commit_url": "https://github.com/CommitMaster/repo/commit/hash"
        }
    }
    ```
    * 해당 기능은 홈 화면 등에 전시될 수 있습니다.

---

## 5. 데이터 모델 (추정)

### 5.1. `CommitData` (내부 저장용)

* `id`: (MongoDB ObjectID)
* `github_id`: (String)
* `commit_hash`: (String)
* `message`: (String)
* `timestamp`: (DateTime)
* `sentiment`: (String: 'positive', 'negative', 'neutral')
* `keywords`: (Array of Strings)
* `profanity_count`: (Integer)
* `raw_data`: (JSON: GitHub API에서 받은 원본 데이터 일부)

### 5.2. `AnalysisResult` (사용자별 분석 결과)

* `id`: (MongoDB ObjectID)
* `github_id`: (String, Unique Index)
* `created_at`: (DateTime)
* `total_commits_90d`: (Integer)
* `sentiment_summary`: (Object)
    * `positive_ratio`: (Float)
    * `negative_ratio`: (Float)
    * `neutral_ratio`: (Float)
    * `most_frequent_negative_words`: (Array of Strings)
    * `most_frequent_positive_words`: (Array of Strings)
* `time_pattern_summary`: (Object)
    * `avg_daily_commits`: (Float)
    * `max_daily_commits`: (Integer)
    * `night_commit_ratio`: (Float)
    * `weekend_commit_ratio`: (Float)
    * `longest_inactive_period_days`: (Integer)
    * `burst_commit_detected`: (Boolean)
* `diagnosis_type`: (String)
* `diagnosis_description`: (String)
* `prescription_text`: (String)
* `share_card_image_url`: (String)
* `profanity_count`: (Integer)
* `easter_egg_message`: (String, Optional)

---

## 6. 기술 스택 및 환경

* **백엔드 프레임워크:** FastAPI (Python)
    * 비동기 처리, 빠른 개발 속도, 타입 힌트 지원
* **NLP 분석:**
    * Huggingface Transformers 라이브러리 (Python)
    * KoELECTRA, KoBERT 등 한국어 감정 분석 모델 활용
* **AI 연동:**
    * **Google Gemini API** (Generative AI)
* **GitHub 연동:**
    * `requests` 라이브러리를 이용한 GitHub REST API 호출
* **데이터베이스:** MongoDB (또는 다른 NoSQL)
    * 유연한 스키마, 빠른 쓰기/읽기 성능
* **이미지 생성:** `Puppeteer` (Python 라이브러리 또는 별도 서비스)
* **배포:** Render / Railway (Docker 컨테이너 기반 배포)
* **환경 관리:** `python-dotenv` 또는 Docker 환경 변수

---

## 7. 비고 및 고려사항

* **GitHub API 인증:** 공개 레포지토리 커밋만 수집한다면 토큰 없이도 가능하지만, Rate Limit에 걸릴 수 있으므로 **GitHub Personal Access Token**을 사용한 인증 및 토큰 관리 전략을 고려합니다. (서버에서 사용자 토큰을 받지 않고, 서비스 자체의 토큰을 사용)
* **성능 최적화:** 대량의 커밋 데이터를 처리할 때의 성능 저하를 방지하기 위해 비동기 처리, 캐싱 전략, 배치 처리 등을 고려합니다.
* **데이터 보안:** 사용자 GitHub ID 외에 민감한 개인 정보를 수집하지 않으며, 수집된 커밋 데이터는 익명화하여 사용될 수 있도록 고려합니다.
* **오류 처리:** GitHub API 호출 실패, **Gemini API** 호출 실패, 데이터 분석 실패 등 발생 가능한 모든 오류에 대한 견고한 오류 처리 로직을 구현합니다.
* **지속적인 모델 개선:** 감정 분석 및 **Gemini 처방전**의 품질을 높이기 위해 주기적인 모델 업데이트 및 프롬프트 튜닝을 계획합니다. 특히 Gemini의 경우, 다양한 프롬프트 엔지니어링 기법을 통해 처방전의 퀄리티와 재미를 극대화할 수 있습니다.
* **유머 및 톤 유지:** 서비스의 핵심 콘셉트인 "재미"와 "유머"가 백엔드 로직에서도 일관성 있게 유지될 수 있도록 (특히 **Gemini 처방전**, 이스터 에그 등) 프롬프트 및 로직 설계 시 유의합니다.

---

이 PRD는 CommitCure 백엔드 개발의 기반이 될 것입니다. **특히 Gemini API를 활용한 처방전 생성 부분은 서비스의 핵심적인 재미 요소가 될 테니, 프롬프트 설계에 많은 공을 들여주세요!**