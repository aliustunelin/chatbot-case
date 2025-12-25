from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Conversation(BaseModel):
    conversation_id: str
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CategoryScore(BaseModel):
    category: str
    score: float = 0.0
    max_score: float = 20.0
    matched_keywords: List[str] = Field(default_factory=list)


class ScoreResult(BaseModel):
    conversation_id: str
    total_score: float = 0.0
    max_possible_score: float = 100.0
    category_scores: List[CategoryScore] = Field(default_factory=list)
    evaluation_summary: str = ""


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    current_score: float = 0.0

