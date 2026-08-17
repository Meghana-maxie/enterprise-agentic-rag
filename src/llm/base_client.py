import abc
import json
import logging
from typing import Any, Dict

import requests
from config.settings import settings

log = logging.getLogger(__name__)


class BaseLLMClient(abc.ABC):
    """Abstract base for LLM providers used throughout the code base."""

    @abc.abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        """Return the model's raw text response for the given prompts."""
        ...


class OllamaClient(BaseLLMClient):
    """Implementation that talks to a local Ollama server.

    The model name defaults to ``settings.OLLAMA_MODEL`` (e.g. ``llama3.2:3b``).
    Logging of the request payload and the raw response is performed at INFO level.
    """

    def __init__(self, model: str | None = None):
        self.model = model or settings.OLLAMA_MODEL
        self.endpoint = "http://localhost:11434/api/chat"

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": max_tokens,
            "stream": False,
        }
        log.info("🟢 Ollama request payload → %s", json.dumps(payload))
        response = requests.post(self.endpoint, json=payload, timeout=90)
        response.raise_for_status()
        raw = response.json()
        log.info("🔵 Ollama raw response  → %s", json.dumps(raw))
        try:
            return raw["message"]["content"]
        except Exception as exc:
            raise RuntimeError(f"Unexpected Ollama response format: {raw}") from exc


class AnthropicClient(BaseLLMClient):
    """Thin wrapper around the official Anthropic SDK (kept for compatibility)."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        import anthropic

        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=settings.LLM_TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        # Anthropic returns a list of ``content`` objects; we take the first text block.
        try:
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Unexpected Anthropic response format: {response}") from e
