"""
Configuration management for RepairForge AI.
Handles model provider settings, execution limits, and harness policies.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Configuration for LLM providers."""
    provider_type: str = Field(default="mock", description="Provider type: 'mock' or 'openai_compatible'")
    model_name: str = Field(default="mock-repair-model", description="Model identifier")
    base_url: Optional[str] = Field(default=None, description="API Base URL for OpenAI compatible endpoints")
    api_key: Optional[str] = Field(default=None, description="API key (never printed or logged)")
    timeout_seconds: float = Field(default=30.0, description="HTTP request timeout in seconds")
    temperature: float = Field(default=0.0, description="Sampling temperature for deterministic generation")

    @classmethod
    def from_env(cls) -> ProviderConfig:
        """Load provider configuration from environment variables."""
        provider = os.getenv("REPAIRFORGE_PROVIDER", "mock").lower()
        model_name = os.getenv("REPAIRFORGE_MODEL", "mock-repair-model")
        base_url = os.getenv("REPAIRFORGE_BASE_URL", os.getenv("OPENAI_BASE_URL"))
        api_key = os.getenv("REPAIRFORGE_API_KEY", os.getenv("OPENAI_API_KEY"))
        timeout = float(os.getenv("REPAIRFORGE_TIMEOUT", "30.0"))
        temperature = float(os.getenv("REPAIRFORGE_TEMPERATURE", "0.0"))

        return cls(
            provider_type=provider,
            model_name=model_name,
            base_url=base_url,
            api_key=api_key,
            timeout_seconds=timeout,
            temperature=temperature,
        )


class ExecutionConfig(BaseModel):
    """Configuration for test and command execution policy."""
    command_timeout_seconds: float = Field(default=60.0, description="Command execution timeout in seconds")
    max_file_size_bytes: int = Field(default=1_048_576, description="Max file size allowed to read (1MB)")
    allow_host_execution: bool = Field(default=True, description="Allow local fixture execution")
    use_docker: bool = Field(default=False, description="Use Docker container for isolated sandboxed execution")
    docker_image: str = Field(default="python:3.11-slim", description="Docker image for isolated sandbox")
    require_human_approval_for_destructive: bool = Field(default=True, description="Strict gate for write/destructive actions")


class AgentConfig(BaseModel):
    """Configuration for the Agent Orchestrator."""
    max_retries: int = Field(default=3, description="Maximum patch generation/validation retries")
    auto_approve_human_review: bool = Field(default=False, description="Automatically approve review checkpoint (for tests/demo only)")
    output_dir: Path = Field(default=Path("results"), description="Directory where reports are saved")


class AppConfig(BaseModel):
    """Top-level application configuration."""
    provider: ProviderConfig = Field(default_factory=ProviderConfig.from_env)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)

