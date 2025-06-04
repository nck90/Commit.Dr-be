from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, List, Tuple
import re

class SentimentService:
    def __init__(self):
        # 한국어 감정 분석 모델 로드
        self.model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        
        # 욕설 및 특정 키워드 패턴 정의
        self.profanity_patterns = [
            r'fuck', r'shit', r'pls', r'wtf', r'idk',
            r'ㅅㅂ', r'ㅈㄹ', r'ㅂㅅ', r'ㅄ', r'ㅈㄴ'
        ]
        
    def analyze_sentiment(self, message: str) -> Dict[str, any]:
        """커밋 메시지의 감정을 분석합니다."""
        # 욕설 카운트
        profanity_count = sum(1 for pattern in self.profanity_patterns 
                            if re.search(pattern, message.lower()))
        
        # 감정 분석
        inputs = self.tokenizer(message, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model(**inputs)
        scores = torch.softmax(outputs.logits, dim=1)
        
        # 감정 점수 계산 (1-5점)
        sentiment_score = torch.argmax(scores).item() + 1
        
        # 감정 레이블 결정
        if sentiment_score >= 4:
            sentiment = "positive"
        elif sentiment_score <= 2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        # 키워드 추출
        keywords = self._extract_keywords(message)
        
        return {
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "keywords": keywords,
            "profanity_count": profanity_count
        }
    
    def _extract_keywords(self, message: str) -> List[str]:
        """커밋 메시지에서 주요 키워드를 추출합니다."""
        # 간단한 키워드 추출 로직
        words = message.lower().split()
        keywords = []
        
        # 특정 패턴 매칭
        for pattern in self.profanity_patterns:
            if re.search(pattern, message.lower()):
                keywords.append(pattern)
                
        # 일반적인 개발 관련 키워드
        dev_keywords = ['fix', 'bug', 'feature', 'update', 'refactor', 'test']
        keywords.extend([word for word in words if word in dev_keywords])
        
        return list(set(keywords)) 