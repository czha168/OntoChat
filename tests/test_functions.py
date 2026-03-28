"""Unit tests for ontochat.functions module."""
import pytest
from unittest.mock import patch, MagicMock

from ontochat.functions import user_story_generator, load_example, current_preidentified


class TestLoadExample:
    def test_load_example_first(self):
        result = load_example(0)
        assert result == current_preidentified[0]

    def test_load_example_second(self):
        result = load_example(1)
        assert result == current_preidentified[1]

    def test_load_example_index_out_of_range(self):
        with pytest.raises(IndexError):
            load_example(100)

    def test_current_preidentified_has_expected_count(self):
        assert len(current_preidentified) == 9


class TestUserStoryGenerator:
    def test_user_story_generator_basic(self):
        mock_response = MagicMock()
        mock_response.content = "Hello! How can I help you today?"
        
        with patch('ontochat.functions.chat_completion') as mock_completion:
            mock_completion.return_value = mock_response
            
            with patch('ontochat.functions.load_config') as mock_config:
                mock_config_instance = MagicMock()
                mock_config_instance.provider = MagicMock()
                mock_config.return_value = mock_config_instance
                
                history = []
                result, empty = user_story_generator("Hello", history)
                
                assert len(result) == 2
                assert result[0]["role"] == "user"
                assert result[0]["content"] == "Hello"
                assert result[1]["role"] == "assistant"
                assert empty == ""

    def test_user_story_generator_with_history(self):
        mock_response = MagicMock()
        mock_response.content = "Great question!"
        
        with patch('ontochat.functions.chat_completion') as mock_completion:
            mock_completion.return_value = mock_response
            
            with patch('ontochat.functions.load_config') as mock_config:
                mock_config_instance = MagicMock()
                mock_config_instance.provider = MagicMock()
                mock_config.return_value = mock_config_instance
                
                history = [{"role": "user", "content": "Previous message"}]
                result, empty = user_story_generator("New message", history)
                
                assert len(result) == 3
                assert result[0]["role"] == "user"
                assert result[0]["content"] == "Previous message"
                assert result[1]["role"] == "user"
                assert result[1]["content"] == "New message"
