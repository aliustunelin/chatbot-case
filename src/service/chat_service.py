import uuid
from typing import Optional
from src.utils.logger import Logger
from src.repository.openai_repository import OpenAIRepository
from src.repository.redis_repository import RedisRepository
from src.service.scoring_service import ScoringService
from src.model.conversation import Message, MessageRole, ChatResponse

logger = Logger.setup()

# System prompt for the healthy eating chatbot
SYSTEM_PROMPT = """You are a friendly and knowledgeable nutrition coach engaged in a role-playing conversation about healthy eating habits. Your role is to:

1. Engage the user in a natural, conversational way about their eating habits and nutrition knowledge
2. Ask thoughtful follow-up questions to encourage them to discuss various aspects of healthy eating
3. Be supportive and encouraging, never judgmental
4. Guide the conversation to cover these key topics (without being too obvious):
   - Fruits & Vegetables: Daily intake, variety, and nutritional benefits
   - Hydration: Importance of drinking enough water throughout the day
   - Balanced Meals: Combining proteins, carbs, and fats in proper proportions
   - Processed Foods: Awareness of additives, sugar, salt, and unhealthy fats
   - Meal Timing: Regular eating patterns and avoiding long gaps without food

Start with a warm greeting and ask about their thoughts on healthy eating. Keep responses concise (2-3 sentences) and always end with a question to keep the conversation going.

Remember: You're having a friendly chat, not giving a lecture. Be curious about their personal experiences and views."""


class ChatService:
    """Ana sohbet servisi"""
    
    def __init__(
        self,
        openai_repo: OpenAIRepository,
        redis_repo: RedisRepository,
        scoring_service: ScoringService
    ):
        self.openai_repo = openai_repo
        self.redis_repo = redis_repo
        self.scoring_service = scoring_service
    
    async def initialize(self):
        """Servisi başlat"""
        await self.openai_repo.initialize()
        await self.redis_repo.initialize()
        await self.scoring_service.initialize()
        logger.info("ChatService initialized")
    
    async def close(self):
        """Servisi kapat"""
        await self.openai_repo.close()
        await self.redis_repo.close()
        logger.info("ChatService closed")
    
    def _create_conversation_id(self) -> str:
        """Yeni conversation ID oluştur"""
        return str(uuid.uuid4())
    
    async def start_conversation(self) -> ChatResponse:
        """
        Yeni bir konuşma başlat
        
        Returns:
            İlk assistant mesajı ile ChatResponse
        """
        conversation_id = self._create_conversation_id()
        
        # System prompt'u kaydet
        system_message = Message(role=MessageRole.SYSTEM, content=SYSTEM_PROMPT)
        await self.redis_repo.save_message(conversation_id, system_message)
        
        # İlk mesajı al
        messages = [system_message]
        initial_response = await self.openai_repo.chat_completion(messages)
        
        # Assistant yanıtını kaydet
        assistant_message = Message(role=MessageRole.ASSISTANT, content=initial_response)
        await self.redis_repo.save_message(conversation_id, assistant_message)
        
        logger.info(f"New conversation started: {conversation_id}")
        
        return ChatResponse(
            conversation_id=conversation_id,
            response=initial_response,
            current_score=0.0
        )
    
    async def send_message(
        self, 
        conversation_id: str, 
        user_message: str
    ) -> ChatResponse:
        """
        Kullanıcı mesajı gönder ve yanıt al
        
        Args:
            conversation_id: Konuşma ID'si
            user_message: Kullanıcı mesajı
            
        Returns:
            Assistant yanıtı ile ChatResponse
        """
        # Kullanıcı mesajını kaydet
        user_msg = Message(role=MessageRole.USER, content=user_message)
        await self.redis_repo.save_message(conversation_id, user_msg)
        
        # Tüm geçmişi al
        history = await self.redis_repo.get_history(conversation_id)
        
        # OpenAI'dan yanıt al
        assistant_response = await self.openai_repo.chat_completion(history)
        
        # Assistant yanıtını kaydet
        assistant_msg = Message(role=MessageRole.ASSISTANT, content=assistant_response)
        await self.redis_repo.save_message(conversation_id, assistant_msg)
        
        # Güncel history ile skor hesapla
        updated_history = await self.redis_repo.get_history(conversation_id)
        score_result = await self.scoring_service.calculate_score(conversation_id, updated_history)
        
        logger.info(f"Message processed for {conversation_id}, score: {score_result.total_score}")
        
        return ChatResponse(
            conversation_id=conversation_id,
            response=assistant_response,
            current_score=score_result.total_score
        )
    
    async def get_score(self, conversation_id: str):
        """
        Konuşma skorunu getir
        
        Args:
            conversation_id: Konuşma ID'si
            
        Returns:
            ScoreResult objesi
        """
        history = await self.redis_repo.get_history(conversation_id)
        return await self.scoring_service.calculate_score(conversation_id, history)
    
    async def reset_conversation(self, conversation_id: str) -> None:
        """
        Konuşmayı sıfırla
        
        Args:
            conversation_id: Konuşma ID'si
        """
        await self.redis_repo.clear_history(conversation_id)
        logger.info(f"Conversation reset: {conversation_id}")
    
    async def get_history(self, conversation_id: str):
        """
        Konuşma geçmişini getir
        
        Args:
            conversation_id: Konuşma ID'si
            
        Returns:
            Mesaj listesi
        """
        return await self.redis_repo.get_history(conversation_id)

