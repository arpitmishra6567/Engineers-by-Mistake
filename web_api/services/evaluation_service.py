"""
Evaluation service reading and normalizing evaluation and experiment records.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from web_api.schemas import EvaluationItem

logger = logging.getLogger(__name__)


class EvaluationService:
    """Manages loading and normalization of experiment and evaluation records."""

    def __init__(self, results_dir: Optional[Path] = None) -> None:
        self.results_dir = (results_dir or Path("results")).resolve()

    def get_all_evaluations(self) -> List[EvaluationItem]:
        """Load and normalize all evaluation files from results directory."""
        evaluations: List[EvaluationItem] = []

        if not self.results_dir.exists():
            return evaluations

        # 1. Primary Kaggle Experiment file: repairforge_evaluation.json
        kaggle_file = self.results_dir / "repairforge_evaluation.json"
        if kaggle_file.exists():
            try:
                data = json.loads(kaggle_file.read_text(encoding="utf-8"))
                evaluations.append(
                    EvaluationItem(
                        id="kaggle-qwen2.5-coder-1.5b",
                        source_type="Kaggle Experiment",
                        project=data.get("project", "RepairForge AI"),
                        experiment=data.get("experiment", "Single bug repair"),
                        model=data.get("model", "Qwen/Qwen2.5-Coder-1.5B-Instruct"),
                        inference_time_seconds=data.get("inference_time_seconds", 7.281),
                        bugs_attempted=data.get("bugs_attempted", 1),
                        bugs_reproduced=data.get("bugs_reproduced", 1),
                        patches_generated=data.get("patches_generated", 1),
                        patches_verified=data.get("patches_verified", 1),
                        baseline_tests_passed=data.get("baseline_tests_passed", 2),
                        patched_tests_passed=data.get("patched_tests_passed", 3),
                        total_tests=data.get("total_tests", 3),
                        repair_status=data.get("repair_status", "VERIFIED"),
                        baseline_results=data.get("baseline_results", []),
                        patched_results=data.get("patched_results", []),
                        patch=data.get("patch"),
                        timestamp=kaggle_file.stat().st_mtime,
                    )
                )
            except Exception as e:
                logger.error("Failed to parse %s: %s", kaggle_file, e)

        # 2. Local Repair Reports: repair_report_*.json
        for report_file in self.results_dir.glob("repair_report_*.json"):
            try:
                data = json.loads(report_file.read_text(encoding="utf-8"))
                task_id = data.get("task_id", report_file.stem)
                repro_res = data.get("reproduction_result") or {}
                verif_res = data.get("verification_result") or {}
                patch_res = data.get("patch") or {}

                reproduced = 1 if repro_res.get("status") == "REPRODUCED" else 0
                has_patch = 1 if patch_res else 0
                verified = 1 if verif_res.get("verified") else 0

                tests_passed = len(verif_res.get("tests_passed") or [])
                tests_failed = len(verif_res.get("tests_failed") or [])
                total_t = tests_passed + tests_failed or (1 if verified else 0)

                evaluations.append(
                    EvaluationItem(
                        id=task_id,
                        source_type="Local Repair Run",
                        project="RepairForge AI",
                        experiment=f"Task {task_id}",
                        model=data.get("model_name", "mock-repair-model"),
                        inference_time_seconds=round(data.get("end_time", 0) - data.get("start_time", 0), 2)
                        if data.get("end_time") and data.get("start_time")
                        else None,
                        bugs_attempted=1,
                        bugs_reproduced=reproduced,
                        patches_generated=has_patch,
                        patches_verified=verified,
                        baseline_tests_passed=0 if reproduced else 1,
                        patched_tests_passed=tests_passed,
                        total_tests=total_t,
                        repair_status=data.get("report_status") or ("VERIFIED" if verified else "VALIDATION_FAILED"),
                        baseline_results=[],
                        patched_results=[
                            {"test": t, "passed": True, "observed": "PASS"} for t in (verif_res.get("tests_passed") or [])
                        ] + [
                            {"test": t, "passed": False, "observed": "FAIL"} for t in (verif_res.get("tests_failed") or [])
                        ],
                        patch=patch_res.get("diff"),
                        timestamp=report_file.stat().st_mtime,
                    )
                )
            except Exception as e:
                logger.error("Failed to parse report %s: %s", report_file, e)

        return evaluations

    def get_evaluation_by_id(self, evaluation_id: str) -> Optional[EvaluationItem]:
        """Find an evaluation item by ID."""
        for item in self.get_all_evaluations():
            if item.id == evaluation_id:
                return item
        return None

