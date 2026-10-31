"""Unit tests for model adapters."""

import pytest
from repairforge.models.base import BaseModelAdapter, Message, MessageRole, ModelResponse
from repairforge.models.mock import MockModelAdapter
from repairforge.models.openai_compatible import (
    OpenAICompatibleModelAdapter,
    ConfigurationError,
)


def test_mock_model_adapter_deterministic():
    """Verify MockModelAdapter returns deterministic responses with mock flags."""
    adapter = MockModelAdapter(model_name="mock-test")
    assert adapter.is_deterministic is True
    assert adapter.model_name == "mock-test"

    messages = [
        Message(role=MessageRole.SYSTEM, content="Analyze root cause"),
        Message(role=MessageRole.USER, content="ZeroDivisionError in calculate_average empty list"),
    ]
    resp = adapter.generate(messages)
    assert isinstance(resp, ModelResponse)
    assert resp.is_mock is True
    assert resp.provider == "mock"
    assert "ZeroDivisionError" in resp.content
    assert adapter.generation_count == 1


def test_mock_model_adapter_patch_generation():
    """Verify MockModelAdapter returns unified diff when patch requested."""
    adapter = MockModelAdapter()
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are an automated code repair generator."),
        Message(role=MessageRole.USER, content="Generate a minimal code patch in unified diff format for average empty"),
    ]
    resp = adapter.generate(messages)
    assert resp.is_mock is True
    assert "--- a/average.py" in resp.content
    assert "+++ b/average.py" in resp.content
    assert "@@" in resp.content


def test_openai_compatible_missing_key_validation(monkeypatch):
    """Verify OpenAICompatibleModelAdapter validates missing credentials without leaking secrets."""
    monkeypatch.delenv("REPAIRFORGE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    adapter = OpenAICompatibleModelAdapter(
        model_name="gpt-4o",
        base_url="https://api.openai.com/v1",
        api_key=None,
    )
    with pytest.raises(ConfigurationError, match="API key is missing"):
        adapter.validate_configuration()

