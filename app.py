import asyncio
import os
import signal
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from src.utils.logger import Logger
from src.router.chat_router import (
    router as chat_router,
    initialize_chat_service,
    shutdown_chat_service
)

load_dotenv()

logger = Logger.setup()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan event handler"""
    # Startup
    logger.info("Starting Healthy Eating Chatbot API...")
    await initialize_chat_service()
    logger.info("Chat service initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await shutdown_chat_service()
    logger.info("Shutdown complete")


# FastAPI app
app = FastAPI(
    title="Healthy Eating Chatbot API",
    description="AI-powered chatbot for healthy eating role-play conversations",
    version="1.0.0",
    lifespan=lifespan
)

# Router'ları ekle
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Healthy Eating Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "start_conversation": "POST /chat/start",
            "send_message": "POST /chat/message",
            "get_score": "GET /chat/score/{conversation_id}",
            "reset": "POST /chat/reset/{conversation_id}",
            "history": "GET /chat/history/{conversation_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


def run_api():
    """API sunucusunu başlat"""
    host = os.getenv("API_HOST")
    port = int(os.getenv("API_PORT"))
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    logger.info("Starting Healthy Eating Chatbot API")
    run_api()
