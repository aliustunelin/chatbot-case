import os
from typing import List, Optional
from openai import AsyncOpenAI
from src.utils.logger import Logger
from src.model.conversation import Message, MessageRole

logger = Logger.setup()


class OpenAIRepository:
    """OpenAI API ile iletişim kuran repository"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.client: Optional[AsyncOpenAI] = None
    
    async def initialize(self):
        """OpenAI client'ı başlat"""
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set, using empty key")
        self.client = AsyncOpenAI(api_key=self.api_key)
        logger.info(f"OpenAI repository initialized with model: {self.model}")
    
    async def close(self):
        """Client'ı kapat"""
        if self.client:
            await self.client.close()
            logger.info("OpenAI client closed")
    
    async def chat_completion(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        OpenAI chat completion API'sini çağır
        
        Args:
            messages: Konuşma mesajları listesi
            temperature: Yaratıcılık seviyesi (0-1)
            max_tokens: Maksimum token sayısı
            
        Returns:
            Assistant yanıtı
        """
        if not self.client:
            await self.initialize()
        
        try:
            # Message'ları OpenAI formatına çevir
            formatted_messages = [
                {"role": msg.role.value, "content": msg.content}
                for msg in messages
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            logger.debug(f"Chat completion received: {result[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise
    
    async def create_embedding(self, text: str) -> List[float]:
        """
        Metin için embedding vektörü oluştur
        
        Args:
            text: Embedding oluşturulacak metin
            
        Returns:
            Embedding vektörü (float listesi)
        """
        if not self.client:
            await self.initialize()
        
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Created embedding for text: {text[:50]}... (dim: {len(embedding)})")
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding creation error: {e}")
            raise
    
    async def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Birden fazla metin için embedding'ler oluştur
        
        Args:
            texts: Metin listesi
            
        Returns:
            Embedding vektörleri listesi
        """
        if not self.client:
            await self.initialize()
        
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.debug(f"Created {len(embeddings)} embeddings in batch")
            return embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding creation error: {e}")
            raise

