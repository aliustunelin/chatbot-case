"""
Tests for Service layer
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np

from src.model.conversation import Message, MessageRole, ScoreResult, CategoryScore
from src.model.keywords import KEYWORD_CATEGORIES
from src.service.scoring_service import ScoringService
from src.service.chat_service import ChatService


class TestScoringService:
    """Tests for Scoring Service"""
    
    @pytest.mark.asyncio
    async def test_cosine_similarity(self, scoring_service):
        """Test cosine similarity calculation"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        similarity = scoring_service._cosine_similarity(vec1, vec2)
        
        assert similarity == pytest.approx(1.0)
    
    @pytest.mark.asyncio
    async def test_cosine_similarity_orthogonal(self, scoring_service):
        """Test cosine similarity for orthogonal vectors"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        
        similarity = scoring_service._cosine_similarity(vec1, vec2)
        
        assert similarity == pytest.approx(0.0)
    
    @pytest.mark.asyncio
    async def test_hash_text(self, scoring_service):
        """Test text hashing"""
        hash1 = scoring_service._hash_text("Hello")
        hash2 = scoring_service._hash_text("hello")  # lowercase should be same
        hash3 = scoring_service._hash_text("World")
        
        assert hash1 == hash2  # Case insensitive
        assert hash1 != hash3
    
    @pytest.mark.asyncio
    async def test_calculate_score_empty_messages(self, scoring_service, mock_redis_repo):
        """Test score calculation with no messages"""
        result = await scoring_service.calculate_score("conv-123", [])
        
        assert result.total_score == 0.0
        assert len(result.category_scores) == 5
    
    @pytest.mark.asyncio
    async def test_calculate_score_with_keywords(self, scoring_service, mock_openai_repo, mock_redis_repo):
        """Test score calculation with keyword matches"""
        messages = [
            Message(role=MessageRole.USER, content="I eat fruits and vegetables every day"),
        ]
        
        result = await scoring_service.calculate_score("conv-123", messages)
        
        assert result.total_score > 0
        assert result.conversation_id == "conv-123"
        
        # Check fruits_vegetables category got score
        fruits_score = next(
            (cs for cs in result.category_scores if cs.category == "Fruits & Vegetables"),
            None
        )
        assert fruits_score is not None
        assert fruits_score.score > 0
    
    @pytest.mark.asyncio
    async def test_calculate_score_full_coverage(self, scoring_service, healthy_eating_message, mock_openai_repo):
        """Test score calculation with full keyword coverage"""
        messages = [healthy_eating_message]
        
        result = await scoring_service.calculate_score("conv-123", messages)
        
        # Should have high score with all keywords
        assert result.total_score >= 60  # At least 60% coverage
    
    @pytest.mark.asyncio
    async def test_generate_summary_excellent(self, scoring_service):
        """Test summary generation for excellent score"""
        category_scores = [
            CategoryScore(category="Test", score=20.0, max_score=20.0)
        ]
        
        summary = scoring_service._generate_summary(category_scores, 85.0)
        
        assert "Excellent" in summary
    
    @pytest.mark.asyncio
    async def test_generate_summary_needs_improvement(self, scoring_service):
        """Test summary generation for low score"""
        category_scores = [
            CategoryScore(category="Test", score=5.0, max_score=20.0)
        ]
        
        summary = scoring_service._generate_summary(category_scores, 10.0)
        
        assert "Needs Improvement" in summary
    
    @pytest.mark.asyncio
    async def test_only_user_messages_scored(self, scoring_service, mock_openai_repo):
        """Test that only user messages are scored"""
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are a nutrition coach."),
            Message(role=MessageRole.ASSISTANT, content="I love fruits and vegetables!"),
            Message(role=MessageRole.USER, content="Hello"),
        ]
        
        result = await scoring_service.calculate_score("conv-123", messages)
        
        # Only "Hello" should be analyzed, no keywords there
        # Fruits/vegetables in assistant message should NOT be counted
        fruits_score = next(
            (cs for cs in result.category_scores if cs.category == "Fruits & Vegetables"),
            None
        )
        # Score should be low since user didn't mention fruits
        assert fruits_score.score < 20.0


class TestChatService:
    """Tests for Chat Service"""
    
    @pytest.mark.asyncio
    async def test_create_conversation_id(self, chat_service):
        """Test conversation ID creation"""
        conv_id = chat_service._create_conversation_id()
        
        assert conv_id is not None
        assert len(conv_id) == 36  # UUID format
    
    @pytest.mark.asyncio
    async def test_start_conversation(self, chat_service, mock_openai_repo, mock_redis_repo):
        """Test starting a new conversation"""
        response = await chat_service.start_conversation()
        
        assert response.conversation_id is not None
        assert response.response is not None
        assert response.current_score == 0.0
        
        # Verify system message was saved
        mock_redis_repo.save_message.assert_called()
    
    @pytest.mark.asyncio
    async def test_send_message(self, chat_service, mock_openai_repo, mock_redis_repo):
        """Test sending a message"""
        # Setup mock history
        mock_redis_repo.get_history = AsyncMock(return_value=[
            Message(role=MessageRole.SYSTEM, content="System prompt"),
            Message(role=MessageRole.ASSISTANT, content="Hello!"),
        ])
        
        response = await chat_service.send_message("conv-123", "I eat fruits")
        
        assert response.conversation_id == "conv-123"
        assert response.response is not None
        
        # Verify message was saved
        assert mock_redis_repo.save_message.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_get_score(self, chat_service, mock_redis_repo):
        """Test getting conversation score"""
        mock_redis_repo.get_history = AsyncMock(return_value=[
            Message(role=MessageRole.USER, content="I love vegetables"),
        ])
        
        result = await chat_service.get_score("conv-123")
        
        assert isinstance(result, ScoreResult)
        assert result.conversation_id == "conv-123"
    
    @pytest.mark.asyncio
    async def test_reset_conversation(self, chat_service, mock_redis_repo):
        """Test resetting a conversation"""
        await chat_service.reset_conversation("conv-123")
        
        mock_redis_repo.clear_history.assert_called_once_with("conv-123")
    
    @pytest.mark.asyncio
    async def test_get_history(self, chat_service, mock_redis_repo):
        """Test getting conversation history"""
        expected_messages = [
            Message(role=MessageRole.USER, content="Hello"),
            Message(role=MessageRole.ASSISTANT, content="Hi!"),
        ]
        mock_redis_repo.get_history = AsyncMock(return_value=expected_messages)
        
        result = await chat_service.get_history("conv-123")
        
        assert len(result) == 2
        mock_redis_repo.get_history.assert_called_once_with("conv-123")
    
    @pytest.mark.asyncio
    async def test_initialize(self, chat_service, mock_openai_repo, mock_redis_repo):
        """Test service initialization"""
        await chat_service.initialize()
        
        mock_openai_repo.initialize.assert_called_once()
        mock_redis_repo.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close(self, chat_service, mock_openai_repo, mock_redis_repo):
        """Test service shutdown"""
        await chat_service.close()
        
        mock_openai_repo.close.assert_called_once()
        mock_redis_repo.close.assert_called_once()


class TestKeywordMatching:
    """Integration tests for keyword matching logic"""
    
    @pytest.mark.asyncio
    async def test_string_matching_english(self, scoring_service, mock_openai_repo):
        """Test string matching with English keywords"""
        messages = [
            Message(role=MessageRole.USER, content="I drink water every day and eat protein"),
        ]
        
        result = await scoring_service.calculate_score("conv-123", messages)
        
        hydration = next(cs for cs in result.category_scores if cs.category == "Hydration")
        balanced = next(cs for cs in result.category_scores if cs.category == "Balanced Meals")
        
        assert "water" in hydration.matched_keywords or hydration.score > 0
        assert "protein" in balanced.matched_keywords or balanced.score > 0
    
    @pytest.mark.asyncio
    async def test_string_matching_turkish(self, scoring_service, mock_openai_repo):
        """Test string matching with Turkish keywords"""
        messages = [
            Message(role=MessageRole.USER, content="Her gün meyve ve sebze yiyorum, su içiyorum"),
        ]
        
        result = await scoring_service.calculate_score("conv-123", messages)
        
        fruits = next(cs for cs in result.category_scores if cs.category == "Fruits & Vegetables")
        hydration = next(cs for cs in result.category_scores if cs.category == "Hydration")
        
        # Should match Turkish keywords
        assert fruits.score > 0 or "meyve" in str(fruits.matched_keywords).lower()
        assert hydration.score > 0 or "su" in str(hydration.matched_keywords).lower()
    
    @pytest.mark.asyncio
    async def test_processed_foods_awareness(self, scoring_service, mock_openai_repo):
        """Test processed foods category matching"""
        messages = [
            Message(role=MessageRole.USER, content="I avoid junk food, sugar and processed foods"),
        ]
        
        result = await scoring_service.calculate_score("conv-123", messages)
        
        processed = next(cs for cs in result.category_scores if cs.category == "Processed Foods")
        
        assert processed.score > 0
    
    @pytest.mark.asyncio
    async def test_meal_timing_matching(self, scoring_service, mock_openai_repo):
        """Test meal timing category matching"""
        messages = [
            Message(role=MessageRole.USER, content="I have breakfast, lunch and dinner at regular times"),
        ]
        
        result = await scoring_service.calculate_score("conv-123", messages)
        
        timing = next(cs for cs in result.category_scores if cs.category == "Meal Timing")
        
        assert timing.score > 0

