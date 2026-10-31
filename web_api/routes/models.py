"""Model configuration and providers route."""

import os
from typing import List
from fastapi import APIRouter
from web_api.schemas import ModelProviderInfo

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=List[ModelProviderInfo])
def list_model_providers() -> List[ModelProviderInfo]:
    """List available model adapters and their configuration status (no credentials exposed)."""
    has_openai_key = bool(os.getenv("REPAIRFORGE_API_KEY") or os.getenv("OPENAI_API_KEY"))
    openai_base = os.getenv("REPAIRFORGE_BASE_URL", os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    openai_model = os.getenv("REPAIRFORGE_MODEL", "gpt-4o-mini")

    current_provider = os.getenv("REPAIRFORGE_PROVIDER", "mock").lower()

    providers = [
        ModelProviderInfo(
            id="mock",
            name="Deterministic Mock Adapter",
            provider_type="mock",
            is_active=(current_provider == "mock"),
            is_deterministic=True,
            description="Predictable, rule-based fixtures for local testing and CI demonstration. Not an LLM.",
            base_url=None,
            model_name="mock-repair-model",
            status="READY",
        ),
        ModelProviderInfo(
            id="openai_compatible",
            name="OpenAI-Compatible API",
            provider_type="openai_compatible",
            is_active=(current_provider == "openai_compatible"),
            is_deterministic=False,
            description="Compatible with OpenAI, vLLM, Ollama, LocalAI, and Hugging Face TGI endpoints.",
            base_url=openai_base if not any(s in openai_base for s in ["key", "secret"]) else "configured",
            model_name=openai_model,
            status="CONFIGURED" if has_openai_key else "KEY_NOT_SET",
        ),
        ModelProviderInfo(
            id="kaggle_qwen",
            name="Qwen2.5-Coder-1.5B (Kaggle Benchmark)",
            provider_type="kaggle_experiment",
            is_active=False,
            is_deterministic=False,
            description="Open-weight code model evaluated in Kaggle notebook environment (offline benchmark).",
            base_url="Hugging Face / Kaggle GPU Runtime",
            model_name="Qwen/Qwen2.5-Coder-1.5B-Instruct",
            status="EXPERIMENT_RECORD",
        ),
    ]

    return providers

