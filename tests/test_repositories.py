"""
Tests for Repository layer
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.model.conversation import Message, MessageRole
from src.repository.openai_repository import OpenAIRepository
from src.repository.redis_repository import RedisRepository


class TestOpenAIRepository:
    """Tests for OpenAI Repository"""
    
    @pytest.fixture
    def openai_repo(self):
        """Create OpenAI repository instance"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            return OpenAIRepository()
    
    def test_init_default_values(self, openai_repo):
        """Test repository initialization with defaults"""
        assert openai_repo.model == "gpt-4o-mini"
        assert openai_repo.embedding_model == "text-embedding-3-small"
    
    @pytest.mark.asyncio
    async def test_chat_completion_formats_messages(self, openai_repo):
        """Test that messages are properly formatted for OpenAI API"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        openai_repo.client = mock_client
        
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are helpful."),
            Message(role=MessageRole.USER, content="Hello"),
        ]
        
        result = await openai_repo.chat_completion(messages)
        
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()
        
        # Check message formatting
        call_args = mock_client.chat.completions.create.call_args
        formatted_messages = call_args.kwargs['messages']
        assert formatted_messages[0]['role'] == 'system'
        assert formatted_messages[1]['role'] == 'user'
    
    @pytest.mark.asyncio
    async def test_create_embedding_returns_vector(self, openai_repo):
        """Test embedding creation returns vector"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].embedding = [0.1] * 1536
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        
        openai_repo.client = mock_client
        
        result = await openai_repo.create_embedding("test text")
        
        assert len(result) == 1536
        assert all(isinstance(x, float) for x in result)
    
    @pytest.mark.asyncio
    async def test_create_embeddings_batch(self, openai_repo):
        """Test batch embedding creation"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(), MagicMock()]
        mock_response.data[0].embedding = [0.1] * 1536
        mock_response.data[1].embedding = [0.2] * 1536
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        
        openai_repo.client = mock_client
        
        result = await openai_repo.create_embeddings_batch(["text1", "text2"])
        
        assert len(result) == 2
        assert len(result[0]) == 1536


class TestRedisRepository:
    """Tests for Redis Repository"""
    
    @pytest.fixture
    def redis_repo(self):
        """Create Redis repository instance"""
        with patch.dict('os.environ', {
            'REDIS_URL': 'redis://localhost:6380',
            'REDIS_PASSWORD': 'test-password'
        }):
            return RedisRepository()
    
    def test_init_default_values(self, redis_repo):
        """Test repository initialization"""
        assert redis_repo.redis_url == "redis://localhost:6380"
        assert redis_repo.conversation_prefix == "conversation:"
        assert redis_repo.score_prefix == "score:"
    
    def test_get_conversation_key(self, redis_repo):
        """Test conversation key generation"""
        key = redis_repo._get_conversation_key("conv-123")
        assert key == "conversation:conv-123"
    
    def test_get_score_key(self, redis_repo):
        """Test score key generation"""
        key = redis_repo._get_score_key("conv-123")
        assert key == "score:conv-123"
    
    @pytest.mark.asyncio
    async def test_save_message(self, redis_repo):
        """Test saving message to Redis"""
        mock_client = AsyncMock()
        redis_repo.client = mock_client
        
        message = Message(role=MessageRole.USER, content="Hello")
        await redis_repo.save_message("conv-123", message)
        
        mock_client.rpush.assert_called_once()
        mock_client.expire.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_history_empty(self, redis_repo):
        """Test getting empty history"""
        mock_client = AsyncMock()
        mock_client.lrange = AsyncMock(return_value=[])
        redis_repo.client = mock_client
        
        result = await redis_repo.get_history("conv-123")
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_history_with_messages(self, redis_repo):
        """Test getting history with messages"""
        mock_client = AsyncMock()
        mock_messages = [
            json.dumps({
                "role": "user",
                "content": "Hello",
                "timestamp": "2024-01-01T12:00:00"
            }),
            json.dumps({
                "role": "assistant",
                "content": "Hi there!",
                "timestamp": "2024-01-01T12:00:01"
            })
        ]
        mock_client.lrange = AsyncMock(return_value=mock_messages)
        redis_repo.client = mock_client
        
        result = await redis_repo.get_history("conv-123")
        
        assert len(result) == 2
        assert result[0].role == MessageRole.USER
        assert result[1].role == MessageRole.ASSISTANT
    
    @pytest.mark.asyncio
    async def test_clear_history(self, redis_repo):
        """Test clearing conversation history"""
        mock_client = AsyncMock()
        redis_repo.client = mock_client
        
        await redis_repo.clear_history("conv-123")
        
        mock_client.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_and_get_score(self, redis_repo):
        """Test saving and getting score"""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value="75.5")
        redis_repo.client = mock_client
        
        await redis_repo.save_score("conv-123", 75.5)
        mock_client.set.assert_called()
        
        result = await redis_repo.get_score("conv-123")
        assert result == 75.5
    
    @pytest.mark.asyncio
    async def test_cache_embedding(self, redis_repo):
        """Test caching embedding"""
        mock_client = AsyncMock()
        redis_repo.client = mock_client
        
        embedding = [0.1] * 1536
        await redis_repo.cache_embedding("hash-123", embedding)
        
        mock_client.set.assert_called()
        mock_client.expire.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_cached_embedding_miss(self, redis_repo):
        """Test cache miss for embedding"""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=None)
        redis_repo.client = mock_client
        
        result = await redis_repo.get_cached_embedding("hash-123")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_cached_embedding_hit(self, redis_repo):
        """Test cache hit for embedding"""
        mock_client = AsyncMock()
        embedding = [0.1] * 10
        mock_client.get = AsyncMock(return_value=json.dumps(embedding))
        redis_repo.client = mock_client
        
        result = await redis_repo.get_cached_embedding("hash-123")
        
        assert result == embedding

