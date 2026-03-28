"""Unit tests for ontochat.ontolib module."""
import pytest
from unittest.mock import patch, MagicMock

from ontochat.ontolib import (
    ChatInterface,
    extract_competency_questions,
    test_competency_questions as validate_competency_questions,
    cqe_prompt_a,
    cqt_prompt_a,
)
from ontochat.config_loader import ProviderConfig, GenerationConfig


class TestChatInterface:
    def test_chat_interface_init_with_provider_config(self):
        provider_config = ProviderConfig(
            name="openai",
            api_key="test-key",
            base_url=None,
            default_model="gpt-4"
        )
        
        with patch('ontochat.ontolib.load_config') as mock_load:
            mock_config = MagicMock()
            mock_config.provider = provider_config
            mock_config.provider.default_model = "gpt-4"
            mock_load.return_value = mock_config
            
            with patch('ontochat.ontolib.get_generation_config') as mock_gen:
                mock_gen.return_value = GenerationConfig(temperature=0.5, seed=42)
                
                interface = ChatInterface()
                assert interface.model_name == "gpt-4"
                assert interface.sampling_seed == 42
                assert interface.temperature == 0.5

    def test_chat_interface_init_with_model_override(self):
        provider_config = ProviderConfig(
            name="openai",
            api_key="test-key",
            base_url=None,
            default_model="gpt-4"
        )
        
        with patch('ontochat.ontolib.load_config') as mock_load:
            mock_config = MagicMock()
            mock_config.provider = provider_config
            mock_load.return_value = mock_config
            
            with patch('ontochat.ontolib.get_generation_config') as mock_gen:
                mock_gen.return_value = GenerationConfig()
                
                interface = ChatInterface(model_name="gpt-3.5-turbo")
                assert interface.model_name == "gpt-3.5-turbo"

    def test_chat_completion(self):
        provider_config = ProviderConfig(
            name="openai",
            api_key="test-key",
            base_url=None,
            default_model="gpt-4"
        )
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('ontochat.ontolib.load_config') as mock_load:
            mock_config = MagicMock()
            mock_config.provider = provider_config
            mock_load.return_value = mock_config
            
            with patch('ontochat.ontolib.get_generation_config') as mock_gen:
                mock_gen.return_value = GenerationConfig()
                
            with patch('ontochat.ontolib.OpenAI', return_value=mock_client):
                interface = ChatInterface()
                result = interface.chat_completion([{"role": "user", "content": "test"}])
                assert result == "Test response"


class TestPrompts:
    def test_cqe_prompt_a_exists(self):
        assert len(cqe_prompt_a) > 0
        assert "competency questions" in cqe_prompt_a.lower()

    def test_cqt_prompt_a_exists(self):
        assert len(cqt_prompt_a) > 0
        assert "Yes, No" in cqt_prompt_a


class TestExtractCompetencyQuestions:
    def test_extract_competency_questions(self):
        provider_config = ProviderConfig(
            name="openai",
            api_key="test-key",
            base_url=None,
            default_model="gpt-4"
        )
        
        mock_interface = MagicMock()
        mock_interface.chat_completion.return_value = "1. What is X?\n2. What is Y?"
        
        with patch('ontochat.ontolib.ChatInterface', return_value=mock_interface):
            result = extract_competency_questions("Sample ontology verbalisation", mock_interface)
            assert "What is" in result


class TestTestCompetencyQuestions:
    def test_test_competency_questions(self):
        provider_config = ProviderConfig(
            name="openai",
            api_key="test-key",
            base_url=None,
            default_model="gpt-4"
        )
        
        mock_interface = MagicMock()
        mock_interface.chat_completion.return_value = "Yes, the ontology can address this question."
        
        with patch('ontochat.ontolib.ChatInterface', return_value=mock_interface):
            result = validate_competency_questions(
                "Sample ontology",
                ["What is X?"],
                mock_interface
            )
            assert "What is X?" in result
            assert result["What is X?"][0] == "Yes"
