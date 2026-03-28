"""Unit tests for ontochat.chatbot module."""
import pytest
from unittest.mock import patch, MagicMock
from ontochat.chatbot import (
    chat_completion,
    build_messages,
    get_client,
    LLMError,
    LLMResponse,
)
from ontochat.config_loader import ProviderConfig, GenerationConfig


class TestGetClient:
    def test_get_client_with_api_key(self):
        config = ProviderConfig(
            name="openai",
            api_key="sk-test-key",
            base_url=None,
            default_model="gpt-4"
        )
        client = get_client(config)
        assert client is not None

    def test_get_client_with_base_url(self):
        config = ProviderConfig(
            name="ollama",
            api_key=None,
            base_url="http://localhost:11434/v1",
            default_model="llama3.2"
        )
        client = get_client(config)
        assert client is not None

    def test_get_client_with_dummy_key(self):
        config = ProviderConfig(
            name="ollama",
            api_key=None,
            base_url="http://localhost:11434/v1",
            default_model="llama3.2"
        )
        client = get_client(config)
        assert client is not None


class TestBuildMessages:
    def test_build_messages_empty(self):
        result = build_messages([])
        assert result == []

    def test_build_messages_single(self):
        history = [{"role": "user", "content": "Hello"}]
        result = build_messages(history)
        assert len(result) == 1
        assert result[0] == {"role": "user", "content": "Hello"}

    def test_build_messages_multiple(self):
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        result = build_messages(history)
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"


class TestChatCompletion:
    def test_chat_completion_success(self):
        provider_config = ProviderConfig(
            name="openai",
            api_key="test-key",
            base_url=None,
            default_model="gpt-4"
        )
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('ontochat.chatbot.get_client', return_value=mock_client):
            with patch('ontochat.chatbot.load_config') as mock_load_config:
                mock_config = MagicMock()
                mock_config.provider.default_model = "gpt-4"
                mock_config.generation.temperature = 0.0
                mock_config.generation.seed = 1234
                mock_load_config.return_value = mock_config
                
                result = chat_completion(provider_config, [{"role": "user", "content": "test"}])
                
                assert isinstance(result, LLMResponse)
                assert result.content == "Test response"

    def test_chat_completion_timeout_error(self):
        provider_config = ProviderConfig(
            name="openai",
            api_key="test-key",
            base_url=None,
            default_model="gpt-4"
        )
        
        from openai import APITimeoutError
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = APITimeoutError("Timeout")
        
        with patch('ontochat.chatbot.get_client', return_value=mock_client):
            with patch('ontochat.chatbot.load_config') as mock_load_config:
                mock_config = MagicMock()
                mock_config.provider.default_model = "gpt-4"
                mock_config.generation.temperature = 0.0
                mock_config.generation.seed = 1234
                mock_load_config.return_value = mock_config
                
                with pytest.raises(LLMError) as exc_info:
                    chat_completion(provider_config, [{"role": "user", "content": "test"}])
                assert "timed out" in str(exc_info.value).lower()

    def test_chat_completion_connection_error(self):
        provider_config = ProviderConfig(
            name="openai",
            api_key="test-key",
            base_url=None,
            default_model="gpt-4"
        )
        
        from openai import APIConnectionError
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = APIConnectionError(request=None)
        
        with patch('ontochat.chatbot.get_client', return_value=mock_client):
            with patch('ontochat.chatbot.load_config') as mock_load_config:
                mock_config = MagicMock()
                mock_config.provider.default_model = "gpt-4"
                mock_config.generation.temperature = 0.0
                mock_config.generation.seed = 1234
                mock_load_config.return_value = mock_config
                
                with pytest.raises(LLMError) as exc_info:
                    chat_completion(provider_config, [{"role": "user", "content": "test"}])
                assert "Connection error" in str(exc_info.value)


class TestLLMResponse:
    def test_llm_response_creation(self):
        response = LLMResponse(
            content="Test content",
            model="gpt-4",
            provider="openai"
        )
        assert response.content == "Test content"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.finish_reason is None
        assert response.usage is None

    def test_llm_response_with_all_fields(self):
        response = LLMResponse(
            content="Test",
            model="gpt-4",
            provider="openai",
            finish_reason="stop",
            usage={"prompt_tokens": 10, "completion_tokens": 20}
        )
        assert response.finish_reason == "stop"
        assert response.usage["prompt_tokens"] == 10
