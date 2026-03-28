"""
Chatbot module for OntoChat LLM provider support.

Provides chat completion functionality with support for multiple LLM providers.
"""
from dataclasses import dataclass
from typing import Optional

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from ontochat.config_loader import (
    Config,
    ConfigurationError,
    ProviderConfig,
    load_config,
)


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


@dataclass
class LLMResponse:
    """Response from LLM chat completion."""
    content: str
    model: str
    provider: str
    finish_reason: Optional[str] = None  # Why generation stopped
    usage: Optional[dict] = None  # Token usage info


def get_client(provider_config: ProviderConfig) -> OpenAI:
    """
    Get or create an OpenAI client based on provider configuration.
    
    Args:
        provider_config: Provider configuration
        
    Returns:
        Configured OpenAI client
    """
    # For OpenAI-compatible providers, use default OpenAI base URL
    # For custom providers (Ollama, vLLM, Groq, etc.), use configured base_url
    kwargs = {
        "api_key": provider_config.api_key or "dummy-key",
        "base_url": provider_config.base_url,
    }
    
    return OpenAI(**kwargs)


def chat_completion(
    provider_config: ProviderConfig,
    messages: list[dict],
    model_override: Optional[str] = None,
    temperature_override: Optional[float] = None,
    seed_override: Optional[int] = None,
) -> LLMResponse:
    """
    Send a chat completion request to the configured LLM provider.
    
    Args:
        provider_config: Provider configuration
        messages: List of message dictionaries
        model_override: Optional model to override default model
        temperature_override: Optional temperature to override default temperature
        seed_override: Optional seed to override default seed
        
    Returns:
        LLMResponse with the completion content
        
    Raises:
        LLMError: If the request fails
    """
    config = load_config()
    
    client = get_client(provider_config)
    
    # Use configured model or default
    model = model_override if model_override else config.provider.default_model
    
    # Use configured temperature and default
    temperature = temperature_override if temperature_override is not None else config.generation.temperature
    
    # Use configured seed by default
    seed = seed_override if seed_override is not None else config.generation.seed
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            seed=seed,
            temperature=temperature,
        )
    except APITimeoutError as e:
        raise LLMError(f"Request timed out. Error information: {e}")
    except APIConnectionError as e:
        raise LLMError(
            f"Connection error. Check network settings, proxy configuration, "
            f"SSL certificates, or firewall rules. Error information: {e}"
        )
    except AuthenticationError as e:
        raise LLMError(
            f"Authentication error. Your API key or token was invalid, expired, or revoked. "
            f"Error information: {e}"
        )
    except RateLimitError as e:
        raise LLMError(
            f"Rate limit exceeded. Please wait and retry. Error information: {e}"
        )
    except Exception as e:
        raise LLMError(f"Unexpected error: {e}")
    
    content = response.choices[0].message.content or ""
    return LLMResponse(
        content=content,
        model=config.provider.default_model,
        provider=config.provider.name,
        finish_reason=response.choices[0].finish_reason if response.choices else None
    )


def build_messages(history: list[dict]) -> list[dict]:
    """
    Convert Gradio Chatbot history to OpenAI client messages.
    
    :param history: List of dictionaries with 'role' and 'content' keys
    :return: List of OpenAI client messages
    """
    messages = []
    for item in history:
        messages.append({"role": item["role"], "content": item["content"]})
    return messages


__all__ = ["chat_completion", "build_messages"]