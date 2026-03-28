"""
Configuration loader for OntoChat LLM provider support.

Handles loading TOML configuration files with environment variable substitution.
"""
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# Python 3.11+ has tomllib in stdlib, otherwise use tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    name: str
    api_key: Optional[str]
    base_url: Optional[str]
    default_model: str

    def __post_init__(self):
        # Validate provider name
        valid_providers = {"openai", "ollama", "vllm", "groq", "mistral", "custom"}
        if self.name not in valid_providers:
            raise ConfigurationError(
                f"Invalid provider '{self.name}'. Must be one of: {', '.join(sorted(valid_providers))}"
            )


@dataclass
class GenerationConfig:
    """Generation parameters for LLM calls."""
    temperature: float = 0.0
    seed: int = 1234


@dataclass
class Config:
    """Full configuration for OntoChat."""
    provider: ProviderConfig
    generation: GenerationConfig


def _substitute_env_vars(value: str) -> str:
    """
    Substitute environment variables in a string.
    
    Supports ${ENV_VAR} syntax.
    
    Args:
        value: String potentially containing ${ENV_VAR} patterns
        
    Returns:
        String with environment variables substituted
        
    Raises:
        ConfigurationError: If referenced env var is not set
    """
    if not value:
        return value
    
    pattern = re.compile(r'\$\{([^}]+)\}')
    
    def replace(match):
        env_var = match.group(1)
        env_value = os.environ.get(env_var)
        if env_value is None:
            raise ConfigurationError(
                f"Environment variable '{env_var}' is not set. "
                f"Please set it before running OntoChat."
            )
        return env_value
    
    return pattern.sub(replace, value)


def _find_config_file() -> Path:
    """
    Find the configuration file.
    
    Looks for config.toml in:
    1. Current working directory
    2. Project root directory (where app.py is located)
    
    Returns:
        Path to the configuration file
        
    Raises:
        ConfigurationError: If config file is not found
    """
    # Try current directory first
    config_path = Path("config.toml")
    if config_path.exists():
        return config_path
    
    # Try project root (where app.py is located)
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config.toml"
    if config_path.exists():
        return config_path
    
    raise ConfigurationError(
        "config.toml not found. "
        "Please copy config.sample.toml to config.toml and configure it."
    )


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load and validate configuration from a TOML file.
    
    Args:
        config_path: Path to config.toml. If None, searches for config file.
        
    Returns:
        Validated Config object
        
    Raises:
        ConfigurationError: If config file is missing, invalid, or has missing required fields
    """
    if config_path is None:
        config_path = _find_config_file()
    
    try:
        with open(config_path, "rb") as f:
            raw_config = tomllib.load(f)
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    except Exception as e:
        raise ConfigurationError(f"Failed to parse config.toml: {e}")
    
    # Validate required sections
    if "provider" not in raw_config:
        raise ConfigurationError("Missing [provider] section in config.toml")
    
    provider_data = raw_config["provider"]
    
    # Extract and substitute provider config
    provider_name = provider_data.get("name")
    if not provider_name:
        raise ConfigurationError("Missing 'name' in [provider] section")
    
    api_key = provider_data.get("api_key")
    if api_key:
        api_key = _substitute_env_vars(api_key)
    
    base_url = provider_data.get("base_url")
    if base_url:
        base_url = _substitute_env_vars(base_url)
    
    default_model = provider_data.get("default_model")
    if not default_model:
        raise ConfigurationError("Missing 'default_model' in [provider] section")
    
    provider_config = ProviderConfig(
        name=provider_name,
        api_key=api_key,
        base_url=base_url,
        default_model=default_model
    )
    
    # Load generation config with defaults
    gen_data = raw_config.get("generation", {})
    generation_config = GenerationConfig(
        temperature=gen_data.get("temperature", 0.0),
        seed=gen_data.get("seed", 1234)
    )
    
    return Config(
        provider=provider_config,
        generation=generation_config
    )


def get_provider_config() -> ProviderConfig:
    """
    Get the current provider configuration.
    
    This is a convenience function that loads the config and returns
    just the provider portion.
    
    Returns:
        ProviderConfig object
    """
    return load_config().provider


def get_generation_config() -> GenerationConfig:
    """
    Get the generation configuration.
    
    Returns:
        GenerationConfig object
    """
    return load_config().generation
