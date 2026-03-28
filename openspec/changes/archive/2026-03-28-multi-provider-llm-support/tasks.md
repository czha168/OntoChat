# Multi-Provider LLM Support - Task List

## 1. Config setup

- [x] 1.1 Create `config.sample.toml` with sample configurations for OpenAI and Ollama
- [x] 1.2 Update `requirements.txt` if needed for `tomli` and `requests` packages
- [x] 1.3 Add `.gitignore` entry for `config.toml` (keep secrets out of version control)

## 2. Config loader

- [x] 2.1 Create `ontochat/config_loader.py` with `load_config()` function
- [x] 2.2 Implement environment variable substitution
- [x] 2.3 Implement configuration validation
- [x] 2.4 Add `get_provider_config()` function to return current provider config
- [x] 2.5 Add `LLMError` exception class in `chatbot.py`
- [x] 2.6 Add unit tests for config loader

## 3. Health checks

- [x] 3.1 Create `ontochat/health_check.py` with `check_provider_health()` function
- [x] 3.2 Implement Ollama health check (GET /api/tags)
- [x] 3.3 Implement OpenAI health check (minimal API call)
- [x] 3.4 Add connection timeout handling
- [x] 3.5 Add error messages for common failure scenarios
- [x] 3.6 Add unit tests for health checks

## 4. chatbot refactor

- [x] 4.1 Update `ontochat/chatbot.py` to use provider config
- [x] 4.2 Create `get_client()` function using `base_url` and `api_key`
- [x] 4.3 Update `chat_completion()` to accept `provider_config` parameter
- [x] 4.4 Update error handling to use `LLMError`
- [x] 4.5 Remove hardcoded OpenAI-specific exception imports (keep generic Exception)
- [x] 4.6 Update `build_messages()` function (no changes needed)
- [x] 4.7 Add unit tests for chatbot

## 5. functions refactor

- [x] 5.1 Remove global `openai_api_key` variable from `ontochat/functions.py`
- [x] 5.2 Remove `set_openai_api_key()` function
- [x] 5.3 Remove `check_api_key()` function
- [x] 5.4 Update `user_story_generator()` to use config loader
- [x] 5.5 Update all functions using chat_completion to pass provider config
- [x] 5.6 Add unit tests for functions

## 6. app UI update

- [x] 6.1 Remove `set_api_key` Gradio Blocks from `app.py`
- [x] 6.2 Remove API key textbox and button
- [x] 6.3 Update `demo` TabbedInterface to remove "Set API Key" tab
- [x] 6.4 Add startup health check before Gradio launch
- [x] 6.5 Add configuration error handling on startup
- [x] 6.6 Update main block to load config on startup

## 7. ontolib update

- [x] 7.1 Update `ontochat/ontolib.py` `ChatInterface` class to use provider config
- [x] 7.2 Update `__init__` to accept provider config instead of API key
- [x] 7.3 Replace hardcoded model names with config values
- [x] 7.4 Update methods to use provider config
- [x] 7.5 Add unit tests for ontolib

## 8. config cleanup

- [x] 8.1 Delete or update `ontochat/config.py` (replace with config_loader.py)
- [x] 8.2 Keep only if needed for backward compatibility
- [x] 8.3 Ensure all imports point to config_loader.py

## 9. Documentation

- [x] 9.1 Update README.md with new setup instructions
- [x] 9.2 Add configuration section explaining config.toml
- [x] 9.3 Add example provider configurations
- [x] 9.4 Document migration from old config.py

## 10. Testing

- [x] 10.1 Run full test suite after changes
- [ ] 10.2 Verify OpenAI provider still works (requires API key)
- [ ] 10.3 Verify Ollama provider works (requires Ollama running)
- [x] 10.4 Test error handling for missing config (covered by unit tests)
- [x] 10.5 Test error handling for invalid config (covered by unit tests)
