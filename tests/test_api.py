"""
Tests for API endpoints
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app import app
from src.model.conversation import ChatResponse, ScoreResult, CategoryScore
from src.router import chat_router


class TestAPIEndpoints:
    """Tests for FastAPI endpoints"""
    
    @pytest.fixture
    def mock_chat_service(self):
        """Mock chat service for testing"""
        service = AsyncMock()
        service.start_conversation = AsyncMock(return_value=ChatResponse(
            conversation_id="test-conv-123",
            response="Hello! Let's talk about healthy eating.",
            current_score=0.0
        ))
        service.send_message = AsyncMock(return_value=ChatResponse(
            conversation_id="test-conv-123",
            response="That's great! Fruits are very healthy.",
            current_score=20.0
        ))
        service.get_score = AsyncMock(return_value=ScoreResult(
            conversation_id="test-conv-123",
            total_score=40.0,
            category_scores=[
                CategoryScore(category="Fruits & Vegetables", score=20.0),
                CategoryScore(category="Hydration", score=20.0),
            ],
            evaluation_summary="Good progress!"
        ))
        service.reset_conversation = AsyncMock()
        service.get_history = AsyncMock(return_value=[])
        return service
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    @pytest.mark.asyncio
    async def test_start_conversation_endpoint(self, mock_chat_service):
        """Test start conversation endpoint"""
        with patch('src.router.chat_router.get_chat_service', return_value=mock_chat_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/chat/start")
        
            assert response.status_code == 200
            data = response.json()
            assert "conversation_id" in data
            assert "response" in data
    
    @pytest.mark.asyncio
    async def test_send_message_endpoint(self, mock_chat_service):
        """Test send message endpoint"""
        with patch('src.router.chat_router.get_chat_service', return_value=mock_chat_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/chat/message", json={
                    "message": "I eat fruits every day",
                    "conversation_id": "test-conv-123"
                })
        
            assert response.status_code == 200
            data = response.json()
            assert data["conversation_id"] == "test-conv-123"
            assert "response" in data
            assert "current_score" in data
    
    @pytest.mark.asyncio
    async def test_send_message_without_conversation_id(self, mock_chat_service):
        """Test send message without conversation_id fails"""
        with patch('src.router.chat_router.get_chat_service', return_value=mock_chat_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/chat/message", json={
                    "message": "Hello"
                })
        
            assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_score_endpoint(self, mock_chat_service):
        """Test get score endpoint"""
        with patch('src.router.chat_router.get_chat_service', return_value=mock_chat_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/chat/score/test-conv-123")
        
            assert response.status_code == 200
            data = response.json()
            assert data["conversation_id"] == "test-conv-123"
            assert "total_score" in data
            assert "category_scores" in data
    
    @pytest.mark.asyncio
    async def test_reset_conversation_endpoint(self, mock_chat_service):
        """Test reset conversation endpoint"""
        with patch('src.router.chat_router.get_chat_service', return_value=mock_chat_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/chat/reset/test-conv-123")
        
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_get_history_endpoint(self, mock_chat_service):
        """Test get history endpoint"""
        with patch('src.router.chat_router.get_chat_service', return_value=mock_chat_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/chat/history/test-conv-123")
        
            assert response.status_code == 200
            data = response.json()
            assert data["conversation_id"] == "test-conv-123"
            assert "messages" in data


class TestAPIValidation:
    """Tests for API request validation"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_invalid_json_body(self, client):
        """Test invalid JSON body handling"""
        response = client.post(
            "/chat/message",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_field(self, client):
        """Test missing required field handling"""
        response = client.post("/chat/message", json={})
        
        assert response.status_code == 422


class TestAPIResponseFormat:
    """Tests for API response formats"""
    
    @pytest.fixture
    def mock_chat_service(self):
        """Mock chat service"""
        service = AsyncMock()
        service.start_conversation = AsyncMock(return_value=ChatResponse(
            conversation_id="test-123",
            response="Hello!",
            current_score=0.0
        ))
        return service
    
    @pytest.mark.asyncio
    async def test_chat_response_format(self, mock_chat_service):
        """Test ChatResponse format"""
        with patch('src.router.chat_router.get_chat_service', return_value=mock_chat_service):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/chat/start")
        
            data = response.json()
            
            # Verify all required fields
            assert "conversation_id" in data
            assert "response" in data
            assert "current_score" in data
            
            # Verify types
            assert isinstance(data["conversation_id"], str)
            assert isinstance(data["response"], str)
            assert isinstance(data["current_score"], (int, float))

