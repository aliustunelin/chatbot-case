from fastapi import APIRouter, HTTPException
from src.utils.logger import Logger
from src.repository.openai_repository import OpenAIRepository
from src.repository.redis_repository import RedisRepository
from src.service.scoring_service import ScoringService
from src.service.chat_service import ChatService
from src.model.conversation import ChatRequest, ChatResponse, ScoreResult

logger = Logger.setup()
router = APIRouter(prefix="/chat", tags=["chat"])

# Global service instance (will be initialized by app.py)
_chat_service: ChatService = None


async def get_chat_service() -> ChatService:
    """ChatService singleton'ı döndür"""
    global _chat_service
    if _chat_service is None:
        openai_repo = OpenAIRepository()
        redis_repo = RedisRepository()
        scoring_service = ScoringService(openai_repo, redis_repo)
        _chat_service = ChatService(openai_repo, redis_repo, scoring_service)
        await _chat_service.initialize()
    return _chat_service


async def initialize_chat_service():
    """ChatService'i başlat (app startup'ta çağrılır)"""
    await get_chat_service()
    logger.info("Chat service initialized via router")


async def shutdown_chat_service():
    """ChatService'i kapat (app shutdown'da çağrılır)"""
    global _chat_service
    if _chat_service:
        await _chat_service.close()
        _chat_service = None
    logger.info("Chat service shutdown via router")


@router.post("/start", response_model=ChatResponse)
async def start_conversation():
    """
    Yeni bir sohbet başlat
    
    Returns:
        conversation_id ve ilk assistant mesajı
    """
    try:
        service = await get_chat_service()
        response = await service.start_conversation()
        return response
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Mesaj gönder ve yanıt al
    
    Args:
        request: ChatRequest (message, conversation_id)
        
    Returns:
        Assistant yanıtı ve güncel skor
    """
    if not request.conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id is required")
    
    try:
        service = await get_chat_service()
        response = await service.send_message(request.conversation_id, request.message)
        return response
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/score/{conversation_id}", response_model=ScoreResult)
async def get_score(conversation_id: str):
    """
    Konuşma skorunu getir
    
    Args:
        conversation_id: Konuşma ID'si
        
    Returns:
        Detaylı skor bilgisi
    """
    try:
        service = await get_chat_service()
        result = await service.get_score(conversation_id)
        return result
    except Exception as e:
        logger.error(f"Error getting score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/{conversation_id}")
async def reset_conversation(conversation_id: str):
    """
    Konuşmayı sıfırla
    
    Args:
        conversation_id: Konuşma ID'si
    """
    try:
        service = await get_chat_service()
        await service.reset_conversation(conversation_id)
        return {"status": "success", "message": f"Conversation {conversation_id} reset"}
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """
    Konuşma geçmişini getir
    
    Args:
        conversation_id: Konuşma ID'si
        
    Returns:
        Mesaj listesi
    """
    try:
        service = await get_chat_service()
        messages = await service.get_history(conversation_id)
        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        }
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

