"""
Pytest fixtures for testing
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.model.conversation import Message, MessageRole, Conversation, ScoreResult, CategoryScore
from src.repository.openai_repository import OpenAIRepository
from src.repository.redis_repository import RedisRepository
from src.service.scoring_service import ScoringService
from src.service.chat_service import ChatService


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_messages():
    """Sample messages for testing"""
    return [
        Message(role=MessageRole.SYSTEM, content="You are a nutrition coach."),
        Message(role=MessageRole.ASSISTANT, content="Hello! Let's talk about healthy eating."),
        Message(role=MessageRole.USER, content="I eat fruits and vegetables every day."),
        Message(role=MessageRole.ASSISTANT, content="That's great! What about hydration?"),
        Message(role=MessageRole.USER, content="I drink 8 glasses of water daily."),
    ]


@pytest.fixture
def sample_conversation(sample_messages):
    """Sample conversation for testing"""
    return Conversation(
        conversation_id="test-conv-123",
        messages=sample_messages
    )


@pytest.fixture
def mock_openai_repo():
    """Mock OpenAI repository"""
    repo = AsyncMock(spec=OpenAIRepository)
    repo.chat_completion = AsyncMock(return_value="This is a test response about healthy eating.")
    repo.create_embedding = AsyncMock(return_value=[0.1] * 1536)  # OpenAI embedding dimension
    repo.create_embeddings_batch = AsyncMock(return_value=[[0.1] * 1536, [0.2] * 1536])
    repo.initialize = AsyncMock()
    repo.close = AsyncMock()
    return repo


@pytest.fixture
def mock_redis_repo():
    """Mock Redis repository"""
    repo = AsyncMock(spec=RedisRepository)
    repo.save_message = AsyncMock()
    repo.get_history = AsyncMock(return_value=[])
    repo.clear_history = AsyncMock()
    repo.save_score = AsyncMock()
    repo.get_score = AsyncMock(return_value=0.0)
    repo.cache_embedding = AsyncMock()
    repo.get_cached_embedding = AsyncMock(return_value=None)
    repo.initialize = AsyncMock()
    repo.close = AsyncMock()
    return repo


@pytest.fixture
def scoring_service(mock_openai_repo, mock_redis_repo):
    """Scoring service with mocked dependencies"""
    return ScoringService(mock_openai_repo, mock_redis_repo)


@pytest.fixture
def chat_service(mock_openai_repo, mock_redis_repo, scoring_service):
    """Chat service with mocked dependencies"""
    return ChatService(mock_openai_repo, mock_redis_repo, scoring_service)


@pytest.fixture
def healthy_eating_message():
    """Message containing healthy eating keywords"""
    return Message(
        role=MessageRole.USER,
        content="I eat fruits and vegetables daily. I drink 8 glasses of water. "
                "I balance my meals with protein, carbs, and healthy fats. "
                "I avoid processed foods and junk food. "
                "I have breakfast, lunch, and dinner at regular times."
    )


@pytest.fixture
def partial_healthy_message():
    """Message with partial healthy eating coverage"""
    return Message(
        role=MessageRole.USER,
        content="I try to eat some fruits occasionally and drink water when I remember."
    )

