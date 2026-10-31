"""
Base abstractions for language model adapters in RepairForge AI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Role in a chat-based interaction."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """A single prompt or completion message."""
    role: MessageRole
    content: str


class ModelResponse(BaseModel):
    """Normalized response from any language model provider."""
    content: str
    model_name: str
    provider: str
    is_mock: bool = False
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseModelAdapter(ABC):
    """Abstract interface for all model adapters."""

    def __init__(self, model_name: str, **kwargs: Any) -> None:
        self.model_name = model_name
        self.extra_kwargs = kwargs

    @abstractmethod
    def generate(self, messages: List[Message], **kwargs: Any) -> ModelResponse:
        """Generate a response given a list of messages."""
        raise NotImplementedError("Subclasses must implement generate()")

    @property
    @abstractmethod
    def is_deterministic(self) -> bool:
        """Indicate whether outputs from this adapter are deterministic mocks."""
        raise NotImplementedError

