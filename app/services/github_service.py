import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from ..core.config import get_settings

settings = get_settings()

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {settings.GITHUB_API_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def get_user_commits(self, github_id: str) -> List[Dict[str, Any]]:
        """최근 90일간의 사용자 커밋 데이터를 수집합니다."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        commits = []
        page = 1
        
        while True:
            url = f"{self.base_url}/search/commits"
            params = {
                "q": f"author:{github_id} committer-date:>={start_date.strftime('%Y-%m-%d')}",
                "per_page": 100,
                "page": page
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                raise Exception(f"GitHub API 호출 실패: {response.status_code}")
            
            data = response.json()
            items = data.get("items", [])
            
            if not items:
                break
                
            for item in items:
                commit_data = {
                    "github_id": github_id,
                    "commit_hash": item["sha"],
                    "message": item["commit"]["message"],
                    "timestamp": item["commit"]["committer"]["date"],
                    "raw_data": item
                }
                commits.append(commit_data)
            
            if len(items) < 100:
                break
                
            page += 1
            
        return commits 