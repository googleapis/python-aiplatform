import pytest
from unittest import mock
import sys


class TestAdkAppMultimodal:
    """Tests for multimodal message support in AdkApp."""

    @pytest.fixture
    def setup_mocks(self):
        """Set up all necessary mocks for ADK and dependencies."""
        # Mock the entire google.adk module structure
        mock_adk = mock.MagicMock()
        mock_agent = mock.MagicMock()
        mock_agent.__class__.__name__ = "BaseAgent"
        
        # Mock google.genai.types
        mock_genai = mock.MagicMock()
        
        # Create mock types classes
        class MockPart:
            def __init__(self, text=None, **kwargs):
                self.text = text
                for k, v in kwargs.items():
                    setattr(self, k, v)
            
            @classmethod
            def from_uri(cls, file_uri, mime_type):
                part = cls()
                part.file_data = mock.MagicMock()
                part.file_data.file_uri = file_uri
                part.file_data.mime_type = mime_type
                return part
            
            @classmethod
            def from_bytes(cls, data, mime_type):
                part = cls()
                part.inline_data = mock.MagicMock()
                part.inline_data.data = data
                part.inline_data.mime_type = mime_type
                return part
        
        class MockContent:
            def __init__(self, role="user", parts=None):
                self.role = role
                self.parts = parts or []
            
            @classmethod
            def model_validate(cls, data):
                if isinstance(data, dict):
                    return cls(role=data.get("role", "user"), parts=data.get("parts", []))
                return data
        
        mock_genai.types.Part = MockPart
        mock_genai.types.Content = MockContent
        
        # Mock the modules in sys.modules
        sys.modules['google.adk'] = mock_adk
        sys.modules['google.adk.agents'] = mock.MagicMock()
        sys.modules['google.adk.events'] = mock.MagicMock()
        sys.modules['google.adk.plugins'] = mock.MagicMock()
        sys.modules['google.adk.sessions'] = mock.MagicMock()
        sys.modules['google.adk.artifacts'] = mock.MagicMock()
        sys.modules['google.adk.memory'] = mock.MagicMock()
        sys.modules['google.adk.runners'] = mock.MagicMock()
        sys.modules['google.genai'] = mock_genai
        
        yield {
            'agent': mock_agent,
            'genai': mock_genai
        }
        
        # Cleanup
        for module in ['google.adk', 'google.adk.agents', 'google.adk.events', 
                      'google.adk.plugins', 'google.adk.sessions', 
                      'google.adk.artifacts', 'google.adk.memory', 
                      'google.adk.runners', 'google.genai']:
            if module in sys.modules:
                del sys.modules[module]

    def test_process_message_to_content_with_string(self, setup_mocks):
        """Test _process_message_to_content with string input."""
        from vertexai.agent_engines.templates.adk import AdkApp
        from google.genai import types
        
        # Initialize without triggering set_up
        with mock.patch('vertexai.agent_engines.templates.adk.get_adk_version', return_value="1.5.0"):
            with mock.patch('vertexai.agent_engines.templates.adk.is_version_sufficient', return_value=True):
                app = AdkApp(agent=setup_mocks['agent'])
        
        message = "Hello, world!"
        result = app._process_message_to_content(message, types)
        
        assert isinstance(result, types.Content)
        assert result.role == "user"
        assert len(result.parts) == 1
        assert result.parts[0].text == "Hello, world!"

    def test_process_message_to_content_with_dict(self, setup_mocks):
        """Test _process_message_to_content with dictionary input."""
        from vertexai.agent_engines.templates.adk import AdkApp
        from google.genai import types
        
        with mock.patch('vertexai.agent_engines.templates.adk.get_adk_version', return_value="1.5.0"):
            with mock.patch('vertexai.agent_engines.templates.adk.is_version_sufficient', return_value=True):
                app = AdkApp(agent=setup_mocks['agent'])
        
        message = {
            "role": "user",
            "parts": [{"text": "Test message"}]
        }
        result = app._process_message_to_content(message, types)
        
        assert isinstance(result, types.Content)
        assert result.role == "user"

    def test_process_message_to_content_with_content_object(self, setup_mocks):
        """Test _process_message_to_content with Content object."""
        from vertexai.agent_engines.templates.adk import AdkApp
        from google.genai import types
        
        with mock.patch('vertexai.agent_engines.templates.adk.get_adk_version', return_value="1.5.0"):
            with mock.patch('vertexai.agent_engines.templates.adk.is_version_sufficient', return_value=True):
                app = AdkApp(agent=setup_mocks['agent'])
        
        content = types.Content(
            role="user",
            parts=[types.Part(text="Test")]
        )
        result = app._process_message_to_content(content, types)
        
        assert result is content
        assert result.role == "user"

    def test_process_message_to_content_with_part_list(self, setup_mocks):
        """Test _process_message_to_content with list of Part objects."""
        from vertexai.agent_engines.templates.adk import AdkApp
        from google.genai import types
        
        with mock.patch('vertexai.agent_engines.templates.adk.get_adk_version', return_value="1.5.0"):
            with mock.patch('vertexai.agent_engines.templates.adk.is_version_sufficient', return_value=True):
                app = AdkApp(agent=setup_mocks['agent'])
        
        parts = [
            types.Part(text="What's in this image?"),
            types.Part.from_uri(
                file_uri="gs://test-bucket/image.jpg",
                mime_type="image/jpeg"
            )
        ]
        result = app._process_message_to_content(parts, types)
        
        assert isinstance(result, types.Content)
        assert result.role == "user"
        assert result.parts == parts

    def test_process_message_to_content_with_inline_data(self, setup_mocks):
        """Test _process_message_to_content with inline binary data."""
        from vertexai.agent_engines.templates.adk import AdkApp
        from google.genai import types
        
        with mock.patch('vertexai.agent_engines.templates.adk.get_adk_version', return_value="1.5.0"):
            with mock.patch('vertexai.agent_engines.templates.adk.is_version_sufficient', return_value=True):
                app = AdkApp(agent=setup_mocks['agent'])
        
        file_bytes = b"test file content"
        parts = [
            types.Part(text="Analyze this file"),
            types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
        ]
        result = app._process_message_to_content(parts, types)
        
        assert isinstance(result, types.Content)
        assert result.role == "user"
        assert len(result.parts) == 2

    def test_process_message_to_content_invalid_type(self, setup_mocks):
        """Test that invalid types raise TypeError."""
        from vertexai.agent_engines.templates.adk import AdkApp
        from google.genai import types
        
        with mock.patch('vertexai.agent_engines.templates.adk.get_adk_version', return_value="1.5.0"):
            with mock.patch('vertexai.agent_engines.templates.adk.is_version_sufficient', return_value=True):
                app = AdkApp(agent=setup_mocks['agent'])
        
        with pytest.raises(TypeError, match="message must be a string"):
            app._process_message_to_content(12345, types)

    def test_process_message_to_content_invalid_list(self, setup_mocks):
        """Test that invalid list raises TypeError."""
        from vertexai.agent_engines.templates.adk import AdkApp
        from google.genai import types
        
        with mock.patch('vertexai.agent_engines.templates.adk.get_adk_version', return_value="1.5.0"):
            with mock.patch('vertexai.agent_engines.templates.adk.is_version_sufficient', return_value=True):
                app = AdkApp(agent=setup_mocks['agent'])
        
        # List with non-Part objects
        with pytest.raises(TypeError, match="all items must be types.Part"):
            app._process_message_to_content(["not", "parts"], types)

    @pytest.mark.asyncio
    async def test_async_stream_query_integration(self, setup_mocks):
        """Integration test for async_stream_query with different message types."""
        from vertexai.agent_engines.templates.adk import AdkApp
        from google.genai import types
        
        with mock.patch('vertexai.agent_engines.templates.adk.get_adk_version', return_value="1.5.0"):
            with mock.patch('vertexai.agent_engines.templates.adk.is_version_sufficient', return_value=True):
                app = AdkApp(agent=setup_mocks['agent'])
        
        # Mock the runner
        mock_runner = mock.MagicMock()
        mock_event = mock.MagicMock()
        mock_event.model_dump = mock.MagicMock(return_value={"event": "data"})
        
        async def mock_run_async(*args, **kwargs):
            yield mock_event
        
        mock_runner.run_async = mock_run_async
        app._tmpl_attrs['runner'] = mock_runner
        app._tmpl_attrs['session_service'] = mock.MagicMock()
        
        # Mock session creation
        mock_session = mock.MagicMock()
        mock_session.id = "test_session_123"
        app._tmpl_attrs['session_service'].create_session = mock.AsyncMock(return_value=mock_session)
        
        # Mock _utils
        with mock.patch('vertexai.agent_engines._utils.dump_event_for_json', return_value={"event": "data"}):
            # Test with string message
            events = []
            async for event in app.async_stream_query(
                user_id="test_user",
                message="Hello"
            ):
                events.append(event)
            
            assert len(events) > 0
            assert events[0] == {"event": "data"}
