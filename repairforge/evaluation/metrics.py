"""
Evaluation metrics calculation from actual execution records.
"""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field

from repairforge.agent.context import ExecutionContext


class ExecutionMetrics(BaseModel):
    """Aggregated evaluation metrics computed across one or more tasks."""
    total_tasks: int = 0
    reproduced_count: int = 0
    verified_count: int = 0
    failed_validation_count: int = 0
    reproduction_rate: float = 0.0
    repair_success_rate: float = 0.0
    average_duration_seconds: float = 0.0
    models_evaluated: List[str] = Field(default_factory=list)


class MetricsCalculator:
    """Calculates factual evaluation metrics from real execution contexts."""

    @staticmethod
    def calculate(contexts: List[ExecutionContext]) -> ExecutionMetrics:
        """Compute metrics without inventing numbers or benchmarks."""
        if not contexts:
            return ExecutionMetrics()

        total = len(contexts)
        reproduced = sum(1 for c in contexts if c.reproduction_result and c.reproduction_result.status == "REPRODUCED")
        verified = sum(1 for c in contexts if c.verification_result and c.verification_result.verified)
        failed_val = sum(1 for c in contexts if c.verification_result and not c.verification_result.verified)

        durations = [
            (c.end_time - c.start_time) for c in contexts if c.end_time and c.end_time >= c.start_time
        ]
        avg_dur = sum(durations) / len(durations) if durations else 0.0

        models = sorted(list({c.model_name for c in contexts}))

        return ExecutionMetrics(
            total_tasks=total,
            reproduced_count=reproduced,
            verified_count=verified,
            failed_validation_count=failed_val,
            reproduction_rate=(reproduced / total) if total > 0 else 0.0,
            repair_success_rate=(verified / total) if total > 0 else 0.0,
            average_duration_seconds=round(avg_dur, 2),
            models_evaluated=models,
        )

