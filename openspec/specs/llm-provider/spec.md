## ADDED Requirements

### Requirement: System loads LLM provider configuration from config.toml
The system SHALL load provider configuration from a `config.toml` file at application startup.
The system SHALL support environment variable substitution in config values (e.g., `${OPENAI_API_KEY}`).
            The system SHALL validate the configuration file exists and is valid TOML.
            The system SHALL fail fast with a clear error message if configuration is invalid or missing.

#### Scenario: Valid config file loads successfully
- **WHEN** a valid `config.toml` file exists with proper provider configuration
- **THEN** the system loads the configuration without errors
- **THEN** the provider client is initialized with the configured settings

#### Scenario: missing config file raises error
- **WHEN** no `config.toml` file exists
- **THEN** the system raises `ConfigurationError` with message "config.toml not found"
- **THEN** the application exits with non-zero status

#### Scenario: invalid TOML syntax raises error
- **WHEN** `config.toml` has invalid TOML syntax
- **THEN** the system raises `ConfigurationError` with parse error details
- **THEN** the application exits with non-zero status

#### Scenario: environment variable substitution works
- **WHEN** config contains `api_key = "${OPENAI_API_KEY}"`
- **AND** environment variable `OPENAI_API_KEY` is set to `sk-test123`
- **THEN** the loaded config has `api_key = "sk-test123"`

### Requirement: System supports multiple LLM providers
The system SHALL support at minimum OpenAI and Ollama providers.
            The system SHALL use OpenAI-compatible API interface for all providers.
            The system SHALL allow configuration of base_url for custom endpoints.

#### Scenario: OpenAI provider works
- **WHEN** provider is configured as "openai" with valid API key
- **THEN** the system uses OpenAI's default base URL
- **THEN** chat completion requests go to OpenAI API

#### Scenario: Ollama provider works
- **WHEN** provider is configured as "ollama" with base_url "http://localhost:11434"
- **THEN** the system uses Ollama's OpenAI-compatible endpoint
- **THEN** chat completion requests go to local Ollama instance

#### Scenario: custom base_url works
- **WHEN** provider is configured with custom base_url (e.g., "http://localhost:8000/v1")
- **THEN** the system uses the custom base URL for API calls

### Requirement: System performs health checks on startup
            The system SHALL validate provider connectivity before launching the application.
            The system SHALL fail fast if the provider is unreachable.
            The system SHALL display a helpful error message when health check fails.

#### Scenario: Ollama health check succeeds
- **WHEN** provider is "ollama" and Ollama is running at configured base_url
- **THEN** health check passes
- **THEN** application starts normally

#### Scenario: ollama health check fails
- **WHEN** provider is "ollama" and Ollama is not running
- **THEN** health check fails with message "Cannot connect to Ollama at http://localhost:11434. Is Ollama running?"
- **THEN** application exits with non-zero status

#### Scenario: cloud provider health check succeeds
- **WHEN** provider is "openai" with valid API key
- **THEN** system makes a minimal API call (list models or test completion)
- **THEN** health check passes
- **THEN** application starts normally

### Requirement: System removes API key UI
            The system SHALL NOT display any API key input UI.
            The system SHALL load API keys exclusively from configuration.

#### Scenario: no API key UI shown
- **WHEN** application starts
- **THEN** the Gradio interface does not include an API key input tab
- **THEN** the interface starts directly at the user story tab

### Requirement: System provides sample configuration file
            The system SHALL include a `config.sample.toml` file with example configurations.
            The sample file SHALL include OpenAI and Ollama examples.
            The sample file SHALL use placeholder values that need to be replaced.

#### Scenario: sample config exists
- **WHEN** user checks out the repository
- **THEN** `config.sample.toml` exists with OpenAI and Ollama configurations
- **THEN** sample file contains comments explaining how to configure
