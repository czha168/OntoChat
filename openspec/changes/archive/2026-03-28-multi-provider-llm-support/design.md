## Context

OntoChat currently has a hardcoded dependency on OpenAI:
- `chatbot.py` imports `from openai import OpenAI` directly
- `config.py` contains hardcoded constants: `DEFAULT_MODEL = "gpt-4o"`
- `functions.py` maintains a global `openai_api_key` variable set via UI
- `app.py` has a dedicated "Set API Key" tab in the Gradio interface

This tight coupling prevents:
1. Using local models (Ollama, vLLM, LM Studio)
2. Using alternative cloud providers (Anthropic, Groq, Mistral)
3. Self-hosting in restricted environments

The good news: Most LLM providers now implement OpenAI-compatible APIs, meaning we can support them all with minimal changes to the codebase.

## Goals / Non-Goals

**Goals:**
- Support any OpenAI-compatible provider via configuration file
- Support local models (Ollama) and cloud providers (OpenAI)
- Configuration via `config.toml` - no UI-based configuration
- Fail fast on configuration errors
- Health checks on startup to validate provider connectivity

**Non-Goals:**
- Multiple simultaneous providers (one at a time only)
- UI-based provider switching
- Provider fallback/redundancy
- Custom non-OpenAI-compatible APIs
- Streaming responses (out of scope for this change)

## Decisions

### 1. Configuration Format: TOML

**Decision:** Use TOML for configuration file.

**Rationale:**
- Python 3.11+ includes `tomllib` in stdlib (no external dependency for reading)
- Human-readable with good support for nested structures
- Commonly used in Python ecosystem (pyproject.toml)
- Supports comments for documentation

**Alternatives Considered:**
- **YAML**: More verbose, requires PyYAML dependency, whitespace-sensitive
- **JSON**: No comments, less human-readable
- **.env**: Flat structure only, can't express nested config

### 2. Provider Abstraction: OpenAI SDK with base_url

**Decision:** Use the existing OpenAI SDK directly, configuring `base_url` for non-OpenAI providers.

**Rationale:**
- Minimal code changes - just parameterize the client initialization
- Ollama, vLLM, Groq, LM Studio all expose OpenAI-compatible endpoints
- No new dependencies required
- Battle-tested SDK

**Alternatives Considered:**
- **LiteLLM**: Adds dependency, but provides unified interface for non-compatible providers like Anthropic
- **LangChain**: Overkill for this use case, adds heavy dependency
- **Custom adapter pattern**: More code to maintain for same result

### 3. Configuration Loading: File-based with env var substitution

**Decision:** Load config from `config.toml`, substitute `${ENV_VAR}` patterns with environment variables.

**Rationale:**
- Secrets stay in environment variables (security best practice)
- Config file can be committed to repo (no secrets)
- Clear separation of config and secrets

**Pattern:**
```toml
[provider]
api_key = "${OPENAI_API_KEY}"  # Substituted from environment
```

### 4. Error Handling: Fail Fast with Custom Exception

**Decision:** Create `LLMError` exception class, raise immediately on config/load errors.

**Rationale:**
- Clear error messages help users fix issues quickly
- Prevents confusing downstream errors
- Consistent error handling across the application

### 5. Health Checks: Startup Validation

**Decision:** Run connectivity check on startup before launching Gradio.

**Rationale:**
- Fails early before user attempts to use the system
- Clear error message with remediation steps
- For Ollama: Check `GET {base_url}/api/tags`
- For cloud providers: Make a minimal API call (list models or test completion)

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| **Ollama not running on startup** | Health check fails with clear message: "Ollama not reachable at http://localhost:11434. Is it running?" |
| **API key missing from environment** | Config loader validates and fails with: "OPENAI_API_KEY not set. Please set the environment variable." |
| **Invalid config.toml syntax** | Fail with parse error and line number |
| **Unknown provider name** | Validate against known providers, suggest correct names |
| **Network issues during startup** | Timeout after 5 seconds, suggest checking network |
| **Breaking change for existing users** | Document migration in README, provide sample config |

## Migration Plan

1. **Create sample config**: Add `config.sample.toml` with OpenAI and Ollama examples
2. **Update documentation**: README with setup instructions
3. **Remove UI tab**: Delete "Set API Key" tab from Gradio interface
4. **Deprecate old config**: `config.py` constants replaced by config file

**Rollback:** If issues arise, users can:
1. Revert to previous version
2. Set API key via UI (previous behavior)
