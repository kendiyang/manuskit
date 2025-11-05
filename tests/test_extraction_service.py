"""
Tests for the extraction service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.extraction_service import ExtractionService, replace_protocol_mapping
from src.models import ExtractionResult


def test_replace_protocol_mapping():
    """Test protocol replacement for WebSocket URLs"""
    assert replace_protocol_mapping("http://localhost:3000") == "ws://localhost:3000"
    assert replace_protocol_mapping("https://example.com") == "wss://example.com"
    assert replace_protocol_mapping("ws://localhost") == "ws://localhost"
    assert replace_protocol_mapping("wss://localhost") == "wss://localhost"


def test_extraction_service_init_with_env_vars():
    """Test ExtractionService initialization with environment variables"""
    with patch.dict('os.environ', {
        'STEEL_API_KEY': 'test_steel_key',
        'OPENAI_API_KEY': 'test_openai_key'
    }):
        service = ExtractionService()
        assert service.steel_api_key == 'test_steel_key'
        assert service.openai_api_key == 'test_openai_key'


def test_extraction_service_init_missing_keys():
    """Test ExtractionService raises error when keys are missing"""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="STEEL_API_KEY is required"):
            ExtractionService()


def test_extraction_service_init_with_params():
    """Test ExtractionService initialization with explicit parameters"""
    service = ExtractionService(
        steel_api_key="explicit_steel_key",
        openai_api_key="explicit_openai_key",
        model="gpt-3.5-turbo"
    )
    assert service.steel_api_key == "explicit_steel_key"
    assert service.openai_api_key == "explicit_openai_key"
    assert service.model == "gpt-3.5-turbo"


@pytest.mark.asyncio
async def test_extract_reddit_answers_success():
    """Test successful Reddit Answers extraction"""
    with patch.dict('os.environ', {
        'STEEL_API_KEY': 'test_key',
        'OPENAI_API_KEY': 'test_key',
        'DOMAIN': 'http://localhost:3000'
    }):
        service = ExtractionService()
        
        # Mock Steel client
        mock_session = Mock()
        mock_session.id = "session-123"
        mock_session.session_viewer_url = "http://viewer.url"
        
        mock_steel_client = Mock()
        mock_steel_client.sessions.create.return_value = mock_session
        
        # Mock Agent
        mock_agent_result = Mock()
        
        with patch.object(service, '_create_steel_client', return_value=mock_steel_client):
            with patch('src.services.extraction_service.Agent') as MockAgent:
                mock_agent = MockAgent.return_value
                mock_agent.run = AsyncMock(return_value=mock_agent_result)
                
                result = await service.extract_reddit_answers("test question")
                
                assert isinstance(result, ExtractionResult)
                assert result.question == "test question"
                
                # Verify Steel session was released
                mock_steel_client.sessions.release.assert_called_once_with("session-123")


@pytest.mark.asyncio
async def test_extract_reddit_answers_cleanup_on_error():
    """Test Steel session cleanup on extraction error"""
    with patch.dict('os.environ', {
        'STEEL_API_KEY': 'test_key',
        'OPENAI_API_KEY': 'test_key'
    }):
        service = ExtractionService()
        
        mock_session = Mock()
        mock_session.id = "session-123"
        mock_steel_client = Mock()
        mock_steel_client.sessions.create.return_value = mock_session
        
        with patch.object(service, '_create_steel_client', return_value=mock_steel_client):
            with patch('src.services.extraction_service.Agent') as MockAgent:
                mock_agent = MockAgent.return_value
                mock_agent.run = AsyncMock(side_effect=Exception("Test error"))
                
                with pytest.raises(Exception, match="Test error"):
                    await service.extract_reddit_answers("test question")
                
                # Verify cleanup was called
                mock_steel_client.sessions.release.assert_called_once_with("session-123")


def test_parse_agent_result_basic():
    """Test basic agent result parsing"""
    with patch.dict('os.environ', {
        'STEEL_API_KEY': 'test_key',
        'OPENAI_API_KEY': 'test_key'
    }):
        service = ExtractionService()
        
        mock_result = Mock()
        result = service._parse_agent_result(mock_result, "test question")
        
        assert isinstance(result, ExtractionResult)
        assert result.question == "test question"
        assert isinstance(result.sources, list)
        assert isinstance(result.sections, list)
