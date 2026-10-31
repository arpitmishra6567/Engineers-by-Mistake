"""
Pydantic schemas for the Forge Command Web API.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    app_name: str = "Forge Command"
    project: str = "RepairForge AI"


class DashboardSummary(BaseModel):
    total_repairs: int = 0
    verified_repairs: int = 0
    reproduced_count: int = 0
    tests_passed: int = 0
    active_repairs: int = 0
    failed_validations: int = 0
    configured_provider: str = "mock"
    execution_mode: str = "SAFE_FIXTURE"
    recent_repairs: List[Dict[str, Any]] = Field(default_factory=list)
    recent_reports: List[Dict[str, Any]] = Field(default_factory=list)


class RepairCreateRequest(BaseModel):
    repo_path: str = Field(..., description="Path to repository")
    title: str = Field(..., description="Bug report title")
    description: str = Field(default="", description="Bug description")
    expected_behavior: str = Field(default="", description="Expected outcome")
    actual_behavior: str = Field(default="", description="Actual defect behavior")
    error_message: Optional[str] = Field(default=None, description="Observed error message")
    stack_trace: Optional[str] = Field(default=None, description="Captured traceback")
    test_command: Optional[str] = Field(default=None, description="Reproduction command")
    provider_type: str = Field(default="mock", description="'mock' or 'openai_compatible'")
    isolate_workspace: bool = Field(default=True, description="Run in temporary clone")
    auto_approve: bool = Field(default=True, description="Auto-approve human review gate for demo")


class RepairTaskResponse(BaseModel):
    task_id: str
    repo_path: str
    model_name: str
    is_mock: bool
    current_state: str
    status: str
    start_time: float
    end_time: Optional[float] = None
    duration_seconds: Optional[float] = None
    bug_report: Optional[Dict[str, Any]] = None
    repo_summary: Optional[Dict[str, Any]] = None
    reproduction_result: Optional[Dict[str, Any]] = None
    root_cause_analysis: Optional[Dict[str, Any]] = None
    patch: Optional[Dict[str, Any]] = None
    verification_result: Optional[Dict[str, Any]] = None
    state_history: List[Dict[str, Any]] = Field(default_factory=list)
    failure_reason: Optional[str] = None
    human_approved: Optional[bool] = None


class LogEntry(BaseModel):
    timestamp: float
    level: str
    stage: str
    message: str


class RepairLogsResponse(BaseModel):
    task_id: str
    logs: List[LogEntry] = Field(default_factory=list)


class EvaluationItem(BaseModel):
    id: str
    source_type: str  # "Kaggle Experiment" | "Local Repair Run"
    project: str
    experiment: str
    model: str
    inference_time_seconds: Optional[float] = None
    bugs_attempted: int
    bugs_reproduced: int
    patches_generated: int
    patches_verified: int
    baseline_tests_passed: int
    patched_tests_passed: int
    total_tests: int
    repair_status: str
    baseline_results: List[Dict[str, Any]] = Field(default_factory=list)
    patched_results: List[Dict[str, Any]] = Field(default_factory=list)
    patch: Optional[str] = None
    timestamp: Optional[float] = None


class RepositoryInspectResponse(BaseModel):
    root_path: str
    total_files: int
    languages: List[str]
    has_git: bool
    has_tests: bool
    test_framework: Optional[str]
    dependency_files: List[str]
    source_files: List[str]


class ModelProviderInfo(BaseModel):
    id: str
    name: str
    provider_type: str
    is_active: bool
    is_deterministic: bool
    description: str
    base_url: Optional[str] = None
    model_name: str
    status: str


class SkillInfo(BaseModel):
    name: str
    description: str
    valid: bool
    skill_file_path: str
    phases: List[str]
    security_rules: List[str]
    supporting_resources: List[str]

