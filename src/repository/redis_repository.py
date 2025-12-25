import os
import json
from typing import List, Optional
from datetime import datetime
import redis.asyncio as redis
from src.utils.logger import Logger
from src.model.conversation import Message, MessageRole, Conversation

logger = Logger.setup()


class RedisRepository:
    """Redis ile conversation history yönetimi"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        self.redis_password = os.getenv("REDIS_PASSWORD")
        self.client: Optional[redis.Redis] = None
        self.conversation_prefix = "conversation:"
        self.score_prefix = "score:"
        self.embedding_prefix = "embedding:"
    
    async def initialize(self):
        """Redis bağlantısını başlat"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                password=self.redis_password if self.redis_password else None,
                decode_responses=True
            )
            # Bağlantıyı test et
            await self.client.ping()
            logger.info(f"Redis connected: {self.redis_url}")
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            raise
    
    async def close(self):
        """Redis bağlantısını kapat"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    def _get_conversation_key(self, conversation_id: str) -> str:
        """Conversation key oluştur"""
        return f"{self.conversation_prefix}{conversation_id}"
    
    def _get_score_key(self, conversation_id: str) -> str:
        """Score key oluştur"""
        return f"{self.score_prefix}{conversation_id}"
    
    def _get_embedding_key(self, text_hash: str) -> str:
        """Embedding cache key oluştur"""
        return f"{self.embedding_prefix}{text_hash}"
    
    async def save_message(self, conversation_id: str, message: Message) -> None:
        """
        Mesajı Redis'e kaydet
        
        Args:
            conversation_id: Konuşma ID'si
            message: Kaydedilecek mesaj
        """
        if not self.client:
            await self.initialize()
        
        try:
            key = self._get_conversation_key(conversation_id)
            message_data = {
                "role": message.role.value,
                "content": message.content,
                "timestamp": message.timestamp.isoformat()
            }
            await self.client.rpush(key, json.dumps(message_data))
            # 24 saat TTL
            await self.client.expire(key, 86400)
            logger.debug(f"Message saved to {key}")
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise
    
    async def get_history(self, conversation_id: str) -> List[Message]:
        """
        Conversation history'yi getir
        
        Args:
            conversation_id: Konuşma ID'si
            
        Returns:
            Mesaj listesi
        """
        if not self.client:
            await self.initialize()
        
        try:
            key = self._get_conversation_key(conversation_id)
            messages_raw = await self.client.lrange(key, 0, -1)
            
            messages = []
            for msg_json in messages_raw:
                msg_data = json.loads(msg_json)
                messages.append(Message(
                    role=MessageRole(msg_data["role"]),
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"])
                ))
            
            logger.debug(f"Retrieved {len(messages)} messages from {key}")
            return messages
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            raise
    
    async def clear_history(self, conversation_id: str) -> None:
        """
        Conversation history'yi sil
        
        Args:
            conversation_id: Konuşma ID'si
        """
        if not self.client:
            await self.initialize()
        
        try:
            conv_key = self._get_conversation_key(conversation_id)
            score_key = self._get_score_key(conversation_id)
            await self.client.delete(conv_key, score_key)
            logger.info(f"Cleared history for conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            raise
    
    async def save_score(self, conversation_id: str, score: float) -> None:
        """
        Skor kaydet
        
        Args:
            conversation_id: Konuşma ID'si
            score: Skor değeri
        """
        if not self.client:
            await self.initialize()
        
        try:
            key = self._get_score_key(conversation_id)
            await self.client.set(key, str(score))
            await self.client.expire(key, 86400)
            logger.debug(f"Score saved: {score} for {conversation_id}")
        except Exception as e:
            logger.error(f"Error saving score: {e}")
            raise
    
    async def get_score(self, conversation_id: str) -> float:
        """
        Skor getir
        
        Args:
            conversation_id: Konuşma ID'si
            
        Returns:
            Skor değeri
        """
        if not self.client:
            await self.initialize()
        
        try:
            key = self._get_score_key(conversation_id)
            score = await self.client.get(key)
            return float(score) if score else 0.0
        except Exception as e:
            logger.error(f"Error getting score: {e}")
            return 0.0
    
    async def cache_embedding(self, text_hash: str, embedding: List[float]) -> None:
        """
        Embedding'i cache'le
        
        Args:
            text_hash: Metin hash'i
            embedding: Embedding vektörü
        """
        if not self.client:
            await self.initialize()
        
        try:
            key = self._get_embedding_key(text_hash)
            await self.client.set(key, json.dumps(embedding))
            # 7 gün TTL
            await self.client.expire(key, 604800)
        except Exception as e:
            logger.error(f"Error caching embedding: {e}")
    
    async def get_cached_embedding(self, text_hash: str) -> Optional[List[float]]:
        """
        Cache'lenmiş embedding'i getir
        
        Args:
            text_hash: Metin hash'i
            
        Returns:
            Embedding vektörü veya None
        """
        if not self.client:
            await self.initialize()
        
        try:
            key = self._get_embedding_key(text_hash)
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting cached embedding: {e}")
            return None

