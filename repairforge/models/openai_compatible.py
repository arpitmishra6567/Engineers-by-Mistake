"""
OpenAI-compatible API model adapter for interchangeable inference backends.
Compatible with OpenAI, vLLM, Ollama, LocalAI, and Hugging Face TGI endpoints.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from repairforge.models.base import BaseModelAdapter, Message, ModelResponse

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required API credentials or URLs are missing."""
    pass


class ModelInferenceError(Exception):
    """Raised when remote model inference fails or times out."""
    pass


class OpenAICompatibleModelAdapter(BaseModelAdapter):
    """
    Adapter for endpoints supporting the standard OpenAI /v1/chat/completions format.
    Credentials and URLs are retrieved from configuration or environment variables.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_seconds: float = 30.0,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> None:
        resolved_model = model_name or os.getenv("REPAIRFORGE_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        super().__init__(model_name=resolved_model, **kwargs)

        self.base_url = (
            base_url
            or os.getenv("REPAIRFORGE_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")

        self._api_key = (
            api_key
            or os.getenv("REPAIRFORGE_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        self.timeout_seconds = timeout_seconds
        self.temperature = temperature

    @property
    def is_deterministic(self) -> bool:
        return False

    def validate_configuration(self) -> None:
        """Validate that required parameters are provided without logging secrets."""
        if not self._api_key:
            # Some local endpoints (Ollama / LocalAI) do not require keys, but cloud endpoints do
            if "localhost" not in self.base_url and "127.0.0.1" not in self.base_url:
                raise ConfigurationError(
                    "API key is missing. Set the REPAIRFORGE_API_KEY or OPENAI_API_KEY "
                    "environment variable, or pass api_key to the adapter."
                )

    def generate(self, messages: List[Message], **kwargs: Any) -> ModelResponse:
        """
        Send chat completion request to the OpenAI-compatible endpoint.
        Uses httpx to minimize heavy dependencies.
        """
        self.validate_configuration()

        try:
            import httpx
        except ImportError as e:
            raise ImportError(
                "httpx is required for OpenAICompatibleModelAdapter. "
                "Install it with `pip install httpx`."
            ) from e

        headers = {
            "Content-Type": "application/json",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "temperature": kwargs.get("temperature", self.temperature),
        }

        endpoint = f"{self.base_url}/chat/completions"
        logger.info("Calling model endpoint: %s with model: %s", endpoint, self.model_name)

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

            choice = data["choices"][0]
            content = choice["message"]["content"]
            usage = data.get("usage", {})

            return ModelResponse(
                content=content,
                model_name=self.model_name,
                provider="openai_compatible",
                is_mock=False,
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                raw_response=data,
            )
        except httpx.TimeoutException as e:
            raise ModelInferenceError(
                f"Model request to {self.base_url} timed out after {self.timeout_seconds}s"
            ) from e
        except httpx.HTTPStatusError as e:
            # Never include request headers (which may have Authorization) in the error string
            raise ModelInferenceError(
                f"Model request failed with status code {e.response.status_code}: {e.response.text}"
            ) from e
        except Exception as e:
            raise ModelInferenceError(f"Inference error: {type(e).__name__}: {str(e)}") from e

