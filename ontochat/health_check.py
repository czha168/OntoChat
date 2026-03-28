"""
Health check module for OntoChat LLM provider support.

Validates provider connectivity before the application starts.
"""
from pathlib import Path
from typing import Optional, Union

import requests

from ontochat.config_loader import Config, ConfigurationError, load_config


class HealthCheckError(Exception):
    """Raised when provider health check fails."""
    pass


def check_ollama_health(base_url: str, timeout: int = 5) -> bool:
    """
    Check if Ollama is running and accessible.
    
    Args:
        base_url: Ollama base URL (e.g., http://localhost:11434 or http://localhost:11434/v1)
        timeout: Timeout in seconds
        
    Returns:
        True if Ollama is healthy, False otherwise
    """
    try:
        # Strip /v1 suffix if present (OpenAI-compatible endpoint)
        # Ollama's native API is at the base URL without /v1
        url = base_url.rstrip('/')
        if url.endswith('/v1'):
            url = url[:-3]
        url = f"{url}/api/tags"
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return True
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.Timeout:
        return False
    except Exception as e:
        raise HealthCheckError(
            f"Failed to connect to Ollama at {base_url}: {e}"
        )


def check_openai_health(api_key: str, timeout: int = 5) -> bool:
    """
    Check if OpenAI is accessible with valid credentials.
    
    Args:
        api_key: OpenAI API key
        timeout: Timeout in seconds
        
    Returns:
        True if OpenAI is healthy, False otherwise
    """
    if not api_key:
        raise HealthCheckError("OpenAI API key is required but not provided")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        client.models.list(timeout=timeout)
        return True
    except Exception as e:
        raise HealthCheckError(
            f"Failed to connect to OpenAI API: {e}"
        )


def check_provider_health(config: Config, timeout: int = 5) -> bool:
    """
    Check provider health based on configuration.
    
    Supports:
    - OpenAI: Makes a minimal API call
    - Ollama: Checks /api/tags endpoint
    - Other providers: Makes a minimal API call
    
    Args:
        config: OntoChat configuration object
        timeout: Timeout in seconds
        
    Returns:
        True if provider is healthy
        
    Raises:
        HealthCheckError: If provider is unreachable
        ConfigurationError: If configuration is invalid
    """
    provider_name = config.provider.name
    
    if provider_name == "ollama":
        base_url = config.provider.base_url or "http://localhost:11434"
        return check_ollama_health(base_url, timeout)
    
    elif provider_name == "openai":
        api_key = config.provider.api_key
        if not api_key:
            raise ConfigurationError(
                "OpenAI provider requires 'api_key' in configuration"
            )
        return check_openai_health(api_key, timeout)
    
    else:
        base_url = config.provider.base_url
        api_key = config.provider.api_key or "dummy-key"
        
        try:
            from openai import OpenAI
            
            if base_url:
                client = OpenAI(api_key=api_key, base_url=base_url)
            else:
                client = OpenAI(api_key=api_key)
            
            client.models.list(timeout=float(timeout))
            return True
        except Exception as e:
            endpoint = base_url if base_url else "OpenAI API"
            raise HealthCheckError(
                f"Failed to connect to {provider_name} at {endpoint}: {e}"
            )


def run_health_check(config_path: Optional[Union[str, Path]] = None) -> bool:
    """
    Run health checks before starting the application.
    
    Args:
        config_path: Optional path to config file. If None, uses default search.
    
    Returns:
        True if health check passes
        
    Raises:
        HealthCheckError: If health check fails
        ConfigurationError: If configuration is invalid
    """
    path = Path(config_path) if isinstance(config_path, str) else config_path
    config = load_config(path)
    
    print(f"Running health checks for provider: {config.provider.name}...")
    
    result = check_provider_health(config)
    
    if result:
        print("✓ Health check passed - provider is ready")
    
    return result
