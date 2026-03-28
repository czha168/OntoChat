"""Unit tests for ontochat.health_check module."""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from ontochat.health_check import (
    check_ollama_health,
    check_openai_health,
    check_provider_health,
    run_health_check,
    HealthCheckError,
)
from ontochat.config_loader import Config, ProviderConfig, GenerationConfig


class TestCheckOllamaHealth:
    def test_ollama_health_success(self):
        with patch('ontochat.health_check.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock(return_value=None)
            mock_get.return_value = mock_response
            result = check_ollama_health("http://localhost:11434")
            assert result is True
            mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

    def test_ollama_health_connection_error(self):
        import requests
        with patch('ontochat.health_check.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            result = check_ollama_health("http://localhost:11434")
            assert result is False

    def test_ollama_health_timeout(self):
        import requests
        with patch('ontochat.health_check.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            result = check_ollama_health("http://localhost:11434")
            assert result is False

    def test_ollama_health_other_error(self):
        with patch('ontochat.health_check.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            with pytest.raises(HealthCheckError):
                check_ollama_health("http://localhost:11434")


class TestCheckOpenaiHealth:
    def test_openai_health_success(self):
        mock_client = MagicMock()
        mock_client.models.list = MagicMock()
        with patch('openai.OpenAI', return_value=mock_client):
            result = check_openai_health("test-api-key")
            assert result is True

    def test_openai_health_missing_key(self):
        with pytest.raises(HealthCheckError):
            check_openai_health(None)

    def test_openai_health_api_error(self):
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_client.models.list.side_effect = Exception("Invalid API key")
            mock_openai.return_value = mock_client
            with pytest.raises(HealthCheckError):
                check_openai_health("invalid-key")


class TestCheckProviderHealth:
    def test_ollama_provider(self):
        config = Config(
            provider=ProviderConfig(
                name="ollama",
                api_key=None,
                base_url="http://localhost:11434",
                default_model="llama3.2"
            ),
            generation=GenerationConfig()
        )
        with patch('ontochat.health_check.check_ollama_health', return_value=True):
            result = check_provider_health(config)
            assert result is True

    def test_openai_provider(self):
        config = Config(
            provider=ProviderConfig(
                name="openai",
                api_key="test-key",
                base_url=None,
                default_model="gpt-4"
            ),
            generation=GenerationConfig()
        )
        with patch('ontochat.health_check.check_openai_health', return_value=True):
            result = check_provider_health(config)
            assert result is True

    def test_custom_provider(self):
        config = Config(
            provider=ProviderConfig(
                name="custom",
                api_key="test-key",
                base_url="http://localhost:8000/v1",
                default_model="local-model"
            ),
            generation=GenerationConfig()
        )
        mock_client = MagicMock()
        mock_client.models.list = MagicMock()
        with patch('openai.OpenAI', return_value=mock_client):
            result = check_provider_health(config)
            assert result is True


class TestRunHealthCheck:
    def test_run_health_check_success(self):
        config = Config(
            provider=ProviderConfig(
                name="ollama",
                api_key=None,
                base_url="http://localhost:11434",
                default_model="llama3.2"
            ),
            generation=GenerationConfig()
        )
        with patch('ontochat.health_check.load_config', return_value=config):
            with patch('ontochat.health_check.check_provider_health', return_value=True):
                result = run_health_check()
                assert result is True

    def test_run_health_check_with_path(self):
        config = Config(
            provider=ProviderConfig(
                name="openai",
                api_key="test-key",
                base_url=None,
                default_model="gpt-4"
            ),
            generation=GenerationConfig()
        )
        with patch('ontochat.health_check.load_config', return_value=config):
            with patch('ontochat.health_check.check_provider_health', return_value=True):
                result = run_health_check(Path("/path/to/config.toml"))
                assert result is True
