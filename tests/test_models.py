"""
Tests for Pydantic models
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from src.model.conversation import (
    Message, 
    MessageRole, 
    Conversation, 
    CategoryScore, 
    ScoreResult,
    ChatRequest,
    ChatResponse
)
from src.model.keywords import (
    KeywordCategory,
    KEYWORD_CATEGORIES,
    get_all_keywords,
    get_category_names
)


class TestMessage:
    """Tests for Message model"""
    
    def test_create_message_with_role(self):
        """Test creating message with different roles"""
        user_msg = Message(role=MessageRole.USER, content="Hello")
        assert user_msg.role == MessageRole.USER
        assert user_msg.content == "Hello"
        assert isinstance(user_msg.timestamp, datetime)
    
    def test_create_system_message(self):
        """Test creating system message"""
        msg = Message(role=MessageRole.SYSTEM, content="You are a helpful assistant.")
        assert msg.role == MessageRole.SYSTEM
    
    def test_create_assistant_message(self):
        """Test creating assistant message"""
        msg = Message(role=MessageRole.ASSISTANT, content="How can I help?")
        assert msg.role == MessageRole.ASSISTANT
    
    def test_message_with_custom_timestamp(self):
        """Test message with custom timestamp"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        msg = Message(role=MessageRole.USER, content="Test", timestamp=custom_time)
        assert msg.timestamp == custom_time


class TestConversation:
    """Tests for Conversation model"""
    
    def test_create_empty_conversation(self):
        """Test creating conversation with no messages"""
        conv = Conversation(conversation_id="test-123")
        assert conv.conversation_id == "test-123"
        assert conv.messages == []
    
    def test_create_conversation_with_messages(self, sample_messages):
        """Test creating conversation with messages"""
        conv = Conversation(
            conversation_id="test-456",
            messages=sample_messages
        )
        assert len(conv.messages) == 5
        assert conv.messages[0].role == MessageRole.SYSTEM


class TestCategoryScore:
    """Tests for CategoryScore model"""
    
    def test_create_category_score(self):
        """Test creating category score"""
        cs = CategoryScore(
            category="Fruits & Vegetables",
            score=15.0,
            max_score=20.0,
            matched_keywords=["fruit", "vegetable", "apple"]
        )
        assert cs.category == "Fruits & Vegetables"
        assert cs.score == 15.0
        assert len(cs.matched_keywords) == 3
    
    def test_default_values(self):
        """Test category score default values"""
        cs = CategoryScore(category="Test")
        assert cs.score == 0.0
        assert cs.max_score == 20.0
        assert cs.matched_keywords == []


class TestScoreResult:
    """Tests for ScoreResult model"""
    
    def test_create_score_result(self):
        """Test creating score result"""
        categories = [
            CategoryScore(category="Test1", score=10.0),
            CategoryScore(category="Test2", score=20.0),
        ]
        result = ScoreResult(
            conversation_id="conv-123",
            total_score=30.0,
            category_scores=categories,
            evaluation_summary="Good progress!"
        )
        assert result.total_score == 30.0
        assert len(result.category_scores) == 2
    
    def test_default_max_score(self):
        """Test default max possible score"""
        result = ScoreResult(conversation_id="test")
        assert result.max_possible_score == 100.0


class TestChatRequest:
    """Tests for ChatRequest model"""
    
    def test_create_chat_request(self):
        """Test creating chat request"""
        req = ChatRequest(message="Hello", conversation_id="conv-123")
        assert req.message == "Hello"
        assert req.conversation_id == "conv-123"
    
    def test_optional_conversation_id(self):
        """Test chat request without conversation_id"""
        req = ChatRequest(message="Start new conversation")
        assert req.message == "Start new conversation"
        assert req.conversation_id is None


class TestChatResponse:
    """Tests for ChatResponse model"""
    
    def test_create_chat_response(self):
        """Test creating chat response"""
        resp = ChatResponse(
            conversation_id="conv-123",
            response="Hello! How are you?",
            current_score=25.5
        )
        assert resp.conversation_id == "conv-123"
        assert resp.response == "Hello! How are you?"
        assert resp.current_score == 25.5


class TestKeywordCategory:
    """Tests for KeywordCategory model"""
    
    def test_create_keyword_category(self):
        """Test creating keyword category"""
        kc = KeywordCategory(
            name="Test Category",
            description="Test description",
            keywords=["keyword1", "keyword2"]
        )
        assert kc.name == "Test Category"
        assert len(kc.keywords) == 2
        assert kc.max_score == 20.0


class TestKeywordCategories:
    """Tests for KEYWORD_CATEGORIES"""
    
    def test_has_five_categories(self):
        """Test that there are exactly 5 categories"""
        assert len(KEYWORD_CATEGORIES) == 5
    
    def test_category_keys(self):
        """Test category key names"""
        expected_keys = [
            "fruits_vegetables",
            "hydration",
            "balanced_meals",
            "processed_foods",
            "meal_timing"
        ]
        assert list(KEYWORD_CATEGORIES.keys()) == expected_keys
    
    def test_each_category_has_keywords(self):
        """Test that each category has keywords"""
        for key, category in KEYWORD_CATEGORIES.items():
            assert len(category.keywords) > 0, f"{key} has no keywords"
    
    def test_fruits_vegetables_keywords(self):
        """Test fruits & vegetables category keywords"""
        category = KEYWORD_CATEGORIES["fruits_vegetables"]
        assert "fruit" in category.keywords
        assert "vegetable" in category.keywords
        assert "meyve" in category.keywords  # Turkish
    
    def test_hydration_keywords(self):
        """Test hydration category keywords"""
        category = KEYWORD_CATEGORIES["hydration"]
        assert "water" in category.keywords
        assert "su" in category.keywords  # Turkish


class TestKeywordHelpers:
    """Tests for keyword helper functions"""
    
    def test_get_all_keywords(self):
        """Test getting all keywords"""
        all_keywords = get_all_keywords()
        assert len(all_keywords) > 50  # Should have many keywords
        assert "fruit" in all_keywords
        assert "water" in all_keywords
    
    def test_get_category_names(self):
        """Test getting category names"""
        names = get_category_names()
        assert len(names) == 5
        assert "Fruits & Vegetables" in names
        assert "Hydration" in names
        assert "Balanced Meals" in names
        assert "Processed Foods" in names
        assert "Meal Timing" in names

