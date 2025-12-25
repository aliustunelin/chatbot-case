import hashlib
from typing import List, Dict, Tuple
import numpy as np
from src.utils.logger import Logger
from src.repository.openai_repository import OpenAIRepository
from src.repository.redis_repository import RedisRepository
from src.model.conversation import CategoryScore, ScoreResult, Message, MessageRole
from src.model.keywords import KEYWORD_CATEGORIES, KeywordCategory

logger = Logger.setup()


class ScoringService:
    """Keyword detection ve puanlama servisi"""
    
    def __init__(
        self, 
        openai_repo: OpenAIRepository,
        redis_repo: RedisRepository
    ):
        self.openai_repo = openai_repo
        self.redis_repo = redis_repo
        self.similarity_threshold = 0.7
        self.keyword_embeddings: Dict[str, List[float]] = {}
    
    async def initialize(self):
        """Keyword embedding'lerini önceden hesapla"""
        logger.info("Initializing keyword embeddings...")
        
        for category_key, category in KEYWORD_CATEGORIES.items():
            for keyword in category.keywords:
                text_hash = self._hash_text(keyword)
                
                # Önce cache'e bak
                cached = await self.redis_repo.get_cached_embedding(text_hash)
                if cached:
                    self.keyword_embeddings[keyword.lower()] = cached
                else:
                    # Cache'de yoksa hesapla
                    embedding = await self.openai_repo.create_embedding(keyword)
                    self.keyword_embeddings[keyword.lower()] = embedding
                    await self.redis_repo.cache_embedding(text_hash, embedding)
        
        logger.info(f"Initialized {len(self.keyword_embeddings)} keyword embeddings")
    
    def _hash_text(self, text: str) -> str:
        """Metin için hash oluştur"""
        return hashlib.md5(text.lower().encode()).hexdigest()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """İki vektör arasındaki cosine similarity hesapla"""
        a = np.array(vec1)
        b = np.array(vec2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    async def _find_matching_keywords(
        self, 
        text: str, 
        category: KeywordCategory
    ) -> Tuple[List[str], float]:
        """
        Metinde kategori keyword'leriyle eşleşenleri bul
        
        Args:
            text: Analiz edilecek metin
            category: Keyword kategorisi
            
        Returns:
            (Eşleşen keyword'ler, skor)
        """
        text_lower = text.lower()
        matched_keywords = []
        
        # Önce basit string matching
        for keyword in category.keywords:
            if keyword.lower() in text_lower:
                if keyword.lower() not in matched_keywords:
                    matched_keywords.append(keyword.lower())
        
        # Sonra semantic matching (embedding similarity)
        if len(matched_keywords) < 3:  # Eğer az eşleşme varsa semantic search yap
            try:
                text_embedding = await self.openai_repo.create_embedding(text)
                
                for keyword in category.keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower in matched_keywords:
                        continue
                    
                    if keyword_lower in self.keyword_embeddings:
                        keyword_embedding = self.keyword_embeddings[keyword_lower]
                        similarity = self._cosine_similarity(text_embedding, keyword_embedding)
                        
                        if similarity >= self.similarity_threshold:
                            matched_keywords.append(keyword_lower)
                            logger.debug(f"Semantic match: '{keyword}' (similarity: {similarity:.3f})")
            except Exception as e:
                logger.warning(f"Semantic matching failed: {e}")
        
        # Skor hesapla: Her eşleşen keyword için puan
        # Maksimum 20 puan, en az 3 keyword gerekli tam puan için
        unique_matches = list(set(matched_keywords))
        if len(unique_matches) >= 3:
            score = category.max_score
        elif len(unique_matches) == 2:
            score = category.max_score * 0.7
        elif len(unique_matches) == 1:
            score = category.max_score * 0.4
        else:
            score = 0.0
        
        return unique_matches, score
    
    async def calculate_score(
        self, 
        conversation_id: str,
        messages: List[Message]
    ) -> ScoreResult:
        """
        Konuşmadaki kullanıcı mesajlarını analiz et ve skor hesapla
        
        Args:
            conversation_id: Konuşma ID'si
            messages: Konuşma mesajları
            
        Returns:
            ScoreResult objesi
        """
        # Sadece kullanıcı mesajlarını al
        user_messages = [msg for msg in messages if msg.role == MessageRole.USER]
        combined_text = " ".join([msg.content for msg in user_messages])
        
        category_scores = []
        total_score = 0.0
        
        for category_key, category in KEYWORD_CATEGORIES.items():
            matched, score = await self._find_matching_keywords(combined_text, category)
            
            category_scores.append(CategoryScore(
                category=category.name,
                score=score,
                max_score=category.max_score,
                matched_keywords=matched
            ))
            total_score += score
        
        # Sonucu oluştur
        result = ScoreResult(
            conversation_id=conversation_id,
            total_score=total_score,
            max_possible_score=100.0,
            category_scores=category_scores,
            evaluation_summary=self._generate_summary(category_scores, total_score)
        )
        
        # Skoru Redis'e kaydet
        await self.redis_repo.save_score(conversation_id, total_score)
        
        logger.info(f"Score calculated for {conversation_id}: {total_score}/100")
        return result
    
    def _generate_summary(self, category_scores: List[CategoryScore], total_score: float) -> str:
        """Değerlendirme özeti oluştur"""
        if total_score >= 80:
            level = "Excellent"
            message = "You have demonstrated comprehensive knowledge about healthy eating!"
        elif total_score >= 60:
            level = "Good"
            message = "You have a solid understanding of healthy eating principles."
        elif total_score >= 40:
            level = "Fair"
            message = "You show some awareness of healthy eating, but there's room for improvement."
        elif total_score >= 20:
            level = "Basic"
            message = "You have touched on a few aspects of healthy eating."
        else:
            level = "Needs Improvement"
            message = "Consider exploring more topics related to healthy eating."
        
        # Eksik kategorileri bul
        weak_categories = [cs.category for cs in category_scores if cs.score < cs.max_score * 0.5]
        
        summary = f"Level: {level} ({total_score:.1f}/100)\n{message}"
        if weak_categories:
            summary += f"\nAreas to explore: {', '.join(weak_categories)}"
        
        return summary

