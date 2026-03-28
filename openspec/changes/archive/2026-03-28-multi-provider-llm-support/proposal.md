## Why

OntoChat currently hardcodes OpenAI as the only LLM provider, limiting users to a single cloud service. This prevents users from:
- Using local models (Ollama, vLLM) for privacy or cost savings
- Using alternative cloud providers (Anthropic, Groq, Mistral)
- Self-hosting in air-gapped environments

With the proliferation of OpenAI-compatible APIs, OntoChat should support any provider that implements the OpenAI chat completion interface.

## What Changes

- **Add TOML configuration file** (`config.toml`) for LLM provider settings
- **Remove `config.py` constants** and replace with config file loading
- **Refactor `chatbot.py`** to use provider config instead of hardcoded OpenAI client
- **Remove API key UI** from Gradio interface (configuration is file-based only)
- **Add startup health checks** to validate provider connectivity before the app starts
- **Add graceful error handling** with clear error messages when providers fail

**BREAKING**: Users will need to create a `config.toml` file instead of entering API keys in the UI.

## Capabilities

### New Capabilities
- `llm-providers`: Multi-provider LLM support via configuration file with OpenAI and Ollama providers

### Modified Capabilities
- None (this is a new capability, existing chat functionality remains the same)

## Impact

- **Configuration**: New `config.toml` file at project root
- **UI**: Removal of "Set API Key" tab from Gradio interface
- **Code**: 
  - `ontochat/config.py` - replaced with config loader
  - `ontochat/chatbot.py` - refactored for provider abstraction
  - `ontochat/functions.py` - remove global API key variable
  - `app.py` - remove API key UI components
- **Dependencies**: `tomllib` (Python 3.11+) or `tomli` for older Python versions
- **Startup**: Health check runs before Gradio launches
